import os
from datetime import date, datetime, timedelta
import re
from dateutil.relativedelta import relativedelta
import pandas as pd
from bs4 import BeautifulSoup
import confighandler
import gsshandler
from costscraper import CostScraper

class BillsHandler(CostScraper):

    def __init__(self, aid, months, year):
        self.aid = aid
        self.months = months
        self.year = year
        super(BillsHandler, self).__init__(self.aid, self.months, self.year)

    def calculate_bills(self):
        water = self.get_smpiast_costs()
        electricity = self.get_tauron_costs()
        gas = self.get_pgnig_costs()
        tennants = pd.DataFrame(gsshandler.get_spreadsheet('tennants').get_all_records())
        no_of_tennants = len(tennants[tennants['ID mieszkania'] == int(self.aid)])
        #print(no_of_tennants)


        tmp_bills = pd.merge(water.assign(grouper=water['data'].dt.to_period('M')),
                             gas.assign(grouper=gas['data'].dt.to_period('M')),
                             how='left', on='grouper')
        bills = pd.merge(tmp_bills.assign(grouper=tmp_bills['data_x'].dt.to_period('M')),
                         electricity.assign(grouper=electricity['data'].dt.to_period('M')),
                         how='left', on='grouper')
        bills = bills.rename(columns={'data_x':'Data', 'zimna':'Woda zimna', 'ciepla':'Woda ciepła',
                                      'kwota_y':'Energia elektryczna', 'kwota_x':'Gaz'})

        bills['Internet'] = confighandler.get_internet_cost(self.aid)
        bills['Internet'] = pd.to_numeric(bills['Internet'])
        bills.drop(['data', 'grouper', 'data_y'], inplace=True, axis=1)
        bills.fillna(value=0, inplace=True)
        bills['Razem wszystkie opłaty'] = (bills['Energia elektryczna'] \
            + bills['Gaz'] + bills['Woda ciepła'] + bills['Woda zimna'] \
            + bills['Internet']).round(decimals=2)
        bills['Razem na jedną osobę'] = (bills['Razem wszystkie opłaty'] \
            /no_of_tennants).round(decimals=2)

        return bills


    def get_smpiast_costs(self):
        super(BillsHandler, self).scrape_smpiast()
        # create dataframe to be filled with info after scraping
        water = pd.DataFrame(columns='data zimna ciepla'.split())

        for month in self.months:
        # extract costs from appropriate table
            with open(confighandler.get_folder('download_dir')+'sm_water_'
                      +str(month)+'_'+str(self.year)) as page:
                soup = BeautifulSoup(page.read(), features='lxml')
                item = soup.select('#charge_table')
                tmp = item[0].find_all('td')
                costs = []
                for i in tmp:
                    costs.append(i.text)

            # append dataframe with appropriate date and cost
            cold_index = costs.index("Zimna woda")
            hot_index = costs.index("Podgrzanie wody")
            water.loc[month] = [self.year+'-'+month+'-01']+[costs[cold_index+1], costs[hot_index+1]]
            water['data'] = pd.to_datetime(water['data'], format='%Y.%m.%d')
            water['zimna'] = pd.to_numeric(water['zimna'])
            water['ciepla'] = pd.to_numeric(water['ciepla'])
            # delete pages saved on disc earlier
            os.remove(confighandler.get_folder('download_dir') \
                     +confighandler.get_file('smpiast')+'_'+str(month)+'_'+str(self.year))

        return water

    def get_pgnig_costs(self):
        super(BillsHandler, self).scrape_pgnig()

        gas = pd.DataFrame(columns="data kwota".split())

        with open(confighandler.get_folder('download_dir')+"pgnig.html") as page:
            soup = BeautifulSoup(page.read(), features='lxml')
            # get the specific table with gas bills
            tmp = soup.findAll("div", {"class": "table-invoices table small-12 large-12 columns"})

        tmp2 = list(tmp[0].stripped_strings)
        # filter dates from scraped data
        date_pattern = re.compile(r'\d\d-\d\d-\d\d\d\d')
        dates = list(filter(date_pattern.match, tmp2))
        dates = [datetime.strptime(s[3:], '%m-%Y') for s in dates]
        dates2 = [date - timedelta(days=1) for date in dates]
        dates.extend(dates2)
        # filter costs from scraped data
        cost_pattern = re.compile(r'\d+,\d+ zł')
        costs = list(filter(cost_pattern.match, tmp2))
        # delete specific 0,00 zl values
        costs = [float(s[:-3].replace(',', '.')) for s in costs if s != '0,00 zł']
        costs = [round((c/2), 2) for c in costs]
        costs.extend(costs)

        gas['data'], gas['kwota'] = dates, costs
        gas['kwota'] = pd.to_numeric(gas['kwota'])

        gas = gas.groupby('data', as_index=False).sum()
        gas = gas[gas['data'].dt.year == int(self.year)]
        gas = gas[pd.to_datetime(gas['data']).dt.month.isin(self.months)]

        #os.remove(confighandler.get_folder('download_dir')+'pgnig.html')

        return gas

    def get_tauron_costs(self):
        super(BillsHandler, self).scrape_tauron()

        tmp = date.today() + relativedelta(years=1)

        electricity = pd.read_csv(confighandler.get_folder('download_dir')
                                  +'2000-01-01_'+str(tmp)+'_export.csv',
                                  encoding='latin1', sep=';')

        electricity.columns = ['SYGNATURA', 'NAZWA DOKUMENTU', 'DATA WYSTAWIENIA',
                               'DODATKOWE INFORMACJE', 'kwota', 'data',
                               'KWOTA DO ZAPLATY', 'ZAPLACONA']
        electricity.drop(['SYGNATURA', 'NAZWA DOKUMENTU', 'DATA WYSTAWIENIA',
                          'DODATKOWE INFORMACJE', 'KWOTA DO ZAPLATY',
                          'ZAPLACONA'], axis=1, inplace=True)

        electricity['data'] = pd.to_datetime(electricity['data'], format='%d.%m.%Y')
        electricity['kwota'] = electricity['kwota'].str.replace(',', '.')
        electricity['kwota'] = pd.to_numeric(electricity['kwota'])

        electricity = electricity.groupby('data', as_index=False).sum()
        electricity = electricity[electricity['data'].dt.year == int(self.year)]
        electricity = electricity[pd.to_datetime(electricity['data']).dt.month.isin(self.months)]

        #os.remove(confighandler.get_folder('download_dir')+'2000-01-01_'+str(tmp)+'_export.csv')

        return electricity
        