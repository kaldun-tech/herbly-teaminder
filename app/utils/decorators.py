from functools import wraps

def authenticated(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # authentication logic here
        pass
    return decorated_function