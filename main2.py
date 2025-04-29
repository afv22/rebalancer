#!/usr/bin/env python3
"""
Plaid Portfolio Holdings Fetcher
--------------------------------
A command-line tool to fetch current portfolio holdings using Plaid's API.
"""

import os
import json
import argparse
import plaid
from plaid.api import plaid_api
from plaid.apis import PlaidApi
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)
from plaid.model.item_public_token_create_request import ItemPublicTokenCreateRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from dotenv import load_dotenv


def setup_plaid_client():
    """Initialize and return a Plaid client using environment variables."""
    load_dotenv()  # Load environment variables from .env file if present

    # Get Plaid API credentials from environment variables
    client_id = os.getenv("PLAID_CLIENT_ID")
    secret = os.getenv("PLAID_SECRET")
    environment = os.getenv("PLAID_ENVIRONMENT", "sandbox")  # Default to sandbox

    if not client_id or not secret:
        raise ValueError(
            "Missing Plaid API credentials. Set PLAID_CLIENT_ID and PLAID_SECRET environment variables."
        )

    # Configure Plaid environment
    host = plaid.Environment.Sandbox
    if environment.lower() == "development":
        host = plaid.Environment.Development
    elif environment.lower() == "production":
        host = plaid.Environment.Production

    # Configure and return API client
    configuration = plaid.Configuration(
        host=host,
        api_key={
            "clientId": client_id,
            "secret": secret,
        },
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


def create_link_token(client: PlaidApi, user_id: str):
    """Create a Link token for initializing Plaid Link."""
    try:
        request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=user_id),
            client_name="Portfolio Holdings App",
            products=[Products("investments")],
            country_codes=[CountryCode("US")],
            language="en",
        )
        response = client.link_token_create(request)
        return response["link_token"]
    except plaid.ApiException as e:
        print(f"Error creating link token: {e}")
        return None

def exchange_link_token(client: PlaidApi, link_token: str):
    try:
        request = ItemPublicTokenCreateRequest()
    except plaid.ApiException as e:
        print(f"Error exchanging link token: {e}")
        return None


def exchange_public_token(client: PlaidApi, public_token: str):
    """Exchange a public token for an access token."""
    try:
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(request)
        return response["access_token"], response["item_id"]
    except plaid.ApiException as e:
        print(f"Error exchanging public token: {e}")
        return None, None


def get_holdings(client: PlaidApi, access_token: str):
    """Fetch investment holdings for the given access token."""
    try:
        request = InvestmentsHoldingsGetRequest(access_token=access_token)
        response = client.investments_holdings_get(request)
        return response
    except plaid.ApiException as e:
        print(f"Error fetching holdings: {e}")
        return None


def display_holdings(holdings_response):
    """Format and display holdings information."""
    if not holdings_response:
        print("No holdings data available.")
        return

    print("\n===== ACCOUNTS =====")
    for account in holdings_response["accounts"]:
        print(f"Account: {account['name']} (${account['balances']['current']:.2f})")
        print(f"  Type: {account['type']} - {account['subtype']}")
        print(f"  Mask: {account.get('mask', 'N/A')}")
        print()

    print("\n===== SECURITIES =====")
    securities_map = {
        security["security_id"]: security
        for security in holdings_response["securities"]
    }

    print("\n===== HOLDINGS =====")
    for holding in holdings_response["holdings"]:
        security = securities_map.get(holding["security_id"], {})
        print(
            f"Security: {security.get('name', 'Unknown')} ({security.get('ticker_symbol', 'N/A')})"
        )
        print(f"  Institution value: ${holding['institution_value']:.2f}")
        print(f"  Quantity: {holding['quantity']:.4f} shares")
        print(f"  Cost basis: ${holding.get('cost_basis', 0):.2f}")
        print()


def export_to_json(holdings_response, filename):
    """Export holdings data to a JSON file."""
    with open(filename, "w") as f:
        json.dump(holdings_response.to_dict(), f, indent=2)
    print(f"Holdings exported to {filename}")


def main():
    """Main function to handle command line arguments and run the program."""
    parser = argparse.ArgumentParser(
        description="Fetch portfolio holdings using Plaid API"
    )
    parser.add_argument("--export", help="Export holdings to JSON file")

    args = parser.parse_args()

    try:
        client = setup_plaid_client()

        link_token = create_link_token(client, "user1")
        print("Public Token: {}".format(link_token))

        access_token, item_id = exchange_public_token(client, public_token)
        print("Access Token: {}".format(access_token))

        print(f"Access token: {access_token}")
        print(f"Item ID: {item_id}")
        print("Use this access token to fetch account data.")

        # Save to .env file if available
        try:
            with open(".env", "a") as env_file:
                env_file.write(f"\nPLAID_ACCESS_TOKEN={access_token}")
                env_file.write(f"\nPLAID_ITEM_ID={item_id}")
            print("Access token and item ID saved to .env file")
        except Exception as e:
            print(f"Could not save to .env file: {e}")

        holdings = get_holdings(client, access_token)
        if holdings:
            display_holdings(holdings)

            if args.export:
                export_to_json(holdings, args.export)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
