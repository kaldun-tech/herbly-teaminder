"""Defines the Tea class"""

class Tea:
    def __init__(self, name, tea_type, steep_time_seconds = 0, steep_temperature_fahrenheit = 0, steep_count = 0):
        if not name:
            raise ValueError("Name cannot be empty")
        if not tea_type:
            raise ValueError("Tea type cannot be empty")
        self.name = name
        self.tea_type = tea_type
        self.steep_time_seconds = steep_time_seconds
        self.steep_temperature_fahrenheit = steep_temperature_fahrenheit
        self.steep_count = steep_count

    def __eq__(self, other):
        if not isinstance(other, Tea):
            return False
        return (
            self.name == other.name and
            self.tea_type == other.tea_type and
            self.steep_time_seconds == other.steep_time_seconds and
            self.steep_temperature_fahrenheit == other.steep_temperature_fahrenheit and
            self.steep_count == other.steep_count
        )

    def __repr__(self):
        return (f'Tea(name="{self.name}", type="{self.tea_type}", steep_time_seconds={self.steep_time_seconds},'
                f'steep_temperature_fahrenheit={self.steep_temperature_fahrenheit}, steep_count={self.steep_count})')

    def to_dict(self):
        return {
            'Name': self.name,
            'Type': self.tea_type,
            'SteepTimeSeconds': self.steep_time_seconds,
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
            tea_dict.get('SteepTimeSeconds', 0),
            tea_dict.get('SteepTemperatureFahrenheit', 0),
            tea_dict.get('SteepCount', 0),
        )
