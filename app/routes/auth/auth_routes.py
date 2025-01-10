"""Authentication routes"""
from flask import Blueprint, request, jsonify, url_for, redirect, flash, render_template
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app.extensions import db
from app.models.user import User

def create_auth_routes():
    """Create authentication routes blueprint"""
    bp = Blueprint('auth', __name__)

    @bp.route('/register', methods=['POST'])
    def register():
        """Register a new user"""
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Check if user exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
            
        # Create user
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User registered successfully'}), 201

    @bp.route('/login', methods=['POST'])
    def login():
        """Log in a user"""
        if current_user.is_authenticated:
            return jsonify({'message': 'Already logged in'}), 400
            
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Check credentials
        user = User.query.filter_by(username=data['username']).first()
        if user is None or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid username or password'}), 401
            
        # Log in user
        login_user(user, remember=data.get('remember_me', False))
        
        # Handle next page
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
            
        return jsonify({
            'message': 'Logged in successfully',
            'next': next_page
        }), 200

    @bp.route('/logout')
    @login_required
    def logout():
        """Log out the current user"""
        logout_user()
        return jsonify({'message': 'Logged out successfully'}), 200

    @bp.route('/profile')
    @login_required
    def profile():
        """Get current user profile"""
        return jsonify({
            'username': current_user.username,
            'email': current_user.email,
            'created_at': current_user.created_at.isoformat()
        }), 200

    return bp
