from flask import Blueprint

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def hello():
    return "Hello, World!"