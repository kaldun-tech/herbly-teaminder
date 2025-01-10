"""Secrets configuration"""
import os

class Config:
    """Configuration class for sensitive environment variables"""
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'dummy_key_id')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'dummy_secret_key')

    DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME', 'default_user')
    DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', 'default_password')

    API_KEY = os.environ.get('API_KEY', 'dummy_api_key')
    API_SECRET = os.environ.get('API_SECRET', 'dummy_api_secret')

    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-CHANGE-IN-PRODUCTION')
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', 'development_encryption_key')
