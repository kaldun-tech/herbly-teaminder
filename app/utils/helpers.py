# Helper functions
def format_date(date):
    return date.strftime('%Y-%m-%d')

def validate_email(email):
    # email validation logic here
    pass

def transform_item(item):
    """Transforms a simple dictionary into a DynamoDB item"""
    transformed_item = {}
    for key, value in item.items():
        if isinstance(value, str):
            transformed_item[key] = {"S": value}
        elif isinstance(value, int):
            transformed_item[key] = {"N": str(value)}
    return transformed_item