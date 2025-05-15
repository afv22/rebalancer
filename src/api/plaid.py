import os

import plaid
from plaid.api import plaid_api

from src.api.secret import GoogleSecretWrapper
from src.utils import is_prod

CLIENT_ID = "61e8a5cf7b79c5001aa87be0"


class PlaidClientWrapper:
    _instance = None

    @classmethod
    def _initialize(cls) -> None:
        if cls._instance is None:
            if is_prod():
                plaid_secret = GoogleSecretWrapper.get_secret("PlaidSecret")
                cls.host = plaid.Environment.Production
            else:
                plaid_secret = os.getenv("PLAID_SECRET")
                cls.host = plaid.Environment.Sandbox

            configuration = plaid.Configuration(
                host=cls.host,
                api_key={
                    "clientId": CLIENT_ID,
                    "secret": plaid_secret,
                    "plaidVersion": "2020-09-14",
                },
            )

            api_client = plaid.ApiClient(configuration)
            cls._instance = plaid_api.PlaidApi(api_client)

    @classmethod
    def get_client(cls) -> plaid_api.PlaidApi:
        cls._initialize()
        return cls._instance

    @classmethod
    def get_host(cls) -> plaid.Environment:
        cls._initialize()
        return cls.host
