from statements.cash_flow_statement import CashFlowStatement
from tests.mocks.liabilities.timed_liability_mock import *
from tests.mocks.cc.statement_mock import *
from tests.mocks.paystubs.wages_mock import *
from unittest.mock import PropertyMock
from pytest import fixture
from decimal import Decimal

@fixture(params=[('1970-01-01', '1971-07-31')])
def cash_flow_statement(request):
    return CashFlowStatement(beginning=request.param[0], ending=request.param[1])

class TestCashFlowStatement:
    def test_add_paystub(self, cash_flow_statement):
        paystub = paystub_mock('1970-01-01', '1970-02-01')
        paystub.earnings = earnings_mock(wages=100, bonuses=20)
        paystub.deductions = deductions_mock(total=50)
        paystub.taxes = taxes_mock(total=10)

        cash_flow_statement.add_paystub(paystub)
        assert 100 == cash_flow_statement.operating.salaries
        assert 20 == cash_flow_statement.operating.bonuses
        assert -50 == cash_flow_statement.operating.deductions
        assert -10 == cash_flow_statement.operating.taxes

    def test_add_paystub_date_out_of_range(self, cash_flow_statement):
        earnings = earnings_mock(wages=100, bonuses=20)

        before_paystub = paystub_mock('1969-12-01', '1969-12-31')
        before_paystub.earnings = earnings
        cash_flow_statement.add_paystub(before_paystub)

        after_paystub = paystub_mock('1971-07-31', '1971-08-01')
        after_paystub.earnings = earnings
        cash_flow_statement.add_paystub(after_paystub)

        assert 0 == cash_flow_statement.operating.salaries
        assert 0 == cash_flow_statement.operating.bonuses

    def test_add_timed_liability(self, cash_flow_statement, timed_liability_mock):
        cash_flow_statement.add_timed_liability(timed_liability_mock)
        exp_months = 18
        exp_amount = -(exp_months * timed_liability_mock.monthly_amount_mock.return_value)
        assert exp_amount == cash_flow_statement.operating.expenses

    def test_add_cc_statement(self, cash_flow_statement, cc_statement_mock):
        cc_statement_mock.transactions = [
                transaction_mock('1970-01-01', 1),
                transaction_mock('1970-01-02', 2),
                transaction_mock('1970-01-03', 3),
                transaction_mock('1970-01-03', 4),
        ]
        cc_statement_mock.transactions[-1].in_category.return_value = True # mock education expense
        cash_flow_statement.add_cc_statement(cc_statement_mock)
        assert 6 == cash_flow_statement.operating.expenses
        assert 4 == cash_flow_statement.investing.education

    def test_add_cc_statement_date_out_of_range(self, cash_flow_statement, cc_statement_mock):
        cc_statement_mock.transactions = [
                transaction_mock('1969-12-31', 5),
                transaction_mock('1971-08-01', 6),
        ]
        cash_flow_statement.add_cc_statement(cc_statement_mock)
        assert 0 == cash_flow_statement.operating.expenses

    def test_add_cc_statement_repeated_transaction(self, cash_flow_statement, cc_statement_mock):
        cc_statement_mock.transactions = [
                transaction_mock('1970-01-01', 7),
                transaction_mock('1970-01-01', 7),
        ]
        cash_flow_statement.add_cc_statement(cc_statement_mock)
        assert 7 == cash_flow_statement.operating.expenses

    def test_operating_cash_flow(self, cash_flow_statement):
        cash_flow_statement.operating = [Decimal(1), Decimal(2), Decimal(3)]
        assert 6 == cash_flow_statement.operating_cash_flow

    def test_current_cash_flow(self, cash_flow_statement):
        type(cash_flow_statement).operating_cash_flow = PropertyMock(return_value=6)
        cash_flow_statement.investing = [Decimal(4), Decimal(5), Decimal(6)]
        cash_flow_statement.financing = [Decimal(7), Decimal(8), Decimal(9)]
        assert 45 == cash_flow_statement.current_cash_flow

    def test_final_cash_balance(self, cash_flow_statement):
        cash_flow_statement.orig_cash_balance = 100
        type(cash_flow_statement).current_cash_flow = PropertyMock(return_value=45)
        assert 145 == cash_flow_statement.final_cash_balance

