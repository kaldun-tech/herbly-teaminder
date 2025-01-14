"""Tests for tea routes"""
import json
import pytest
from flask import Flask, jsonify
from app.models.tea import Tea
from app.models.user import User
from app.routes.api.tea_routes import create_tea_routes
from app.extensions import db, login_manager

@pytest.fixture
def app():
    """Create application for testing"""
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'TEST-secret-key-NOT-FOR-PRODUCTION'
    })
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configure unauthorized handler for API routes
    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Configure user loader
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Register blueprint
    tea_bp = create_tea_routes()
    app.register_blueprint(tea_bp, url_prefix='/api')
    
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

@pytest.fixture
def auth_client(client, app):
    """Create an authenticated test client"""
    with app.app_context():
        # Create a test user
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Get fresh user instance from database
        user = db.session.get(User, user.id)
        
        # Log in the user
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        
        return client, user

@pytest.fixture
def sample_tea(auth_client):
    """Create a sample tea for testing"""
    client, user = auth_client
    with client.application.app_context():
        tea = Tea(
            name='Test Green Tea',
            type='green',
            steep_time=180,
            steep_temperature=80,
            notes='Test notes',
            user_id=user.id
        )
        db.session.add(tea)
        db.session.commit()
        # Get fresh tea instance from database
        tea = db.session.get(Tea, tea.id)
        return tea

def test_get_teas_unauthorized(client):
    """Test that unauthorized users cannot access teas"""
    response = client.get('/api/teas')
    assert response.status_code == 401

def test_get_teas(auth_client, sample_tea):
    """Test getting all teas"""
    client, _ = auth_client
    response = client.get('/api/teas')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['name'] == 'Test Green Tea'

def test_create_tea(auth_client):
    """Test creating a new tea"""
    client, _ = auth_client
    tea_data = {
        'name': 'New Green Tea',
        'type': 'green',
        'steep_time': 180,
        'steep_temperature': 80,
        'notes': 'Test notes'
    }
    response = client.post('/api/teas', json=tea_data)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == tea_data['name']
    assert data['type'] == tea_data['type']

def test_create_duplicate_tea(auth_client, sample_tea):
    """Test creating a tea with a duplicate name"""
    client, _ = auth_client
    tea_data = {
        'name': 'Test Green Tea',  # Same name as sample_tea
        'type': 'green',
        'steep_time': 180,
        'steep_temperature': 80
    }
    response = client.post('/api/teas', json=tea_data)
    assert response.status_code == 400
    assert b'already exists' in response.data

def test_get_tea(auth_client, sample_tea):
    """Test getting a specific tea"""
    client, _ = auth_client
    response = client.get(f'/api/teas/{sample_tea.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Test Green Tea'

def test_update_tea(auth_client, sample_tea):
    """Test updating a tea"""
    client, _ = auth_client
    update_data = {'name': 'Updated Tea Name'}
    response = client.put(f'/api/teas/{sample_tea.id}', json=update_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Updated Tea Name'

def test_delete_tea(auth_client, sample_tea):
    """Test deleting a tea"""
    client, _ = auth_client
    response = client.delete(f'/api/teas/{sample_tea.id}')
    assert response.status_code == 204
    
    # Verify tea was deleted
    tea = db.session.get(Tea, sample_tea.id)
    assert tea is None

def test_increment_steep_count(auth_client, sample_tea):
    """Test incrementing steep count"""
    client, _ = auth_client
    initial_count = sample_tea.steep_count
    response = client.post(f'/api/teas/{sample_tea.id}/steep')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['steep_count'] == initial_count + 1

def test_clear_steep_count(auth_client, sample_tea):
    """Test clearing steep count"""
    client, _ = auth_client
    # First increment the count
    sample_tea.steep_count = 5
    db.session.commit()
    
    response = client.delete(f'/api/teas/{sample_tea.id}/steep')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['steep_count'] == 0

def test_user_cannot_access_others_tea(auth_client, app):
    """Test that users cannot access teas belonging to other users"""
    client, user1 = auth_client
    
    # Create another user with their own tea
    with app.app_context():
        user2 = User(username='other_user', email='other@example.com')
        user2.set_password('password123')
        db.session.add(user2)
        db.session.commit()
        
        tea = Tea(
            name='Other User Tea',
            type='black',
            steep_time=180,
            steep_temperature=100,
            user_id=user2.id
        )
        db.session.add(tea)
        db.session.commit()
        
        # Try to access the other user's tea
        response = client.get(f'/api/teas/{tea.id}')
        assert response.status_code == 404
