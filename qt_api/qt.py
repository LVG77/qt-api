from typing import Union
from pathlib import Path
import yaml
import json
import httpx
import pydantic
from pydantic import BaseModel

TOKEN_URL = "https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token="

class QTTokenFile(BaseModel):
    access_token: str
    api_server: str
    expires_in: int
    refresh_token: str
    token_type: str

def render_errors(errors):
    output = []
    for error in errors:
        output.append(", ".join(error["loc"]))
        output.append("  " + error["msg"])
    return "\n".join(output)

def user_dir():
    path = Path().home() / ".qt_api"
    path.mkdir(exist_ok=True, parents=True)
    return path


def save_creds(creds: QTTokenFile, acct_flag:str = None):
    creds_dict = creds.model_dump()
    creds_name = f"creds_{acct_flag}.yaml" if acct_flag else "creds.yaml"
    path = user_dir() / creds_name
    path.write_text(yaml.dump(creds_dict, indent=4))


def load_creds(acct_flag:str = None)->QTTokenFile:
    if acct_flag:
        path = user_dir() / f"creds_{acct_flag}.yaml"
    else:
        path = user_dir() / "creds.yaml"
    if not path.exists():
        raise FileNotFoundError("QT credentials file not found!\nProdive new access code!")
    creds = yaml.safe_load(path.read_text())
    try:
        return QTTokenFile(**creds)
    except pydantic.ValidationError as ex:
        msg = "A validation error occurred:\n"
        msg += render_errors(ex.errors())
        raise ValueError(msg)


def validate_dict(input_dict):
    try:
        QTTokenFile(**input_dict)
    except pydantic.ValidationError as ex:
        msg = "A validation error occurred:\n"
        msg += render_errors(ex.errors())
        raise ValueError(msg)


class Questrade:
    """A class for interacting with the Questrade API.

    This class provides methods for getting account information, positions,
    and executions, as well as retrieving quotes for tickers. The class can
    also be used to refresh the access token if it has expired.

    To use this class, either an access code or an access token must be provided.
    If an access code is provided, the class will use it to generate and save
    an access token to a file in the user's home directory. If an access token
    is provided, it will be used instead of generating one from an access code.

    Args:
        access_code (str): The access code for generating an access token.
            If not provided, the class will try to load an access token from
            a file in the user's home directory.
        acct_flag (str): A unique identifier for the account. This will be used
            when saving the access token to a file. If not provided, the
            access token will be saved to a file named "creds.yaml".
    """
    def __init__(self, access_code:str = None, acct_flag:str = None):
        self.access_code = access_code
        self.acct_flag = acct_flag
        self.headers = None
        self.client = httpx.Client()
        if access_code is None:
            self.access_token = load_creds(self.acct_flag)
            self.headers = {"Authorization": self.access_token.token_type 
                            + " " + self.access_token.access_token}
        else:
            self._get_access_token()

    def _get_access_token(self)->None:
        """Get access token
        This internal method gets the access token from the access code and saves it in
        creds.yaml.
        """
        url = TOKEN_URL + self.access_code
        data = httpx.get(url)
        data.raise_for_status()
        r = data.json()
        # validate reponse
        validate_dict(r)
        self.access_token = QTTokenFile(**r)
        self.headers = {"Authorization": self.access_token.token_type 
                        + " " + self.access_token.access_token}
        # save access token to file
        save_creds(self.access_token, self.acct_flag)
    
    def refresh_access_token(self)->None:
        "Refresh access token before it has expired"
        old_access_token = self.access_token
        
        url = TOKEN_URL + old_access_token.refresh_token
        data = httpx.get(url)
        data.raise_for_status()
        r = data.json()
        # validate reponse
        validate_dict(r)
        self.access_token = QTTokenFile(**r)
        self.headers = {"Authorization": self.access_token.token_type 
                        + " " + self.access_token.access_token}
        # save access token to file
        save_creds(self.access_token, self.acct_flag)
        print("Token refreshed successfully")


    def _send_request(self, endpoint:str, params: dict[str, any] = None)->dict[str,any]:
        "Send API requests"
        if self.access_token is not None:
            url = self.access_token.api_server + "v1/" + endpoint
        else:
            raise Exception("Access token not set ...")
        r = self.client.get(url, headers=self.headers, params=params)
        r.raise_for_status()
        return r.json()

    def get_symbols_quote(self, tickers:Union[str,list[str]])->list[dict]:
        "Get quote of single ticker or list of tickers"
        if isinstance(tickers, str):
            tickers = [tickers]
        params = {"names": ",".join(tickers)}
        r = self._send_request("symbols", params=params)
        return r["symbols"]

    def get_account(self)->list[dict]:
        "Get a list of all accounts. Each account record is a dict"
        r = self._send_request("accounts")
        return r["accounts"]

    def get_activities(self, account:int, from_dt:str, to_dt:str)->list[dict]:
        "Get account activities for up to 30 days at a time"
        params = {"startTime": from_dt + "T00:00:00-05:00",
                  "endTime": to_dt + "T00:00:00-05:00"}
        r = self._send_request(f"accounts/{account}/activities", params=params)
        return r["activities"]

    def get_positions(self, account:int)->list[dict]:
        "Get all positions for an account"
        r = self._send_request(f"accounts/{account}/positions")
        return r["positions"]

    def get_executions(self, account:int, from_dt:str = None, to_dt:str = None)->list[dict]:
        """Get executions for an account. If no start and end times are provided,
        the results will be for today only."""
        if all([from_dt, to_dt]):
            params = {"startTime": from_dt + "T00:00:00-05:00",
                      "endTime": to_dt + "T00:00:00-05:00"}
            r = self._send_request(f"accounts/{account}/executions", params=params)
        else:
            r = self._send_request(f"accounts/{account}/executions")
        return r["executions"]

    def get_balances(self, account:int)->dict[str, any]:
        """Get all balances for an account. The results are returned as a dict with
        the following keys: perCurrencyBalances, combinedBalances, sodPerCurrencyBalances,
        and sodCombinedBalances."""
        return self._send_request(f"accounts/{account}/balances")