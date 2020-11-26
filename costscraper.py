import os
import logging
logger = logging.getLogger(__name__)
import time
import glob
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from twill.commands import go, fv, submit, save_html
import confighandler

class CostScraper(object):

    def __init__(self, aid, months, year):
        self.aid = aid
        self.months = months
        self.year = year
        self.download_dir = confighandler.get_folder('download_dir')
        # run browser silently
        self.options = Options()
        #self.options.headless = True
        self.options.add_argument("--start-maximized")
        self.options.add_experimental_option("prefs", {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
        })

    def _get_page_element(self, driver, wait, how, descriptor):
        '''
        Searches the page for an element with provided string 
        either by XPATH, NAME or PARTIAL LINK TEXT

        Args:
            driver: webdriver for manipulating web pages
            wait: wait object, allowing to wait for certain elements
            how: method of searching
            descriptor: string representation of searched element

        '''

        retries = 0
        while retries < 5:
            try:
                if how == 'xpath':
                    return wait.until(EC.visibility_of_element_located((By.XPATH, descriptor)))
                elif how == 'name':
                    return wait.until(EC.visibility_of_element_located((By.NAME, descriptor)))
                elif how == 'partial_link_text':
                    return wait.until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT,
                                                                        descriptor)))
                break
            except TimeoutException:
                driver.refresh()
                retries += 1
                logger.error(f"Could not reach page, retrying [{retries}]")

    def scrape_smpiast(self):
        files = []
        # login to smpiast webpage
        url = confighandler.get_smpiast_url(self.aid)
        go(url)
        fv("2", "username", confighandler.get_smpiast_login(self.aid))
        fv("2", "password", confighandler.get_smpiast_password(self.aid))
        submit()

        # extract all costs according to specified months and years
        for month in self.months:
            # enter site with costs for specified month and year
            go('https://www.smpiast.com.pl/ebom/naliczenia-miesieczne')
            fv("4", "getmonth", str(month))
            fv("4", "getyear", str(self.year))
            submit()
            # save page as a textfile for further processing
            file = confighandler.get_folder('download_dir') \
                      +confighandler.get_file('smpiast')+'_'+ str(month)+'_'+str(self.year)
            save_html(file)
            files.append(file)

        return files

    def scrape_tauron(self):
        logger.info('Scraping TAURON...')
        driver = webdriver.Chrome(chrome_options=self.options)
        wait = WebDriverWait(driver, 15)
        # login to tauron web page
        driver.get(confighandler.get_tauron_url(self.aid))
        username = driver.find_element_by_id("username1")
        username.clear()
        username.send_keys(confighandler.get_tauron_login(self.aid))
        password = driver.find_element_by_id("password1")
        password.clear()
        password.send_keys(confighandler.get_tauron_password(self.aid))

        driver.find_element_by_xpath("//a[@title='Zaloguj się']").click()
        logger.info('Logged in successfully')

        # go through a number of pages, to reach bills history
        self._get_page_element(driver, wait, 'xpath', "/html/body/main/div[2]/div/div/" \
                          "div[2]/div[1]/div[1]/div[3]/div" \
                          "[2]/a").click()
        logger.info("Reached bills and payments")


        self._get_page_element(driver, wait, 'xpath', "/html/body/main/div[2]/div/div/div[2]/" \
                               "div[1]/div[1]/div[2]/div/div[3]/ul/" \
                               "li[1]/a").click()
        logger.info("Reached bills history")

        # specify the dates range of bills
        self._get_page_element(driver, wait, 'name', "dataOd")
        from_date = driver.find_element_by_name('dataOd')
        from_date.clear()
        from_date.send_keys('2000-01-01')

        to_date = driver.find_element_by_name('dataDo')
        to_date.clear()
        to_date.send_keys('2030-01-01')
        time.sleep(5)
        # since it is a datepicker element, we confirm choice by hitting enter via keyboard twice
        to_date.send_keys(u'\ue007')
        to_date.send_keys(u'\ue007')

        #search for link to download bills CSV file
        self._get_page_element(driver, wait, 'xpath', '//h2[contains(text(),' \
                               ' "Faktury za okres 2000-01-01")]').click()
        time.sleep(2)
        logger.info("Filtered data")

        self._get_page_element(driver, wait, 'partial_link_text', 'Pobierz plik CSV').click()
        time.sleep(2)
        logger.info("File saved successfully")
        driver.quit()
        #save file for further processing
        for file in os.listdir(self.download_dir):
            if file.endswith(".csv"):
                return self.download_dir + str(file)


    def scrape_pgnig(self):
        logger.info('Scraping PGNiG...')
        #set options to reliably run chrome in headless mode
        driver = webdriver.Chrome(chrome_options=self.options)
        driver.set_window_size(1920, 1080)
        wait = WebDriverWait(driver, 15)
        driver.get(confighandler.get_pgnig_url())

        #login to PGNiG
        self._get_page_element(driver, wait, 'xpath', '/html/body/div[1]/div/div/div[4]/div/div'\
                               '/div[2]/div/div[1]/div/form/div/div/div/'\
                               'label[1]/input').click()

        login = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[4]/div/div/div[2]/' \
                                             'div/div[1]/div/form/div/div/div/label[1]/input')
        password = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[4]/div/div/div[2]/' \
                                                'div/div[1]/div/form/div/div/div/label[2]/div[2]/' \
                                                'input')

        login.send_keys(confighandler.get_pgnig_login())
        password.send_keys(confighandler.get_pgnig_password())

        driver.find_element_by_xpath('/html/body/div[1]/div/div/div[4]/div/div/div[2]/div/div[1]' \
                                          '/div/form/div/div/div/button').click()
        logger.info('Logged in successfully')
        #dismiss a youtube video popping out after logging in
        self._get_page_element(driver, wait, 'xpath', '/html/body/div[1]/div/div/span/div[1]' \
                               '/div/div/button/i').click()
        logger.info('Video dismissed')

        # get through a numer of pages to reach bills history
        self._get_page_element(driver, wait, 'partial_link_text', 'Zobacz faktury').click()
        logger.info('Reached bills and payments')

        self._get_page_element(driver, wait, 'xpath', '/html/body/div[1]/div/div/div[4]/div' \
                               '/div[1]/div[3]/div/div/div[1]/div[1]/div').click()

        # open a dropdown menu and then push keyboard arrows a numer of times 
        # to pick the desided apartment
        element = driver.find_element_by_css_selector('.animationIn .css-1wa3eu0-placeholder')
        time.sleep(1)
        element.click()
        self._push_number_of_times(driver)
        logger.info('Filtered data')

        time.sleep(2)

        #save file for further processing
        file = confighandler.get_folder('download_dir') + 'pgnig.html'
        with open(file, 'w') as f:
            f.write(driver.page_source)
        
        driver.quit()

        return file

    # def _dismiss_popup(self, driver):
    #     pushes = int(confighandler.get_tauron_pushes())

    #     actions = ActionChains(driver)
    #     time.sleep(5)
    #     for times in range(pushes):
    #         actions.send_keys(Keys.TAB)
    #         time.sleep(1)
    #         actions.perform()

    #     actions.send_keys(Keys.ENTER)
    #     actions.perform()

    def _push_number_of_times(self, driver):
        pushes = int(confighandler.get_pushes(self.aid))

        actions = ActionChains(driver)

        for times in range(pushes):
            actions.send_keys(Keys.DOWN)
            actions.perform()

        actions.send_keys(Keys.ENTER)
        actions.perform()
