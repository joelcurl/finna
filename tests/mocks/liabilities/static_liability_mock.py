from liabilities.static_liability import StaticLiability
from unittest.mock import Mock, PropertyMock
from pytest import fixture

@fixture
def static_liability_mock():
    mock = Mock(spec=StaticLiability)
    mock.amount_remaining.return_value = 250
    return mock

