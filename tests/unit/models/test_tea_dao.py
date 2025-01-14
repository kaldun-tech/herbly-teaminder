"""Tests for TeaDao"""
import os
import pytest
from moto import mock_dynamodb
from app.dao.tea_dao import TeaDao

@pytest.fixture(scope="function", autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    yield
    os.environ.pop("AWS_ACCESS_KEY_ID", None)
    os.environ.pop("AWS_SECRET_ACCESS_KEY", None)
    os.environ.pop("AWS_DEFAULT_REGION", None)
    os.environ.pop("AWS_SECURITY_TOKEN", None)
    os.environ.pop("AWS_SESSION_TOKEN", None)

@pytest.fixture(scope="function")
def dynamodb():
    """Create a mock DynamoDB resource."""
    with mock_dynamodb():
        import boto3
        yield boto3.resource("dynamodb", region_name="us-east-1")

@pytest.fixture(scope="function")
def tea_table_setup(dynamodb):
    """Create the DynamoDB table for testing."""
    table = dynamodb.create_table(
        TableName="Tea",
        KeySchema=[
            {"AttributeName": "user_id", "KeyType": "HASH"},
            {"AttributeName": "tea_id", "KeyType": "RANGE"}
        ],
        AttributeDefinitions=[
            {"AttributeName": "user_id", "AttributeType": "S"},
            {"AttributeName": "tea_id", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST"
    )
    table.meta.client.get_waiter("table_exists").wait(TableName="Tea")
    yield table
    table.delete()

@pytest.fixture(scope="function")
def tea_table(tea_table_setup):
    """Return TeaDao instance with mocked table."""
    return TeaDao(region_name="us-east-1", table_name="Tea")

@pytest.mark.usefixtures("aws_credentials")
class TestTeaDao:
    """Test cases for Tea model"""
    
    def test_get_table(self, tea_table):
        """Test getting the DynamoDB table"""
        table = tea_table.get_table()
        assert table.name == "Tea"

    def test_get_all_tea_items(self, tea_table):
        """Test getting all tea items"""
        user_id = "test_user"
        tea_table.create_tea_item(user_id, {
            'Name': 'Earl Grey',
            'Type': 'Black'
        })
        tea_table.create_tea_item(user_id, {
            'Name': 'Green Tea',
            'Type': 'Green'
        })
        items = tea_table.get_all_tea_items(user_id)
        assert len(items) == 2
        assert any(item['Name'] == 'Earl Grey' for item in items)
        assert any(item['Name'] == 'Green Tea' for item in items)

    def test_create_tea_item(self, tea_table):
        """Test creating a tea item"""
        user_id = "test_user"
        tea_item = {
            'Name': 'Earl Grey',
            'Type': 'Black',
            'SteepTimeMinutes': 3,
            'SteepTemperatureFahrenheit': 200
        }
        result = tea_table.create_tea_item(user_id, tea_item)
        assert result['Name'] == 'Earl Grey'
        assert result['Type'] == 'Black'
        assert result['SteepTimeMinutes'] == 3
        assert result['SteepTemperatureFahrenheit'] == 200
        assert result['SteepCount'] == 0
        assert result['user_id'] == user_id
        assert 'tea_id' in result

    def test_create_tea_item_minimal(self, tea_table):
        """Test creating a tea item with minimal fields"""
        user_id = "test_user"
        tea_item = {'Name': 'Earl Grey', 'Type': 'Black'}
        result = tea_table.create_tea_item(user_id, tea_item)
        assert result['Name'] == 'Earl Grey'
        assert result['Type'] == 'Black'
        assert result['SteepTimeMinutes'] == 0
        assert result['SteepTemperatureFahrenheit'] == 0
        assert result['SteepCount'] == 0
        assert result['user_id'] == user_id
        assert 'tea_id' in result

    def test_get_tea_item(self, tea_table):
        """Test getting a tea item"""
        user_id = "test_user"
        tea_item = {
            'Name': 'Green Tea',
            'Type': 'Green',
            'SteepTimeMinutes': 2,
            'SteepTemperatureFahrenheit': 175
        }
        created = tea_table.create_tea_item(user_id, tea_item)
        result = tea_table.get_tea_item(user_id, created['tea_id'])
        assert result['Name'] == 'Green Tea'
        assert result['Type'] == 'Green'
        assert result['SteepTimeMinutes'] == 2
        assert result['SteepTemperatureFahrenheit'] == 175

    def test_update_tea_item(self, tea_table):
        """Test updating a tea item"""
        user_id = "test_user"
        # Create initial tea
        tea_item = {
            'Name': 'Earl Grey',
            'Type': 'Black',
            'SteepTimeMinutes': 3,
            'SteepTemperatureFahrenheit': 200
        }
        created = tea_table.create_tea_item(user_id, tea_item)
        tea_id = created['tea_id']

        # Update the tea
        update_item = {
            'Type': 'Black Tea',
            'SteepTimeMinutes': 4
        }
        tea_table.update_tea_item(user_id, tea_id, update_item)

        # Verify the update
        updated = tea_table.get_tea_item(user_id, tea_id)
        assert updated['Type'] == 'Black Tea'
        assert updated['SteepTimeMinutes'] == 4
        assert updated['SteepTemperatureFahrenheit'] == 200  # Unchanged

    def test_update_tea_item_partial(self, tea_table):
        """Test partial update of a tea item"""
        user_id = "test_user"
        # Create initial tea
        tea_item = {
            'Name': 'Earl Grey',
            'Type': 'Black',
            'SteepTimeMinutes': 3,
            'SteepTemperatureFahrenheit': 200
        }
        created = tea_table.create_tea_item(user_id, tea_item)
        tea_id = created['tea_id']

        # Update only the type
        tea_table.update_tea_item(user_id, tea_id, {'Type': 'Black Tea'})

        # Verify the update
        updated = tea_table.get_tea_item(user_id, tea_id)
        assert updated['Type'] == 'Black Tea'
        assert updated['SteepTimeMinutes'] == 3  # Unchanged
        assert updated['SteepTemperatureFahrenheit'] == 200  # Unchanged

    def test_increment_steep_count(self, tea_table):
        """Test incrementing steep count"""
        user_id = "test_user"
        tea_item = {
            'Name': 'Earl Grey',
            'Type': 'Black',
            'SteepTimeMinutes': 3,
            'SteepCount': 0
        }
        created = tea_table.create_tea_item(user_id, tea_item)
        tea_id = created['tea_id']

        tea_table.increment_steep_count(user_id, tea_id)
        updated = tea_table.get_tea_item(user_id, tea_id)
        assert updated['SteepCount'] == 1

    def test_clear_steep_count(self, tea_table):
        """Test clearing steep count"""
        user_id = "test_user"
        tea_item = {'Name': 'Earl Grey', 'Type': 'Black', 'SteepCount': 1}
        created = tea_table.create_tea_item(user_id, tea_item)
        tea_id = created['tea_id']

        tea_table.clear_steep_count(user_id, tea_id)
        updated = tea_table.get_tea_item(user_id, tea_id)
        assert updated['SteepCount'] == 0

    def test_delete_tea_item(self, tea_table):
        """Test deleting a tea item"""
        user_id = "test_user"
        tea_item = {'Name': 'Earl Grey', 'Type': 'Black'}
        created = tea_table.create_tea_item(user_id, tea_item)
        tea_id = created['tea_id']

        tea_table.delete_tea_item(user_id, tea_id)
        result = tea_table.get_tea_item(user_id, tea_id)
        assert result is None
