"""Authentication routes"""
from flask import Blueprint, render_template

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login')
def login():
    return render_template('html/login.html')

@bp.route('/register')
def register():
    """Register a new user"""
    return render_template('html/register.html')

@bp.route('/logout')
def logout():
    """Log out the current user"""
    return render_template('html/logout.html')
