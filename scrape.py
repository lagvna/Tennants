import os
import requests
from bs4 import BeautifulSoup
from twill.commands import *

def get_smpiast_costs(months, years):
    # login to smpiast webpage
    url = "https://www.smpiast.com.pl/#TB_inline?width=330&height=205&inlineId=tb_wrapper"
    go(url)
    fv("2", "username", "xxx")
    fv("2", "password", "xxx")
    submit()

    cost_keys = []
    cost_values = []

    # extract all costs according to specified months and years
    for year in years:
        for month in months:
            # enter site with costs for specified month and year
            go('https://www.smpiast.com.pl/ebom/naliczenia-miesieczne')
            fv("4", "getmonth", str(month))
            fv("4", "getyear", str(year))
            submit()
            # save page as a textfile for further processing
            save_html('sm_water'+'_'+str(month)+'_'+str(year))

            # extract costs from appropriate table
            with open("sm_water"+'_'+str(month)+'_'+str(year)) as f:
                soup = BeautifulSoup(f.read(), features='lxml')
                item = soup.select('#charge_table')
                tmp = item[0].find_all('td')
                costs = []
                for i in tmp:
                        costs.append(i.text)
                print(costs)
            
            # fill in lists of keys and values and then zip them to a dict
            a = costs.index("Zimna woda")
            cost_keys.append("Zimna woda"+'_'+str(month)+'_'+str(year))
            cost_values.append(costs[a+1])
            b = costs.index("Podgrzanie wody")
            cost_keys.append("Podgrzanie wody"+'_'+str(month)+'_'+str(year))
            cost_values.append(costs[b+1])

            # delete pages saved on disc earlier
            os.remove('sm_water'+'_'+str(month)+'_'+str(year))

    # create the dictionary with specific costs
    zip_iterator = zip(cost_keys, cost_values)

    return dict(zip_iterator)

#get_smpiast_costs([1,2,3], [2019, 2020])