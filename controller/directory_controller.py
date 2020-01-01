from .controller import Controller, StatementFactory
from cc.visa import TransactionDb
from dataclasses import dataclass
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
    cc_db: str = 'sqlite:///:memory:'
    mcc_codes: str = DirStructUtil.path('../cc/mcc-codes/mcc_codes.csv')
    cc_statements: str = DirStructUtil.path('../input/cc/*')
    paystubs: str = DirStructUtil.path('../input/paystubs/*')

class DirectoryController(Controller):
    def __init__(self, balance_sheet, income_statement, cash_flow_statement, statement_factory=StatementFactory(), dir_structure=DirStructure()):
        super().__init__(balance_sheet, income_statement, cash_flow_statement, statement_factory)
        self.dir_structure = dir_structure
        self.db = TransactionDb()
        self.db.connect(self.dir_structure.cc_db)

    def discover_bank_statements(self):
        for statement in glob(self.dir_structure.bank_statements):
            with open(statement) as f:
                self.balance_sheet.add_bank_statement(self.statement_factory.bank(f.read()))
        self.cash_flow_statement.orig_cash_balance = self.balance_sheet.assets.current.cash

    def discover_brokerage_statements(self):
        for statement in glob(self.dir_structure.brokerage_statements):
            with open(statement) as f:
                brokerage_accounts = self.statement_factory.brokerage(f.read())
                for account in brokerage_accounts.accounts:
                    self.balance_sheet.add_brokerage_statement(account)

    def discover_paystubs(self):
        paystubs = glob(self.dir_structure.paystubs)
        paystubs.sort()
        for paystub_statement in paystubs:
            with open(paystub_statement, 'rb') as f:
                paystub = self.statement_factory.paystub(f)
                self.cash_flow_statement.add_paystub(paystub)
                self.balance_sheet.add_paystub(paystub)
                self.income_statement.add_paystub(paystub)

    def discover_cc_statements(self):
        with open(self.dir_structure.mcc_codes) as mcc_f:
            mcc = mcc_f.read()
            for statement in glob(self.dir_structure.cc_statements):
                with open(statement) as cc:
                    cc_statement = self.statement_factory.cc(cc.read(), mcc)
                    self.cash_flow_statement.add_cc_statement(cc_statement)
                    self.balance_sheet.add_cc_statement(cc_statement)
                    self.income_statement.add_cc_statement(cc_statement)

