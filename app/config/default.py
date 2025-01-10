"""Default configuration for the application"""
import os

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-CHANGE-IN-PRODUCTION')
    TESTING = False
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    FORCE_HTTPS = os.environ.get('FORCE_HTTPS', 'True').lower() == 'true'
    
    # AWS Configuration
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'teas')

    def __iter__(self):
        """Make Config iterable for Flask's config.update()"""
        for key in dir(self):
            if not key.startswith('_'):
                value = getattr(self, key)
                if not callable(value):
                    yield key, value
