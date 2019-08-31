from util.downloader import Downloader
from selenium.common.exceptions import NoSuchElementException

class FidelityDownloader(Downloader):
    def __init__(self, username, password, mfa_callback, cookie_file = 'fidelity.cookies', quick_timeout = 5):
        super().__init__()
        self.username = username
        self.password = password
        self.mfa_callback = mfa_callback
        self.cookie_file = cookie_file
        self.quick_timeout = quick_timeout

    def get_statement(self):
        self.login()

    def login(self, login_url = 'https://digital.fidelity.com/prgw/digital/login/full-page'):
        self.driver.get(login_url)
        try:
            self.load_cookies(self.cookie_file)
        except FileNotFoundError: # no cookies - yet
            pass
        username_field = self.find_element_by_xpath('//*[@id="userId-input"]')
        username_field.send_keys(self.username)
        password_field = self.find_element_by_xpath('//*[@id="password"]')
        password_field.send_keys(self.password)
        submit_button = self.find_element_by_xpath('//*[@id="fs-login-button"]')
        submit_button.click()
        self.check_login()

    def check_login(self):
        if not self.logged_in():
            self.mfa_auth()

    def logged_in(self):
        try:
            self.find_element_by_xpath('//*[text()="Log Out"]', timeout = quick_timeout)
            return True
        except Exception as e:
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
        if self.logged_in():
            self.save_cookies(self.cookie_file)

import os
fd = FidelityDownloader(os.environ['FIDELITY_USER'], os.environ['FIDELITY_PASS'], lambda: input('MFA code: '))
statement = fd.get_statement()
