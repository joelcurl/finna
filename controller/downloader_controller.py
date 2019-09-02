from .controller import Controller, StatementFactory
from util.credentials import KeepassCredentials
from banking.macu_downloader import MacuDownloader
from brokerage.fidelity_downloader import FidelityDownloader
from dataclasses import dataclass, field
from typing import Dict
import os

@dataclass
class DownloaderFactory:
    bank_downloader: object = MacuDownloader
    brokerage_downloader: object = FidelityDownloader
    cc_downloader: object = FidelityDownloader
    mfa_callback: object = lambda: input('MFA code: ')
    credentials: object = KeepassCredentials
    creds_location: str = os.environ.get('CREDS_PATH', '')
    creds_password: str = os.environ.get('CREDS_PASS', '')
    cred_entries: Dict = field(default_factory=lambda: {'banking': 'MACU', 'brokerage': 'Fidelity', 'cc': 'Fidelity'})

    bank_instance = None
    fidelity_instance = None
    creds_instance = None

    def bank(self):
        if not self.bank_instance:
            self.bank_instance = self.bank_downloader(*self.user_pass('banking'))
        return self.bank_instance

    def brokerage(self):
        return self.fidelity(*self.user_pass('brokerage'))

    def cc(self):
        return self.fidelity(*self.user_pass('cc'))

    def user_pass(self, thing):
        return [self.username(thing), self.password(thing)]

    def username(self, thing):
        return self.creds.username(self.cred_entries[thing])

    def password(self, thing):
        return self.creds.password(self.cred_entries[thing])

    def fidelity(self, username, password):
        if not self.fidelity_instance:
            self.fidelity_instance = FidelityDownloader(username, password, self.mfa_callback)
        return self.fidelity_instance

    @property
    def creds(self):
        if not self.creds_instance:
            self.creds_instance = self.credentials(self.creds_location, self.creds_password)
        return self.creds_instance

class DownloaderController(Controller):
    def __init__(self, balance_sheet, income_statement, cash_flow_statement, statement_factory=StatementFactory(), downloader_factory=DownloaderFactory()):
        super().__init__(balance_sheet, income_statement, cash_flow_statement, statement_factory)
        self.downloader_factory = downloader_factory
        self.start_date = min(balance_sheet.then, income_statement.beginning, cash_flow_statement.beginning)
        self.end_date = max(balance_sheet.now, income_statement.ending, cash_flow_statement.ending)

    def discover_bank_statements(self):
        downloader = self.downloader_factory.bank()
        statements = downloader.download_statements(self.start_date, self.end_date)
        for statement in statements:
            with open(statement) as f:
                self.balance_sheet.add_bank_statement(self.statement_factory.bank(f.read()))
        self.cash_flow_statement.orig_cash_balance = self.balance_sheet.assets.current.cash

    def discover_brokerage_statements(self):
        raise NotImplementedError

    def discover_cc_statements(self):
        raise NotImplementedError

