"""
Class for interacting with the DynamoDB table.
See https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/WorkingWithItems.html
"""
import boto3
import uuid

class TeaDao:
    def __init__(self, region_name, table_name):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb', region_name)

    def get_table(self):
        """Get database table"""
        return self.dynamodb.Table(self.table_name)

    def get_all_tea_items(self, user_id):
        """
        Retrieve all tea items for a user from the DynamoDB table.

        Args:
            user_id (str): The ID of the user.

        Returns:
            list: A list of dictionaries containing the tea item attributes.
        """
        table = self.get_table()
        response = table.query(
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        return response['Items']

    def get_tea_item(self, user_id, tea_id):
        """
        Retrieve a tea item from the DynamoDB table.

        Args:
            user_id (str): The ID of the user.
            tea_id (str): The ID of the tea item.

        Returns:
            dict: A dictionary containing the tea item attributes.
        """
        table = self.get_table()
        response = table.get_item(Key={"user_id": user_id, "tea_id": tea_id})
        return response.get('Item')

    def create_tea_item(self, user_id, tea_item):
        """
        Create a tea item in the DynamoDB table.

        Args:
            user_id (str): The ID of the user.
            tea_item (dict): A dictionary containing the tea item attributes.

        Returns:
            dict: The created item
        """
        table = self.get_table()
        tea_id = str(uuid.uuid4())
        item = {
            "user_id": user_id,
            "tea_id": tea_id,
            "Name": tea_item['Name'],
            "Type": tea_item['Type'],
            "SteepTimeMinutes": tea_item.get('SteepTimeMinutes', 0),
            "SteepTemperatureFahrenheit": tea_item.get('SteepTemperatureFahrenheit', 0),
            "SteepCount": tea_item.get('SteepCount', 0)
        }
        table.put_item(Item=item)
        return item

    def update_tea_item(self, user_id, tea_id, tea_item):
        """
        Update a tea item in the DynamoDB table.
        See https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.UpdateExpressions.html

        Args:
            user_id (str): The ID of the user.
            tea_id (str): The ID of the tea item.
            tea_item (dict): A dictionary containing the tea item attributes to update.
        """
        table = self.get_table()
        update_expr = []
        expr_names = {}
        expr_values = {}

        if 'Type' in tea_item:
            update_expr.append('#type = :type')
            expr_names['#type'] = 'Type'
            expr_values[':type'] = tea_item['Type']

        if 'Name' in tea_item:
            update_expr.append('#name = :name')
            expr_names['#name'] = 'Name'
            expr_values[':name'] = tea_item['Name']

        if 'SteepTimeMinutes' in tea_item:
            update_expr.append('#steep_time_minutes = :steep_time_minutes')
            expr_names['#steep_time_minutes'] = 'SteepTimeMinutes'
            expr_values[':steep_time_minutes'] = tea_item['SteepTimeMinutes']

        if 'SteepTemperatureFahrenheit' in tea_item:
            update_expr.append('#steep_temperature_fahrenheit = :steep_temperature_fahrenheit')
            expr_names['#steep_temperature_fahrenheit'] = 'SteepTemperatureFahrenheit'
            expr_values[':steep_temperature_fahrenheit'] = tea_item['SteepTemperatureFahrenheit']

        if update_expr:
            table.update_item(
                Key={"user_id": user_id, "tea_id": tea_id},
                UpdateExpression="SET " + ", ".join(update_expr),
                ExpressionAttributeNames=expr_names,
                ExpressionAttributeValues=expr_values
            )

    def increment_steep_count(self, user_id, tea_id):
        """
        Increment the steep count for a tea item.

        Args:
            user_id (str): The ID of the user.
            tea_id (str): The ID of the tea item.
        """
        table = self.get_table()
        table.update_item(
            Key={"user_id": user_id, "tea_id": tea_id},
            UpdateExpression="SET SteepCount = SteepCount + :inc",
            ExpressionAttributeValues={":inc": 1}
        )

    def clear_steep_count(self, user_id, tea_id):
        """
        Reset the steep count for a tea item to 0.

        Args:
            user_id (str): The ID of the user.
            tea_id (str): The ID of the tea item.
        """
        table = self.get_table()
        table.update_item(
            Key={"user_id": user_id, "tea_id": tea_id},
            UpdateExpression="SET SteepCount = :zero",
            ExpressionAttributeValues={":zero": 0}
        )

    def delete_tea_item(self, user_id, tea_id):
        """
        Delete a tea item from the DynamoDB table.

        Args:
            user_id (str): The ID of the user.
            tea_id (str): The ID of the tea item.
        """
        table = self.get_table()
        table.delete_item(Key={"user_id": user_id, "tea_id": tea_id})
