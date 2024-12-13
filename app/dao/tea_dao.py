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
        return self.dynamodb.Table(self.table_name)

    def get_tea_item(self, name):
        """
        Retrieve a tea item from the DynamoDB table.

        Args:
            name (str): The name of the tea item.

        Returns:
            dict: A dictionary containing the tea item attributes.
        """
        table = self.get_table()
        response = table.get_item(Key={"Name":{"S":name}})
        return response['Item']


    def create_tea_item(self, tea_item):
        """
        Create a tea item in the DynamoDB table.

        Args:
            tea_item (dict): A dictionary containing the tea item attributes.

        Returns:
            None
        """
        table = self.get_table()
        table.put_item(Item={
            "Name": {"S": tea_item['Name']},
            "Type": {"S": tea_item['Type']},
            "SteepTimeSeconds": {"N": tea_item['SteepTimeSeconds']},
            "SteepTemperatureFahrenheit": {"N": tea_item['SteepTemperatureFahrenheit']},
            "SteepCount": {"N": tea_item['SteepCount']}
        })

    def update_tea_item(self, tea_item):
        """
        Update a tea item in the DynamoDB table.
        See https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.UpdateExpressions.html

        Args:
            tea_item (dict): A dictionary containing the tea item attributes:
                - 'Name' (str): The name of the tea.
                - 'Type' (str): The type of the tea.
                - 'SteepTimeSeconds' (int): The steep time in seconds.
                - 'SteepTemperatureFahrenheit' (int): The steep temperature in Fahrenheit.
                - 'SteepCount' (int): The number of times the tea has been steeped.

        The method updates the existing tea item with the provided attributes.
        """
        table = self.get_table()
        table.update_item(
            Key={'Name': {"S": tea_item['Name']}},
            UpdateExpression='set #type = :type, #steep_time_seconds = :steep_time_seconds, '
                             '#steep_temperature_fahrenheit = :steep_temperature_fahrenheit, '
                             '#steep_count = :steep_count',
            ExpressionAttributeNames={
                '#type': 'Type',
                '#steep_time_seconds': 'SteepTimeSeconds',
                '#steep_temperature_fahrenheit': 'SteepTemperatureFahrenheit',
                '#steep_count': 'SteepCount'
            },
            ExpressionAttributeValues={
                ':type': tea_item['Type'],
                ':steep_time_seconds': tea_item['SteepTimeSeconds'],
                ':steep_temperature_fahrenheit': tea_item['SteepTemperatureFahrenheit'],
                ':steep_count': tea_item['SteepCount']
            }
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
            Key={'Name': name},
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
            Key={'Name': name},
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
        table.delete_item(Key={'Name': name})
