from liabilities.timed_liability import TimedLiability
from unittest.mock import Mock, PropertyMock
from pytest import fixture

@fixture
def timed_liability_mock():
    mock = Mock(spec=TimedLiability)

    monthly_amount = PropertyMock(return_value=1)
    type(mock).monthly_amount = monthly_amount
    mock.monthly_amount_mock = monthly_amount

    mock.amount_from.return_value = 1000

    return mock

