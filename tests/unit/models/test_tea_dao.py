import pytest
import boto3
import os
from app.dao.tea_dao import TeaDao
from moto import mock_aws

@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture(scope="function")
def dynamodb(aws_credentials):
    """Return a mocked DynamoDB resource."""
    with mock_aws():
        yield boto3.resource('dynamodb', region_name=os.environ["AWS_DEFAULT_REGION"])

@pytest.fixture(scope="function")
def mocked_aws(aws_credentials):
    """
    Mock all AWS interactions
    Requires you to create your own boto3 clients
    """
    with mock_aws():
        yield

table_name = 'mock_tea_table'
region_name = 'us-east-1'

@pytest.fixture
def tea_table():
    return TeaDao(region_name, table_name)

def test_get_dynamodb_table(tea_table):
    table = tea_table.get_table()
    assert table is not None
    assert table.name == table_name

def test_get_all_tea_items(tea_table):
    result = tea_table.get_all_tea_items()
    assert result == []

def test_create_tea_item(tea_table):
    tea_item = {'Name': 'Earl Grey', 'Type': 'Black'}
    result = tea_table.create_tea_item(tea_item)
    assert result['Name'] == {"S": 'Earl Grey'}
    assert result['Type'] == {"S": "Black"}
    assert result['SteepTimeSeconds'] == {"N": 0}
    assert result['SteepTemperatureFahrenheit'] == {"N": 0}
    assert result['SteepCount'] == {"N": 0}
    all_items = tea_table.get_all_tea_items()
    assert len(all_items) == 1
    assert all_items[0]['Name'] == {"S": 'Earl Grey'}

def test_get_tea_item(tea_table):
    tea_item = {'Name': 'Earl Grey', 'Type': 'Black'}
    tea_table.create_tea_item(tea_item)
    result = tea_table.get_tea_item('Earl Grey')
    assert result['Name'] == {"S": 'Earl Grey'}
    assert result['Type'] == {"S": "Black"}

def test_update_tea_item(tea_table):
    tea_item = {'Name': 'Earl Grey', 'Type': 'Black'}
    tea_table.create_tea_item(tea_item)
    tea_item['Type'] = 'Green'
    tea_item['SteepTemperatureFahrenheit'] = 180
    tea_table.update_tea_item(tea_item)
    result = tea_table.get_tea_item('Earl Grey')
    assert result['Name'] == {"S": 'Earl Grey'}
    assert result['Type'] == {"S": "Black"}
    assert result['SteepTemperatureFahrenheit'] == {"N": 180}

def test_increment_steep_count(tea_table):
    tea_item = {'Name': 'Earl Grey', 'Type': 'Black', 'SteepCount': 0}
    tea_table.create_tea_item(tea_item)
    tea_table.increment_steep_count('Earl Grey')
    result = tea_table.get_tea_item('Earl Grey')
    assert result['Name'] == {"S": 'Earl Grey'}
    assert result['Type'] == {"S": "Black"}
    assert result['SteepCount'] == {"N": 1}

def test_delete_tea_item(tea_table):
    tea_item = {'Name': 'Earl Grey', 'Type': 'Black'}
    tea_table.create_tea_item(tea_item)
    tea_table.delete_tea_item('Earl Grey')
    with pytest.raises(KeyError):
        tea_table.get_tea_item('Earl Grey')