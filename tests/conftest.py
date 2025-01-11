"""Pytest configuration file."""
import pytest
from app import create_app
from app.extensions import db

def get_test_config():
    """Get test configuration."""
    return {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    }

@pytest.fixture
def test_app():
    """Create application for the tests."""
    _app = create_app(get_test_config())
    _app.config['TESTING'] = True
    return _app

@pytest.fixture
def test_client(test_app):  # pylint: disable=redefined-outer-name
    """Create a test client for the app."""
    return test_app.test_client()

@pytest.fixture
def test_db(test_app):  # pylint: disable=redefined-outer-name
    """Create a test database."""
    with test_app.app_context():
        db.create_all()
        yield db
        db.drop_all()
