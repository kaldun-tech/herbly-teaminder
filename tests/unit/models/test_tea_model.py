import pytest
from app.models.tea import Tea

class TestTeaModel:
    def test_init(self):
        tea = Tea("Earl Grey", "Black")
        assert tea.name == "Earl Grey"
        assert tea.tea_type == "Black"
        assert tea.steep_time_minutes == 0
        assert tea.steep_temperature_fahrenheit == 0
        assert tea.steep_count == 0

    def test_init_with_steep_time(self):
        tea = Tea("Earl Grey", "Black", steep_time_minutes=3)
        assert tea.name == "Earl Grey"
        assert tea.tea_type == "Black"
        assert tea.steep_time_minutes == 3
        assert tea.steep_temperature_fahrenheit == 0
        assert tea.steep_count == 0

    def test_init_with_steep_temperature(self):
        tea = Tea("Earl Grey", "Black", steep_temperature_fahrenheit=200)
        assert tea.name == "Earl Grey"
        assert tea.tea_type == "Black"
        assert tea.steep_time_minutes == 0
        assert tea.steep_temperature_fahrenheit == 200
        assert tea.steep_count == 0

    def test_init_with_steep_count(self):
        tea = Tea("Earl Grey", "Black", steep_count=2)
        assert tea.name == "Earl Grey"
        assert tea.tea_type == "Black"
        assert tea.steep_time_minutes == 0
        assert tea.steep_temperature_fahrenheit == 0
        assert tea.steep_count == 2

    def test_init_with_all_params(self):
        tea = Tea("Green Tea", "Green", steep_time_minutes=2,
                 steep_temperature_fahrenheit=175, steep_count=1)
        assert tea.name == "Green Tea"
        assert tea.tea_type == "Green"
        assert tea.steep_time_minutes == 2
        assert tea.steep_temperature_fahrenheit == 175
        assert tea.steep_count == 1

    def test_repr(self):
        tea = Tea("Earl Grey", "Black", steep_time_minutes=3, steep_temperature_fahrenheit=200)
        expected = 'Tea(name="Earl Grey", tea_type="Black", steep_time_minutes=3, steep_temperature_fahrenheit=200, steep_count=0)'
        assert repr(tea) == expected

    def test_eq(self):
        tea1 = Tea("Earl Grey", "Black", steep_time_minutes=3)
        tea2 = Tea("Earl Grey", "Black", steep_time_minutes=3)
        assert tea1 == tea2

    def test_eq_different_times(self):
        tea1 = Tea("Earl Grey", "Black", steep_time_minutes=3)
        tea2 = Tea("Earl Grey", "Black", steep_time_minutes=4)
        assert tea1 != tea2

    def test_to_dict(self):
        tea = Tea("Earl Grey", "Black", steep_time_minutes=3)
        expected_dict = {
            "Name": "Earl Grey",
            "Type": "Black",
            "SteepTimeMinutes": 3,
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
        assert tea.steep_time_minutes == 3
        assert tea.steep_temperature_fahrenheit == 200
        assert tea.steep_count == 2

    def test_from_dict_missing_fields(self):
        tea_dict = {
            "Name": "Earl Grey",
            "Type": "Black"
        }
        tea = Tea.from_dict(tea_dict)
        assert tea.name == "Earl Grey"
        assert tea.tea_type == "Black"
        assert tea.steep_time_minutes == 0
        assert tea.steep_temperature_fahrenheit == 0
        assert tea.steep_count == 0

    def test_from_dict_invalid_name(self):
        with pytest.raises(ValueError):
            Tea.from_dict({"Type": "Black"})

    def test_from_dict_invalid_type(self):
        with pytest.raises(ValueError):
            Tea.from_dict({"Name": "Earl Grey"})
