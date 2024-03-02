import pytest
import yaml
from qt_api.qt import load_creds, save_creds, QTTokenFile, validate_dict
from pydantic import ValidationError


def test_save_creds(tmp_path, sample_creds_data, monkeypatch):
    # Override user_dir to return the temporary directory path
    monkeypatch.setattr("qt_api.qt.user_dir", lambda: tmp_path)

    creds = QTTokenFile(**sample_creds_data)
    save_creds(creds)

    expected_path = tmp_path / "creds.yaml"
    assert expected_path.exists()

    # Read the saved YAML file and check its content
    saved_data = yaml.safe_load(expected_path.read_text())
    assert saved_data == sample_creds_data

def test_save_creds_acct(tmp_path, sample_creds_data, monkeypatch):
    # Override user_dir to return the temporary directory path
    monkeypatch.setattr("qt_api.qt.user_dir", lambda: tmp_path)

    creds = QTTokenFile(**sample_creds_data)
    save_creds(creds, acct_flag="some_flag")

    expected_path = tmp_path / "creds_some_flag.yaml"
    assert expected_path.exists()

    # Read the saved YAML file and check its content
    saved_data = yaml.safe_load(expected_path.read_text())
    assert saved_data == sample_creds_data

def test_load_creds(tmp_path, sample_creds_data, monkeypatch):
    # Override user_dir to return the specific directory path
    monkeypatch.setattr("qt_api.qt.user_dir", lambda: tmp_path)

    # Save sample credentials to a YAML file
    creds = QTTokenFile(**sample_creds_data)
    save_creds(creds)

    # Load the credentials and check if they match the saved data
    loaded_creds = load_creds()
    assert loaded_creds == creds

def test_load_creds_acct(tmp_path, sample_creds_data, monkeypatch):
    # Override user_dir to return the specific directory path
    monkeypatch.setattr("qt_api.qt.user_dir", lambda: tmp_path)

    # Save sample credentials to a YAML file
    creds = QTTokenFile(**sample_creds_data)
    save_creds(creds, acct_flag="some_flag")

    # Load the credentials and check if they match the saved data
    loaded_creds = load_creds(acct_flag="some_flag")
    assert loaded_creds == creds

def test_validate_dict_valid_input(sample_creds_data):
    try:
        validate_dict(sample_creds_data)
    except ValueError:
        pytest.fail("Unexpected ValueError raised for valid input")

def test_validate_dict_invalid_input():
    invalid_input = {
        'token': 123,
        'expiry': 'invalid_date',
        'refresh_token': None
    }
    with pytest.raises(ValueError) as ex:
        validate_dict(invalid_input)
    assert "A validation error occurred:" in str(ex.value)

def test_validate_dict_missing_fields():
    incomplete_input = {
        'token': 'some_token',
        'expiry': '2021-12-31T23:59:59'
        # 'refresh_token' is missing
    }
    with pytest.raises(ValueError) as ex:
        validate_dict(incomplete_input)
    assert "A validation error occurred:" in str(ex.value)

def test_validate_dict_no_extra_fields():
    extra_fields_input = {
        'access_token': 'some_token',
        'api_server': 'server_addrs',
        'expires_in': 1234,
        'refresh_token': 'some_refresh_token',
        'token_type': 'bearer',
        'extra_field': 'not_needed'
    }
    toks = QTTokenFile(**extra_fields_input)
    with pytest.raises(AttributeError) as att_err:
        toks.extra_field
    assert "has no attribute 'extra_field'" in str(att_err.value)
