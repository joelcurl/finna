from brokerage.fidelity_downloader import FidelityDownloader
from controller.downloader_controller import DownloaderFactory
from datetime import date
from time import time
import os
from pytest import fixture

@fixture
def fidelity_downloader():
    creds = DownloaderFactory().user_pass('brokerage')
    mfa_callback = lambda: input('MFA code: ')
    args = creds + [mfa_callback]
    return FidelityDownloader(*args)

class TestFidelityDownloader:
    @property
    def start_date(self):
        return date.fromisoformat('2019-08-01')

    @property
    def end_date(self):
        return date.fromisoformat('2019-08-31')

    def assert_download_time(self, download, start_time):
        downloaded_time = os.path.getmtime(download)
        assert start_time < downloaded_time
        if os.path.exists(download):
            os.unlink(download)

    def test_login(self, fidelity_downloader):
        fidelity_downloader.login()
        assert fidelity_downloader.logged_in()

    def test_logout(self, fidelity_downloader):
        self.test_login(fidelity_downloader) # login first
        fidelity_downloader.logout()
        assert not fidelity_downloader.logged_in()

    def test_download_brokerage_statement(self, fidelity_downloader):
        test_start_time = time()
        downloaded_statement = fidelity_downloader.download_brokerage_statement()
        self.assert_download_time(downloaded_statement, test_start_time)

    def test_download_cc_statement(self, fidelity_downloader):
        test_start_time = time()
        downloaded_statement = fidelity_downloader.download_cc_statement(self.start_date, self.end_date)
        self.assert_download_time(downloaded_statement, test_start_time)
