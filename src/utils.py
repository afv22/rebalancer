import os


def is_prod():
    return not os.environ.get("ENVIRONMENT") == "dev"
