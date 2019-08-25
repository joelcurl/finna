from statements.balance_sheet_statement import BalanceSheetStatement
from cc.categories import *
from tests.mocks.property.property_mock import *
from tests.mocks.liabilities.timed_liability_mock import *
from tests.mocks.cc.statement_mock import *
from tests.mocks.paystubs.wages_mock import *
from unittest.mock import PropertyMock, patch
from copy import deepcopy
from dateutil.relativedelta import relativedelta
from pytest import fixture, mark
from decimal import Decimal

@fixture(params=['1971-07-31'])
def balance_sheet(request):
    return BalanceSheetStatement(now=request.param)

class TestBalanceSheetStatement:
    def test_add_bank_statement(self, balance_sheet):
        bank_statement = Mock()
        type(bank_statement).balance = 1
        balance_sheet.add_bank_statement(bank_statement)
        assert 1 == balance_sheet.assets.current.cash

    def test_add_brokerage_statement_to_current(self, balance_sheet):
        brokerage_statement = Mock()
        type(brokerage_statement).total = 2
        balance_sheet.add_brokerage_statement_to_current('test account', brokerage_statement)
        assert 2 == balance_sheet.assets.current.brokerage['test account']

    def test_add_brokerage_statement_to_noncurrent(self, balance_sheet):
        brokerage_statement = Mock()
        type(brokerage_statement).total = 3
        balance_sheet.add_brokerage_statement_to_noncurrent('test account', brokerage_statement)
        assert 3 == balance_sheet.assets.noncurrent.brokerage['test account']

    def test_add_paystub(self, balance_sheet):
        paystub = paystub_mock('1970-01-01', '1970-02-01')
        taxes = taxes_withholding_mock(100, 30, 80)
        paystub.taxes = taxes
        balance_sheet.add_paystub(paystub)
        assert 100 == balance_sheet.assets.noncurrent.taxes.federal_withheld
        assert 30 == balance_sheet.assets.noncurrent.taxes.state_withheld
        assert 80 == sum(balance_sheet.paystub_taxable.values())

    def test_add_paystub_duplicate_paystub(self, balance_sheet):
        paystub = paystub_mock('1970-01-01', '1970-02-01')
        taxes = taxes_withholding_mock(100, 30, 80)
        paystub.taxes = taxes
        balance_sheet.add_paystub(paystub)
        balance_sheet.add_paystub(paystub)
        assert 100 == balance_sheet.assets.noncurrent.taxes.federal_withheld
        assert 30 == balance_sheet.assets.noncurrent.taxes.state_withheld
        assert 80 == sum(balance_sheet.paystub_taxable.values())

    def test_add_paystub_multiple_employers(self, balance_sheet):
        paystub1 = paystub_mock('1970-01-01', '1970-02-01', 'dr. evil')
        paystub2 = paystub_mock('1970-01-01', '1970-02-01', 'acme')
        taxes = taxes_withholding_mock(100, 30, 80)
        paystub1.taxes = taxes
        paystub2.taxes = taxes
        balance_sheet.add_paystub(paystub1)
        balance_sheet.add_paystub(paystub2)
        assert 200 == balance_sheet.assets.noncurrent.taxes.federal_withheld
        assert 60 == balance_sheet.assets.noncurrent.taxes.state_withheld
        assert 160 == sum(balance_sheet.paystub_taxable.values())

    def test_add_paystub_updated_paystub(self, balance_sheet):
        before_paystub = paystub_mock('1969-12-01', '1969-12-31')
        before_taxes = taxes_withholding_mock(100, 30, 80)
        before_paystub.taxes = before_taxes
        balance_sheet.add_paystub(before_paystub)

        after_paystub = paystub_mock('1971-07-31', '1971-08-01')
        after_taxes = taxes_withholding_mock(150, 40, 120)
        after_paystub.taxes = after_taxes
        balance_sheet.add_paystub(after_paystub)

        assert 150 == balance_sheet.assets.noncurrent.taxes.federal_withheld
        assert 40 == balance_sheet.assets.noncurrent.taxes.state_withheld
        assert 120 == sum(balance_sheet.paystub_taxable.values())

    def test_add_fixed_asset(self, balance_sheet):
        fixed_asset = property_mock(4)
        balance_sheet.add_fixed_asset(fixed_asset)
        assert 4 == balance_sheet.assets.noncurrent.fixed

    def test_add_cc_statement(self, balance_sheet, cc_statement_mock):
        cc_statement_mock.transactions = [
                transaction_mock('1970-01-05', 5),
                transaction_mock('1970-01-06', 6),
                transaction_mock('1970-01-07', 7),
        ]
        balance_sheet.add_cc_statement(cc_statement_mock)
        assert -18 == sum(balance_sheet.liabilities.current.credit.values())

    def test_add_cc_statement_duplicate_statement(self, balance_sheet, cc_statement_mock):
        cc_statement_mock.transactions = [
                transaction_mock('1970-01-05', 5),
                transaction_mock('1970-01-06', 6),
                transaction_mock('1970-01-07', 7),
        ]
        balance_sheet.add_cc_statement(cc_statement_mock)
        balance_sheet.add_cc_statement(cc_statement_mock)
        assert -18 == sum(balance_sheet.liabilities.current.credit.values())

    def test_add_cc_statement_multiple_creditors(self, balance_sheet, cc_statement_mock):
        cc_statement_mock.transactions = [
                transaction_mock('1970-01-05', 5),
                transaction_mock('1970-01-06', 6),
                transaction_mock('1970-01-07', 7),
        ]
        cc_statement1 = deepcopy(cc_statement_mock)
        type(cc_statement1).creditor = PropertyMock(return_value='dr. evil')
        balance_sheet.add_cc_statement(cc_statement1)

        cc_statement2 = deepcopy(cc_statement_mock)
        type(cc_statement2).creditor = PropertyMock(return_value='acme')
        balance_sheet.add_cc_statement(cc_statement2)

        assert -36 == sum(balance_sheet.liabilities.current.credit.values())

    def test_add_cc_statement_updated_statement(self, balance_sheet, cc_statement_mock):
        cc_statement_mock.transactions = [
                transaction_mock('1970-01-05', 5),
                transaction_mock('1970-01-06', 6),
                transaction_mock('1970-01-07', 7),
        ]
        balance_sheet.add_cc_statement(cc_statement_mock)

        cc_statement_mock.transactions = [
                transaction_mock('1970-01-05', 8),
                transaction_mock('1970-01-06', 9),
                transaction_mock('1970-01-07', 10),
        ]
        type(cc_statement_mock).end = PropertyMock(return_value=balance_sheet.now)
        balance_sheet.add_cc_statement(cc_statement_mock)
        assert -27 == sum(balance_sheet.liabilities.current.credit.values())

    def test_add_cc_statement_previous_statement(self, balance_sheet, cc_statement_mock):
        cc_statement_mock.transactions = [
                transaction_mock('1970-01-05', 5),
                transaction_mock('1970-01-06', 6),
                transaction_mock('1970-01-07', 7),
        ]
        type(cc_statement_mock).end = PropertyMock(return_value=balance_sheet.now)
        balance_sheet.add_cc_statement(cc_statement_mock)

        cc_statement_mock.transactions = [
                transaction_mock('1970-01-05', 8),
                transaction_mock('1970-01-06', 9),
                transaction_mock('1970-01-07', 10),
        ]
        previous = balance_sheet.now - relativedelta(days=+1)
        type(cc_statement_mock).end = PropertyMock(return_value=previous)
        balance_sheet.add_cc_statement(cc_statement_mock)
        assert -18 == sum(balance_sheet.liabilities.current.credit.values())

    def test_add_timed_liability(self, balance_sheet, timed_liability_mock):
        balance_sheet.add_timed_liability(timed_liability_mock)
        assert -timed_liability_mock.amount_remaining.return_value == balance_sheet.liabilities.current.leases

    def test_current_asset_total(self, balance_sheet):
        balance_sheet.assets.current.cash = 11
        balance_sheet.assets.current.brokerage = {'realest estate': 12, 'ponzi inc.': 13}
        assert 36 == balance_sheet.current_asset_total

    def test_noncurrent_asset_total(self, balance_sheet):
        balance_sheet.assets.noncurrent.brokerage = {'realest estate': 14, 'ponzi inc.': 15}
        real_tax_withheld = type(balance_sheet).tax_withheld
        type(balance_sheet).tax_withheld = PropertyMock(return_value=16)
        balance_sheet.assets.noncurrent.fixed = 17
        assert 62 == balance_sheet.noncurrent_asset_total
        type(balance_sheet).tax_withheld = real_tax_withheld

    def test_asset_total(self, balance_sheet):
        type(balance_sheet).current_asset_total = 18
        type(balance_sheet).noncurrent_asset_total = 19
        assert 37 == balance_sheet.asset_total

    def test_current_liability_total(self, balance_sheet):
        real_outstanding_credit = type(balance_sheet).outstanding_credit
        type(balance_sheet).outstanding_credit = PropertyMock(return_value=20)
        balance_sheet.liabilities.current.leases = 21
        assert 41 == balance_sheet.current_liability_total
        type(balance_sheet).outstanding_credit = real_outstanding_credit

    def test_noncurrent_liability_total(self, balance_sheet):
        real_tax_burden = type(balance_sheet).tax_burden
        type(balance_sheet).tax_burden = 22
        balance_sheet.liabilities.noncurrent.loans = 23
        assert 45 == balance_sheet.noncurrent_liability_total
        type(balance_sheet).tax_burden = real_tax_burden

    def test_ordinary_taxable_income(self, balance_sheet):
        balance_sheet.paystub_taxable = {'dr. evil': 24, 'acme': 25}
        balance_sheet.miscellaneous_income = 26
        assert 75 == balance_sheet.ordinary_taxable_income

    def test_tax_withheld(self, balance_sheet):
        balance_sheet.assets.noncurrent.taxes.federal_withheld = 27
        balance_sheet.assets.noncurrent.taxes.state_withheld = 28
        assert 55 == balance_sheet.tax_withheld

    def test_federal_tax_burden(self, balance_sheet):
        with patch('taxes.tax.SingleTax.calc_income_tax') as tax_mock:
            tax_mock.return_value = 29
            assert -29 == balance_sheet.federal_tax_burden
            assert -29 == balance_sheet.liabilities.noncurrent.taxes.federal_tax_ytd

    def test_state_tax_burden(self, balance_sheet):
        with patch('taxes.tax.SingleTax.calc_flat_tax') as tax_mock:
            tax_mock.return_value = 30
            assert -30 == balance_sheet.state_tax_burden
            assert -30 == balance_sheet.liabilities.noncurrent.taxes.state_tax_ytd

    def test_tax_burden(self, balance_sheet):
        real_federal_tax_burden = type(balance_sheet).federal_tax_burden
        real_state_tax_burden = type(balance_sheet).state_tax_burden
        type(balance_sheet).federal_tax_burden = PropertyMock(return_value=-31)
        type(balance_sheet).state_tax_burden = PropertyMock(return_value=-32)
        assert -63 == balance_sheet.tax_burden
        type(balance_sheet).federal_tax_burden = real_federal_tax_burden
        type(balance_sheet).state_tax_burden = real_state_tax_burden

    def test_liability_total(self, balance_sheet):
        real_current_liability_total = type(balance_sheet).current_liability_total
        real_noncurrent_liability_total = type(balance_sheet).noncurrent_liability_total
        type(balance_sheet).current_liability_total = PropertyMock(return_value=-33)
        type(balance_sheet).noncurrent_liability_total = PropertyMock(return_value=-34)
        assert -67 == balance_sheet.liability_total
        type(balance_sheet).current_liability_total = real_current_liability_total
        type(balance_sheet).noncurrent_liability_total = real_noncurrent_liability_total

    def test_equity(self, balance_sheet):
        real_asset_total = type(balance_sheet).asset_total
        real_liability_total = type(balance_sheet).liability_total
        type(balance_sheet).asset_total = PropertyMock(return_value=35)
        type(balance_sheet).liability_total = PropertyMock(return_value=-36)
        assert -1 == balance_sheet.equity
        type(balance_sheet).asset_total = real_asset_total
        type(balance_sheet).liability_total = real_liability_total

    def test_outstanding_credit(self, balance_sheet):
        balance_sheet.liabilities.current.credit = {'war': -37, 'famine': -38, 'pestilence': -39, 'death': -40}
        assert -154 == balance_sheet.outstanding_credit

