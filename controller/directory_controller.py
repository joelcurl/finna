from liabilities.timed_liability import concept_lease
from property.mac_book import MacBook
from property.kelly_valuator import ChevyMalibu05Valuator
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
    bank_statements: str = DirStructUtil.path('../banking/input/*')
    brokerage_statements: str = DirStructUtil.path('../brokerage/input/*')
    cc_statements: str = DirStructUtil.path('../cc/input/*')
    paystubs: str = DirStructUtil.path('../paystubs/input/*')
    liabilities: List[str] = field(default_factory=lambda: [concept_lease])
    properties: List[object] = field(default_factory=lambda: [MacBook(), ChevyMalibu05Valuator(milage=150000, sell_zip=84102)])

class DirectoryController:
    def __init__(self, balance_sheet, income_statement, cash_flow_statement, dir_structure = DirStructure()):
        self.balance_sheet = balance_sheet
        self.income_statement = income_statement
        self.cash_flow_statement = cash_flow_statement
        self.dir_structure = dir_structure
        self._discover()

    def _discover(self):
        self._discover_bank_statements()
        self._discover_brokerage_statements()
        self._discover_cc_statements()
        self._discover_paystubs()
        self._discover_liabilities()
        self._discover_properties()

    def _discover_bank_statements(self):
        for statement in glob(self.dir_structure.bank_statements):
            pass

    def _discover_brokerage_statements(self):
        for statement in glob(self.dir_structure.brokerage_statements):
            pass

    def _discover_cc_statements(self):
        for statement in glob(self.dir_structure.cc_statements):
            pass

    def _discover_paystubs(self):
        for paystub in glob(self.dir_structure.paystubs):
            pass

    def _discover_liabilities(self):
        for liability in self.dir_structure.liabilities:
            pass

    def _discover_properties(self):
        for fixed_asset in self.dir_structure.properties:
            pass
