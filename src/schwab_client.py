import os
from schwab import auth
from schwab.client import Client


class SchwabClient(Client):
    @staticmethod
    def create() -> "SchwabClient":
        api_key = os.getenv("SCHWAB_API_KEY")
        app_secret = os.getenv("SCHWAB_SECRET")

        if not api_key or not app_secret:
            raise ValueError("Schwab API details not found")

        return auth.easy_client(
            api_key=api_key,
            app_secret=app_secret,
            callback_url="https://127.0.0.1:8182",
            token_path="/tmp/token.json",
            interactive=False,
        )
