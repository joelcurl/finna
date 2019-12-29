from paystubs.wages import AcmePaystub
from paystubs.reader import AcmePaystubReader
from csv import DictReader
import os
from datetime import date
from decimal import Decimal
from glob import glob
from pytest import fixture, mark

def pytest_generate_tests(metafunc):
    base_dir = os.path.join(os.path.dirname(__file__), 'input')
    paystubs = glob(os.path.join(base_dir, '*.pdf'))
    paystubs.sort()
    del paystubs[9:] # todo undo
    expected_vals_fpath = os.path.join(base_dir, 'expected_vals.csv')
    metafunc.parametrize('paystub_fpath,expected_vals_fpath,expected_vals_row',
            [(paystub_fpath, expected_vals_fpath, i) for i, paystub_fpath in enumerate(paystubs)]
        )

class TestAcmePaystub:
    @staticmethod
    def translate_field(field):
        return field.strip(' ').translate(str.maketrans(' ', '_'))

    def assert_paystub(self, expected_vals, paystub):
        assert date.fromisoformat(expected_vals['Pay_Period_Start']) == paystub.pay_period.start
        assert date.fromisoformat(expected_vals['Pay_Period_End']) == paystub.pay_period.end
        self.assert_current(expected_vals, paystub)
        self.assert_ytd(expected_vals, paystub)

    def assert_current(self, expected_vals, paystub):
        assert Decimal(expected_vals['Current_Wages']) == paystub.current.earnings.wages
        assert Decimal(expected_vals['Current_Bonuses']) == paystub.current.earnings.bonuses

        assert Decimal(expected_vals['Current_Deductions']) == paystub.current.deductions.total
        assert Decimal(expected_vals['Current_Deductions_Pretax']) == paystub.current.deductions.pretax.total
        assert Decimal(expected_vals['Current_Deductions_Posttax']) == paystub.current.deductions.posttax.total

        assert Decimal(expected_vals['Current_Taxes']) == paystub.current.taxes.total
        assert Decimal(expected_vals['Current_Taxable_Wages']) == paystub.current.taxes.taxable_wages
        assert Decimal(expected_vals['Current_Federal_Tax_Withheld']) == paystub.current.taxes.federal_withheld
        assert Decimal(expected_vals['Current_State_Tax_Withheld']) == paystub.current.taxes.state_withheld

    def assert_ytd(self, expected_vals, paystub):
        assert Decimal(expected_vals['YTD_Wages']) == paystub.ytd.earnings.wages
        assert Decimal(expected_vals['YTD_Bonuses']) == paystub.ytd.earnings.bonuses

        assert Decimal(expected_vals['YTD_Deductions']) == paystub.ytd.deductions.total
        assert Decimal(expected_vals['YTD_Deductions_Pretax']) == paystub.ytd.deductions.pretax.total
        assert Decimal(expected_vals['YTD_Deductions_Posttax']) == paystub.ytd.deductions.posttax.total

        assert Decimal(expected_vals['YTD_Taxes']) == paystub.ytd.taxes.total
        assert Decimal(expected_vals['YTD_Taxable_Wages']) == paystub.ytd.taxes.taxable_wages
        assert Decimal(expected_vals['YTD_Federal_Tax_Withheld']) == paystub.ytd.taxes.federal_withheld
        assert Decimal(expected_vals['YTD_State_Tax_Withheld']) == paystub.ytd.taxes.state_withheld

    def test_paystub(self, paystub_fpath, expected_vals_fpath, expected_vals_row):
        reader = None
        with open(paystub_fpath, 'rb') as f:
            reader = AcmePaystubReader(f)
        paystub = AcmePaystub(reader.text)

        csv_str = None
        with open(expected_vals_fpath, 'r') as f:
            csv_str = f.read()
        csv_iter = csv_str.split('\n')
        csv_reader = DictReader(csv_iter)
        expected_vals = [row for row in csv_reader][expected_vals_row]
        self.assert_paystub(expected_vals, paystub)



