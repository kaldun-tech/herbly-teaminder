"""Database configuration"""
class Config:
    DYNAMODB_ENDPOINT = 'https://dynamodb.us-east-1.amazonaws.com'
    DATABASE_MAX_RETRIES = 3
    DATABASE_TIMEOUT = 30
