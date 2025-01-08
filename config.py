"""Application configuration"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Basic Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key_change_in_production')
    DEBUG = False
    TESTING = False

    # SQLAlchemy configuration from database.py will be merged here
    from app.config.database import Config as DBConfig
    SQLALCHEMY_DATABASE_URI = DBConfig.SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = DBConfig.SQLALCHEMY_TRACK_MODIFICATIONS
    SQLALCHEMY_POOL_SIZE = DBConfig.SQLALCHEMY_POOL_SIZE
    SQLALCHEMY_MAX_OVERFLOW = DBConfig.SQLALCHEMY_MAX_OVERFLOW
    SQLALCHEMY_POOL_TIMEOUT = DBConfig.SQLALCHEMY_POOL_TIMEOUT

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Security headers
    STRICT_TRANSPORT_SECURITY = True
    STRICT_TRANSPORT_SECURITY_PRELOAD = True
    STRICT_TRANSPORT_SECURITY_MAX_AGE = 31536000  # 1 year
    STRICT_TRANSPORT_SECURITY_INCLUDE_SUBDOMAINS = True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    
    # Override database URL for development if needed
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DEV_DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/teaminder_dev'
    )

class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    
    # Use SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF protection in testing
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration"""
    # Ensure all required environment variables are set
    REQUIRED_ENV_VARS = [
        'SECRET_KEY',
        'DATABASE_URL',
    ]

    def __init__(self):
        for var in self.REQUIRED_ENV_VARS:
            if not os.getenv(var):
                raise ValueError(f'Environment variable {var} is required in production')

    # Use strong secret key in production
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # Additional security headers for production
    CONTENT_SECURITY_POLICY = {
        'default-src': "'self'",
        'img-src': "'self' data: https:",
        'script-src': "'self'",
        'style-src': "'self' 'unsafe-inline'",
        'frame-ancestors': "'none'"
    }

# Dictionary to map environment names to config classes
config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
