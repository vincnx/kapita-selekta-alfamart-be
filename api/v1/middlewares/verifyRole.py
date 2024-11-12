from functools import wraps
from typing import Callable

from flask import abort, g


def verifyRole(allowed_roles: list[str]):
    def decorator(f: Callable):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user['userRole'] not in allowed_roles:
                abort(403, 'Forbidden')
            return f(*args, **kwargs)
        return decorated_function
    return decorator