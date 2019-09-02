from .controller import Controller, StatementFactory
from banking.macu_downloader import MacuDownloader
from brokerage.fidelity_downloader import FidelityDownloader
from dataclasses import dataclass

@dataclass
class DownloaderFactory:
    bank_downloader: object = MacuDownloader
    brokerage_downloader: object = FidelityDownloader
    cc_downloader: object = FidelityDownloader
    mfa_callback: object = lambda: input('MFA code: ')

    def bank(self, username, password):
        return self.bank_downloader(username, password)

    def brokerage(self, username, password):
        return fidelity(username, password)

    def cc(self, username, password):
        return fidelity(username, password)

    def fidelity(self, username, password):
        if not self.fidelity_instance:
            self.fidelity_instance = FidelityDownloader(username, password, self.mfa_callback)
        return self.fidelity_instance

class DownloaderController(Controller):
    def __init__(self, balance_sheet, income_statement, cash_flow_statement, statement_factory=StatementFactory(), downloader_factory=DownloaderFactory()):
        super().__init__(balance_sheet, income_statement, cash_flow_statement, statement_factory)
        self.downloader_factory = downloader_factory

    def discover_bank_statements(self):
        pass

    def discover_brokerage_statements(self):
        pass

    def discover_cc_statements(self):
        pass

