import pytest

@pytest.fixture
def sample_creds_data():
    return {'access_token': 'abc',
            'api_server': 'xxx',
            'expires_in': 1800,
            'refresh_token': '123abc',
            'token_type': 'some'}

@pytest.fixture
def mock_access_code():
    return "mock_access_code"

@pytest.fixture
def expected_date_pairs():
    return [("2022-01-20", "2022-01-10"), ("2022-01-09", "2021-12-30")]

@pytest.fixture
def mock_generate_date_pairs(monkeypatch):
    # Mock the generate_date_pairs function
    def mock_generate_date_pairs(n_pairs):
        return [("2022-01-01", "2021-12-23"), ("2021-12-22", "2021-12-01")]
    monkeypatch.setattr("qt_api.utils.generate_date_pairs", mock_generate_date_pairs)