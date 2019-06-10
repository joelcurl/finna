from recordclass import recordclass
from decimal import Decimal

class CashFlowStatement:
    OperatingActivities = recordclass('OperatingActivities', 'salaries bonuses deductions expenses taxes')
    InvestingActivities = recordclass('InvestingActivities', 'education investment')
    FinancingActivities = recordclass('FinancingActivities', 'creditor_obligations')

    def __init__(self, beginning, ending, orig_cash_balance):
        self.beginning = beginning
        self.ending = ending
        self.orig_cash_balance = orig_cash_balance
        self.operating = self.OperatingActivities(Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0))
        self.investing = self.InvestingActivities(Decimal(0), Decimal(0))
        self.financing = self.FinancingActivities(Decimal(0))

    def add_paystub(self, paystub):
        self.operating.salaries += sum(paystub.earnings.wages.values())
        self.operating.bonuses += sum(paystub.earnings.bonus.values())
        self.operating.deductions -= sum(paystub.deductions.total.values())
        self.operating.taxes -= sum(paystub.taxes.total.values())

    def add_cc_statement(self, statement):
        self.investing.education += statement.category('Education').total
        self.operating.expenses += (statement.total - self.investing.education)
