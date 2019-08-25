from banking.macu_statement import MacuStatement
from brokerage.fidelity_statement import FidelityStatement, ACCOUNTS
from liabilities.timed_liability import TimedLiability, concept_lease
from liabilities.static_liability import StaticLiability, education_liabilities
from paystubs.reader import AcmePaystubReader
from paystubs.wages import AcmePaystub
from property.mac_book import MacBook
from property.kelly_valuator import ChevyMalibu05Valuator
from cc.visa import TransactionDb, MccReader
from cc.elan_statement import ElanStatementReader
from cc.statement import CcStatement
from dataclasses import dataclass, field
from typing import List
from glob import glob
import os

class DirStructUtil:
    @staticmethod
    def dir():
        return os.path.dirname(os.path.realpath(__file__))

    @staticmethod
    def path(fname):
        return os.path.abspath(os.path.join(DirStructUtil.dir(), fname))

@dataclass
class DirStructure:
    bank_statements: str = DirStructUtil.path('../input/banking/*')
    brokerage_statements: str = DirStructUtil.path('../input/brokerage/*')
    cc_db: str = 'sqlite:///cc/cc.db'
    mcc_codes: str = DirStructUtil.path('../cc/mcc-codes/mcc_codes.csv')
    cc_statements: str = DirStructUtil.path('../input/cc/*')
    paystubs: str = DirStructUtil.path('../input/paystubs/*')
    properties: List[object] = field(default_factory=lambda: [MacBook(), ChevyMalibu05Valuator(milage=150000, sell_zip=84102)])
    timed_liabilities: List[TimedLiability] = field(default_factory=lambda: [concept_lease])
    static_liabilities: List[StaticLiability] = field(default_factory=lambda: education_liabilities)

class StatementFactory:
    bank_statement = MacuStatement
    brokerage_statement = FidelityStatement
    paystub_reader = lambda self, fname: AcmePaystub(AcmePaystubReader(fname).text)
    cc_statement = lambda self, cc_contents, mcc_contents: CcStatement(ElanStatementReader(cc_contents), MccReader(mcc_contents))

    def bank(self, contents):
        return self.bank_statement(contents)

    def brokerage(self, contents):
        return self.brokerage_statement(contents)

    def paystub(self, fname):
        return self.paystub_reader(fname)

    def cc(self, cc_contents, mcc_contents):
        return self.cc_statement(cc_contents, mcc_contents)

class DirectoryController:
    def __init__(self, balance_sheet, income_statement, cash_flow_statement, dir_structure = DirStructure(), factory = StatementFactory()):
        self.balance_sheet = balance_sheet
        self.income_statement = income_statement
        self.cash_flow_statement = cash_flow_statement
        self.dir_structure = dir_structure
        self.factory = factory

        self.db = TransactionDb()
        self.db.connect(self.dir_structure.cc_db)
        self._discover()

    def _discover(self):
        self._discover_bank_statements()
        self._discover_brokerage_statements()
        self._discover_paystubs()
        self._discover_properties()
        self._discover_cc_statements()
        self._discover_liabilities()

    def _discover_bank_statements(self):
        for statement in glob(self.dir_structure.bank_statements):
            with open(statement) as f:
                self.balance_sheet.add_bank_statement(self.factory.bank(f.read()))
        self.cash_flow_statement.orig_cash_balance = self.balance_sheet.assets.current.cash

    def _discover_brokerage_statements(self):
        for statement in glob(self.dir_structure.brokerage_statements):
            with open(statement) as f:
                brokerage_accounts = self.factory.brokerage(f.read())
                for account in ACCOUNTS.keys():
                    if account == 'SAVINGS' or account == 'INVESTMENT': # todo this should probably be a detail of the class
                        self.balance_sheet.add_brokerage_statement_to_current(account, brokerage_accounts.accounts[account])
                    else:
                        self.balance_sheet.add_brokerage_statement_to_noncurrent(account, brokerage_accounts.accounts[account])

    def _discover_paystubs(self):
        for paystub_statement in glob(self.dir_structure.paystubs):
            with open(paystub_statement, 'rb') as f:
                paystub = self.factory.paystub(f)
                self.cash_flow_statement.add_paystub(paystub)
                self.balance_sheet.add_paystub(paystub)
                self.income_statement.add_paystub(paystub)

    def _discover_properties(self):
        for fixed_asset in self.dir_structure.properties:
            self.balance_sheet.add_fixed_asset(fixed_asset)

    def _discover_cc_statements(self):
        with open(self.dir_structure.mcc_codes) as mcc_f:
            mcc = mcc_f.read()
            for statement in glob(self.dir_structure.cc_statements):
                with open(statement) as cc:
                    cc_statement = self.factory.cc(cc.read(), mcc)
                    self.cash_flow_statement.add_cc_statement(cc_statement)
                    self.balance_sheet.add_cc_statement(cc_statement)
                    self.income_statement.add_cc_statement(cc_statement)

    def _discover_liabilities(self):
        for liability in self.dir_structure.timed_liabilities:
            self.cash_flow_statement.add_timed_liability(liability)
            self.balance_sheet.add_timed_liability(liability)
            self.income_statement.add_timed_liability(liability)

        for liability in self.dir_structure.static_liabilities:
            self.balance_sheet.add_static_liability(liability)

