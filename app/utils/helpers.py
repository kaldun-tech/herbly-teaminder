"""Helper functions"""

import re
from datetime import datetime

def format_date(date):
    if date is None:
        return None
    if isinstance(date, datetime):
        return date.strftime('%Y-%m-%d')
    raise ValueError("Invalid date object")

def validate_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(pattern, email):
        return True
    return False

def transform_dict_to_dynamodb_item(item):
    """Transforms a simple dictionary into a DynamoDB item"""
    transformed_item = {}
    for key, value in item.items():
        if isinstance(value, str):
            transformed_item[key] = {"S": value}
        elif isinstance(value, int):
            transformed_item[key] = {"N": str(value)}
    return transformed_item

def transform_dynamodb_item_to_dict(item):
    """Transforms a DynamoDB item into a simple dictionary"""
    transformed_item = {}
    for key, value in item.items():
        if "S" in value:
            transformed_item[key] = value["S"]
        elif "N" in value:
            transformed_item[key] = int(value["N"])
    return transformed_item
