from controller.directory_controller import DirectoryController, DirStructure
from controller.directory_controller import DirStructUtil as Util
from statements.balance_sheet_statement import BalanceSheetStatement
from statements.income_statement import IncomeStatement
from statements.cash_flow_statement import CashFlowStatement
from datetime import date
import decimal

decimal.getcontext().prec = 6 # to avoid printing too many decimal places

now = date.fromisoformat('2019-08-24')
then = now.replace(month=now.month-1)
now = now.isoformat()
then = then.isoformat()

balance_sheet = BalanceSheetStatement(now)
income_statement = IncomeStatement(then, now)
cash_flow_statement = CashFlowStatement(then, now)

dir_structure = DirStructure()
#dir_structure.bank_statements = Util.path('../banking/input/*')
#dir_structure.brokerage_statements = Util.path('../brokerage/input/*')
#dir_structure.cc_statements = Util.path('../cc/input/*')
#dir_structure.paystubs = Util.path('../paystubs/input/*')

controller = DirectoryController(balance_sheet, income_statement, cash_flow_statement, dir_structure)

print(cash_flow_statement.to_table())
print(balance_sheet.to_table())
print(income_statement.to_table())

