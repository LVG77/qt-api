import pytest
from unittest import mock
from qt_api.utils import generate_date_pairs, get_acct_activities

def test_generate_date_pairs(expected_date_pairs):
    n_pairs = 2
    time_delta = 10
    start_date = "2022-01-20"

    result = generate_date_pairs(n_pairs, time_delta, start_date)
    assert result == expected_date_pairs

@mock.patch('qt_api.qt.Questrade')
def test_get_acct_activities(mock_qt, mock_generate_date_pairs):
    acct_no = 123
    n = 2
    expected_output = [{"activity": "mock_activity"}, {"activity": "mock_activity"}]

    mock_qt.get_activities.return_value = [{"activity": "mock_activity"}]
    result = get_acct_activities(mock_qt, acct_no, n)
    assert mock_qt.get_activities.call_count == n
    assert result == expected_output