import os
import dotenv
from schwab import auth

from src.get_rebalance_amounts import get_rebalance_amounts
from src.send_email import send_email


def main():
    # Fetch holdings
    api_key = os.getenv("SCHWAB_API_KEY")
    app_secret = os.getenv("SCHWAB_SECRET")

    if not api_key or not app_secret:
        raise ValueError("Schwab API details not found")

    c = auth.easy_client(
        api_key=api_key,
        app_secret=app_secret,
        callback_url="https://127.0.0.1:8182",
        token_path="/tmp/token.json",
    )

    accounts = c.get_accounts(fields=[c.Account.Fields.POSITIONS])
    holdings = []
    for account in accounts.json():
        if "positions" not in account["securitiesAccount"]:
            continue
        for position in account["securitiesAccount"]["positions"]:
            holding = {
                "asset": position["instrument"]["symbol"],
                "value": position["marketValue"],
            }
            holdings.append(holding)

    # Process allocations
    target_allocations = {"VOO": 0.55, "VXUS": 0.30, "GLDM": 0.05, "VGIT": 0.10}
    rebalance_amounts = get_rebalance_amounts(holdings, target_allocations)

    # Check if any asset is outside the allowed window
    for asset in rebalance_amounts:
        if asset["absolute_difference"] >= 0.05:
            break
        if asset["relative_difference"] >= 0.25:
            break
    else:
        return

    # Alert me or automatically rebalance
    print("Time to rebalance!")
    # send_email()


if __name__ == "__main__":
    dotenv.load_dotenv()
    main()
