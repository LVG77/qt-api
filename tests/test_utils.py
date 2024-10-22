import time
import pytest
from unittest import mock
from qt_api.utils import generate_date_pairs, get_acct_activities
from qt_api.qt import check_for_expiration

@pytest.fixture
def temp_yaml_file(tmp_path):
    """Create a temporary YAML file for testing."""
    test_file = tmp_path / "test.yaml"
    test_file.write_text("test content")
    return test_file

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

def test_file_not_expired(temp_yaml_file):
    """Test when file modification time is recent (not expired)."""
    # File was just created, so it shouldn't be expired
    result = check_for_expiration(str(temp_yaml_file))
    assert result is False

def test_file_expired(temp_yaml_file):
    """Test when file modification time is old (expired)."""
    current_time = time.time()
    with mock.patch('time.time') as mock_time:
        file_time = current_time + 2000  # file modified 2000 seconds ago
        # Set current time to be 2000 seconds after file creation
        mock_time.return_value = file_time
        
        result = check_for_expiration(str(temp_yaml_file))
        assert result is True

def test_custom_threshold(temp_yaml_file):
    """Test with a custom time threshold."""
    # Set a very small threshold to force expiration
    result = check_for_expiration(str(temp_yaml_file), time_threshold=0)
    assert result is True
