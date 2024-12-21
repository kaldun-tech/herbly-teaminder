from datetime import datetime
import pytest

from app.utils import helpers

def test_format_date_none():
    date = helpers.format_date(None)
    assert date is None

def test_format_date_normal():
    date = helpers.format_date(datetime(2022, 1, 1))
    assert date == '2022-01-01'

def test_format_date_invalid():
    with pytest.raises(ValueError):
        helpers.format_date('2022-01-01')

def test_validate_email():
    assert helpers.validate_email('a@b.com')

def test_validate_email_invalid():
    assert not helpers.validate_email('fake')
    assert not helpers.validate_email('fake@letter')
    assert not helpers.validate_email('fake.letter')
    assert not helpers.validate_email('fake@letter.')

def test_transform_dynamodb_item_to_dict():
    item = {'id': {"N": 1}, 'name': {"S": "John Doe"}, 'email': {"S": "john@example.com"}}
    transformed_item = helpers.transform_dynamodb_item_to_dict(item)
    assert transformed_item == {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'}

def test_transform_dict_to_dynamodb_item():
    item = {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'}
    transformed_item = helpers.transform_dict_to_dynamodb_item(item)
    assert transformed_item == {'id': {'N': '1'}, 'name': {'S': 'John Doe'}, 'email': {'S': 'john@example.com'}}
