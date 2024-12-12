from boto3 import resource

dynamodb = resource('dynamodb')

class TeaTableDAO:
    def __init__(self):
        self.table_name = 'tea_table'

    def get_tea_item(self, name):
        table = dynamodb.Table(self.table_name)
        response = table.get_item(Key={'Name': name})
        return response['Item']

    def create_tea_item(self, tea_item):
        table = dynamodb.Table(self.table_name)
        table.put_item(Item={
            'Name': tea_item['Name'],
            'Type': tea_item['Type'],
            'SteepTimeSeconds': tea_item['SteepTimeSeconds'],
            'SteepTemperatureFahrenheit': tea_item['SteepTemperatureFahrenheit'],
            'SteepCount': tea_item['SteepCount']
        })

    def update_tea_item(self, tea_item):
        table = dynamodb.Table(self.table_name)
        table.update_item(
            Key={'Name': tea_item['Name']},
            UpdateExpression='set #type = :type, #steep_time_seconds = :steep_time_seconds, #steep_temperature_fahrenheit = :steep_temperature_fahrenheit, #steep_count = :steep_count',
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
        table = dynamodb.Table(self.table_name)
        table.update_item(
            Key={'Name': name},
            UpdateExpression='set #steep_count = #steep_count + :increment',
            ExpressionAttributeNames={'#steep_count': 'SteepCount'},
            ExpressionAttributeValues={':increment': 1}
        )

    def delete_tea_item(self, name):
        table = dynamodb.Table(self.table_name)
        table.delete_item(Key={'Name': name})
