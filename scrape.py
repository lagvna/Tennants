import os
import time
from datetime import datetime, timedelta
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from twill.commands import *
from bs4 import BeautifulSoup
import gsshandler


def scrape_smpiast(aid, months, year):
    # login to smpiast webpage
    url = gsshandler.get_smpiast_url(aid)
    go(url)
    fv("2", "username", gsshandler.get_smpiast_login(aid))
    fv("2", "password", gsshandler.get_smpiast_password(aid))
    submit()

    # extract all costs according to specified months and years
    for month in months:
        # enter site with costs for specified month and year
        go('https://www.smpiast.com.pl/ebom/naliczenia-miesieczne')
        fv("4", "getmonth", str(month))
        fv("4", "getyear", str(year))
        submit()
        # save page as a textfile for further processing
        save_html(gsshandler.get_folder('download_dir')+'sm_water_'+ str(month)+'_'+str(year))


def scrape_tauron(aid):
    download_dir = gsshandler.get_folder('download_dir')

    options = Options()
    options.headless = True

    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2) # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', download_dir)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

    driver = webdriver.Firefox(firefox_profile=profile, options=options)
    driver.get(gsshandler.get_tauron_url(aid))

    username = driver.find_element_by_id("username1")
    username.clear()
    username.send_keys(gsshandler.get_tauron_login(aid))

    password = driver.find_element_by_id("password1")
    password.clear()
    password.send_keys(gsshandler.get_tauron_password(aid))

    driver.find_element_by_xpath("//a[@title='Zaloguj się']").click()
    wait = WebDriverWait(driver, 60)
    wait.until(EC.visibility_of_element_located((By.XPATH,
                                                 "/html/body/main/div[2]/div/div/" \
                                                 "div[2]/div[1]/div[1]/div[3]/div" \
                                                 "[2]/a"))).click()
    print("wszedlem w faktury i platnosci")

    wait.until(EC.visibility_of_element_located((By.XPATH,
                                                 "/html/body/main/div[2]/div/div/div[2]/" \
                                                 "div[1]/div[1]/div[2]/div/div[3]/ul/" \
                                                 "li[1]/a"))).click()
    print("wszedlem w archiwum faktur")
    wait.until(EC.visibility_of_element_located((By.NAME, "dataOd")))

    from_date = driver.find_element_by_name('dataOd')
    from_date.clear()
    from_date.send_keys('2000-01-01')

    to_date = driver.find_element_by_name('dataDo')
    to_date.clear()
    to_date.send_keys('2030-01-01')
    to_date.send_keys(u'\ue007')
    to_date.send_keys(u'\ue007')

    wait.until(EC.visibility_of_element_located((By.XPATH,
                                                 '//h2[contains(text(),' \
                                                 ' "Faktury za okres 2000-01-01 ' \
                                                 '- 2030-01-01")]')))

    wait.until(EC.visibility_of_element_located((By.XPATH,
                                                 "/html/body/div[1]/div/div[3]/" \
                                                 "div[1]/div/form/div[3]/div[2]/" \
                                                 "div[2]/input"))).click()

    print("przefiltrowalem dane")

    wait.until(EC.visibility_of_element_located((By.XPATH,
                                                 "/html/body/div[1]/div/div[3]" \
                                                 "/div[2]/a"))).click()

    driver.implicitly_wait(30)

    driver.quit()
    print("File saved successfully")

def scrape_pgnig():
    download_dir = gsshandler.get_folder('download_dir')
    # run browser silently
    options = Options()
    options.headless = True

    foptions = webdriver.FirefoxOptions()
    # these options decline to share location
    # foptions.set_preference("geo.prompt.testing", True)
    # foptions.set_preference("geo.prompt.testing.allow", False)
    # foptions.set_preference('dom.push.enabled', False)
    #options.headless = True

    profile = webdriver.FirefoxProfile()
    profile.set_preference("dom.webnotifications.enabled", False)
    profile.set_preference('browser.download.folderList', 2) # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', download_dir)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

    driver = webdriver.Firefox(firefox_profile=profile, options=options,
                               firefox_options=foptions)
    driver.get(gsshandler.get_pgnig_url())
    wait = WebDriverWait(driver, 10)



    wait.until(EC.visibility_of_element_located((By.XPATH,
                                                 '/html/body/div[1]/div/div/div[4]/div/div'\
                                                 '/div[2]/div/div[1]/div/form/div/div/div/'\
                                                 'label[1]/input')))
    login = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[4]/div/div/div[2]/div/' \
                                         'div[1]/div/form/div/div/div/label[1]/input')
    password = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[4]/div/div/div[2]/div/' \
                                            'div[1]/div/form/div/div/div/label[2]/div[2]/input')

    login.send_keys(gsshandler.get_pgnig_login())
    password.send_keys(gsshandler.get_pgnig_password())


    driver.find_element_by_xpath('/html/body/div[1]/div/div/div[4]/div/div/div[2]/div/div[1]' \
                                 '/div/form/div/div/div/button').click()
    wait.until(EC.visibility_of_element_located((By.XPATH,
                                                 '/html/body/div[1]/div/div/nav/div[3]/div[2]' \
                                                 '/div/div[2]/div/div[2]/ul/li[1]/a'))).click()

    wait.until(EC.visibility_of_element_located((By.XPATH,
                                                 '/html/body/div[1]/div/div/div[4]/div' \
                                                 '/div[1]/div[3]/div/div/div[1]/div[1]/div')))

    wait.until(EC.visibility_of_element_located((By.XPATH,
                                                 '/html/body/div[1]/div/div/span/div[1]' \
                                                 '/div/div/button/i'))).click()
    element = driver.find_element_by_css_selector('.animationIn .css-1wa3eu0-placeholder')
    time.sleep(1)
    element.click()

    #once - third option
    actions = ActionChains(driver)
    actions.send_keys(Keys.DOWN)
    actions.perform()
    #twice - second option
    # time.sleep(1)
    # actions.send_keys(Keys.DOWN)
    # actions.perform()
    # #three times - second option
    # time.sleep(1)
    # actions.send_keys(Keys.DOWN)
    # actions.perform()
    # time.sleep(1)
    # actions.send_keys(Keys.DOWN)
    # actions.perform()
    # time.sleep(1)
    # actions.send_keys(Keys.DOWN)
    # actions.perform()
    # # six times - fourth option
    # time.sleep(1)
    # actions.send_keys(Keys.DOWN)
    # actions.perform()
    actions.send_keys(Keys.ENTER)
    actions.perform()

    time.sleep(2)

    with open(gsshandler.get_folder('download_dir') + '/pgnig.html', 'w') as f:
        f.write(driver.page_source)

    driver.implicitly_wait(30)
    driver.quit()

def get_smpiast_costs(aid, months, year):
    scrape_smpiast(aid, months, year)
    # create dataframe to be filled with info after scraping
    water = pd.DataFrame(columns='data zimna ciepla'.split())

    for month in months:
    # extract costs from appropriate table
        with open(gsshandler.get_folder('download_dir')+'sm_water_'
                  +str(month)+'_'+str(year)) as page:
            soup = BeautifulSoup(page.read(), features='lxml')
            item = soup.select('#charge_table')
            tmp = item[0].find_all('td')
            costs = []
            for i in tmp:
                costs.append(i.text)

        # append dataframe with appropriate date and cost
        cold_index = costs.index("Zimna woda")
        hot_index = costs.index("Podgrzanie wody")
        water.loc[month] = [year+'-'+month+'-01']+[costs[cold_index+1], costs[hot_index+1]]
        water['data'] = pd.to_datetime(water['data'], format='%Y.%m.%d')
        water['zimna'] = pd.to_numeric(water['zimna'])
        water['ciepla'] = pd.to_numeric(water['ciepla'])
        # delete pages saved on disc earlier
        os.remove(gsshandler.get_folder('download_dir')+'sm_water_'+str(month)+'_'+str(year))

    return water

def get_pgnig_costs(months, year):
    scrape_pgnig()

    gas = pd.DataFrame(columns="data kwota".split())

    with open(gsshandler.get_folder('download_dir')+"pgnig.html") as page:
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

    print("robie")
    gas['data'] = dates
    gas['kwota'] = costs
    gas['kwota'] = pd.to_numeric(gas['kwota'])

    gas = gas.groupby('data', as_index=False).sum()
    gas = gas[gas['data'].dt.year == int(year)]
    gas = gas[pd.to_datetime(gas['data']).dt.month.isin(months)]

    return gas

def get_tauron_costs(aid, months, year):
    scrape_tauron(aid)
    electricity = pd.read_csv(gsshandler.get_folder('download_dir')
                              +'2000-01-01_2030-01-01_export.csv', encoding='latin1', sep=';')

    electricity.columns = ['SYGNATURA', 'NAZWA DOKUMENTU', 'DATA WYSTAWIENIA',
                           'DODATKOWE INFORMACJE', 'kwota', 'data', 'KWOTA DO ZAPLATY', 'ZAPLACONA']
    electricity.drop(['SYGNATURA', 'NAZWA DOKUMENTU', 'DATA WYSTAWIENIA', 'DODATKOWE INFORMACJE',
                      'KWOTA DO ZAPLATY', 'ZAPLACONA'], axis=1, inplace=True)

    electricity['data'] = pd.to_datetime(electricity['data'], format='%d.%m.%Y')
    electricity['kwota'] = electricity['kwota'].str.replace(',', '.')
    electricity['kwota'] = pd.to_numeric(electricity['kwota'])

    electricity = electricity.groupby('data', as_index=False).sum()
    electricity = electricity[electricity['data'].dt.year == int(year)]
    electricity = electricity[pd.to_datetime(electricity['data']).dt.month.isin(months)]

    return electricity
