from controller.directory_controller import DirectoryController
from statements.balance_sheet_statement import BalanceSheetStatement
from statements.income_statement import IncomeStatement
from statements.cash_flow_statement import CashFlowStatement
from datetime import datetime

now = datetime.today().date()
then = now.replace(month=now.month-1)
now = now.isoformat()
then = then.isoformat()

balance_sheet = BalanceSheetStatement(now)
income_statement = IncomeStatement(then, now)
cash_flow_statement = CashFlowStatement(then, now, 0) # todo orig_cash_balance == 0? here?

controller = DirectoryController(balance_sheet, income_statement, cash_flow_statement)

