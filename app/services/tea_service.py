"""Services for teas"""
class TeaService:
    def __init__(self, tea_table):
        self.tea_table = tea_table

    def get_teas(self):
        return self.tea_table.get_teas()

    def get_tea_item(self, name):
        return self.tea_table.get_tea_item(name)

    def create_tea_item(self, tea_item):
        self.tea_table.create_tea_item(tea_item)

    def update_tea_item(self, tea_item):
        self.tea_table.update_tea_item(tea_item)

    def increment_steep_count(self, name):
        self.tea_table.increment_steep_count(name)

    def delete_tea_item(self, name):
        self.tea_table.delete_tea_item(name)