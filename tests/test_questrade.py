import pytest
from unittest import mock
from qt_api.qt import Questrade, TOKEN_URL, QTTokenFile, save_creds, validate_dict


@mock.patch('httpx.get')
@mock.patch('qt_api.qt.save_creds')
@mock.patch('qt_api.qt.validate_dict')
def test_get_access_token(mock_validate_dict, mock_save_creds, mock_get, mock_access_code, sample_creds_data):
    # Arrange
    mock_response_obj = mock.MagicMock()
    mock_response_obj.json.return_value = sample_creds_data
    mock_response_obj.raise_for_status = mock.MagicMock()
    mock_get.return_value = mock_response_obj
    questrade = Questrade(access_code=mock_access_code)
    # Assert
    mock_get.assert_called_once_with(TOKEN_URL + mock_access_code)
    mock_validate_dict.assert_called_once_with(sample_creds_data)
    mock_save_creds.assert_called_once_with(QTTokenFile(**sample_creds_data), None)
    assert questrade.headers == {"Authorization": "some abc"}

@mock.patch('qt_api.qt.load_creds')
def test_create_qt(mock_load_creds, sample_creds_data):
    mock_load_creds.return_value = QTTokenFile(**sample_creds_data)
    questrade = Questrade(acct_flag="xx")
    mock_load_creds.assert_called_once_with("xx")
    assert questrade.headers == {"Authorization": "some abc"}

@mock.patch('qt_api.qt.Questrade._get_access_token')
@mock.patch('httpx.Client')
def test_send_request(mock_client, mock_get_access_token, sample_creds_data):
    mock_get_access_token.return_value = QTTokenFile(**sample_creds_data)
    qt = Questrade(access_code="xxxv1")
    qt.access_token = QTTokenFile(**sample_creds_data)
    assert mock_get_access_token.called_once

    mock_client.get.raise_for_status.return_value = None
    mock_client.get.return_value.json.return_value = {"key1": "value1", "key2": "value2"}
    qt.client = mock_client
    req = qt._send_request("test", {"some": "params"})
    assert mock_client.get.call_args[0][0] == "xxxv1/test"
    assert mock_client.get.call_args[1]["params"] == {"some": "params"}
    assert req == {"key1": "value1", "key2": "value2"}
    
@mock.patch('qt_api.qt.Questrade._get_access_token')
@mock.patch('httpx.get')
@mock.patch('qt_api.qt.save_creds')
@mock.patch('qt_api.qt.validate_dict')
def test_refresh_access_token(mock_validate_dict, mock_save_creds, mock_get, mock_get_access_token, sample_creds_data):
    qt = Questrade(access_code="xxxv1", acct_flag="xx")
    qt.access_token = QTTokenFile(**sample_creds_data)
    mock_get.raise_for_status.return_value = None
    mock_get.return_value.json.return_value = sample_creds_data
    req = qt.refresh_access_token()
    assert mock_get.call_args[0][0] == TOKEN_URL + qt.access_token.refresh_token
    mock_validate_dict.assert_called_once_with(sample_creds_data)
    mock_save_creds.assert_called_once_with(QTTokenFile(**sample_creds_data), "xx")