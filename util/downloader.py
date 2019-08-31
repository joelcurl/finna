from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import InvalidCookieDomainException
import pickle
import os

class Downloader:
    def __init__(self, timeout = 10, storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.selenium'))):
        self.storage_dir = storage_dir
        self.timeout = timeout
        self.driver = webdriver.Firefox(options=self.default_options, firefox_profile=self.default_profile)

    def __del__(self):
        self.driver.quit()

    def find_element_by_xpath(self, xpath, timeout = None):
        if not timeout:
            timeout = self.timeout
        WebDriverWait(self.driver, timeout).until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))
        elements = self.driver.find_elements_by_xpath(xpath)
        for element in elements:
            if element.is_displayed():
                return element
        if len(elements) > 0:
            return elements[0]

    @property
    def default_options(self):
        options = Options()
        #options.headless = True # todo undo
        return options

    @property
    def default_profile(self):
        profile = FirefoxProfile(profile_directory=os.path.join(self.storage_dir, 'profile'))
        profile.set_preference('browser.download.folderList', 2) # custom location
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference('browser.download.dir', os.path.join(self.storage_dir, 'downloads'))
        profile.set_preference('browser.helperApps.alwaysAsk.force', False)
        return profile

    def screenshot(self, fpath = '/mnt/c/Users/jcurl/Documents/selenium.png'):
        self.driver.save_screenshot(fpath)

    def save_cookies(self, fname):
        with open(os.path.join(self.storage_dir, fname), 'wb') as f:
            pickle.dump(self.driver.get_cookies(), f)

    def load_cookies(self, fname):
        with open(os.path.join(self.storage_dir, fname), 'rb') as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except InvalidCookieDomainException: # ignore cookies from other sessions
                    pass

