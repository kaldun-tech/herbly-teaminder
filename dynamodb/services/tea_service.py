"""Services for teas"""
from services.dynamodb_utils import create_transaction, commit_transaction, rollback_transaction
import boto3

dynamodb = boto3.resource('dynamodb')

class TeaService:
    def __init__(self):
        self.table_name = 'tea_table'

    def get_tea(self, tea_id):
        """Get tea from database"""
        pass

    def create_tea(self, tea_item):
        """Create a new tea in the database"""
        transaction = create_transaction(self.table_name)
        try:
            # Create the tea item in the table
            table = dynamodb.Table(self.table_name)
            table.put_item(Item=tea_item)
            commit_transaction(transaction)
        except Exception as e:
            rollback_transaction(transaction)
            raise e

    def update_tea(self, tea_id, tea_data):
        """Update an existing tea in the database"""
        pass