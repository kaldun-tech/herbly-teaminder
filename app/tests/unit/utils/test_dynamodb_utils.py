import pytest
import boto3
from moto import mock_dynamodb
from dynamodb.services.dynamodb_utils import create_transaction, commit_transaction, rollback_transaction

@pytest.fixture
def dynamodb():
    with mock_dynamodb():
        yield boto3.client('dynamodb')

def test_create_transaction():
    table_name = 'my_table'
    transaction_id = create_transaction( table_name)
    assert transaction_id is not None

def test_commit_transaction(dynamodb):
    table_name = 'my_table'
    transaction_id = create_transaction(dynamodb, table_name)
    commit_transaction(dynamodb, table_name, transaction_id)
    # Verify that the transaction was committed successfully

def test_rollback_transaction(dynamodb):
    table_name = 'my_table'
    transaction_id = create_transaction(dynamodb, table_name)
    rollback_transaction(dynamodb, table_name, transaction_id)
    # Verify that the transaction was rolled back successfully