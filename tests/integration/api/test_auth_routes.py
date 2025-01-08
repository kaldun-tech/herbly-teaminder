"""Tests for authentication routes"""
import json
import pytest
from flask import Flask
from flask_login import LoginManager
from app.models.user import User
from app.routes.auth.auth_routes import create_auth_routes
from app.extensions import db

@pytest.fixture
def app():
    """Create application for testing"""
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test_secret_key'
    })
    
    # Initialize extensions
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprint
    auth_bp = create_auth_routes()
    app.register_blueprint(auth_bp)
    
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_register(client):
    """Test user registration"""
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }
    response = client.post('/auth/register', json=data)
    assert response.status_code == 201
    
    # Check response
    json_data = response.get_json()
    assert json_data['user']['username'] == data['username']
    assert json_data['user']['email'] == data['email']
    
    # Check user was created in database
    user = User.query.filter_by(username=data['username']).first()
    assert user is not None
    assert user.email == data['email']

def test_register_duplicate_username(client):
    """Test registration with duplicate username"""
    # Create first user
    data = {
        'username': 'testuser',
        'email': 'test1@example.com',
        'password': 'password123'
    }
    client.post('/auth/register', json=data)
    
    # Try to create second user with same username
    data['email'] = 'test2@example.com'
    response = client.post('/auth/register', json=data)
    assert response.status_code == 400
    assert b'Username already exists' in response.data

def test_login_success(client):
    """Test successful login"""
    # Register user
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }
    client.post('/auth/register', json=data)
    
    # Login
    response = client.post('/auth/login', json={
        'username': data['username'],
        'password': data['password']
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['user']['username'] == data['username']

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/auth/login', json={
        'username': 'nonexistent',
        'password': 'wrong'
    })
    assert response.status_code == 401

def test_logout(client):
    """Test user logout"""
    # Register and login user
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }
    client.post('/auth/register', json=data)
    client.post('/auth/login', json={
        'username': data['username'],
        'password': data['password']
    })
    
    # Logout
    response = client.post('/auth/logout')
    assert response.status_code == 200
    
    # Verify logout by trying to access protected route
    response = client.get('/auth/me')
    assert response.status_code == 401

def test_get_current_user(client):
    """Test getting current user info"""
    # Register and login user
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }
    client.post('/auth/register', json=data)
    client.post('/auth/login', json={
        'username': data['username'],
        'password': data['password']
    })
    
    # Get current user
    response = client.get('/auth/me')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['user']['username'] == data['username']
    assert json_data['user']['email'] == data['email']

def test_update_current_user(client):
    """Test updating current user info"""
    # Register and login user
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }
    client.post('/auth/register', json=data)
    client.post('/auth/login', json={
        'username': data['username'],
        'password': data['password']
    })
    
    # Update user
    update_data = {
        'username': 'newusername',
        'email': 'newemail@example.com',
        'password': 'newpassword123'
    }
    response = client.put('/auth/me', json=update_data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['user']['username'] == update_data['username']
    assert json_data['user']['email'] == update_data['email']
    
    # Verify password change by logging in with new password
    response = client.post('/auth/login', json={
        'username': update_data['username'],
        'password': update_data['password']
    })
    assert response.status_code == 200

def test_update_to_existing_username(client):
    """Test updating to an already existing username"""
    # Create first user
    client.post('/auth/register', json={
        'username': 'user1',
        'email': 'user1@example.com',
        'password': 'password123'
    })
    
    # Create and login second user
    data = {
        'username': 'user2',
        'email': 'user2@example.com',
        'password': 'password123'
    }
    client.post('/auth/register', json=data)
    client.post('/auth/login', json={
        'username': data['username'],
        'password': data['password']
    })
    
    # Try to update to first user's username
    response = client.put('/auth/me', json={'username': 'user1'})
    assert response.status_code == 400
    assert b'Username already exists' in response.data
