"""Authentication routes for the application"""
from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.user import User
from app.extensions import db

def create_auth_routes():
    """Factory function to create authentication routes blueprint"""
    auth_routes = Blueprint('auth_routes', __name__)

    @auth_routes.route('/auth/register', methods=['POST'])
    def register():
        """Register a new user"""
        data = request.get_json()

        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if username already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400

        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400

        # Create new user
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 201

    @auth_routes.route('/auth/login', methods=['POST'])
    def login():
        """Login a user"""
        data = request.get_json()

        # Validate required fields
        required_fields = ['username', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Find user by username
        user = User.query.filter_by(username=data['username']).first()
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid username or password'}), 401

        # Login user
        login_user(user)

        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })

    @auth_routes.route('/auth/logout', methods=['POST'])
    @login_required
    def logout():
        """Logout the current user"""
        logout_user()
        return jsonify({'message': 'Logout successful'})

    @auth_routes.route('/auth/me', methods=['GET'])
    @login_required
    def get_current_user():
        """Get the current user's information"""
        return jsonify({
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email
            }
        })

    @auth_routes.route('/auth/me', methods=['PUT'])
    @login_required
    def update_current_user():
        """Update the current user's information"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        if 'username' in data:
            # Check if new username is already taken
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.id != current_user.id:
                return jsonify({'error': 'Username already exists'}), 400
            current_user.username = data['username']

        if 'email' in data:
            # Check if new email is already taken
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != current_user.id:
                return jsonify({'error': 'Email already exists'}), 400
            current_user.email = data['email']

        if 'password' in data:
            current_user.set_password(data['password'])

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

        return jsonify({
            'message': 'User updated successfully',
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email
            }
        })

    return auth_routes
