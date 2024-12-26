"""Tests for tea routes"""
# pylint: disable=redefined-outer-name
from unittest.mock import Mock
import pytest
from flask import Flask
from app.services.tea_service import TeaService
from app.routes.api.tea_routes import create_tea_routes

@pytest.fixture
def mock_tea_dao():
    mock_dao = Mock()
    mock_dao.get_all_tea_items.return_value = [
        {"Name": "Earl Grey", "Type": "Black", "SteepTimeSeconds": 180, "SteepTemperatureFahrenheit": 200, "SteepCount": 0},
        {"Name": "Oolong", "Type": "Green", "SteepTimeSeconds": 120, "SteepTemperatureFahrenheit": 175, "SteepCount": 0}
    ]
    return mock_dao

@pytest.fixture
def mock_tea_service(mock_tea_dao):
    return TeaService(mock_tea_dao)

@pytest.fixture
def app(mock_tea_service):
    """Create application for testing"""
    app = Flask(__name__)
    test_config = {
        'TESTING': True,
        'AWS_REGION': 'us-east-1',
        'DYNAMODB_TABLE_NAME': 'test_teas'
    }
    app.config.update(test_config)

    # Register blueprint with the mock service
    app.register_blueprint(create_tea_routes(mock_tea_service), url_prefix='/api')

    return app

@pytest.fixture
def client(app):
    """Create test client"""
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def sample_tea_data():
    """Sample tea data for testing"""
    return {
        "Name": "Green Tea",
        "Type": "Green",
        "SteepTimeSeconds": 120,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 0
    }

def test_get_teas(client):
    """Test getting all teas"""
    response = client.get('/api/teas')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["Name"] == "Earl Grey"

def test_create_tea(client, mock_tea_dao, sample_tea_data):
    """Test creating a new tea"""
    mock_tea_dao.get_tea_item.return_value = None  # Tea doesn't exist yet
    mock_tea_dao.create_tea_item.return_value = sample_tea_data
    response = client.post('/api/teas', json=sample_tea_data)
    assert response.status_code == 201
    mock_tea_dao.create_tea_item.assert_called_once()

def test_get_tea(client, mock_tea_dao):
    """Test getting a specific tea"""
    # Mock tea exists
    mock_tea_dao.get_tea_item.return_value = {
        "Name": "Earl Grey",
        "Type": "Black",
        "SteepTimeSeconds": 180,
        "SteepTemperatureFahrenheit": 200,
        "SteepCount": 0
    }

    response = client.get('/api/teas/Earl Grey')
    assert response.status_code == 200
    data = response.get_json()
    assert data["Name"] == "Earl Grey"

    # Mock tea doesn't exist
    mock_tea_dao.get_tea_item.side_effect = KeyError("Tea not found")
    response = client.get('/api/teas/Nonexistent')
    assert response.status_code == 404

def test_update_tea(client, mock_tea_dao, sample_tea_data):
    """Test updating a tea"""
    # Mock existing tea
    mock_tea_dao.get_tea_item.return_value = {
        "Name": "Green Tea",
        "Type": "Green",
        "SteepTimeSeconds": 120,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 0
    }
    mock_tea_dao.update_tea_item.return_value = sample_tea_data

    response = client.put('/api/teas/Green Tea', json=sample_tea_data)
    assert response.status_code == 200
    mock_tea_dao.update_tea_item.assert_called_once()

def test_delete_tea(client, mock_tea_dao):
    """Test deleting a tea"""
    # Mock existing tea
    mock_tea_dao.get_tea_item.return_value = {
        "Name": "Green Tea",
        "Type": "Green",
        "SteepTimeSeconds": 120,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 0
    }

    response = client.delete('/api/teas/Green Tea')
    assert response.status_code == 204
    mock_tea_dao.delete_tea_item.assert_called_once_with("Green Tea")

def test_increment_steep(client, mock_tea_dao):
    """Test incrementing steep count for a tea"""
    # Mock initial tea state
    mock_tea_dao.get_tea_item.return_value = {
        "Name": "Green Tea",
        "Type": "Green",
        "SteepTimeSeconds": 120,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 0
    }

    # Mock the incremented tea state
    mock_tea_dao.increment_steep_count.return_value = {
        "Name": "Green Tea",
        "Type": "Green",
        "SteepTimeSeconds": 120,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 1
    }

    response = client.post('/api/teas/Green Tea/steep')
    assert response.status_code == 200
    mock_tea_dao.increment_steep_count.assert_called_once_with("Green Tea")

def test_clear_steep(client, mock_tea_dao):
    """Test clearing steep count for a tea"""
    # Mock initial tea state
    mock_tea_dao.get_tea_item.return_value = {
        "Name": "Green Tea",
        "Type": "Green",
        "SteepTimeSeconds": 120,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 3
    }

    response = client.post('/api/teas/Green Tea/clear')
    assert response.status_code == 200
    mock_tea_dao.clear_steep_count.assert_called_once_with("Green Tea")
