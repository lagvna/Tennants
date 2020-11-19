import os
import requests
from bs4 import BeautifulSoup
from twill.commands import *
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains


def scrape_smpiast(months, years):
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

def get_smpiast_costs(months, years):
    scrape_smpiast()

def get_pgnig_costs(months, years):
    scrape_pgnig()

def get_tauron_costs(months, years):

    scrape_tauron()

def scrape_tauron():
    download_dir = "/home/lagvna/Tennants"

    options = Options()
    options.headless = True

    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2) # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', download_dir)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

    driver = webdriver.Firefox(firefox_profile = profile, options = options)
    driver.get("https://logowanie.tauron.pl")

    username = driver.find_element_by_id("username1")
    username.clear()
    username.send_keys("xxx")

    password = driver.find_element_by_id("password1")
    password.clear()
    password.send_keys("xxx")

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
    download_dir = "/home/lagvna/Tennants"

    options = Options()
    #options.headless = True

    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2) # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', download_dir)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

    driver = webdriver.Firefox(firefox_profile = profile, options = options)
    driver.get("https://ebok.pgnig.pl")
    wait = WebDriverWait(driver, 60)



    page1 = wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[4]/div/div/div[2]/div/div[1]/div/form/div/div/div/label[1]/input')))
    login = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[4]/div/div/div[2]/div/div[1]/div/form/div/div/div/label[1]/input')
    password = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[4]/div/div/div[2]/div/div[1]/div/form/div/div/div/label[2]/div[2]/input')

    login.send_keys("xxx")
    password.send_keys("xxx")

    driver.find_element_by_xpath('/html/body/div[1]/div/div/div[4]/div/div/div[2]/div/div[1]/div/form/div/div/div/button').click()


    # driver.get("http://www.example.com")
    # with open('page.html', 'w') as f:
    #     f.write(driver.page_source)

scrape_tauron()