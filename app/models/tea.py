from dataclasses import dataclass

@dataclass
class Tea:
    id: int
    name: str
    type: str
    steep_time_seconds: int
    steep_temperature_fahrenheit: int
    steep_count: int