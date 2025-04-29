import dotenv

from src.get_rebalance_amounts import get_rebalance_amounts
from src.send_email import send_email
from src.schwab_client import SchwabClient


def main():
    c = SchwabClient.create()

    # Fetch holdings
    accounts = c.get_accounts(fields=[SchwabClient.Account.Fields.POSITIONS])
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
        print("Everything looks good.")
        return

    # Alert me or automatically rebalance
    print("Time to rebalance!")
    # send_email()


if __name__ == "__main__":
    dotenv.load_dotenv()
    main()
