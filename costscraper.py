import time
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
        download_dir = confighandler.get_folder('download_dir')
        # run browser silently
        self.options = Options()
        self.options.headless = True
        self.options.add_argument("--start-maximized")
        self.options.add_experimental_option("prefs", {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
        })

    def _get_page_element(self, driver, wait, how, descriptor):
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
                print(f"Could not reach page, retrying [{retries}]")

    def scrape_smpiast(self):
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
            save_html(confighandler.get_folder('download_dir') \
                      +confighandler.get_file('smpiast')+'_'+ str(month)+'_'+str(self.year))

    def scrape_tauron(self):
        print('Scraping TAURON...')
        driver = webdriver.Chrome(chrome_options=self.options)
        wait = WebDriverWait(driver, 15)
        driver.get(confighandler.get_tauron_url(self.aid))

        username = driver.find_element_by_id("username1")
        username.clear()
        username.send_keys(confighandler.get_tauron_login(self.aid))
        password = driver.find_element_by_id("password1")
        password.clear()
        password.send_keys(confighandler.get_tauron_password(self.aid))

        driver.find_element_by_xpath("//a[@title='Zaloguj się']").click()
        print('Logged in successfully')

        self._get_page_element(driver, wait, 'xpath', "/html/body/main/div[2]/div/div/" \
                          "div[2]/div[1]/div[1]/div[3]/div" \
                          "[2]/a").click()
        print("Reached bills and payments")


        self._get_page_element(driver, wait, 'xpath', "/html/body/main/div[2]/div/div/div[2]/" \
                               "div[1]/div[1]/div[2]/div/div[3]/ul/" \
                               "li[1]/a").click()
        print("Reached bills history")

        self._get_page_element(driver, wait, 'name', "dataOd")
        from_date = driver.find_element_by_name('dataOd')
        from_date.clear()
        from_date.send_keys('2000-01-01')

        to_date = driver.find_element_by_name('dataDo')
        to_date.clear()
        to_date.send_keys('2030-01-01')
        time.sleep(2)
        to_date.send_keys(u'\ue007')
        to_date.send_keys(u'\ue007')
        #to_date.send_keys(u'\ue007')


        self._get_page_element(driver, wait, 'xpath', '//h2[contains(text(),' \
                               ' "Faktury za okres 2000-01-01")]').click()
        time.sleep(2)
        print("Filtered data")


        self._get_page_element(driver, wait, 'partial_link_text', 'Pobierz plik CSV').click()
        time.sleep(2)
        print("File saved successfully")
        driver.quit()

    def scrape_pgnig(self):
        print('Scraping PGNiG...')
        driver = webdriver.Chrome(chrome_options=self.options)
        driver.set_window_size(1920, 1080)
        wait = WebDriverWait(driver, 15)
        driver.get(confighandler.get_pgnig_url())

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
        print('Logged in successfully')

        self._get_page_element(driver, wait, 'xpath', '/html/body/div[1]/div/div/span/div[1]' \
                               '/div/div/button/i').click()
        print('Video dismissed')

        self._get_page_element(driver, wait, 'partial_link_text', 'Zobacz faktury').click()
        print('Reached bills and payments')

        self._get_page_element(driver, wait, 'xpath', '/html/body/div[1]/div/div/div[4]/div' \
                               '/div[1]/div[3]/div/div/div[1]/div[1]/div').click()

        element = driver.find_element_by_css_selector('.animationIn .css-1wa3eu0-placeholder')
        time.sleep(1)
        element.click()

        self._push_number_of_times(driver)

        print('Filtered data')

        time.sleep(2)

        with open(confighandler.get_folder('download_dir') + '/pgnig.html', 'w') as file:
            file.write(driver.page_source)

        driver.quit()

    def _push_number_of_times(self, driver):
        pushes = int(confighandler.get_pushes(self.aid))

        actions = ActionChains(driver)

        for times in range(pushes):
            actions.send_keys(Keys.DOWN)
            actions.perform()

        actions.send_keys(Keys.ENTER)
        actions.perform()
