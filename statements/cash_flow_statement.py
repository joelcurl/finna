from .util import is_date_between
from cc.categories import Education
from recordclass import recordclass
from decimal import Decimal
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tabulate import tabulate

class CashFlowStatement:
    OperatingActivities = recordclass('OperatingActivities', 'salaries bonuses deductions expenses taxes')
    InvestingActivities = recordclass('InvestingActivities', 'education investment')
    FinancingActivities = recordclass('FinancingActivities', 'loans')

    cc_transactions = {}

    def __init__(self, beginning, ending):
        self.beginning = datetime.fromisoformat(beginning).date()
        self.ending = datetime.fromisoformat(ending).date()
        self.orig_cash_balance = Decimal(0)
        self.operating = self.OperatingActivities(Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0))
        self.investing = self.InvestingActivities(Decimal(0), Decimal(0))
        self.financing = self.FinancingActivities(Decimal(0))

    def add_paystub(self, paystub):
        pay_period = paystub.pay_period
        paystub = paystub.current
        if not is_date_between(date=pay_period.end, start=self.beginning, end=self.ending):
            return
        self.operating.salaries += sum(paystub.earnings.wages.values())
        self.operating.bonuses += sum(paystub.earnings.bonus.values())
        self.operating.deductions -= sum(paystub.deductions.total.values())
        self.operating.taxes -= sum(paystub.taxes.total.values())

    def add_timed_liability(self, liability):
        # assume monthly payments
        months = relativedelta(self.ending, self.beginning).months
        self.operating.expenses += months * -liability.monthly_amount

    def add_cc_statement(self, statement):
        for transaction in statement.transactions:
            if is_date_between(transaction.date, self.beginning, self.ending) and transaction.id not in self.cc_transactions:
                self.cc_transactions[transaction.id] = transaction
                if transaction.in_category(Education):
                    self.investing.education += transaction.amount
                else:
                    self.operating.expenses += transaction.amount

    @property
    def operating_cash_flow(self):
        return sum(self.operating)

    @property
    def current_cash_flow(self):
        return self.operating_cash_flow + sum(self.investing) + sum(self.financing)

    @property
    def final_cash_balance(self):
        return self.orig_cash_balance + self.current_cash_flow

    def to_table(self):
        tables = [[
                    ['Cash flow Statement', 'for period'],
                    ['Beginning', self.beginning],
                    ['Ending', self.ending],
                ],
                [

                    ['Operating Activities', 'Amount'],
                    ['Salaries', self.operating.salaries],
                    ['Bonuses', self.operating.bonuses],
                    ['Deductions', self.operating.deductions],
                    ['Expenses', self.operating.expenses],
                    ['Taxes', self.operating.taxes],

                    ['\nOperating Cash Flow\n', self.operating_cash_flow],
                ],
                [
                    ['Investing Activities', 'Amount'],
                    ['Education', self.investing.education],
                    ['Dividends / Interest', self.investing.investment],
                ],
                [
                    ['Financing Activities', 'Amount'],
                    ['Loan Payments', self.financing.loans],
                ],
                [
                    ['Summary', ''],
                    ['Cash Flow this Period', self.current_cash_flow],
                    ['Beginning Cash Balance', self.orig_cash_balance],
                    ['Final Cash Balance', self.final_cash_balance],
                ],
        ]
        formatted_tables = ''
        for table in tables:
            formatted_tables += tabulate(table, tablefmt='fancy_grid', floatfmt='.2f', headers='firstrow') + '\n\n'
        return formatted_tables

