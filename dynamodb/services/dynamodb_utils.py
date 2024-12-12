"""Helpers for DynamoDB"""
import boto3

dynamodb = boto3.resource('dynamodb')

def create_transaction(table_name):
    """Create DynamoDB transaction"""
    table = dynamodb.Table(table_name)
    transaction = table.meta.client.begin_transaction()
    return transaction

def commit_transaction(transaction):
    transaction.commit()

def rollback_transaction(transaction):
    transaction.rollback()
