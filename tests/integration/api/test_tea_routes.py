"""Tests for tea routes"""
# pylint: disable=redefined-outer-name
from unittest.mock import Mock
import pytest
from app.app import create_app
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
    test_config = {
        'TESTING': True,
        'AWS_REGION': 'us-east-1',
        'DYNAMODB_TABLE_NAME': 'test_teas'
    }
    app = create_app(test_config)
    app.register_blueprint(create_tea_routes(mock_tea_service))
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def sample_tea_data():
    return {
        "name": "Green Tea",
        "tea_type": "Green",
        "steep_time": 120,
        "steep_temperature": 175,
        "steep_count": 0
    }

def test_get_teas(client):
    """Test getting all teas"""
    response = client.get('/teas')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["Name"] == "Earl Grey"
    assert data[1]["Name"] == "Oolong"

def test_create_tea(client, mock_tea_dao, sample_tea_data):
    """Test creating a new tea"""
    mock_tea_dao.get_tea_item.return_value = None  # Tea doesn't exist yet
    response = client.post('/teas', json=sample_tea_data)
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

    response = client.get('/teas/Earl Grey')
    assert response.status_code == 200
    data = response.get_json()
    assert data["Name"] == "Earl Grey"

    # Mock tea doesn't exist
    mock_tea_dao.get_tea_item.return_value = None
    response = client.get('/teas/Nonexistent')
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

    response = client.put('/teas/Green Tea', json=sample_tea_data)
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

    response = client.delete('/teas/Green Tea')
    assert response.status_code == 200
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

    response = client.post('/teas/Green Tea/steep')
    assert response.status_code == 200
    mock_tea_dao.increment_steep_count.assert_called_once_with("Green Tea")

    # Verify the updated steep count
    mock_tea_dao.get_tea_item.return_value = mock_tea_dao.increment_steep_count.return_value
    response = client.get('/teas/Green Tea')
    assert response.status_code == 200
    data = response.get_json()
    assert data["SteepCount"] == 1

def test_clear_steep(client, mock_tea_dao):
    """Test clearing steep count for a tea"""
    # Mock initial tea state with steep count of 3
    mock_tea_dao.get_tea_item.return_value = {
        "Name": "Green Tea",
        "Type": "Green",
        "SteepTimeSeconds": 120,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 3
    }

    response = client.post('/teas/Green Tea/clear')
    assert response.status_code == 200
    mock_tea_dao.clear_steep_count.assert_called_once_with("Green Tea")
