import os
import functools


def is_prod():
    return not os.environ.get("ENV") == "dev"


def error_handler(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return {"data": f(*args, **kwargs)}
        except Exception as e:
            return {"error": str(e)}

    return wrapper
