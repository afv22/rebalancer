from flask import Blueprint, current_app

from app.api.email import EmailClientWrapper
from app.generate_email import generate_email
from app.get_holdings import get_holdings
from app.get_rebalance_amounts import get_rebalance_amounts
from app.utils import error_handler

portfolio_bp = Blueprint("portfolio", __name__)


@portfolio_bp.route("/holdings")
@error_handler
def holdings():
    user_id = current_app.config["USER_ID"]
    return list(map(lambda h: h.symbol, get_holdings(user_id)))


@portfolio_bp.route("/rebalance_amounts")
@error_handler
def rebalance_amounts():
    user_id = current_app.config["USER_ID"]
    holdings = get_holdings(user_id)
    return get_rebalance_amounts(holdings).to_json()


@portfolio_bp.route("/check_allocation")
@error_handler
def check_allocation():
    user_id = current_app.config["USER_ID"]
    holdings = get_holdings(user_id)
    rebalance_amounts = get_rebalance_amounts(holdings)

    need_rebalance = False
    for _, asset in rebalance_amounts.iterrows():
        if abs(asset["absolute_difference"]) >= 0.05:
            need_rebalance = True
            break
        if abs(asset["relative_difference"]) >= 0.25:
            need_rebalance = True
            break

    if not need_rebalance:
        return {"status": "rebalance_not_required"}

    EmailClientWrapper.send("Time to rebalance!", generate_email(rebalance_amounts))
    return {"status": "rebalance_required"}
