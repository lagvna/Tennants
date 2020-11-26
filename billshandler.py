import os
from datetime import date, datetime, timedelta
import re
from dateutil.relativedelta import relativedelta
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
import confighandler
import gsshandler
from costscraper import CostScraper

class BillsHandler(CostScraper):
    '''
    The BillsHandler object inherits from CostScraper
    and provides tools for building bills dataframes
    from data scraped from TAURON, PGNiG and SM Piast Wroclaw.
    
    Args:
        aid: Apartment ID
        months (list): For which months bills should be scraped and generated
        year: For which year bills should be scraped and generated

    '''

    def __init__(self, aid, months, year):
        self.aid = aid
        self.months = months
        self.year = year
        self.download_dir = confighandler.get_folder('download_dir')
        self.cost_files = []
        Path(self.download_dir).mkdir(parents=True, exist_ok=True)

        super(BillsHandler, self).__init__(self.aid, self.months, self.year)

    def calculate_bills(self):
        # extract bills into dataframes from earlier scraped files
        water = self.get_smpiast_costs()
        electricity = self.get_tauron_costs()
        gas = self.get_pgnig_costs()
        no_of_tennants = self._get_tennants_count()

        # merge all dataframes into one
        tmp_bills = pd.merge(water.assign(grouper=water['data'].dt.to_period('M')),
                             gas.assign(grouper=gas['data'].dt.to_period('M')),
                             how='left', on='grouper')
        bills = pd.merge(tmp_bills.assign(grouper=tmp_bills['data_x'].dt.to_period('M')),
                         electricity.assign(grouper=electricity['data'].dt.to_period('M')),
                         how='left', on='grouper')
        bills = bills.rename(columns={'data_x':'Data', 'zimna':'Woda zimna', 'ciepla':'Woda ciepła',
                             'kwota_y':'Energia elektryczna', 'kwota_x':'Gaz'})

        
        # add internet bills (the price is constant so provided from config file)
        bills['Internet'] = confighandler.get_internet_cost(self.aid)
        bills['Internet'] = pd.to_numeric(bills['Internet'])

        # tidy the dataframe
        bills.drop(['data', 'grouper', 'data_y'], inplace=True, axis=1)
        bills.fillna(value=0, inplace=True)
        # calculate the sum of bills and bills per tennant
        bills['Razem wszystkie opłaty'] = (bills['Energia elektryczna'] \
            + bills['Gaz'] + bills['Woda ciepła'] + bills['Woda zimna'] \
            + bills['Internet']).round(decimals=2)
        bills['Razem na jedną osobę'] = (bills['Razem wszystkie opłaty'] \
            /no_of_tennants).round(decimals=2)

        self._delete_files(self.cost_files)

        return bills

    def _get_tennants_count(self):
        tennants = pd.DataFrame(gsshandler.get_spreadsheet('tennants').get_all_records())
        no_of_tennants = len(tennants[tennants['ID mieszkania'] == int(self.aid)])

        return no_of_tennants
        

    def get_smpiast_costs(self):
        water_files = super(BillsHandler, self).scrape_smpiast()
        self.cost_files.extend(water_files)

        water_bills = pd.DataFrame(columns='data zimna ciepla'.split())
        # open files one by one and extract bills
        for month in self.months:
            page = [file for file in water_files if str(month)+'_'+str(self.year) in file]
            # extract costs from appropriate table
            with open(page[0]) as p:
                content = BeautifulSoup(p.read(), features='lxml')
                table = content.select('#charge_table')
                details = table[0].find_all('td')
                costs = []
                for i in details:
                    costs.append(i.text)
            #find appropriate key and append dataframe with the following element (value)
            cold_index = costs.index("Zimna woda")
            hot_index = costs.index("Podgrzanie wody")
            water_bills.loc[month] = [self.year+'-'+month+'-01']+[costs[cold_index+1], costs[hot_index+1]]
            # tidy dataframe
            water_bills['data'] = pd.to_datetime(water_bills['data'], format='%Y.%m.%d')
            water_bills['zimna'] = pd.to_numeric(water_bills['zimna'])
            water_bills['ciepla'] = pd.to_numeric(water_bills['ciepla'])

        return water_bills

    def get_pgnig_costs(self):
        gas_file = super(BillsHandler, self).scrape_pgnig()
        self.cost_files.append(gas_file)

        with open(gas_file) as page:
            content = BeautifulSoup(page.read(), features='lxml')
            # get the specific table with gas bills
            tmp = content.findAll("div", {"class": "table-invoices table small-12 large-12 columns"})

        raw_data = list(tmp[0].stripped_strings)
        gas_bills = self._process_gas_bills(raw_data)

        return gas_bills

    def _process_gas_bills(self, raw_data):
        gas = pd.DataFrame(columns="data kwota".split())

        # filter dates from scraped data
        date_pattern = re.compile(r'\d\d-\d\d-\d\d\d\d')
        dates = list(filter(date_pattern.match, raw_data))
        dates = [datetime.strptime(s[3:], '%m-%Y') for s in dates]
        # since day = 1 in dates, we create another list of dates by 
        # substracting one day from the current ones, this gives us twice as much dates
        # representing all months in the year
        # reason being is that bills come every second month and tennants pay each month
        dates2 = [date - timedelta(days=1) for date in dates]
        dates.extend(dates2)
        # filter costs from scraped data
        cost_pattern = re.compile(r'\d+,\d+ zł')
        costs = list(filter(cost_pattern.match, raw_data))
        # delete specific 0,00 zl values (these are remaining payments element values from web page)
        costs = [float(s[:-3].replace(',', '.')) for s in costs if s != '0,00 zł']
        # since bills come every second month and tennants pay each month, need to divide by 2
        costs = [round((c/2), 2) for c in costs]
        costs.extend(costs)
        #append values to dataframe
        gas['data'], gas['kwota'] = dates, costs
        gas['kwota'] = pd.to_numeric(gas['kwota'])
        # sum bills from same months tidy dataframe
        gas = gas.groupby('data', as_index=False).sum()
        gas = gas[gas['data'].dt.year == int(self.year)]
        gas = gas[pd.to_datetime(gas['data']).dt.month.isin(self.months)]

        return gas

    def get_tauron_costs(self):
        electricity_file = super(BillsHandler, self).scrape_tauron()
        self.cost_files.append(electricity_file)
        electricity_bill = self._process_electricity_bills(electricity_file)

        return electricity_bill

    def _process_electricity_bills(self, electricity_file):
        electricity = pd.read_csv(electricity_file, encoding='latin1', sep=';')

        # file encoding is messed up, so need to rename columns
        electricity.columns = ['SYGNATURA', 'NAZWA DOKUMENTU', 'DATA WYSTAWIENIA',
                               'DODATKOWE INFORMACJE', 'kwota', 'data',
                               'KWOTA DO ZAPLATY', 'ZAPLACONA']
        # drop unwanted columns
        electricity.drop(['SYGNATURA', 'NAZWA DOKUMENTU', 'DATA WYSTAWIENIA',
                          'DODATKOWE INFORMACJE', 'KWOTA DO ZAPLATY',
                          'ZAPLACONA'], axis=1, inplace=True)
        # tidy dataframe
        electricity['data'] = pd.to_datetime(electricity['data'], format='%d.%m.%Y')
        electricity['kwota'] = electricity['kwota'].str.replace(',', '.')
        electricity['kwota'] = pd.to_numeric(electricity['kwota'])
        # sum bills from same months and tidy
        electricity = electricity.groupby('data', as_index=False).sum()
        electricity = electricity[electricity['data'].dt.year == int(self.year)]
        electricity = electricity[pd.to_datetime(electricity['data']).dt.month.isin(self.months)]

        return electricity
        
    def _delete_files(self, files):
        for file in files:
            os.remove(str(file))
