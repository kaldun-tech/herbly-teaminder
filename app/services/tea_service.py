from app.dao.tea_dao import TeaDao

class TeaService:
    """Services for teas"""
    def __init__(self, tea_dao: TeaDao):
        self.tea_table = tea_dao

    def get_teas(self):
        return self.tea_table.get_all_tea_items()

    def get_tea_item(self, name):
        return self.tea_table.get_tea_item(name)

    def create_tea_item(self, tea_item):
        self.tea_table.create_tea_item(tea_item)

    def update_tea_item(self, tea_item):
        self.tea_table.update_tea_item(tea_item)

    def increment_steep_count(self, name):
        self.tea_table.increment_steep_count(name)

    def clear_steep_count(self, name):
        self.tea_table.clear_steep_count(name)

    def delete_tea_item(self, name):
        self.tea_table.delete_tea_item(name)
