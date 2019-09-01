from util.timeout import timeout
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import InvalidCookieDomainException
from time import sleep
import distutils
import pickle
import os
import re

class Downloader:
    def __init__(self, timeout = 10, storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.selenium'))):
        self.storage_dir = storage_dir
        self.download_dir = os.path.join(self.storage_dir, 'downloads')
        self.timeout = timeout
        profile = self.default_profile
        self.driver = webdriver.Firefox(options=self.default_options, firefox_profile=profile)

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
        profile = FirefoxProfile()
        profile.set_preference('browser.download.folderList', 2) # custom location
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference('browser.download.dir', self.download_dir)
        profile.set_preference('browser.helperApps.alwaysAsk.force', False)
        profile.set_preference('browser.download.useDownloadDir', True)
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', self.all_mime_types)
        return profile

    @property
    def all_mime_types(self):
        mime_types = [
                'text/comma-separated-values',
                'application/x-csv',
        ]
        return ';'.join(mime_types)

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
                except InvalidCookieDomainException: # ignore cookies from other domains
                    pass

    def wait_for_download(self, num_previous_downloads, pattern=None):
        last_size = 0
        current_size = 0
        current_downloads = self.num_current_downloads()
        
        with timeout(self.timeout):
            while current_downloads <= num_previous_downloads:
                current_downloads = self.num_current_downloads()
        download_path = self.find_latest_downloaded(pattern)
        current_size = os.path.getsize(download_path)
        with timeout(self.timeout):
            while current_size > last_size or current_size == 0:
                last_size = current_size
                sleep(1)
                current_size = os.path.getsize(download_path)



    def num_current_downloads(self):
        return len([fname for fname in os.listdir(self.download_dir) if os.path.isfile(os.path.join(self.download_dir, fname))])

    def find_latest_downloaded(self, pattern=None):
        latest_mtime = None
        latest_downloaded = None
        if not pattern:
            pattern = '.*'
        for fname in os.listdir(self.download_dir):
            fpath = os.path.join(self.download_dir, fname)
            if not os.path.isfile(fpath) or not re.search(pattern, fname):
                continue
            mtime = os.path.getmtime(fpath)
            if not latest_mtime or mtime >= latest_mtime:
                latest_mtime = mtime
                latest_downloaded = fpath
        return latest_downloaded

