"""
Unit tests for the utility functions module (src/utils.py).

Tests metric conversion functions, data validation, and logging utilities.
"""

import pytest
import logging
from hypothesis import given, strategies as st
from src.utils import (
    setup_logging,
    fahrenheit_to_celsius,
    celsius_to_fahrenheit,
    mph_to_kmh,
    kmh_to_mph,
    validate_temperature,
    validate_wind_speed,
    validate_humidity,
    validate_pressure,
    validate_precipitation,
    validate_uv_index,
    validate_pollen_concentration,
    validate_weather_data,
    validate_pollen_data,
)


class TestSetupLogging:
    """Test logging setup function."""
    
    def test_setup_logging_returns_logger(self):
        """Test that setup_logging returns a logger instance."""
        logger = setup_logging("test_logger")
        assert isinstance(logger, logging.Logger)
    
    def test_setup_logging_sets_level(self):
        """Test that setup_logging sets the correct logging level."""
        logger = setup_logging("test_logger_level", level=logging.DEBUG)
        assert logger.level == logging.DEBUG


class TestFahrenheitToCelsius:
    """Test Fahrenheit to Celsius conversion."""
    
    def test_freezing_point(self):
        """Test conversion of freezing point (32°F = 0°C)."""
        result = fahrenheit_to_celsius(32)
        assert abs(result - 0) < 0.01
    
    def test_boiling_point(self):
        """Test conversion of boiling point (212°F = 100°C)."""
        result = fahrenheit_to_celsius(212)
        assert abs(result - 100) < 0.01
    
    def test_room_temperature(self):
        """Test conversion of room temperature (72°F ≈ 22.2°C)."""
        result = fahrenheit_to_celsius(72)
        assert abs(result - 22.22) < 0.01
    
    def test_negative_temperature(self):
        """Test conversion of negative temperature (-40°F = -40°C)."""
        result = fahrenheit_to_celsius(-40)
        assert abs(result - (-40)) < 0.01
    
    def test_type_error_on_string(self):
        """Test that TypeError is raised for string input."""
        with pytest.raises(TypeError):
            fahrenheit_to_celsius("32")
    
    def test_type_error_on_none(self):
        """Test that TypeError is raised for None input."""
        with pytest.raises(TypeError):
            fahrenheit_to_celsius(None)


class TestCelsiusToFahrenheit:
    """Test Celsius to Fahrenheit conversion."""
    
    def test_freezing_point(self):
        """Test conversion of freezing point (0°C = 32°F)."""
        result = celsius_to_fahrenheit(0)
        assert abs(result - 32) < 0.01
    
    def test_boiling_point(self):
        """Test conversion of boiling point (100°C = 212°F)."""
        result = celsius_to_fahrenheit(100)
        assert abs(result - 212) < 0.01
    
    def test_room_temperature(self):
        """Test conversion of room temperature (22.2°C ≈ 72°F)."""
        result = celsius_to_fahrenheit(22.2)
        assert abs(result - 72) < 0.1
    
    def test_negative_temperature(self):
        """Test conversion of negative temperature (-40°C = -40°F)."""
        result = celsius_to_fahrenheit(-40)
        assert abs(result - (-40)) < 0.01
    
    def test_type_error_on_string(self):
        """Test that TypeError is raised for string input."""
        with pytest.raises(TypeError):
            celsius_to_fahrenheit("0")


class TestMphToKmh:
    """Test miles per hour to kilometers per hour conversion."""
    
    def test_zero_speed(self):
        """Test conversion of zero speed."""
        result = mph_to_kmh(0)
        assert abs(result - 0) < 0.01
    
    def test_common_speed(self):
        """Test conversion of common speed (60 mph ≈ 96.56 km/h)."""
        result = mph_to_kmh(60)
        assert abs(result - 96.56) < 0.01
    
    def test_high_speed(self):
        """Test conversion of high speed (100 mph ≈ 160.93 km/h)."""
        result = mph_to_kmh(100)
        assert abs(result - 160.93) < 0.01
    
    def test_type_error_on_string(self):
        """Test that TypeError is raised for string input."""
        with pytest.raises(TypeError):
            mph_to_kmh("60")


class TestKmhToMph:
    """Test kilometers per hour to miles per hour conversion."""
    
    def test_zero_speed(self):
        """Test conversion of zero speed."""
        result = kmh_to_mph(0)
        assert abs(result - 0) < 0.01
    
    def test_common_speed(self):
        """Test conversion of common speed (100 km/h ≈ 62.14 mph)."""
        result = kmh_to_mph(100)
        assert abs(result - 62.14) < 0.01
    
    def test_high_speed(self):
        """Test conversion of high speed (160.93 km/h ≈ 100 mph)."""
        result = kmh_to_mph(160.93)
        assert abs(result - 100) < 0.01
    
    def test_type_error_on_string(self):
        """Test that TypeError is raised for string input."""
        with pytest.raises(TypeError):
            kmh_to_mph("100")


class TestValidateTemperature:
    """Test temperature validation."""
    
    def test_valid_fahrenheit_temperature(self):
        """Test validation of valid Fahrenheit temperature."""
        assert validate_temperature(72, 'F') is True
    
    def test_valid_celsius_temperature(self):
        """Test validation of valid Celsius temperature."""
        assert validate_temperature(22, 'C') is True
    
    def test_fahrenheit_too_high(self):
        """Test validation of too-high Fahrenheit temperature."""
        assert validate_temperature(200, 'F') is False
    
    def test_fahrenheit_too_low(self):
        """Test validation of too-low Fahrenheit temperature."""
        assert validate_temperature(-150, 'F') is False
    
    def test_celsius_too_high(self):
        """Test validation of too-high Celsius temperature."""
        assert validate_temperature(100, 'C') is False
    
    def test_celsius_too_low(self):
        """Test validation of too-low Celsius temperature."""
        assert validate_temperature(-100, 'C') is False
    
    def test_invalid_unit(self):
        """Test validation with invalid unit."""
        assert validate_temperature(72, 'K') is False
    
    def test_non_numeric_input(self):
        """Test validation with non-numeric input."""
        assert validate_temperature("72", 'F') is False


class TestValidateWindSpeed:
    """Test wind speed validation."""
    
    def test_valid_mph_speed(self):
        """Test validation of valid mph wind speed."""
        assert validate_wind_speed(25, 'mph') is True
    
    def test_valid_kmh_speed(self):
        """Test validation of valid km/h wind speed."""
        assert validate_wind_speed(40, 'kmh') is True
    
    def test_zero_speed(self):
        """Test validation of zero wind speed."""
        assert validate_wind_speed(0, 'mph') is True
    
    def test_mph_too_high(self):
        """Test validation of too-high mph wind speed."""
        assert validate_wind_speed(250, 'mph') is False
    
    def test_kmh_too_high(self):
        """Test validation of too-high km/h wind speed."""
        assert validate_wind_speed(400, 'kmh') is False
    
    def test_negative_speed(self):
        """Test validation of negative wind speed."""
        assert validate_wind_speed(-10, 'mph') is False
    
    def test_invalid_unit(self):
        """Test validation with invalid unit."""
        assert validate_wind_speed(25, 'knots') is False
    
    def test_non_numeric_input(self):
        """Test validation with non-numeric input."""
        assert validate_wind_speed("25", 'mph') is False


class TestValidateHumidity:
    """Test humidity validation."""
    
    def test_valid_humidity(self):
        """Test validation of valid humidity."""
        assert validate_humidity(65) is True
    
    def test_zero_humidity(self):
        """Test validation of zero humidity."""
        assert validate_humidity(0) is True
    
    def test_max_humidity(self):
        """Test validation of maximum humidity."""
        assert validate_humidity(100) is True
    
    def test_humidity_too_high(self):
        """Test validation of too-high humidity."""
        assert validate_humidity(150) is False
    
    def test_negative_humidity(self):
        """Test validation of negative humidity."""
        assert validate_humidity(-10) is False
    
    def test_non_numeric_input(self):
        """Test validation with non-numeric input."""
        assert validate_humidity("65") is False


class TestValidatePressure:
    """Test atmospheric pressure validation."""
    
    def test_valid_pressure(self):
        """Test validation of valid pressure."""
        assert validate_pressure(1013) is True
    
    def test_low_pressure(self):
        """Test validation of low pressure."""
        assert validate_pressure(900) is True
    
    def test_high_pressure(self):
        """Test validation of high pressure."""
        assert validate_pressure(1050) is True
    
    def test_pressure_too_low(self):
        """Test validation of too-low pressure."""
        assert validate_pressure(800) is False
    
    def test_pressure_too_high(self):
        """Test validation of too-high pressure."""
        assert validate_pressure(1100) is False
    
    def test_non_numeric_input(self):
        """Test validation with non-numeric input."""
        assert validate_pressure("1013") is False


class TestValidatePrecipitation:
    """Test precipitation validation."""
    
    def test_zero_precipitation(self):
        """Test validation of zero precipitation."""
        assert validate_precipitation(0) is True
    
    def test_valid_precipitation(self):
        """Test validation of valid precipitation."""
        assert validate_precipitation(5.5) is True
    
    def test_high_precipitation(self):
        """Test validation of high precipitation."""
        assert validate_precipitation(100) is True
    
    def test_negative_precipitation(self):
        """Test validation of negative precipitation."""
        assert validate_precipitation(-1) is False
    
    def test_non_numeric_input(self):
        """Test validation with non-numeric input."""
        assert validate_precipitation("5") is False


class TestValidateUVIndex:
    """Test UV index validation."""
    
    def test_zero_uv_index(self):
        """Test validation of zero UV index."""
        assert validate_uv_index(0) is True
    
    def test_valid_uv_index(self):
        """Test validation of valid UV index."""
        assert validate_uv_index(6) is True
    
    def test_max_uv_index(self):
        """Test validation of maximum UV index."""
        assert validate_uv_index(20) is True
    
    def test_uv_index_too_high(self):
        """Test validation of too-high UV index."""
        assert validate_uv_index(25) is False
    
    def test_negative_uv_index(self):
        """Test validation of negative UV index."""
        assert validate_uv_index(-1) is False
    
    def test_non_numeric_input(self):
        """Test validation with non-numeric input."""
        assert validate_uv_index("6") is False


class TestValidatePollenConcentration:
    """Test pollen concentration validation."""
    
    def test_zero_concentration(self):
        """Test validation of zero pollen concentration."""
        assert validate_pollen_concentration(0) is True
    
    def test_valid_concentration(self):
        """Test validation of valid pollen concentration."""
        assert validate_pollen_concentration(850) is True
    
    def test_high_concentration(self):
        """Test validation of high pollen concentration."""
        assert validate_pollen_concentration(5000) is True
    
    def test_negative_concentration(self):
        """Test validation of negative pollen concentration."""
        assert validate_pollen_concentration(-100) is False
    
    def test_non_numeric_input(self):
        """Test validation with non-numeric input."""
        assert validate_pollen_concentration("850") is False


class TestValidateWeatherData:
    """Test complete weather data validation."""
    
    def test_valid_weather_data(self):
        """Test validation of valid weather data."""
        data = {
            'temperature': 72,
            'humidity': 65,
            'wind_speed': 12,
            'pressure': 1013,
            'precipitation': 0,
            'uv_index': 6
        }
        is_valid, errors = validate_weather_data(data)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_invalid_temperature(self):
        """Test validation with invalid temperature."""
        data = {
            'temperature': 200,
            'humidity': 65,
            'wind_speed': 12,
            'pressure': 1013,
            'precipitation': 0,
            'uv_index': 6
        }
        is_valid, errors = validate_weather_data(data)
        assert is_valid is False
        assert len(errors) > 0
    
    def test_invalid_humidity(self):
        """Test validation with invalid humidity."""
        data = {
            'temperature': 72,
            'humidity': 150,
            'wind_speed': 12,
            'pressure': 1013,
            'precipitation': 0,
            'uv_index': 6
        }
        is_valid, errors = validate_weather_data(data)
        assert is_valid is False
    
    def test_multiple_invalid_fields(self):
        """Test validation with multiple invalid fields."""
        data = {
            'temperature': 200,
            'humidity': 150,
            'wind_speed': 250,
            'pressure': 800,
            'precipitation': -5,
            'uv_index': 25
        }
        is_valid, errors = validate_weather_data(data)
        assert is_valid is False
        assert len(errors) > 1
    
    def test_non_dict_input(self):
        """Test validation with non-dict input."""
        is_valid, errors = validate_weather_data("not a dict")
        assert is_valid is False
        assert len(errors) > 0
    
    def test_partial_weather_data(self):
        """Test validation with partial weather data."""
        data = {
            'temperature': 72,
            'humidity': 65
        }
        is_valid, errors = validate_weather_data(data)
        assert is_valid is True


class TestValidatePollenData:
    """Test complete pollen data validation."""
    
    def test_valid_pollen_data(self):
        """Test validation of valid pollen data."""
        data = {
            'grass': 850,
            'tree': 450,
            'weed': 150,
            'ragweed': 200,
            'mold': 320
        }
        is_valid, errors = validate_pollen_data(data)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_missing_pollen_type(self):
        """Test validation with missing pollen type."""
        data = {
            'grass': 850,
            'tree': 450,
            'weed': 150,
            'ragweed': 200
            # Missing 'mold'
        }
        is_valid, errors = validate_pollen_data(data)
        assert is_valid is False
        assert len(errors) > 0
    
    def test_invalid_concentration(self):
        """Test validation with invalid concentration."""
        data = {
            'grass': -100,
            'tree': 450,
            'weed': 150,
            'ragweed': 200,
            'mold': 320
        }
        is_valid, errors = validate_pollen_data(data)
        assert is_valid is False
    
    def test_non_dict_input(self):
        """Test validation with non-dict input."""
        is_valid, errors = validate_pollen_data("not a dict")
        assert is_valid is False
        assert len(errors) > 0
    
    def test_all_pollen_types_required(self):
        """Test that all five pollen types are required."""
        data = {
            'grass': 850,
            'tree': 450,
            'weed': 150,
            'ragweed': 200,
            'mold': 320,
            'extra': 100  # Extra field should not cause issues
        }
        is_valid, errors = validate_pollen_data(data)
        assert is_valid is True



class TestMetricConversionProperties:
    """Property-based tests for metric conversion accuracy.
    
    **Feature: data-mashup-dashboard, Property 8: Metric Conversion Accuracy**
    **Validates: Requirements 8.2, 8.3**
    """
    
    @given(st.floats(min_value=-100, max_value=150, allow_nan=False, allow_infinity=False))
    def test_fahrenheit_celsius_round_trip(self, fahrenheit):
        """
        Property: For any temperature value in Fahrenheit, converting to Celsius 
        and back should produce the original value (within rounding tolerance).
        
        This tests the round-trip property: F -> C -> F should equal F
        """
        # Convert Fahrenheit to Celsius and back to Fahrenheit
        celsius = fahrenheit_to_celsius(fahrenheit)
        result = celsius_to_fahrenheit(celsius)
        
        # Allow for floating-point rounding errors (tolerance of 0.01 degrees)
        assert abs(result - fahrenheit) < 0.01, \
            f"Round trip failed: {fahrenheit}°F -> {celsius}°C -> {result}°F"
    
    @given(st.floats(min_value=-73, max_value=65, allow_nan=False, allow_infinity=False))
    def test_celsius_fahrenheit_round_trip(self, celsius):
        """
        Property: For any temperature value in Celsius, converting to Fahrenheit 
        and back should produce the original value (within rounding tolerance).
        
        This tests the inverse round-trip property: C -> F -> C should equal C
        """
        # Convert Celsius to Fahrenheit and back to Celsius
        fahrenheit = celsius_to_fahrenheit(celsius)
        result = fahrenheit_to_celsius(fahrenheit)
        
        # Allow for floating-point rounding errors (tolerance of 0.01 degrees)
        assert abs(result - celsius) < 0.01, \
            f"Round trip failed: {celsius}°C -> {fahrenheit}°F -> {result}°C"
    
    @given(st.floats(min_value=0, max_value=200, allow_nan=False, allow_infinity=False))
    def test_mph_kmh_round_trip(self, mph):
        """
        Property: For any wind speed value in mph, converting to km/h 
        and back should produce the original value (within rounding tolerance).
        
        This tests the round-trip property: mph -> km/h -> mph should equal mph
        """
        # Convert mph to km/h and back to mph
        kmh = mph_to_kmh(mph)
        result = kmh_to_mph(kmh)
        
        # Allow for floating-point rounding errors (tolerance of 0.01 mph)
        assert abs(result - mph) < 0.01, \
            f"Round trip failed: {mph} mph -> {kmh} km/h -> {result} mph"
    
    @given(st.floats(min_value=0, max_value=322, allow_nan=False, allow_infinity=False))
    def test_kmh_mph_round_trip(self, kmh):
        """
        Property: For any wind speed value in km/h, converting to mph 
        and back should produce the original value (within rounding tolerance).
        
        This tests the inverse round-trip property: km/h -> mph -> km/h should equal km/h
        """
        # Convert km/h to mph and back to km/h
        mph = kmh_to_mph(kmh)
        result = mph_to_kmh(mph)
        
        # Allow for floating-point rounding errors (tolerance of 0.01 km/h)
        assert abs(result - kmh) < 0.01, \
            f"Round trip failed: {kmh} km/h -> {mph} mph -> {result} km/h"
