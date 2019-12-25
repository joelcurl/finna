from statements.income_statement import IncomeStatement
from cc.categories import *
from tests.mocks.liabilities.timed_liability_mock import *
from tests.mocks.cc.statement_mock import *
from tests.mocks.paystubs.wages_mock import *
from pytest import fixture, mark
from decimal import Decimal

@fixture(params=[('1970-01-01', '1971-07-31')])
def income_statement(request):
    return IncomeStatement(beginning=request.param[0], ending=request.param[1])

class TestIncomeStatement:
    def test_add_paystub(self, income_statement):
        paystub = paystub_mock('1970-01-01', '1970-02-01')
        paystub.earnings = earnings_mock(wages=100, bonuses=20)
        paystub.deductions = deductions_mock(total=50)
        paystub.taxes = taxes_mock(total=10)

        income_statement.add_paystub(paystub)
        assert 100 == income_statement.revenue.salaries
        assert 20 == income_statement.revenue.bonuses
        assert -50 == income_statement.expenses.ebit.deductions
        assert -10 == income_statement.expenses.it.taxes

    def test_add_paystub_date_out_of_range(self, income_statement):
        earnings = earnings_mock(wages=100, bonuses=20)

        before_paystub = paystub_mock('1969-12-01', '1969-12-31')
        before_paystub.earnings = earnings
        income_statement.add_paystub(before_paystub)

        after_paystub = paystub_mock('1971-07-31', '1971-08-01')
        after_paystub.earnings = earnings
        income_statement.add_paystub(after_paystub)

        assert 0 == income_statement.revenue.salaries
        assert 0 == income_statement.revenue.bonuses

    def test_timed_liability(self, income_statement, timed_liability_mock):
        income_statement.add_timed_liability(timed_liability_mock)
        assert -timed_liability_mock.amount_from.return_value == income_statement.expenses.ebit.o_and_a

    def test_add_cc_statement(self, income_statement, cc_statement_mock):
        cc_statement_mock.transactions = [
                transaction_mock('1970-01-01', 1, Automotive),
                transaction_mock('1970-01-02', 2, Education),
                transaction_mock('1970-01-03', 3, Entertainment),
                transaction_mock('1970-01-04', 4, Food),
                transaction_mock('1970-01-05', 5, Luxuries),
                transaction_mock('1970-01-06', 6, Medical),
                transaction_mock('1970-01-07', 7, Utilities),
                transaction_mock('1970-01-08', 8, Other),
        ]
        income_statement.add_cc_statement(cc_statement_mock)
        assert -(1+4+6+7) == income_statement.expenses.ebit.o_and_a
        assert -(2) == income_statement.expenses.ebit.education
        assert -(3+5+8) == income_statement.expenses.ebit.discretionary

    def test_add_cc_statement_date_out_of_range(self, income_statement, cc_statement_mock):
        cc_statement_mock.transactions = [
                transaction_mock('1969-12-31', 9),
                transaction_mock('1971-08-01', 10),
        ]
        income_statement.add_cc_statement(cc_statement_mock)
        assert 0 == income_statement.expenses.ebit.o_and_a
        assert 0 == income_statement.expenses.ebit.education
        assert 0 == income_statement.expenses.ebit.discretionary

    def test_add_cc_statement_repeated_transaction(self, income_statement, cc_statement_mock):
        cc_statement_mock.transactions = [
                transaction_mock('1970-01-01', 11),
                transaction_mock('1970-01-01', 11),
        ]
        income_statement.add_cc_statement(cc_statement_mock)
        assert -11 == income_statement.expenses.ebit.discretionary

    def test_revenue_total(self, income_statement):
        income_statement.revenue = [12, 13, 14]
        assert 39 == income_statement.revenue_total

    def test_ebit_expenses(self, income_statement):
        income_statement.expenses.ebit = [-15, -16]
        assert -31 == income_statement.ebit_expenses

    def test_it_expenses(self, income_statement):
        income_statement.expenses.it = [-17, -18]
        assert -35 == income_statement.it_expenses

    def test_expenses_total(self, income_statement):
        type(income_statement).ebit_expenses = -19
        type(income_statement).it_expenses = -20
        assert -39 == income_statement.expenses_total

    def test_operating_income(self, income_statement):
        type(income_statement).revenue_total = 21
        type(income_statement).ebit_expenses = -22
        assert -1 == income_statement.operating_income

    def test_net_income(self, income_statement):
        type(income_statement).revenue_total = 23
        type(income_statement).expenses_total = -24
        assert -1 == income_statement.net_income

