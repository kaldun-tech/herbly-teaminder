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
        {"Name": "Earl Grey", "Type": "Black", "SteepTimeMinutes": 3, "SteepTemperatureFahrenheit": 200, "SteepCount": 0},
        {"Name": "Oolong", "Type": "Green", "SteepTimeMinutes": 2, "SteepTemperatureFahrenheit": 175, "SteepCount": 0}
    ]

    def mock_increment_steep(name):
        return {"Name": name, "Type": "Black", "SteepTimeMinutes": 3, "SteepTemperatureFahrenheit": 200, "SteepCount": 1}

    mock_dao.increment_steep_count.side_effect = mock_increment_steep
    mock_dao.get_tea_item.return_value = {"Name": "Earl Grey", "Type": "Black", "SteepTimeMinutes": 3,
        "SteepTemperatureFahrenheit": 200, "SteepCount": 0}
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

    # Register blueprint with mock service
    tea_bp = create_tea_routes(mock_tea_service)
    app.register_blueprint(tea_bp, url_prefix='/api')

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
        "SteepTimeMinutes": 2,
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
        "SteepTimeMinutes": 3,
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
        "SteepTimeMinutes": 2,
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
        "SteepTimeMinutes": 2,
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
        "SteepTimeMinutes": 2,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 0
    }

    # Mock the incremented tea state
    mock_tea_dao.increment_steep_count.return_value = {
        "Name": "Green Tea",
        "Type": "Green",
        "SteepTimeMinutes": 2,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 1
    }

    response = client.post('/api/teas/Green Tea/steep')
    assert response.status_code == 200
    mock_tea_dao.increment_steep_count.assert_called_once_with("Green Tea")

def test_clear_steep(client, mock_tea_dao):
    """Test clearing steep count for a tea"""
    # Mock initial tea state with nonzero steep count
    initial_tea = {
        "Name": "Green Tea",
        "Type": "Green",
        "SteepTimeMinutes": 2,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 3  # Start with nonzero steep count
    }
    cleared_tea = dict(initial_tea)  # Create a copy
    cleared_tea["SteepCount"] = 0    # Set steep count to 0
    
    mock_tea_dao.get_tea_item.return_value = initial_tea
    mock_tea_dao.clear_steep_count.return_value = cleared_tea

    response = client.delete('/api/teas/Green Tea/steep')
    assert response.status_code == 200
    mock_tea_dao.clear_steep_count.assert_called_once_with("Green Tea")
    
    # Verify the response shows steep count was cleared
    response_data = response.get_json()
    assert response_data["SteepCount"] == 0

def test_create_tea_with_defaults(client, mock_tea_dao):
    """Test creating a tea with minimal data"""
    minimal_tea = {
        "Name": "Basic Tea",
        "Type": "Black"
    }
    expected_tea = {
        "Name": "Basic Tea",
        "Type": "Black",
        "SteepTimeMinutes": 0,
        "SteepTemperatureFahrenheit": 0,
        "SteepCount": 0
    }
    mock_tea_dao.get_tea_item.return_value = None
    mock_tea_dao.create_tea_item.return_value = expected_tea

    response = client.post('/api/teas', json=minimal_tea)
    assert response.status_code == 201
    data = response.get_json()
    assert data["SteepTimeMinutes"] == 0
    assert data["SteepTemperatureFahrenheit"] == 0
    assert data["SteepCount"] == 0

def test_update_tea_steep_time(client, mock_tea_dao):
    """Test updating just the steep time of a tea"""
    original_tea = {
        "Name": "Green Tea",
        "Type": "Green",
        "SteepTimeMinutes": 2,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 0
    }
    mock_tea_dao.get_tea_item.return_value = original_tea

    update_data = {
        "Name": "Green Tea",
        "SteepTimeMinutes": 3
    }
    expected_tea = original_tea.copy()
    expected_tea["SteepTimeMinutes"] = 3
    mock_tea_dao.update_tea_item.return_value = expected_tea

    response = client.put('/api/teas/Green Tea', json=update_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data["SteepTimeMinutes"] == 3
    assert data["Type"] == "Green"  # Unchanged
    assert data["SteepTemperatureFahrenheit"] == 175  # Unchanged

def test_get_tea_defaults(client):
    """Test getting tea defaults from config"""
    response = client.get('/api/defaults')
    assert response.status_code == 200
    data = response.get_json()

    # Check structure for each tea type
    for tea_type in data:
        assert 'steep_time' in data[tea_type]
        assert 'temperature' in data[tea_type]
        assert isinstance(data[tea_type]['steep_time'], int)
        assert isinstance(data[tea_type]['temperature'], int)

def test_increment_steep_preserves_time(client, mock_tea_dao):
    """Test that incrementing steep count preserves steep time"""
    original_tea = {
        "Name": "Green Tea",
        "Type": "Green",
        "SteepTimeMinutes": 2,
        "SteepTemperatureFahrenheit": 175,
        "SteepCount": 0
    }

    incremented_tea = original_tea.copy()
    incremented_tea["SteepCount"] = 1

    # First return original tea, then return incremented tea
    mock_tea_dao.get_tea_item.side_effect = [original_tea, incremented_tea]
    # Override the default side_effect with a return_value
    mock_tea_dao.increment_steep_count = Mock(return_value=incremented_tea)

    response = client.post('/api/teas/Green Tea/steep')
    assert response.status_code == 200
    data = response.get_json()
    assert data["SteepTimeMinutes"] == 2  # Time preserved
    assert data["SteepCount"] == 1  # Count incremented
