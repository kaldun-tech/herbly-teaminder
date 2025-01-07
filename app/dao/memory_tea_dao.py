"""In-memory implementation of TeaDao for development"""

class MemoryTeaDao:
    """In-memory storage for teas"""
    def __init__(self):
        self.teas = {}

    def get_all_tea_items(self):
        """Get all teas"""
        return list(self.teas.values())

    def get_tea_item(self, name):
        """Get a tea by name"""
        if name not in self.teas:
            raise KeyError(f"Tea '{name}' not found")
        return self.teas[name]

    def create_tea_item(self, tea_item):
        """Create a new tea"""
        name = tea_item["Name"]
        if name in self.teas:
            raise ValueError(f"Tea '{name}' already exists")
        self.teas[name] = tea_item
        return tea_item

    def update_tea_item(self, name, tea_item):
        """Update a tea"""
        if name not in self.teas:
            raise KeyError(f"Tea '{name}' not found")
        self.teas[name] = tea_item
        return tea_item

    def increment_steep_count(self, name):
        """Increment steep count"""
        if name not in self.teas:
            raise KeyError(f"Tea '{name}' not found")
        tea = self.teas[name]
        tea["SteepCount"] = tea.get("SteepCount", 0) + 1
        return tea

    def clear_steep_count(self, name):
        """Clear steep count"""
        if name not in self.teas:
            raise KeyError(f"Tea '{name}' not found")
        tea = self.teas[name]
        tea["SteepCount"] = 0
        return tea

    def delete_tea_item(self, name):
        """Delete a tea"""
        if name not in self.teas:
            raise KeyError(f"Tea '{name}' not found")
        del self.teas[name]
