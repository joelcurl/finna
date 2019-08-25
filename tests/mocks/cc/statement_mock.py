from cc.statement import CcStatement
from cc.visa import VisaTransaction
from unittest.mock import Mock, PropertyMock
from pytest import fixture
from datetime import datetime

def transaction_mock(date, amount, category = None):
    date = datetime.fromisoformat(date).date()
    mock = Mock(spec=VisaTransaction)
    amount = -amount

    date_mock = PropertyMock(return_value=date)
    type(mock).date = date_mock
    mock.date_mock = date_mock

    id_mock = PropertyMock(return_value=f'{date} ${amount}')
    type(mock).id = id_mock
    mock.id_mock = id_mock

    amount_mock = PropertyMock(return_value=amount)
    type(mock).amount = amount_mock
    mock.amount_mock = amount_mock

    mock.in_category.side_effect = lambda test_category: test_category == category
    return mock

@fixture
def cc_statement_mock(creditor = 'Acme', end = '1970-02-01'):
    mock = Mock(spec=CcStatement)

    creditor_mock = PropertyMock(return_value=creditor)
    type(mock).creditor = creditor_mock
    mock.creditor_mock = creditor_mock

    total_mock = PropertyMock(side_effect=lambda: sum([transaction.amount for transaction in mock.transactions]))
    type(mock).total = total_mock
    mock.total_mock = total_mock

    end_mock = PropertyMock(return_value=datetime.fromisoformat(end).date())
    type(mock).end = end_mock
    mock.end_mock = end_mock

    return mock

