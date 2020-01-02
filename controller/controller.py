from banking.macu_statement import MacuStatement
from brokerage.fidelity_statement import FidelityStatement
from paystubs.reader import AcmePaystubReader
from paystubs.wages import AcmePaystub
from cc.elan_statement import ElanStatementReader
from cc.statement import CcStatement
from cc.visa import MccReader
from liabilities.timed_liability import TimedLiability, real_estate_leases
from liabilities.static_liability import StaticLiability, education_liabilities
from property.mac_book import MacBook
from property.kelly_valuator import ChevyMalibu05Valuator
from dataclasses import dataclass, field
from typing import List

@dataclass
class StatementFactory:
    bank_statement = MacuStatement
    brokerage_statement = FidelityStatement
    paystub_reader = lambda self, fname: AcmePaystub(AcmePaystubReader(fname).text)
    cc_statement = lambda self, cc_contents, mcc_contents: CcStatement(ElanStatementReader(cc_contents), MccReader(mcc_contents))
    properties: List[object] = field(default_factory=lambda: [MacBook(), ChevyMalibu05Valuator(milage=150000, sell_zip=84102)])
    timed_liabilities: List[TimedLiability] = field(default_factory=lambda: real_estate_leases)
    static_liabilities: List[StaticLiability] = field(default_factory=lambda: education_liabilities)

    def bank(self, contents):
        return self.bank_statement(contents)

    def brokerage(self, contents):
        return self.brokerage_statement(contents)

    def paystub(self, fname):
        return self.paystub_reader(fname)

    def cc(self, cc_contents, mcc_contents):
        return self.cc_statement(cc_contents, mcc_contents)

class Controller:
    def __init__(self, balance_sheet, income_statement, cash_flow_statement, statement_factory=StatementFactory()):
        self.balance_sheet = balance_sheet
        self.income_statement = income_statement
        self.cash_flow_statement = cash_flow_statement
        self.statement_factory = statement_factory

    def discover(self):
        self.discover_brokerage_statements()
        self.discover_cc_statements()
        self.discover_bank_statements()
        self.discover_paystubs()
        self.discover_properties()
        self.discover_liabilities()

    def discover_liabilities(self):
        for liability in self.statement_factory.timed_liabilities:
            self.cash_flow_statement.add_timed_liability(liability)
            self.balance_sheet.add_timed_liability(liability)
            self.income_statement.add_timed_liability(liability)

        for liability in self.statement_factory.static_liabilities:
            self.balance_sheet.add_static_liability(liability)

    def discover_properties(self):
        for fixed_asset in self.statement_factory.properties:
            self.balance_sheet.add_fixed_asset(fixed_asset)

    def discover_bank_statements(self):
        raise NotImplementedError

    def discover_brokerage_statements(self):
        raise NotImplementedError

    def discover_paystubs(self):
        raise NotImplementedError

    def discover_cc_statements(self):
        raise NotImplementedError

