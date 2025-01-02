"""
Class for interacting with the DynamoDB table.
See https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/WorkingWithItems.html
"""
import boto3

class TeaDao:
    def __init__(self, region_name, table_name):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb', region_name)


    def get_table(self):
        """Get database table"""
        return self.dynamodb.Table(self.table_name)


    def get_all_tea_items(self):
        """
        Retrieve all tea items from the DynamoDB table.

        Returns:
            list: A list of dictionaries containing the tea item attributes.
        """
        table = self.get_table()
        response = table.scan()
        return response['Items']


    def get_tea_item(self, name):
        """
        Retrieve a tea item from the DynamoDB table.

        Args:
            name (str): The name of the tea item.

        Returns:
            dict: A dictionary containing the tea item attributes.
        """
        table = self.get_table()
        response = table.get_item(Key={"Name": name})
        return response['Item']


    def create_tea_item(self, tea_item):
        """
        Create a tea item in the DynamoDB table.

        Args:
            tea_item (dict): A dictionary containing the tea item attributes.

        Returns:
            dict: The created item
        """
        table = self.get_table()
        item = {
            "Name": tea_item['Name'],
            "Type": tea_item['Type'],
            "SteepTimeMinutes": tea_item.get('SteepTimeMinutes', 0),
            "SteepTemperatureFahrenheit": tea_item.get('SteepTemperatureFahrenheit', 0),
            "SteepCount": tea_item.get('SteepCount', 0)
        }
        table.put_item(Item=item)
        return item


    def update_tea_item(self, tea_item):
        """
        Update a tea item in the DynamoDB table.
        See https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.UpdateExpressions.html

        Args:
            tea_item (dict): A dictionary containing the tea item attributes:
                - 'Name' (str): The name of the tea.
                - 'Type' (str): The type of the tea.
                - 'SteepTimeMinutes' (int): The steep time in minutes.
                - 'SteepTemperatureFahrenheit' (int): The steep temperature in Fahrenheit.
                - 'SteepCount' (int): The number of times the tea has been steeped.

        The method updates the existing tea item with the provided attributes.
        """
        table = self.get_table()
        update_expr = []
        expr_names = {}
        expr_values = {}

        if 'Type' in tea_item:
            update_expr.append('#type = :type')
            expr_names['#type'] = 'Type'
            expr_values[':type'] = tea_item['Type']

        if 'SteepTimeMinutes' in tea_item:
            update_expr.append('#steep_time_seconds = :steep_time_seconds')
            expr_names['#steep_time_seconds'] = 'SteepTimeMinutes'
            expr_values[':steep_time_seconds'] = tea_item['SteepTimeMinutes']

        if 'SteepTemperatureFahrenheit' in tea_item:
            update_expr.append('#steep_temperature_fahrenheit = :steep_temperature_fahrenheit')
            expr_names['#steep_temperature_fahrenheit'] = 'SteepTemperatureFahrenheit'
            expr_values[':steep_temperature_fahrenheit'] = tea_item['SteepTemperatureFahrenheit']

        if 'SteepCount' in tea_item:
            update_expr.append('#steep_count = :steep_count')
            expr_names['#steep_count'] = 'SteepCount'
            expr_values[':steep_count'] = tea_item['SteepCount']

        if update_expr:
            table.update_item(
                Key={"Name": tea_item['Name']},
                UpdateExpression='set ' + ', '.join(update_expr),
                ExpressionAttributeNames=expr_names,
                ExpressionAttributeValues=expr_values
            )


    def increment_steep_count(self, name):
        """
        Increment the steep count for a tea item in the DynamoDB table.

        Args:
            name (str): The name of the tea item.

        The method increments the existing steep count for the tea item with the
        provided name.
        """
        table = self.get_table()
        table.update_item(
            Key={"Name": name},
            UpdateExpression='set #steep_count = #steep_count + :increment',
            ExpressionAttributeNames={'#steep_count': 'SteepCount'},
            ExpressionAttributeValues={':increment': 1}
        )


    def clear_steep_count(self, name):
        """
        Clear the steep count for a tea item in the DynamoDB table.

        Args:
            name (str): The name of the tea item.

        The method sets the existing steep count for the tea item with the
        provided name to 0.
        """
        table = self.get_table()
        table.update_item(
            Key={"Name": name},
            UpdateExpression='set #steep_count = :clear',
            ExpressionAttributeNames={'#steep_count': 'SteepCount'},
            ExpressionAttributeValues={':clear': 0}
        )


    def delete_tea_item(self, name):
        """
        Delete a tea item from the DynamoDB table.

        Args:
            name (str): The name of the tea item.

        The method deletes the existing tea item with the provided name from the
        DynamoDB table.
        """
        table = self.get_table()
        table.delete_item(Key={"Name": name})
