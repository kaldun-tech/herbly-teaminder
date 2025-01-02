"""Defines the Tea class"""

class Tea:
    # pylint: disable=too-many-arguments
    def __init__(self, name, tea_type, steep_time_minutes = 0, steep_temperature_fahrenheit = 0, steep_count = 0):
        if not name:
            raise ValueError("Name cannot be empty")
        if not tea_type:
            raise ValueError("Tea type cannot be empty")
        self.name = name
        self.tea_type = tea_type
        self.steep_time_minutes = steep_time_minutes
        self.steep_temperature_fahrenheit = steep_temperature_fahrenheit
        self.steep_count = steep_count

    def __eq__(self, other):
        if not isinstance(other, Tea):
            return False
        return (
            self.name == other.name and
            self.tea_type == other.tea_type and
            self.steep_time_minutes == other.steep_time_minutes and
            self.steep_temperature_fahrenheit == other.steep_temperature_fahrenheit and
            self.steep_count == other.steep_count
        )

    def __repr__(self):
        return (f'Tea(name="{self.name}", tea_type="{self.tea_type}", steep_time_minutes={self.steep_time_minutes},'
                f' steep_temperature_fahrenheit={self.steep_temperature_fahrenheit}, steep_count={self.steep_count})')

    def to_dict(self):
        return {
            'Name': self.name,
            'Type': self.tea_type,
            'SteepTimeMinutes': self.steep_time_minutes,
            'SteepTemperatureFahrenheit': self.steep_temperature_fahrenheit,
            'SteepCount': self.steep_count
        }

    @staticmethod
    def from_dict(tea_dict):
        if not tea_dict:
            raise ValueError("Tea dictionary cannot be empty")
        if not tea_dict.get("Name"):
            raise ValueError("Name cannot be empty")
        if not tea_dict.get("Type"):
            raise ValueError("Type cannot be empty")
        return Tea(
            tea_dict.get('Name'),
            tea_dict.get('Type'),
            tea_dict.get('SteepTimeMinutes', 0),
            tea_dict.get('SteepTemperatureFahrenheit', 0),
            tea_dict.get('SteepCount', 0),
        )
