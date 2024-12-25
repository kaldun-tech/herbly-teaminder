"""Authentication service module"""
from flask import session

def is_authenticated():
    """Check if user is authenticated"""
    return 'user_id' in session
