from .controller import Controller, StatementFactory
from .downloader_controller import DownloaderController, DownloaderFactory
from .directory_controller import DirectoryController, DirStructure
from statements.balance_sheet_statement import BalanceSheetStatement
from statements.income_statement import IncomeStatement
from statements.cash_flow_statement import CashFlowStatement
from dataclasses import dataclass

@dataclass
class CompositeFactory:
    balance_sheet: BalanceSheetStatement
    income_statement: IncomeStatement
    cash_flow_statement: CashFlowStatement
    statement_factory: StatementFactory = StatementFactory()
    downloader_factory: DownloaderFactory = DownloaderFactory()
    dir_structure: DirStructure = DirStructure()
    downloader_controller_inst: DownloaderController = None
    directory_controller_inst: DirectoryController = None

    @property
    def statements(self):
        return [self.balance_sheet, self.income_statement, self.cash_flow_statement]

    @property
    def downloader_controller(self):
        if not self.downloader_controller_inst:
            self.downloader_controller_inst = DownloaderController(*(self.statements + [self.statement_factory, self.downloader_factory]))
        return self.downloader_controller_inst

    @property
    def directory_controller(self):
        if not self.directory_controller_inst:
            self.directory_controller_inst = DirectoryController(*(self.statements + [self.statement_factory, self.dir_structure]))
        return self.directory_controller_inst

    @property
    def bank_controller(self):
        return self.downloader_controller

    @property
    def brokerage_controller(self):
        return self.downloader_controller

    @property
    def paystub_controller(self):
        return self.directory_controller

    @property
    def properties_controller(self):
        return self.directory_controller

    @property
    def cc_controller(self):
        return self.downloader_controller

    @property
    def liabilities_controller(self):
        return self.directory_controller

class ControllerComposite(Controller):
    def __init__(self, composite_factory):
        self.composite_factory = composite_factory

    def discover_bank_statements(self):
        return self.composite_factory.bank_controller.discover_bank_statements()

    def discover_brokerage_statements(self):
        return self.composite_factory.brokerage_controller.discover_brokerage_statements()

    def discover_paystubs(self):
        return self.composite_factory.paystub_controller.discover_paystubs()

    def discover_properties(self):
        return self.composite_factory.properties_controller.discover_properties()

    def discover_cc_statements(self):
        return self.composite_factory.cc_controller.discover_cc_statements()

    def discover_liabilities(self):
        return self.composite_factory.liabilities_controller.discover_liabilities()
