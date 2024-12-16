"""Secrets configuration"""
import os

class Config:
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

    DATABASE_USERNAME = os.environ['DATABASE_USERNAME']
    DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']

    API_KEY = os.environ['API_KEY']
    API_SECRET = os.environ['API_SECRET']

    SECRET_KEY = os.environ['SECRET_KEY']
    ENCRYPTION_KEY = os.environ['ENCRYPTION_KEY']
