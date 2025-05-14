from src.api.plaid import PlaidClientWrapper
from src.api.firestore import FirestoreClient
from src.classes.holding import Holding, HoldingType

from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.investments_holdings_get_response import InvestmentsHoldingsGetResponse
from plaid.model.security import Security as PlaidSecurity
from plaid.model.holding import Holding as PlaidHolding

from google.cloud.firestore_v1.base_query import FieldFilter


def get_holdings(user_id: int) -> list[Holding]:
    item_query = FirestoreClient.query_items()
    items = item_query.where(filter=FieldFilter("user_id", "==", user_id)).get()
    plaid_client = PlaidClientWrapper.get_client()
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
            item_holdings[security.security_id] = Holding(
                security.ticker_symbol or security.name,
                HoldingType.OTHER,
            )

        plaid_holdings: list[PlaidHolding] = response["holdings"]
        for holding in plaid_holdings:
            existing_holding = item_holdings[holding.security_id]
            existing_holding.value += holding.institution_value
            if existing_holding.price == 0:
                existing_holding.price = holding.institution_price

        holdings += list(item_holdings.values())
    return holdings
