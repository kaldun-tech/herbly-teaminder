"""Application configuration"""
import os
from datetime import timedelta
from app.config.database import Config as DBConfig

class Config:
    """Base configuration"""
    # Basic Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-CHANGE-IN-PRODUCTION')
    DEBUG = False
    TESTING = False

    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = DBConfig.SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = DBConfig.SQLALCHEMY_TRACK_MODIFICATIONS
    SQLALCHEMY_POOL_SIZE = DBConfig.SQLALCHEMY_POOL_SIZE
    SQLALCHEMY_MAX_OVERFLOW = DBConfig.SQLALCHEMY_MAX_OVERFLOW
    SQLALCHEMY_POOL_TIMEOUT = DBConfig.SQLALCHEMY_POOL_TIMEOUT
    SQLALCHEMY_ENGINE_OPTIONS = DBConfig.SQLALCHEMY_ENGINE_OPTIONS

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
    # Override database URL if specified in environment
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///dev.db')

class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration"""
    REQUIRED_ENV_VARS = [
        'SECRET_KEY',
        'DATABASE_URL',
    ]

    def __init__(self):
        for var in self.REQUIRED_ENV_VARS:
            if not os.getenv(var):
                raise ValueError(f'Environment variable {var} is required in production')
        
        super().__init__()
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        self.SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    # Security settings
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
