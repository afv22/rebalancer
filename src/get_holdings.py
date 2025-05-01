from src.api.plaid import client as plaid_client
from src.api.firestore import client as fs_client

from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.investments_holdings_get_response import InvestmentsHoldingsGetResponse
from plaid.model.security import Security as PlaidSecurity
from plaid.model.holding import Holding as PlaidHolding

from google.cloud.firestore_v1.base_query import FieldFilter


class Holding:
    def __init__(self, symbol: str, type: str, price: float = 0, value: float = 0):
        self.symbol = symbol
        self.type = type
        self.price = price
        self.value = value

    @staticmethod
    def from_security(security: PlaidSecurity):
        return Holding(
            security.ticker_symbol or security.name,
            security.type,
        )

    def add_holding(self, holding: PlaidHolding) -> None:
        self.value += holding.institution_value
        if self.price == 0:
            self.price = holding.institution_price


def get_holdings(user_id: int) -> list[Holding]:
    items = fs_client.Items.where(filter=FieldFilter("user_id", "==", user_id)).get()
    holdings = []
    for item in items:
        access_token = item.get("access_token")
        request = InvestmentsHoldingsGetRequest(access_token=access_token)
        response: InvestmentsHoldingsGetResponse = (
            plaid_client.investments_holdings_get(request)
        )
        item_holdings: dict[str, Holding] = {}
        plaid_securities: list[PlaidSecurity] = response.securities
        for security in plaid_securities:
            item_holdings[security.security_id] = Holding.from_security(security)

        plaid_holdings: list[PlaidHolding] = response["holdings"]
        for holding in plaid_holdings:
            item_holdings[holding.security_id].add_holding(holding)

        holdings += list(item_holdings.values())
    return holdings
