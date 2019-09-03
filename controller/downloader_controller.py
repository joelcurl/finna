from controller.controller import Controller, StatementFactory
from controller.directory_controller import DirStructUtil
from util.credentials import KeepassCredentials
from banking.macu_downloader import MacuDownloader
from brokerage.fidelity_downloader import FidelityDownloader
from cc.visa import TransactionDb
from dataclasses import dataclass, field
from typing import Dict
import os

@dataclass
class DownloaderFactory:
    bank_downloader: object = MacuDownloader
    brokerage_downloader: object = FidelityDownloader
    cc_downloader: object = FidelityDownloader
    mcc_codes: str = DirStructUtil.path('../cc/mcc-codes/mcc_codes.csv')
    cc_db: str = 'sqlite:///:memory:'
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

# todo remove temp files?
class DownloaderController(Controller):
    def __init__(self, balance_sheet, income_statement, cash_flow_statement, statement_factory=StatementFactory(), downloader_factory=DownloaderFactory()):
        super().__init__(balance_sheet, income_statement, cash_flow_statement, statement_factory)
        self.downloader_factory = downloader_factory
        self.start_date = min(balance_sheet.then, income_statement.beginning, cash_flow_statement.beginning)
        self.end_date = max(balance_sheet.now, income_statement.ending, cash_flow_statement.ending)
        self.db = TransactionDb()
        self.db.connect(self.downloader_factory.cc_db)

    def discover_bank_statements(self):
        downloader = self.downloader_factory.bank()
        statements = downloader.download_statements(self.start_date, self.end_date)
        for fname in statements:
            with open(fname) as f:
                statement = self.statement_factory.bank(f.read())
                self.balance_sheet.add_bank_statement(statement)
        self.cash_flow_statement.orig_cash_balance = self.balance_sheet.assets.current.cash

    def discover_brokerage_statements(self):
        downloader = self.downloader_factory.brokerage()
        fname = downloader.download_brokerage_statement()
        with open(fname) as f:
            statement = self.statement_factory.brokerage(f.read())
            for account in statement.accounts:
                self.balance_sheet.add_brokerage_statement(account)

    def discover_cc_statements(self):
        downloader = self.downloader_factory.brokerage()
        fname = downloader.download_cc_statement(self.start_date, self.end_date)
        with open(self.downloader_factory.mcc_codes) as mcc_f:
            mcc = mcc_f.read()
            with open(fname) as cc:
                statement = self.statement_factory.cc(cc.read(), mcc)
                self.cash_flow_statement.add_cc_statement(statement)
                self.balance_sheet.add_cc_statement(statement)
                self.income_statement.add_cc_statement(statement)

