from cc.elan_statement import ElanStatementReader
from cc.visa import VisaTransaction
import os
from decimal import Decimal
from pytest import fixture

@fixture
def elan_statement_reader():
    with open(os.path.join(os.path.dirname(__file__), 'input/download.csv')) as csv_f:
        return ElanStatementReader(csv_f.read())

class TestElanStatementReader:
    def test_elan_transactions(self, elan_statement_reader):
        assert Decimal('-10670.16') == sum([t.amount for t in elan_statement_reader.elan_transactions])

    def test_elan_payments(self, elan_statement_reader):
        assert Decimal('10607.28') == sum([p.amount for p in elan_statement_reader.elan_payments])

    def test_visa_transactions(self, elan_statement_reader):
        actual = elan_statement_reader.visa_transactions
        assert Decimal('-10670.16') == sum([t.amount for t in actual])
        for t in actual:
            assert VisaTransaction == type(t)

    def test_payments(self, elan_statement_reader):
        actual = elan_statement_reader.payments
        assert Decimal('10607.28') == sum([p.amount for p in actual])
        for p in actual:
            assert VisaTransaction == type(p)

