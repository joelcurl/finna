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
def cc_statement_mock():
    mock = Mock(spec=CcStatement)
    return mock

