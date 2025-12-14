"""
Utility functions for the Weather & Pollen Dashboard.

Provides metric conversion functions, data validation, and logging utilities.
"""

import logging
import sys
from typing import Union, Tuple


# Configure logging
def setup_logging(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging configuration for the application.
    
    Args:
        name: Logger name (typically __name__)
        level: Logging level (default: logging.INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger if not already present
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger


# Metric conversion functions
def fahrenheit_to_celsius(fahrenheit: Union[int, float]) -> float:
    """
    Convert temperature from Fahrenheit to Celsius.
    
    Formula: C = (F - 32) * 5/9
    
    Args:
        fahrenheit: Temperature in Fahrenheit
    
    Returns:
        Temperature in Celsius
    
    Raises:
        TypeError: If input is not a number
    """
    if not isinstance(fahrenheit, (int, float)):
        raise TypeError(f"Expected number, got {type(fahrenheit).__name__}")
    
    return (fahrenheit - 32) * 5 / 9


def celsius_to_fahrenheit(celsius: Union[int, float]) -> float:
    """
    Convert temperature from Celsius to Fahrenheit.
    
    Formula: F = C * 9/5 + 32
    
    Args:
        celsius: Temperature in Celsius
    
    Returns:
        Temperature in Fahrenheit
    
    Raises:
        TypeError: If input is not a number
    """
    if not isinstance(celsius, (int, float)):
        raise TypeError(f"Expected number, got {type(celsius).__name__}")
    
    return celsius * 9 / 5 + 32


def mph_to_kmh(mph: Union[int, float]) -> float:
    """
    Convert speed from miles per hour to kilometers per hour.
    
    Formula: km/h = mph * 1.60934
    
    Args:
        mph: Speed in miles per hour
    
    Returns:
        Speed in kilometers per hour
    
    Raises:
        TypeError: If input is not a number
    """
    if not isinstance(mph, (int, float)):
        raise TypeError(f"Expected number, got {type(mph).__name__}")
    
    return mph * 1.60934


def kmh_to_mph(kmh: Union[int, float]) -> float:
    """
    Convert speed from kilometers per hour to miles per hour.
    
    Formula: mph = km/h / 1.60934
    
    Args:
        kmh: Speed in kilometers per hour
    
    Returns:
        Speed in miles per hour
    
    Raises:
        TypeError: If input is not a number
    """
    if not isinstance(kmh, (int, float)):
        raise TypeError(f"Expected number, got {type(kmh).__name__}")
    
    return kmh / 1.60934


# Data validation functions
def validate_temperature(temp: Union[int, float], unit: str = 'F') -> bool:
    """
    Validate that temperature is within reasonable bounds.
    
    Reasonable bounds:
    - Fahrenheit: -100 to 150 (covers extreme weather)
    - Celsius: -73 to 65 (equivalent range)
    
    Args:
        temp: Temperature value
        unit: Temperature unit ('F' for Fahrenheit, 'C' for Celsius)
    
    Returns:
        True if temperature is valid, False otherwise
    """
    if not isinstance(temp, (int, float)):
        return False
    
    if unit.upper() == 'F':
        return -100 <= temp <= 150
    elif unit.upper() == 'C':
        return -73 <= temp <= 65
    else:
        return False


def validate_wind_speed(speed: Union[int, float], unit: str = 'mph') -> bool:
    """
    Validate that wind speed is within reasonable bounds.
    
    Reasonable bounds:
    - mph: 0 to 200 (covers extreme hurricanes)
    - km/h: 0 to 322 (equivalent range)
    
    Args:
        speed: Wind speed value
        unit: Speed unit ('mph' or 'kmh')
    
    Returns:
        True if wind speed is valid, False otherwise
    """
    if not isinstance(speed, (int, float)):
        return False
    
    if speed < 0:
        return False
    
    if unit.lower() == 'mph':
        return speed <= 200
    elif unit.lower() == 'kmh':
        return speed <= 322
    else:
        return False


def validate_humidity(humidity: Union[int, float]) -> bool:
    """
    Validate that humidity is within valid bounds (0-100%).
    
    Args:
        humidity: Humidity percentage
    
    Returns:
        True if humidity is valid, False otherwise
    """
    if not isinstance(humidity, (int, float)):
        return False
    
    return 0 <= humidity <= 100


def validate_pressure(pressure: Union[int, float]) -> bool:
    """
    Validate that atmospheric pressure is within reasonable bounds.
    
    Reasonable bounds: 870 to 1085 mb (covers extreme weather)
    
    Args:
        pressure: Atmospheric pressure in millibars
    
    Returns:
        True if pressure is valid, False otherwise
    """
    if not isinstance(pressure, (int, float)):
        return False
    
    return 870 <= pressure <= 1085


def validate_precipitation(precip: Union[int, float]) -> bool:
    """
    Validate that precipitation is non-negative.
    
    Args:
        precip: Precipitation amount in mm
    
    Returns:
        True if precipitation is valid, False otherwise
    """
    if not isinstance(precip, (int, float)):
        return False
    
    return precip >= 0


def validate_uv_index(uv_index: Union[int, float]) -> bool:
    """
    Validate that UV index is within reasonable bounds (0-20).
    
    Args:
        uv_index: UV index value
    
    Returns:
        True if UV index is valid, False otherwise
    """
    if not isinstance(uv_index, (int, float)):
        return False
    
    return 0 <= uv_index <= 20


def validate_pollen_concentration(concentration: Union[int, float]) -> bool:
    """
    Validate that pollen concentration is non-negative.
    
    Args:
        concentration: Pollen concentration in gr/m³ or ppm
    
    Returns:
        True if concentration is valid, False otherwise
    """
    if not isinstance(concentration, (int, float)):
        return False
    
    return concentration >= 0


def validate_weather_data(data: dict) -> Tuple[bool, list]:
    """
    Validate a complete weather data dictionary.
    
    Args:
        data: Weather data dictionary with keys: temperature, humidity, 
              wind_speed, pressure, precipitation, uv_index
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not isinstance(data, dict):
        return False, ["Data must be a dictionary"]
    
    # Validate temperature
    if 'temperature' in data:
        if not validate_temperature(data['temperature'], 'F'):
            errors.append(f"Invalid temperature: {data['temperature']}")
    
    # Validate humidity
    if 'humidity' in data:
        if not validate_humidity(data['humidity']):
            errors.append(f"Invalid humidity: {data['humidity']}")
    
    # Validate wind speed
    if 'wind_speed' in data:
        if not validate_wind_speed(data['wind_speed'], 'mph'):
            errors.append(f"Invalid wind speed: {data['wind_speed']}")
    
    # Validate pressure
    if 'pressure' in data:
        if not validate_pressure(data['pressure']):
            errors.append(f"Invalid pressure: {data['pressure']}")
    
    # Validate precipitation
    if 'precipitation' in data:
        if not validate_precipitation(data['precipitation']):
            errors.append(f"Invalid precipitation: {data['precipitation']}")
    
    # Validate UV index
    if 'uv_index' in data:
        if not validate_uv_index(data['uv_index']):
            errors.append(f"Invalid UV index: {data['uv_index']}")
    
    return len(errors) == 0, errors


def validate_pollen_data(data: dict) -> Tuple[bool, list]:
    """
    Validate a complete pollen data dictionary.
    
    Args:
        data: Pollen data dictionary with pollen types as keys
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not isinstance(data, dict):
        return False, ["Data must be a dictionary"]
    
    required_pollen_types = {'grass', 'tree', 'weed', 'ragweed', 'mold'}
    
    for pollen_type in required_pollen_types:
        if pollen_type not in data:
            errors.append(f"Missing pollen type: {pollen_type}")
        elif not validate_pollen_concentration(data[pollen_type]):
            errors.append(f"Invalid concentration for {pollen_type}: {data[pollen_type]}")
    
    return len(errors) == 0, errors
