"""Helpers for DynamoDB"""
import boto3

# Resource is used for update operations while client is used for read
db_resource = boto3.resource('dynamodb')
db_client = boto3.client('dynamodb')

def get_dynamodb_table(table_name):
    return db_client.Table(table_name)

def create_transaction(table_name):
    table = db_resource.Table(table_name)
    transaction = table.meta.client.begin_transaction()
    return transaction

def commit_transaction(transaction):
    transaction.commit()

def rollback_transaction(transaction):
    transaction.rollback()
