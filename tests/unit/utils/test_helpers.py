import unittest
from datetime import datetime

from app.utils import helpers

class TestHelpers(unittest.TestCase):
    def test_format_date_none(self):
        date = helpers.format_date(None)
        self.assertEqual(date, None)

    def test_format_date_normal(self):
        date = helpers.format_date(datetime(2022, 1, 1))
        self.assertEqual(date, '2022-01-01')

    def test_format_date_invalid(self):
        with self.assertRaises(ValueError):
            helpers.format_date('2022-01-01')

    def test_validate_email(self):
        self.assertTrue(helpers.validate_email('a@b.com'))

    def test_validate_email_invalid(self):
        self.assertFalse(helpers.validate_email('fakenews'))
        self.assertFalse(helpers.validate_email('fakenews@letter'))
        self.assertFalse(helpers.validate_email('fakenews.com'))

    def test_transform_dynamodb_item_to_dict(self):
        item = {'id': {"N": 1}, 'name': {"S": "John Doe"}, 'email': {"S": "john@example.com"}}
        transformed_item = helpers.transform_dynamodb_item_to_dict(item)
        self.assertEqual(transformed_item, {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'})

    def test_transform_dict_to_dynamodb_item(self):
        item = {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'}
        transformed_item = helpers.transform_dict_to_dynamodb_item(item)
        self.assertEqual(transformed_item, {'id': {'N': '1'}, 'name': {'S': 'John Doe'}, 'email': {'S': 'john@example.com'}})
