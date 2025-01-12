"""Pytest configuration file."""
import pytest
from app import create_app
from app.extensions import db

def get_test_config():
    """Get test configuration."""
    return {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key-NOT-FOR-PRODUCTION',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'LOGIN_DISABLED': False,  # Enable login for testing
        'PRESERVE_CONTEXT_ON_EXCEPTION': False
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
        db.session.remove()
        db.drop_all()
