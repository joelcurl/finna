from banking.macu_downloader import MacuDownloader
from controller.downloader_controller import DownloaderFactory
from datetime import date
from time import time
import os
from pytest import fixture

@fixture
def macu_downloader():
    creds = DownloaderFactory().user_pass('banking')
    return MacuDownloader(*creds)

class TestMacuDownloader:
    @property
    def start_date(self):
        return date.fromisoformat('2019-08-01')

    @property
    def end_date(self):
        return date.fromisoformat('2019-08-31')

    def assert_download_time(self, downloads, start_time):
        for download in downloads:
            downloaded_time = os.path.getmtime(download)
            assert start_time < downloaded_time
            if os.path.exists(download):
                os.unlink(download)

    def test_login(self, macu_downloader):
        macu_downloader.login()
        assert macu_downloader.logged_in()

    def test_logout(self, macu_downloader):
        self.test_login(macu_downloader) # to login
        macu_downloader.logout()
        assert not macu_downloader.logged_in()

    def test_download_statement(self, macu_downloader):
        test_start_time = time()
        downloaded_statement = macu_downloader.download_statement(macu_downloader.accounts[0], self.start_date, self.end_date)
        self.assert_download_time([downloaded_statement], test_start_time)

    def test_download_statements(self, macu_downloader):
        test_start_time = time()
        downloaded_statements = macu_downloader.download_statements(self.start_date, self.end_date)
        self.assert_download_time(downloaded_statements, test_start_time)
