"""Database configuration"""
class Config:
    DYNAMODB_ENDPOINT = 'https://dynamodb.us-west-2.amazonaws.com'
    DATABASE_MAX_RETRIES = 3
    DATABASE_TIMEOUT = 30
