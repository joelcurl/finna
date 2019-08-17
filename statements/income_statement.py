from recordclass import recordclass
from decimal import Decimal
from taxes.tax import SingleTax as Tax
from liabilities.accrual_basis import SemesterAccrualBasis
from tabulate import tabulate

# todo o_and_a need cc statements, res. lease

class IncomeStatement:
    Revenue = recordclass('Revenue', 'salaries bonuses capital_gains')
    EbitExpenses = recordclass('EbitExpenses', 'o_and_a education a_and_m discretionary debts')
    ItExpenses = recordclass('ItExpenses', 'interest taxes')
    Expenses = recordclass('Expenses', 'ebit it')

    def __init__(self, beginning, ending):
        self.beginning = beginning
        self.ending = ending

        self.revenue = self.Revenue(Decimal(0), Decimal(0), Decimal(0))
        self.expenses = self.Expenses(
                self.EbitExpenses(Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0)),
                self.ItExpenses(Decimal(0), Decimal(0)),
        )

    def add_paystub(self, paystub):
        self.revenue.salaries += sum(paystub.current.earnings.wages.values())
        self.revenue.bonuses += sum(paystub.current.earnings.bonus.values())
        self.expenses.ebit.o_and_a += -sum(paystub.current.deductions.total.values())
        self.expenses.it.taxes += -sum(paystub.current.taxes.total.values())

    def add_timed_liability(self, liability):
        self.expenses.ebit.o_and_a += -liability.amount_from(self.beginning, self.ending)

    def add_cc_statement(self, statement):
        self.expenses.ebit.o_and_a += statement.category('Automotive').total
        self.expenses.ebit.education += -SemesterAccrualBasis(statement.category('Education').total).accrued(self.beginning, self.ending)
        self.expenses.ebit.discretionary += statement.category('Entertainment').total
        self.expenses.ebit.o_and_a += statement.category('Food').total
        self.expenses.ebit.discretionary += statement.category('Luxuries').total
        self.expenses.ebit.o_and_a += statement.category('Medical').total
        self.expenses.ebit.o_and_a += statement.category('Utilities').total
        self.expenses.ebit.discretionary += statement.category('Other').total

    @property
    def revenue_total(self):
        return sum([source for source in self.revenue])

    @property
    def ebit_expenses(self):
        return sum([source for source in self.expenses.ebit])

    @property
    def it_expenses(self):
        return sum([source for source in self.expenses.it])

    @property
    def expenses_total(self):
        return sum([self.ebit_expenses, self.it_expenses])

    @property
    def operating_income(self):
        return self.revenue_total - ebit_expenses

    @property
    def net_income(self):
        return self.revenue_total + self.expenses_total # expenses are negative, so really revenue - expenses

    def to_table(self):
        tables = [
                [
                    ['Income Statement', 'for period'],
                    ['Beginning', self.beginning],
                    ['Ending', self.ending],
                ],

                [['Revenue']],

                [
                    ['Salaries', self.revenue.salaries],
                    ['Bonuses', self.revenue.bonuses],
                    ['Realized Capital Gains', self.revenue.capital_gains],
                    ['Total', self.revenue_total],
                ],

                [['Expenses']],

                [
                    ['Operating and Administrative', self.expenses.ebit.o_and_a],
                    ['Education', self.expenses.ebit.education],
                    ['Acquisition and Maintenence', self.expenses.ebit.a_and_m],
                    ['Discretionary', self.expenses.ebit.discretionary],
                    ['Creditor Obligations', self.expenses.ebit.debts],
                    ['Total', self.ebit_expenses],
                ],

                [['Operating Income (EBIT)', self.ebit_expenses]],

                [
                    ['Interest Expense', self.expenses.it.interest],
                    ['Income Tax Expense', self.expenses.it.taxes],
                    ['Total', self.it_expenses]
                ],

                [['Net Income', self.net_income]],
        ]

        formatted_tables = ''
        for table in tables:
            formatted_tables += tabulate(table, tablefmt='fancy_grid', floatfmt='.2f', headers='firstrow') + '\n\n'
        return formatted_tables
