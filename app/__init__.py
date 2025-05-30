from flask import Flask

from app.utils import is_prod
from app.blueprints.main import main_bp
from app.blueprints.portfolio import portfolio_bp


def create_app():
    user_id = 2 if is_prod() else 1

    app = Flask(__name__)
    app.config["USER_ID"] = user_id

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(portfolio_bp, url_prefix="/portfolio")

    return app
