from unittest.mock import Mock

def property_mock(value):
    mock = Mock()
    mock.mark_to_market.return_value = value
    return mock
