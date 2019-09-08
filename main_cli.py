from controller.controller_composite import ControllerComposite, CompositeFactory
from statements.balance_sheet_statement import BalanceSheetStatement
from statements.income_statement import IncomeStatement
from statements.cash_flow_statement import CashFlowStatement
from datetime import date
import decimal

decimal.getcontext().prec = 6 # to avoid printing too many decimal places

def dates():
    now = date.fromisoformat('2019-08-31')
    then = date.fromisoformat('2019-08-01')
    now = now.isoformat()
    then = then.isoformat()
    return [then, now]

if __name__ == "__main__":
    balance_sheet = BalanceSheetStatement(*dates())
    income_statement = IncomeStatement(*dates())
    cash_flow_statement = CashFlowStatement(*dates())

    composite_factory = CompositeFactory(balance_sheet, income_statement, cash_flow_statement)
    controller = ControllerComposite(composite_factory)
    controller.discover()

    print(cash_flow_statement.to_table())
    print(balance_sheet.to_table())
    print(income_statement.to_table())

