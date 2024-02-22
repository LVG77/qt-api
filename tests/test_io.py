import pytest
import yaml
from qt_api.qt import load_creds, save_creds, QTTokenFile
from pydantic import ValidationError


def test_save_creds(tmp_path, sample_creds_data, monkeypatch):
    # Override user_dir to return the temporary directory path
    monkeypatch.setattr("cisco_llm.cli.user_dir", lambda: tmp_path)

    creds = QTTokenFile(**sample_creds_data)
    save_creds(creds)

    expected_path = tmp_path / "creds.yaml"
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
