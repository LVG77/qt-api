import pytest

@pytest.fixture
def sample_creds_data():
    return {'access_token': 'abc',
            'api_server': 'xxx',
            'expires_in': 1800,
            'refresh_token': '123abc',
            'token_type': 'some'}