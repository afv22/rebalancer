from src.api.email import send_email
from src.api.plaid import host

from src.get_holdings import get_holdings
from src.get_rebalance_amounts import get_rebalance_amounts
from src.generate_email import generate_email

from plaid import Environment


def main():
    is_prod = host == Environment.Production
    holdings = get_holdings(2 if is_prod else 1)
    rebalance_amounts = get_rebalance_amounts(holdings, is_prod)

    # Check if any asset is outside the allowed window
    for _, asset in rebalance_amounts.iterrows():
        if abs(asset["absolute_difference"]) >= 0.05:
            break
        if abs(asset["relative_difference"]) >= 0.25:
            break
    else:
        print("Everything looks good.")
        return

    send_email("Time to rebalance!", generate_email(rebalance_amounts))


if __name__ == "__main__":
    main()
