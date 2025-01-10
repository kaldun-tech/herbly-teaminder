"""Models package"""
from app.models.user import User
from app.models.tea import Tea

# This ensures all models are registered with SQLAlchemy
__all__ = ['User', 'Tea']