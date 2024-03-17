# qt-api

[![PyPI](https://img.shields.io/pypi/v/qt-api.svg)](https://pypi.org/project/qt-api/)
[![Tests](https://github.com/LVG77/qt-api/actions/workflows/test.yml/badge.svg)](https://github.com/LVG77/qt-api/actions/workflows/test.yml)
[![Changelog](https://img.shields.io/github/v/release/LVG77/qt-api?include_prereleases&label=changelog)](https://github.com/LVG77/qt-api/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/LVG77/qt-api/blob/main/LICENSE)

Python wrapper for Questrade API

## Installation

Install this library using `pip`:
```bash
# not released yet
pip install qt-api
```
## Usage

Use access code from Questrade API.
Also optionally you can use acct_flag to create account-specific credentials file.

```python
from qt_api.qt import Questrade

qt = Questrade(access_code="xxx", acct_flag="zz")
```

Optionally, you can refresh access token like so:
```python
qt.refresh_access_token()
```

Then you can use any of the provided methods. For example to get a list of all accounts:
```python
accounts = qt.get_account()
```
... or to get a quote for a list of symbols:
```python
quotes = qt.get_symbol_quote(symbols=["AAPL", "MSFT"])
```

## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:
```bash
cd qt-api
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
pytest
```
