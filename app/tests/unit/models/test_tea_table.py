import pytest
from dynamodb.dao.tea_table import TeaTableDAO

@pytest.fixture
def tea_table():
    return TeaTableDAO()

def test_create_tea_item(tea_table):
    tea_item = {'Name': 'Earl Grey', 'Type': 'Black'}
    result = tea_table.create_tea_item(tea_item)
    assert result['Name'] == 'Earl Grey'
    assert result['Type'] == 'Black'

def test_get_tea_item(tea_table):
    tea_item = {'Name': 'Earl Grey', 'Type': 'Black'}
    tea_table.create_tea_item(tea_item)
    result = tea_table.get_tea_item('Earl Grey')
    assert result['Name'] == 'Earl Grey'
    assert result['Type'] == 'Black'

def test_update_tea_item(tea_table):
    tea_item = {'Name': 'Earl Grey', 'Type': 'Black'}
    tea_table.create_tea_item(tea_item)
    tea_item['Type'] = 'Green'
    tea_table.update_tea_item(tea_item)
    result = tea_table.get_tea_item('Earl Grey')
    assert result['Name'] == 'Earl Grey'
    assert result['Type'] == 'Green'

def test_increment_steep_count(tea_table):
    tea_item = {'Name': 'Earl Grey', 'Type': 'Black', 'SteepCount': 0}
    tea_table.create_tea_item(tea_item)
    tea_table.increment_steep_count('Earl Grey')
    result = tea_table.get_tea_item('Earl Grey')
    assert result['Name'] == 'Earl Grey'
    assert result['Type'] == 'Black'
    assert result['SteepCount'] == 1

def test_delete_tea_item(tea_table):
    tea_item = {'Name': 'Earl Grey', 'Type': 'Black'}
    tea_table.create_tea_item(tea_item)
    tea_table.delete_tea_item('Earl Grey')
    with pytest.raises(KeyError):
        tea_table.get_tea_item('Earl Grey')