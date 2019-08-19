from controller.directory_controller import DirectoryController
from statements.balance_sheet_statement import BalanceSheetStatement
from statements.income_statement import IncomeStatement
from statements.cash_flow_statement import CashFlowStatement
from datetime import datetime

now = datetime.today().date()
then = now.replace(month=now.month-3)
now = now.isoformat()
then = then.isoformat()

balance_sheet = BalanceSheetStatement(now)
income_statement = IncomeStatement(then, now)
cash_flow_statement = CashFlowStatement(then, now)

controller = DirectoryController(balance_sheet, income_statement, cash_flow_statement)

print(cash_flow_statement.to_table())
#print(balance_sheet.to_table())
#print(income_statement.to_table())
