"""Database configuration"""
import os

class Config:
    """Database configuration settings"""
    # DynamoDB settings (for legacy support)
    DYNAMODB_ENDPOINT = 'https://dynamodb.us-east-1.amazonaws.com'
    DATABASE_MAX_RETRIES = 3
    DATABASE_TIMEOUT = 30

    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_MAX_OVERFLOW = 10
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  
        'pool_recycle': 3600,   
    }
