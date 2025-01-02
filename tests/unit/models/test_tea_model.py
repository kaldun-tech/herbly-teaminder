import pytest
from app.models.tea import Tea

class TestTeaModel:
    def test_init(self):
        tea = Tea("Earl Grey", "Black")
        assert tea.name == "Earl Grey"
        assert tea.tea_type == "Black"
        assert tea.steep_time_seconds == 0
        assert tea.steep_temperature_fahrenheit == 0
        assert tea.steep_count == 0

    def test_init_with_steep_time(self):
        tea = Tea("Earl Grey", "Black", steep_time_seconds=3)
        assert tea.name == "Earl Grey"
        assert tea.tea_type == "Black"
        assert tea.steep_time_seconds == 3
        assert tea.steep_temperature_fahrenheit == 0
        assert tea.steep_count == 0

    def test_init_with_steep_temperature(self):
        tea = Tea("Earl Grey", "Black", steep_temperature_fahrenheit=200)
        assert tea.name == "Earl Grey"
        assert tea.tea_type == "Black"
        assert tea.steep_time_seconds == 0
        assert tea.steep_temperature_fahrenheit == 200
        assert tea.steep_count == 0

    def test_init_with_steep_count(self):
        tea = Tea("Earl Grey", "Black", steep_count=2)
        assert tea.name == "Earl Grey"
        assert tea.tea_type == "Black"
        assert tea.steep_time_seconds == 0
        assert tea.steep_temperature_fahrenheit == 0
        assert tea.steep_count == 2

    def test_repr(self):
        tea = Tea("Earl Grey", "Black")
        assert repr(tea) == ('Tea(name="Earl Grey", type="Black", steep_time_seconds=0,'
                             'steep_temperature_fahrenheit=0, steep_count=0)')

    def test_eq(self):
        tea1 = Tea("Earl Grey", "Black")
        tea2 = Tea("Earl Grey", "Black")
        assert tea1 == tea2

    def test_to_dict(self):
        tea = Tea("Earl Grey", "Black")
        expected_dict = {
            "Name": "Earl Grey",
            "Type": "Black",
            "SteepTimeMinutes": 0,
            "SteepTemperatureFahrenheit": 0,
            "SteepCount": 0
        }
        assert tea.to_dict() == expected_dict

    def test_from_dict(self):
        tea_dict = {
            "Name": "Earl Grey",
            "Type": "Black",
            "SteepTimeMinutes": 3,
            "SteepTemperatureFahrenheit": 200,
            "SteepCount": 2
        }
        tea = Tea.from_dict(tea_dict)
        assert tea.name == "Earl Grey"
        assert tea.tea_type == "Black"
        assert tea.steep_time_seconds == 3
        assert tea.steep_temperature_fahrenheit == 200
        assert tea.steep_count == 2

    def test_from_dict_invalid_name(self):
        with pytest.raises(ValueError):
            Tea.from_dict({"Type": "Black"})

    def test_from_dict_invalid_type(self):
        with pytest.raises(ValueError):
            Tea.from_dict({"Name": "Earl Grey"})
