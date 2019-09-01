from util.downloader import Downloader
from selenium.common.exceptions import NoSuchElementException

class FidelityDownloader(Downloader):
    login_url = 'https://digital.fidelity.com/prgw/digital/login/full-page'
    portfolio_url = 'https://oltx.fidelity.com/ftgw/fbc/oftop/portfolio'
    statement_fname_regex = '(Portfolio_Position_.{3}-[0-9]{1,2}-[0-9]{2,4}.*\.csv)'
    log_out_xpath = '//*[text()="Log Out"]'

    def __init__(self, username, password, mfa_callback, quick_timeout = 5):
        super().__init__()
        self.username = username
        self.password = password
        self.mfa_callback = mfa_callback
        self.quick_timeout = quick_timeout

    def download_statement(self):
        num_initial_downloads = self.num_current_downloads()
        self.login()
        self.driver.get(self.portfolio_url)
        positions_tab = self.find_element_by_xpath('//a[text()="Positions" and @href="#tabContentPositions"]', timeout=self.timeout*2)
        positions_tab.click()
        download_link = self.find_element_by_xpath('//*[text()="Download"]')
        download_link.click()
        self.logout()
        num_final_downloads = self.num_current_downloads()
        assert num_final_downloads > num_initial_downloads
        return self.find_latest_downloaded(pattern=self.statement_fname_regex)

    def login(self):
        self.driver.get(self.login_url)
        username_field = self.find_element_by_xpath('//*[@id="userId-input"]')
        username_field.send_keys(self.username)
        password_field = self.find_element_by_xpath('//*[@id="password"]')
        password_field.send_keys(self.password)
        submit_button = self.find_element_by_xpath('//*[@id="fs-login-button"]')
        submit_button.click()
        self.check_login()

    def logout(self):
        if self.logged_in():
            log_out_link = self.find_element_by_xpath(self.log_out_xpath)
            log_out_link.click()
            self.find_element_by_xpath('//*[text()="Login"]') # wait until logged out

    def check_login(self):
        if not self.logged_in():
            self.mfa_auth()

    def logged_in(self):
        try:
            self.find_element_by_xpath(self.log_out_xpath)
            return True
        except:
            pass
        return False

    def mfa_auth(self):
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

import os
fd = FidelityDownloader(os.environ['FIDELITY_USER'], os.environ['FIDELITY_PASS'], lambda: input('MFA code: '))
statement_fname = fd.download_statement()
print(statement_fname)
