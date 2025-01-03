import os
import pytest
import boto3
from moto import mock_aws
from app.dao.tea_dao import TeaDao

@pytest.fixture(scope="session")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

# pylint: disable=redefined-outer-name disable=unused-argument
@pytest.fixture(scope="session")
def dynamodb(aws_credentials):
    """Return a mocked DynamoDB resource."""
    with mock_aws():
        yield boto3.resource('dynamodb', region_name=os.environ["AWS_DEFAULT_REGION"])

# pylint: disable=redefined-outer-name disable=unused-argument
@pytest.fixture(scope="function")
def tea_table_setup(dynamodb):
    """Create the DynamoDB table for testing"""
    table = dynamodb.create_table(
        TableName='mock_tea_table',
        KeySchema=[{'AttributeName': 'Name', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'Name', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    table.meta.client.get_waiter('table_exists').wait(TableName='mock_tea_table')
    yield table
    table.delete()

@pytest.fixture(scope="function")
def tea_table(tea_table_setup):
    """Return TeaDao instance with mocked table"""
    return TeaDao('us-east-1', 'mock_tea_table')

@pytest.mark.usefixtures("aws_credentials")
class TestTeaDao:
    def test_get_table(self, tea_table):
        table = tea_table.get_table()
        assert table is not None
        assert table.name == 'mock_tea_table'

    def test_get_all_tea_items(self, tea_table):
        result = tea_table.get_all_tea_items()
        assert result == []

    def test_create_tea_item(self, tea_table):
        tea_item = {
            'Name': 'Earl Grey',
            'Type': 'Black',
            'SteepTimeMinutes': 3,
            'SteepTemperatureFahrenheit': 200
        }
        result = tea_table.create_tea_item(tea_item)
        assert result['Name'] == 'Earl Grey'
        assert result['Type'] == 'Black'
        assert result['SteepTimeMinutes'] == 3
        assert result['SteepTemperatureFahrenheit'] == 200
        assert result['SteepCount'] == 0

        # Verify item was stored correctly
        all_items = tea_table.get_all_tea_items()
        assert len(all_items) == 1
        assert all_items[0]['Name'] == 'Earl Grey'
        assert all_items[0]['SteepTimeMinutes'] == 3

    def test_create_tea_item_minimal(self, tea_table):
        tea_item = {'Name': 'Earl Grey', 'Type': 'Black'}
        result = tea_table.create_tea_item(tea_item)
        assert result['Name'] == 'Earl Grey'
        assert result['Type'] == 'Black'
        assert result['SteepTimeMinutes'] == 0
        assert result['SteepTemperatureFahrenheit'] == 0
        assert result['SteepCount'] == 0

    def test_get_tea_item(self, tea_table):
        tea_item = {
            'Name': 'Green Tea',
            'Type': 'Green',
            'SteepTimeMinutes': 2,
            'SteepTemperatureFahrenheit': 175
        }
        tea_table.create_tea_item(tea_item)
        result = tea_table.get_tea_item('Green Tea')
        assert result['Name'] == 'Green Tea'
        assert result['Type'] == 'Green'
        assert result['SteepTimeMinutes'] == 2
        assert result['SteepTemperatureFahrenheit'] == 175
        assert result['SteepCount'] == 0

    def test_update_tea_item(self, tea_table):
        # Create initial tea
        tea_item = {
            'Name': 'Earl Grey',
            'Type': 'Black',
            'SteepTimeMinutes': 3,
            'SteepTemperatureFahrenheit': 200
        }
        tea_table.create_tea_item(tea_item)

        # Update the tea
        tea_item['Type'] = 'Green'
        tea_item['SteepTimeMinutes'] = 2
        tea_item['SteepTemperatureFahrenheit'] = 175
        tea_table.update_tea_item(tea_item)

        # Verify updates
        result = tea_table.get_tea_item('Earl Grey')
        assert result['Name'] == 'Earl Grey'
        assert result['Type'] == 'Green'
        assert result['SteepTimeMinutes'] == 2
        assert result['SteepTemperatureFahrenheit'] == 175
        assert result['SteepCount'] == 0

    def test_update_tea_item_partial(self, tea_table):
        # Create initial tea
        tea_item = {
            'Name': 'Earl Grey',
            'Type': 'Black',
            'SteepTimeMinutes': 3,
            'SteepTemperatureFahrenheit': 200
        }
        tea_table.create_tea_item(tea_item)

        # Update only some fields
        update_item = {
            'Name': 'Earl Grey',
            'SteepTimeMinutes': 4
        }
        tea_table.update_tea_item(update_item)

        # Verify only specified fields were updated
        result = tea_table.get_tea_item('Earl Grey')
        assert result['Name'] == 'Earl Grey'
        assert result['Type'] == 'Black'  # Unchanged
        assert result['SteepTimeMinutes'] == 4  # Updated
        assert result['SteepTemperatureFahrenheit'] == 200  # Unchanged
        assert result['SteepCount'] == 0  # Unchanged

    def test_increment_steep_count(self, tea_table):
        tea_item = {
            'Name': 'Earl Grey',
            'Type': 'Black',
            'SteepTimeMinutes': 3,
            'SteepCount': 0
        }
        tea_table.create_tea_item(tea_item)

        # Increment multiple times
        for i in range(3):
            result = tea_table.increment_steep_count('Earl Grey')
            assert result['Name'] == 'Earl Grey'
            assert result['Type'] == 'Black'
            assert result['SteepTimeMinutes'] == 3
            assert result['SteepCount'] == i + 1

        # Verify final state matches last returned value
        final_state = tea_table.get_tea_item('Earl Grey')
        assert final_state == result

    def test_clear_steep_count(self, tea_table):
        tea_item = {'Name': 'Earl Grey', 'Type': 'Black', 'SteepCount': 1}
        tea_table.create_tea_item(tea_item)
        tea_table.clear_steep_count('Earl Grey')
        result = tea_table.get_tea_item('Earl Grey')
        assert result['Name'] == 'Earl Grey'
        assert result['Type'] == 'Black'
        assert result['SteepCount'] == 0

    def test_delete_tea_item(self, tea_table):
        tea_item = {'Name': 'Earl Grey', 'Type': 'Black'}
        tea_table.create_tea_item(tea_item)
        tea_table.delete_tea_item('Earl Grey')
        with pytest.raises(KeyError):
            tea_table.get_tea_item('Earl Grey')
