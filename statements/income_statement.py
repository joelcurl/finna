from .util import is_date_between
from cc.categories import *
from decimal import Decimal
from taxes.tax import SingleTax as Tax
from liabilities.accrual_basis import SemesterAccrualBasis
from recordclass import recordclass
from datetime import date
from tabulate import tabulate

class IncomeStatement:
    Revenue = recordclass('Revenue', 'salaries bonuses capital_gains')
    EbitExpenses = recordclass('EbitExpenses', 'o_and_a education a_and_m discretionary debts')
    ItExpenses = recordclass('ItExpenses', 'interest taxes')
    Expenses = recordclass('Expenses', 'ebit it')

    cc_transactions = {}

    def __init__(self, beginning, ending):
        self.beginning = date.fromisoformat(beginning)
        self.ending = date.fromisoformat(ending)

        self.revenue = self.Revenue(Decimal(0), Decimal(0), Decimal(0))
        self.expenses = self.Expenses(
                self.EbitExpenses(Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0)),
                self.ItExpenses(Decimal(0), Decimal(0)),
        )

    def add_paystub(self, paystub):
        pay_period = paystub.pay_period
        paystub = paystub.current
        if not is_date_between(date=pay_period.end, start=self.beginning, end=self.ending):
            return
        self.revenue.salaries += sum(paystub.earnings.wages.values())
        self.revenue.bonuses += sum(paystub.earnings.bonus.values())
        self.expenses.ebit.o_and_a += -sum(paystub.deductions.total.values())
        self.expenses.it.taxes += -sum(paystub.taxes.total.values())

    def add_timed_liability(self, liability):
        self.expenses.ebit.o_and_a += -liability.amount_from(self.beginning, self.ending)

    def add_cc_statement(self, statement):
        for transaction in statement.transactions:
            if is_date_between(transaction.date, self.beginning, self.ending) and transaction.id not in self.cc_transactions:
                self.cc_transactions[transaction.id] = transaction
                if transaction.in_category(Automotive):
                    self.expenses.ebit.o_and_a += transaction.amount
                elif transaction.in_category(Education):
                    self.expenses.ebit.education += -SemesterAccrualBasis(transaction.amount).accrued(self.beginning, self.ending)
                elif transaction.in_category(Entertainment):
                    self.expenses.ebit.discretionary += transaction.amount
                elif transaction.in_category(Food):
                    self.expenses.ebit.o_and_a += transaction.amount
                elif transaction.in_category(Luxuries):
                    self.expenses.ebit.discretionary += transaction.amount
                elif transaction.in_category(Medical):
                    self.expenses.ebit.o_and_a += transaction.amount
                elif transaction.in_category(Utilities):
                    self.expenses.ebit.o_and_a += transaction.amount
                else:
                    self.expenses.ebit.discretionary += transaction.amount

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
        return self.revenue_total + self.ebit_expenses # expenses are negative, so really revenue - expenses

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

                [['Operating Income (EBIT)', self.operating_income]],

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
