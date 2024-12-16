"""Prod configuration"""
class Config:
    DEBUG = False
    TESTING = False
    DYNAMODB_TABLE_NAME = 'tea_table'
    AWS_REGION = 'us-east-1'
