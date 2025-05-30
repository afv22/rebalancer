import os

from waitress import serve

from app import create_app


if __name__ == "__main__":
    host, port = "0.0.0.0", os.environ.get("PORT", 8080)
    print(f"Running server on {host}:{port}")
    serve(create_app(), host=host, port=port)
