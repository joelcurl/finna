from util.downloader import Downloader
import requests

class MacuDownloader(Downloader):
    login_url = 'https://o.macu.com/Authentication'
    logout_url = 'https://o.macu.com/Logout'
    accounts_url = 'https://o.macu.com/MyAccountsV2'
    statement_fname_regex = '(ExportedTransactions.*\.csv)'
    log_out_xpath = '//*[@href="/Logout"]'
    accounts = ['DEBIT CHECKING', 'PAPER CHECKING', 'MONEY MARKET', 'PRIMARY SAVINGS']
    date_format = '{:%m/%d/%Y}'

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password

    def download_statements(self, start_date, end_date, logout_after=False):
        downloads = []
        for account in self.accounts:
            downloads += [self.download_statement(account, start_date, end_date, logout_after=False)]
        if logout_after:
            self.logout()
        return downloads

    def download_statement(self, account, start_date, end_date, logout_after=False):
        num_initial_downloads = self.num_current_downloads()
        if not self.logged_in():
            self.login()
        self.driver.get(self.accounts_url)
        account_tab = self.find_element_by_xpath(f'//*[text()="{account}"]')
        account_tab.click()
        export_link = self.find_element_by_xpath('//*[@id="export_trigger"]')
        self.find_element_by_xpath('//*[@id="posted_transactions"]') # wait for transactions table to load
        export_link.click()
        dropdown = self.find_element_by_xpath('//input[@id="ext-gen5"]')
        dropdown.click()
        csv_selection = self.find_element_by_xpath('//*[text()="Comma Separated Values (CSV)"]')
        csv_selection.click()
        start_date_input = self.find_element_by_xpath('//input[@id="Parameters_StartDate"]')
        start_date_input.clear()
        start_date_input.send_keys(self.date_format.format(start_date))
        end_date_input = self.find_element_by_xpath('//input[@id="Parameters_EndDate"]')
        end_date_input.clear()
        end_date_input.send_keys(self.date_format.format(end_date))
        download_button = self.find_element_by_xpath('//button[@id="export_transactions_confirm_button"]')
        download_button.click()
        self.wait_for_download(num_initial_downloads, self.statement_fname_regex)
        if logout_after:
            self.logout()
        return self.find_latest_downloaded(pattern=self.statement_fname_regex)

    def login(self):
        self.driver.get(self.login_url)
        username_field = self.find_element_by_xpath('//input[@id="UserName"]')
        username_field.send_keys(self.username)
        password_field = self.find_element_by_xpath('//input[@id="Password"]')
        password_field.send_keys(self.password)
        login_button = self.find_element_by_xpath('//button[text()="Log In"]')
        login_button.click()
        self.logged_in() # wait until logged in

    def logout(self):
        if self.logged_in():
            self.driver.get(self.logout_url)
            self.find_element_by_xpath('//*[contains(., "Log in")]') # wait until logged out

    def logged_in(self):
        try:
            self.find_element_by_xpath(self.log_out_xpath)
            return True
        except:
            pass
        return False

