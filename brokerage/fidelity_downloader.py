from util.downloader import Downloader
from brokerage.fidelity_statement import ACCOUNTS
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class FidelityDownloader(Downloader):
    login_url = 'https://login.fidelity.com/ftgw/Fidelity/RtlCust/Login/Init'
    portfolio_url = 'https://oltx.fidelity.com/ftgw/fbc/oftop/portfolio#positions'
    cc_url = 'https://oltx.fidelity.com/ftgw/fbc/ofcashmgmt/cashMgmtApp?ACCOUNT=&ACCOUNTS=&GOTO=CCT'
    statement_fname_regex = '(Portfolio_Position_.{3}-[0-9]{1,2}-[0-9]{2,4}.*\.csv)'
    cc_statement_fname_regex = '(download.*\.csv)'
    log_out_xpath = '//*[text()="Log Out"]'
    date_format = '{:%m/%d/%Y}'

    def __init__(self, username, password, mfa_callback, quick_timeout = 5):
        super().__init__()
        self.username = username
        self.password = password
        self.mfa_callback = mfa_callback
        self.quick_timeout = quick_timeout

    def download_brokerage_statement(self, logout_after=False):
        num_initial_downloads = self.num_current_downloads()
        if not self.logged_in():
            self.login()
        self.driver.get(self.portfolio_url)
        # throbber obscures all_accounts element for a bit
        all_accounts = WebDriverWait(self.driver, self.timeout).until(EC.element_to_be_clickable((By.XPATH, '//*[text()="All Accounts" and @class="account-selector--header-title"]')))
        all_accounts.click()
        for account_number in ACCOUNTS.values():
            # wait for all accounts to be displayed so the report includes them
            self.find_element_by_xpath(f'//*[contains(text(),"{account_number}") and (@class="magicgrid--account-title-description" or @class="magicgrid--account-title-text")]')
        download_link = self.find_element_by_xpath('//*[text()="Download"]')
        download_link.click()
        self.wait_for_download(num_initial_downloads, self.statement_fname_regex)
        if logout_after:
            self.logout()
        return self.find_latest_downloaded(pattern=self.statement_fname_regex)
    
    def download_cc_statement(self, start_date, end_date, logout_after=False):
        num_initial_downloads = self.num_current_downloads()
        if not self.logged_in():
            self.login()
        self.driver.get(self.cc_url)
        transaction_link = self.find_element_by_xpath('//*[@id="viewTransactions"]')
        view_transactions = self.find_element_by_xpath('//*[text()="View Transactions"]')
        view_transactions.click()

        main_window = self.driver.window_handles[0]
        new_window = self.driver.window_handles[-1]
        self.driver.switch_to_window(new_window)

        download_transactions = self.find_element_by_xpath('//*[text()="Download Transactions"]')
        download_transactions.click()
        format_option = self.find_element_by_xpath('//option[text()="Microsoft Excel"]') # csv
        format_option.click()
        start_date_input = self.find_element_by_xpath('//input[@id="startDate"]')
        start_date_input.clear()
        start_date_input.send_keys(self.date_format.format(start_date))
        end_date_input = self.find_element_by_xpath('//input[@id="endDate"]')
        end_date_input.clear()
        end_date_input.send_keys(self.date_format.format(end_date))
        download_button = self.find_element_by_xpath('//button[text()="Download"]')
        download_button.click()
        self.driver.switch_to_window(main_window)

        self.wait_for_download(num_initial_downloads, self.cc_statement_fname_regex)
        if logout_after:
            self.logout()
        return self.find_latest_downloaded(pattern=self.cc_statement_fname_regex)

    def login(self):
        self.driver.get(self.login_url)
        username_field = self.find_element_by_xpath('//*[@id="userId-input"]')
        username_field.send_keys(self.username)
        password_field = self.find_element_by_xpath('//*[@id="password"]')
        password_field.send_keys(self.password)
        password_field.send_keys(Keys.RETURN)
        self.check_login()

    def logout(self):
        if self.logged_in():
            log_out_link = self.find_element_by_xpath(self.log_out_xpath)
            log_out_link.click()
            self.find_element_by_xpath('//*[text()="Login"]') # wait until logged out

    def check_login(self):
        if not self.logged_in():
            self.mfa_login()
        self.logged_in() # wait until logged in

    def logged_in(self):
        try:
            self.find_element_by_xpath(self.log_out_xpath)
            return True
        except:
            pass
        return False

    def mfa_login(self):
        self.find_element_by_xpath('//*[@id="step-challenge"]', timeout = self.quick_timeout) # sanity check
        next_button = self.find_element_by_xpath('//button[text()="Next"]')
        next_button.click()
        sms_radio = self.find_element_by_xpath('//*[@id="channel-label-sms"]')
        sms_radio.click()
        next_button = self.find_element_by_xpath('//button[text()="Next"]')
        next_button.click()
        code_input_field = self.find_element_by_xpath('//*[@id="code"]')
        code_input_field.send_keys(self.mfa_callback())
        remember_checkbox = self.find_element_by_xpath('//*[@id="saveDevice"]')
        remember_checkbox.click()
        next_button = self.find_element_by_xpath('//button[text()="Next"]')
        next_button.click()
        self.logged_in() # wait until logged in

#import os
#import datetime
#fd = FidelityDownloader(os.environ['FIDELITY_USER'], os.environ['FIDELITY_PASS'], lambda: input('MFA code: '))
#brokerage_statement_fname = fd.download_brokerage_statement()
#print(brokerage_statement_fname)
#cc_statement_fname = fd.download_cc_statement(start_date=datetime.date(2019,4,1), end_date=datetime.date(2019,8,31))
#print(cc_statement_fname)

