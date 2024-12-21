"""Tests for tea routes"""
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
def mock_tea_service(tea_dao_fixture):
    return TeaService(tea_dao_fixture)

@pytest.fixture
def app(tea_service_fixture):
    """Create application for testing"""
    test_config = {
        'TESTING': True,
        'AWS_REGION': 'us-east-1',
        'DYNAMODB_TABLE_NAME': 'test_teas'
    }
    mock_app = create_app(test_config)

    # Override the blueprint registration to use our mocked service
    mock_app.register_blueprint(create_tea_routes(tea_service_fixture))

    return mock_app

@pytest.fixture
def client(mock_app):
    """Create test client"""
    return mock_app.test_client()

@pytest.fixture
def sample_tea_data():
    return {
        "name": "Green Tea",
        "tea_type": "Green",
        "steep_time": 120,
        "steep_temperature": 175,
        "steep_count": 0
    }

def test_get_teas(client_fixture):
    """Test getting all teas"""
    response = client_fixture.get('/teas')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["Name"] == "Earl Grey"
    assert data[1]["Name"] == "Oolong"

def test_create_tea(client_fixture, tea_dao_fixture, sample_tea_data):
    """Test creating a new tea"""
    tea_dao_fixture.get_tea_item.return_value = None  # Tea doesn't exist yet
    response = client_fixture.post('/teas', json=sample_tea_data)
    assert response.status_code == 201
    tea_dao_fixture.create_tea_item.assert_called_once()

def test_get_tea(client_fixture, tea_dao_fixture):
    """Test getting a specific tea"""
    # Mock tea exists
    tea_dao_fixture.get_tea_item.return_value = {
        "Name": "Earl Grey",
        "Type": "Black",
        "SteepTimeSeconds": 180,
        "SteepTemperatureFahrenheit": 200,
        "SteepCount": 0
    }

    response = client_fixture.get('/teas/Earl Grey')
    assert response.status_code == 200
    data = response.get_json()
    assert data["Name"] == "Earl Grey"

    # Mock tea doesn't exist
    tea_dao_fixture.get_tea_item.return_value = None
    response = client_fixture.get('/teas/Nonexistent')
    assert response.status_code == 404

def test_update_tea(client_fixture, tea_dao_fixture):
    """Test updating a tea"""
    # Mock existing tea
    tea_dao_fixture.get_tea_item.return_value = {
        "Name": "Green Tea",
        "Type": "Green",
        "SteepTimeSeconds": 120,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 0
    }

    response = client_fixture.put('/teas/Green Tea', json=sample_tea_data)
    assert response.status_code == 200
    tea_dao_fixture.update_tea_item.assert_called_once()

def test_delete_tea(client_fixture, tea_dao_fixture):
    """Test deleting a tea"""
    # Mock existing tea
    tea_dao_fixture.get_tea_item.return_value = {
        "Name": "Green Tea",
        "Type": "Green",
        "SteepTimeSeconds": 120,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 0
    }

    response = client_fixture.delete('/teas/Green Tea')
    assert response.status_code == 200
    tea_dao_fixture.delete_tea_item.assert_called_once_with("Green Tea")

def test_increment_steep(client_fixture, tea_dao_fixture):
    """Test incrementing steep count for a tea"""
    # Mock initial tea state
    tea_dao_fixture.get_tea_item.return_value = {
        "Name": "Green Tea",
        "Type": "Green",
        "SteepTimeSeconds": 120,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 0
    }

    # Mock the incremented tea state
    tea_dao_fixture.increment_steep_count.return_value = {
        "Name": "Green Tea",
        "Type": "Green",
        "SteepTimeSeconds": 120,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 1
    }

    response = client_fixture.post('/teas/Green Tea/steep')
    assert response.status_code == 200
    tea_dao_fixture.increment_steep_count.assert_called_once_with("Green Tea")
    
    # Verify the updated steep count
    tea_dao_fixture.get_tea_item.return_value = tea_dao_fixture.increment_steep_count.return_value
    response = client_fixture.get('/teas/Green Tea')
    assert response.status_code == 200
    data = response.get_json()
    assert data["SteepCount"] == 1

def test_clear_steep(client_fixture, tea_dao_fixture):
    """Test clearing steep count for a tea"""
    # Mock initial tea state with steep count of 3
    tea_dao_fixture.get_tea_item.return_value = {
        "Name": "Green Tea",
        "Type": "Green",
        "SteepTimeSeconds": 120,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 3
    }

    # Mock the cleared tea state
    tea_dao_fixture.clear_steep_count.return_value = {
        "Name": "Green Tea",
        "Type": "Green",
        "SteepTimeSeconds": 120,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 0
    }

    response = client_fixture.post('/teas/Green Tea/clear')
    assert response.status_code == 200
    tea_dao_fixture.clear_steep_count.assert_called_once_with("Green Tea")

    # Verify the cleared steep count
    tea_dao_fixture.get_tea_item.return_value = tea_dao_fixture.clear_steep_count.return_value
    response = client_fixture.get('/teas/Green Tea')
    assert response.status_code == 200
    data = response.get_json()
    assert data["SteepCount"] == 0
