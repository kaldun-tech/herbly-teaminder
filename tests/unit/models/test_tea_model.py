"""Tests for Tea model"""
import pytest
from datetime import datetime
from flask import Flask
from app.models.tea import Tea
from app.extensions import db

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
    
    return app

class TestTeaModel:
    """Test cases for Tea model"""
    
    def test_init(self, app):
        """Test basic tea initialization"""
        with app.app_context():
            tea = Tea(
                name="Earl Grey",
                tea_type="Black",
                steep_time=180,  # 3 minutes in seconds
                steep_temperature=95,  # celsius
                notes="Test notes",
                user_id=1
            )
            assert tea.name == "Earl Grey"
            assert tea.type == "Black"
            assert tea.steep_time == 180
            assert tea.steep_temperature == 95
            assert tea.steep_count == 0
            assert tea.notes == "Test notes"
            assert tea.user_id == 1
            assert isinstance(tea.created_at, datetime)
            assert isinstance(tea.updated_at, datetime)

    def test_to_dict(self, app):
        """Test dictionary conversion"""
        with app.app_context():
            now = datetime.utcnow()
            tea = Tea(
                name="Green Tea",
                tea_type="Green",
                steep_time=120,
                steep_temperature=80,
                steep_count=1,
                notes="Test notes",
                user_id=1,
                created_at=now,
                updated_at=now
            )
            tea_dict = tea.to_dict()
            assert tea_dict["name"] == "Green Tea"
            assert tea_dict["type"] == "Green"
            assert tea_dict["steep_time"] == 120
            assert tea_dict["steep_temperature"] == 80
            assert tea_dict["steep_count"] == 1
            assert tea_dict["notes"] == "Test notes"
            assert tea_dict["created_at"] == now.isoformat()
            assert tea_dict["updated_at"] == now.isoformat()

    def test_repr(self, app):
        """Test string representation"""
        with app.app_context():
            tea = Tea(
                name="Earl Grey",
                tea_type="Black",
                steep_time=180,
                steep_temperature=95,
                notes="Test notes",
                user_id=1
            )
            assert repr(tea) == '<Tea Earl Grey>'

    def test_required_fields(self, app):
        """Test that required fields raise error when missing"""
        with app.app_context():
            with pytest.raises(Exception):  # SQLAlchemy will raise an error
                Tea().save()  # Missing required fields

            with pytest.raises(Exception):
                Tea(name="Test Tea").save()  # Missing type

            with pytest.raises(Exception):
                Tea(name="Test Tea", tea_type="Black").save()  # Missing user_id
