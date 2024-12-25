"""Authentication decorators"""
from functools import wraps
from flask import redirect, url_for
from app.auth.auth_service import is_authenticated

def authenticated(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
