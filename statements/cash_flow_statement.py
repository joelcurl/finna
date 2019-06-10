from recordclass import recordclass
from decimal import Decimal
from tabulate import tabulate

class CashFlowStatement:
    OperatingActivities = recordclass('OperatingActivities', 'salaries bonuses deductions expenses taxes')
    InvestingActivities = recordclass('InvestingActivities', 'education investment')
    FinancingActivities = recordclass('FinancingActivities', 'loans')
    operating_cash_flow = Decimal(0)
    current_cash_flow = Decimal(0)
    final_cash_balance = Decimal(0)

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
        self.__compute_summaries()

    def add_cc_statement(self, statement):
        self.investing.education += statement.category('Education').total
        self.operating.expenses += (statement.total - self.investing.education)
        self.__compute_summaries()

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

    def __compute_summaries(self):
        self.operating_cash_flow = sum(self.operating)
        self.current_cash_flow = self.operating_cash_flow + sum(self.investing) + sum(self.financing)
        self.final_cash_balance = self.orig_cash_balance + self.current_cash_flow
