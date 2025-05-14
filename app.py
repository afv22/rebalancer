import os
from flask import Flask
from waitress import serve
from dotenv import load_dotenv

from src.api.email import EmailClientWrapper

from src.generate_email import generate_email
from src.get_holdings import get_holdings
from src.get_rebalance_amounts import get_rebalance_amounts
from src.utils import is_prod


def create_app():
    load_dotenv(override=True)

    user_id = 2 if is_prod() else 1

    app = Flask(__name__)

    @app.route("/")
    def hello():
        return "Hello!"

    @app.route("/holdings")
    def holdings():
        return map(lambda h: h.symbol, get_holdings(user_id))

    @app.route("/rebalance_amounts")
    def rebalance_amounts():
        holdings = get_holdings(user_id)
        return get_rebalance_amounts(holdings).to_dict()

    @app.route("/check_allocation")
    def check_allocation():
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
            return {"status": "ok", "message": "Everything looks good."}

        EmailClientWrapper.send("Time to rebalance!", generate_email(rebalance_amounts))
        return {
            "status": "rebalance_required",
            "message": "Email sent with rebalance instructions.",
        }

    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    host = "0.0.0.0"
    print(f"Running server on {host}:{port}")
    serve(create_app(), host=host, port=port)
