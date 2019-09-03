from controller.downloader_controller import DownloaderController
from statements.balance_sheet_statement import BalanceSheetStatement
from statements.income_statement import IncomeStatement
from statements.cash_flow_statement import CashFlowStatement
from datetime import date
import decimal

decimal.getcontext().prec = 6 # to avoid printing too many decimal places

now = date.fromisoformat('2019-08-31')
then = date.fromisoformat('2019-08-01')
now = now.isoformat()
then = then.isoformat()

balance_sheet = BalanceSheetStatement(then, now)
income_statement = IncomeStatement(then, now)
cash_flow_statement = CashFlowStatement(then, now)


controller = DownloaderController(balance_sheet, income_statement, cash_flow_statement)
controller.discover_brokerage_statements()
controller.discover_cc_statements()
controller.discover_bank_statements()
print(cash_flow_statement.to_table())
print(balance_sheet.to_table())
print(income_statement.to_table())

