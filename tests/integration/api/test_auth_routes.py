"""Tests for authentication routes"""
import json
from datetime import datetime
import pytest
from flask import url_for
from flask_login import LoginManager
from app.models.user import User
from app.extensions import db

@pytest.fixture
def auth_client(test_app, test_client, test_db):
    """Create test client with auth blueprint"""
    # Initialize login manager if not already initialized
    if not test_app.login_manager:
        login_manager = LoginManager()
        login_manager.init_app(test_app)
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
    
    return test_client

def test_register(auth_client):
    """Test user registration"""
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }
    response = auth_client.post('/auth/register', json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['message'] == 'User registered successfully'
    
    # Check user was created in database
    user = User.query.filter_by(username=data['username']).first()
    assert user is not None
    assert user.email == data['email']
    assert user.check_password(data['password'])

def test_register_duplicate_username(auth_client):
    """Test registration with duplicate username"""
    data = {
        'username': 'testuser',
        'email': 'test1@example.com',
        'password': 'password123'
    }
    auth_client.post('/auth/register', json=data)
    
    # Try to create second user with same username
    data['email'] = 'test2@example.com'
    response = auth_client.post('/auth/register', json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['error'] == 'Username already exists'

def test_register_duplicate_email(auth_client):
    """Test registration with duplicate email"""
    data = {
        'username': 'user1',
        'email': 'test@example.com',
        'password': 'password123'
    }
    auth_client.post('/auth/register', json=data)
    
    # Try to create second user with same email
    data['username'] = 'user2'
    response = auth_client.post('/auth/register', json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['error'] == 'Email already exists'

def test_login_success(auth_client):
    """Test successful login"""
    # Register user
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }
    auth_client.post('/auth/register', json=data)
    
    # Login
    login_data = {
        'username': data['username'],
        'password': data['password'],
        'remember_me': True
    }
    response = auth_client.post('/auth/login', json=login_data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == 'Logged in successfully'
    assert 'next' in json_data

def test_login_invalid_credentials(auth_client):
    """Test login with invalid credentials"""
    response = auth_client.post('/auth/login', json={
        'username': 'nonexistent',
        'password': 'wrong'
    })
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['error'] == 'Invalid username or password'

def test_login_already_authenticated(auth_client):
    """Test login when already authenticated"""
    # Register and login first
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }
    auth_client.post('/auth/register', json=data)
    auth_client.post('/auth/login', json=data)
    
    # Try to login again
    response = auth_client.post('/auth/login', json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == 'Already logged in'

def test_logout(auth_client):
    """Test user logout"""
    # Register and login user
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }
    auth_client.post('/auth/register', json=data)
    auth_client.post('/auth/login', json=data)
    
    # Logout
    response = auth_client.post('/auth/logout')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == 'Logged out successfully'
    
    # Verify logout by trying to access protected route
    response = auth_client.get('/auth/profile')
    assert response.status_code == 401

def test_profile(auth_client):
    """Test getting user profile"""
    # Register and login user
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }
    auth_client.post('/auth/register', json=data)
    auth_client.post('/auth/login', json=data)
    
    # Get profile
    response = auth_client.get('/auth/profile')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['username'] == data['username']
    assert json_data['email'] == data['email']
    assert 'created_at' in json_data
