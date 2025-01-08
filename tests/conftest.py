"""Test configuration and fixtures"""
import pytest
from app import create_app
from app.extensions import db as _db
from config import TestConfig

@pytest.fixture
def app():
    """Create application for the tests."""
    _app = create_app(TestConfig)
    _app.config['TESTING'] = True
    return _app

@pytest.fixture
def test_client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def test_db(app):
    """Create a test database."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.close()
        _db.drop_all()
