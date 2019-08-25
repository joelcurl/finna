from paystubs.wages import AcmePaystub, Earnings, Deductions, Taxes, PayPeriod
from unittest.mock import Mock, PropertyMock
from pytest import fixture
from datetime import datetime

def earnings_mock(wages, bonuses):
    mock = Mock(spec=Earnings)

    wages_mock = PropertyMock(return_value=wages)
    type(mock).wages = wages_mock
    mock.wages_mock = wages_mock

    bonuses_mock = PropertyMock(return_value=bonuses)
    type(mock).bonuses = bonuses_mock
    mock.bonuses_mock = bonuses_mock

    return mock

def deductions_mock(total):
    mock = Mock(spec=Deductions)

    total_mock = PropertyMock(return_value=total)
    type(mock).total = total_mock
    mock.total_mock = total_mock

    return mock

def taxes_mock(total):
    mock = Mock(spec=Taxes)

    total_mock = PropertyMock(return_value=total)
    type(mock).total = total_mock
    mock.total_mock = total_mock

    return mock

def paystub_mock(start_date, end_date):
    mock = Mock(spec=AcmePaystub)
    mock.pay_period = PayPeriod(datetime.fromisoformat(start_date).date(), datetime.fromisoformat(end_date).date())
    type(mock).current = PropertyMock(return_value=mock)
    return mock

