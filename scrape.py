import os
import requests
import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from twill.commands import *
from configparser import SafeConfigParser
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time


config_file = '/home/lagvna/config.ini'
config_parser = SafeConfigParser()
config_parser.read(config_file)

def scrape_smpiast(months, year):
    # login to smpiast webpage
    url = config_parser.get('smpiast9', 'url')
    go(url)
    fv("2", "username", config_parser.get('smpiast9', 'login'))
    fv("2", "password", config_parser.get('smpiast9', 'password'))
    submit()

    # extract all costs according to specified months and years
    for month in months:
        # enter site with costs for specified month and year
        go('https://www.smpiast.com.pl/ebom/naliczenia-miesieczne')
        fv("4", "getmonth", str(month))
        fv("4", "getyear", str(year))
        submit()
        # save page as a textfile for further processing
        save_html(config_parser.get('folders', 'download_dir')
            +'/sm_water_'+ str(month)+'_'+str(year))


def scrape_tauron():
    download_dir = config_parser.get('folders', 'download_dir')

    options = Options()
    options.headless = True

    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2) # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', download_dir)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

    driver = webdriver.Firefox(firefox_profile = profile, options = options)
    driver.get(config_parser.get('tauron9', 'url'))

    username = driver.find_element_by_id("username1")
    username.clear()
    username.send_keys(config_parser.get('tauron9', 'login'))

    password = driver.find_element_by_id("password1")
    password.clear()
    password.send_keys(config_parser.get('tauron9', 'password'))

    driver.find_element_by_xpath("//a[@title='Zaloguj się']").click()
    
    wait = WebDriverWait(driver, 60)
    page1 = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/main/div[2]/div/div/div[2]/div[1]/div[1]/div[3]/div[2]/a")))
    page1.click()
    print("wszedlem w faktury i platnosci")

    page2 = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/main/div[2]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[3]/ul/li[1]/a")))
    page2.click()
    print("wszedlem w archiwum faktur")
    
    page35 = wait.until(EC.visibility_of_element_located((By.NAME, "dataOd")))

    from_date = driver.find_element_by_name('dataOd')
    from_date.clear()
    from_date.send_keys('2000-01-01')

    to_date = driver.find_element_by_name('dataDo')
    to_date.clear()
    to_date.send_keys('2030-01-01')
    to_date.send_keys(u'\ue007')
    to_date.send_keys(u'\ue007')

    page5 = wait.until(EC.visibility_of_element_located((By.XPATH, '//h2[contains(text(), "Faktury za okres 2000-01-01 - 2030-01-01")]')))

    page3 = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div[3]/div[1]/div/form/div[3]/div[2]/div[2]/input")))
    page3.click()

    print("przefiltrowalem dane")

    page4 = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div[3]/div[2]/a")))
    page4.click()

    driver.implicitly_wait(30)

    driver.quit()
    print("File saved successfully")

def scrape_pgnig():
    download_dir = config_parser.get('folders', 'download_dir')
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
    profile.set_preference("dom.webnotifications.enabled", False);
    profile.set_preference('browser.download.folderList', 2) # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', download_dir)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

    driver = webdriver.Firefox(firefox_profile = profile, options = options, firefox_options = foptions)
    driver.get(config_parser.get('pgnig', 'url'))
    wait = WebDriverWait(driver, 10)



    page1 = wait.until(EC.visibility_of_element_located((By.XPATH,
     '/html/body/div[1]/div/div/div[4]/div/div/div[2]/div/div[1]/div/form/div/div/div/label[1]/input')))
    login = driver.find_element_by_xpath(
        '/html/body/div[1]/div/div/div[4]/div/div/div[2]/div/div[1]/div/form/div/div/div/label[1]/input')
    password = driver.find_element_by_xpath(
        '/html/body/div[1]/div/div/div[4]/div/div/div[2]/div/div[1]/div/form/div/div/div/label[2]/div[2]/input')

    login.send_keys(config_parser.get('pgnig', 'login'))
    password.send_keys(config_parser.get('pgnig', 'password'))


    driver.find_element_by_xpath(
        '/html/body/div[1]/div/div/div[4]/div/div/div[2]/div/div[1]/div/form/div/div/div/button').click()

    page2 = wait.until(EC.visibility_of_element_located((By.XPATH, 
        '/html/body/div[1]/div/div/nav/div[3]/div[2]/div/div[2]/div/div[2]/ul/li[1]/a'))).click()

    page3 = wait.until(EC.visibility_of_element_located((By.XPATH, 
        '/html/body/div[1]/div/div/div[4]/div/div[1]/div[3]/div/div/div[1]/div[1]/div')))

    page5 = wait.until(EC.visibility_of_element_located((By.XPATH, 
        '/html/body/div[1]/div/div/span/div[1]/div/div/button/i'))).click()
    
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

    with open(config_parser.get('folders', 'download_dir') + '/pgnig.html', 'w') as f:
        f.write(driver.page_source)

    driver.implicitly_wait(30)
    driver.quit()

def get_smpiast_costs(months, year):
    scrape_smpiast(months, year)
    # create dataframe to be filled with info after scraping
    df = pd.DataFrame(columns = 'zimna_woda ciepla_woda'.split())

    for month in months:
    # extract costs from appropriate table
        with open(config_parser.get('folders', 'download_dir')
            +'/sm_water_'+str(month)+'_'+str(year)) as f:
            soup = BeautifulSoup(f.read(), features='lxml')
            item = soup.select('#charge_table')
            tmp = item[0].find_all('td')
            costs = []
            for i in tmp:
                costs.append(i.text)
            
        # append dataframe with appropriate date and cost
        a = costs.index("Zimna woda")
        b = costs.index("Podgrzanie wody")
        df.loc[datetime.strptime(str(month)+'-'+str(year), '%m-%Y')] = [costs[a+1], costs[b+1]]

        # delete pages saved on disc earlier
        os.remove(config_parser.get('folders', 'download_dir')
            +'/sm_water_'+str(month)+'_'+str(year))

    return df

def get_pgnig_costs(months, year):
    #scrape_pgnig()

    df = pd.DataFrame(columns = "data kwota".split())

    with open(config_parser.get('folders', 'download_dir')+"/pgnig.html") as f:
        soup = BeautifulSoup(f.read(), features='lxml')
        # get the specific table with gas bills
        tmp = soup.findAll("div", {"class": "table-invoices table small-12 large-12 columns"})
    
    tmp2 = list(tmp[0].stripped_strings)
    # filter dates from scraped data
    date_pattern = re.compile(r'\d\d-\d\d-\d\d\d\d')
    dates = list(filter(date_pattern.match, tmp2))
    dates = [datetime.strptime(s[3:], '%m-%Y') for s in dates]
    dates2 = [date - timedelta(days=1) for date in dates]
    dates.extend(dates2)
    #print(dates)
    # filter costs from scraped data
    cost_pattern = re.compile(r'\d+,\d+ zł')
    costs = list(filter(cost_pattern.match, tmp2))
    # delete specific 0,00 zl values
    costs = [float(s[:-3].replace(',','.')) for s in costs if s != '0,00 zł']
    costs = [round((c/2), 2) for c in costs]
    costs.extend(costs)
    #print(costs)

    print("robie")
    df['data'] = dates
    df['kwota'] = costs
    #print(df)
    df = df.groupby('data', as_index=False).sum()
    df = df[df['data'].dt.year == int(year)]
    df = df[pd.to_datetime(df['data']).dt.month.isin(months)]

    return df

def get_tauron_costs(months, year):
    #scrape_tauron()
    df = pd.read_csv(config_parser.get('folders', 'download_dir')
        +'/2000-01-01_2030-01-01_export.csv', encoding = 'latin1', sep=';')

    df.columns = ['SYGNATURA', 'NAZWA DOKUMENTU', 'DATA WYSTAWIENIA', 'DODATKOWE INFORMACJE', 
    'kwota', 'data', 'KWOTA DO ZAPLATY', 'ZAPLACONA']
    df.drop(['SYGNATURA', 'NAZWA DOKUMENTU', 'DATA WYSTAWIENIA', 'DODATKOWE INFORMACJE', 
        'KWOTA DO ZAPLATY','ZAPLACONA'], axis = 1, inplace=True)

    
    df['data'] = pd.to_datetime(df['data'], format='%d.%m.%Y')
    df['kwota'] = df['kwota'].str.replace(',', '.')
    df['kwota'] = pd.to_numeric(df['kwota'])
    #df['kwota'] = df['kwota'].round(decimals=2)
    # potraktowac te kolumne jako float, a nie string
    df = df.groupby('data', as_index=False).sum()
    df = df[df['data'].dt.year == int(year)]
    df = df[pd.to_datetime(df['data']).dt.month.isin(months)]
    
    return df


#get_pgnig_costs([1,2,3], 2020)
