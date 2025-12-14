"""
Data Service module for Weather & Pollen Dashboard.

This module provides data fetching, processing, aggregation, and combination
functionality for weather and pollen data from external APIs.

Key responsibilities:
- Fetch weather and pollen data from APIs
- Aggregate data by time period (weekly, monthly, half-yearly, yearly)
- Combine and merge weather and pollen datasets
- Handle data validation and error cases
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
import pandas as pd
import numpy as np

from src.api_client import APIClient, APIClientError, WeatherAPIError, PollenAPIError
from src.cache_manager import CacheManager, CacheManagerError
from config import get_location_config

logger = logging.getLogger(__name__)


class DataServiceError(Exception):
    """Base exception for data service errors."""
    pass


class DataAggregationError(DataServiceError):
    """Exception raised for data aggregation errors."""
    pass


class DataCombinationError(DataServiceError):
    """Exception raised for data combination errors."""
    pass


class DataService:
    """
    Service for fetching, processing, and aggregating weather and pollen data.
    
    This class provides methods to:
    - Fetch weather and pollen data from external APIs
    - Aggregate data by different time periods
    - Combine weather and pollen datasets
    - Validate and normalize data
    """
    
    # Time period configurations for aggregation
    TIME_PERIODS = {
        'weekly': 7,
        'monthly': 30,
        'half_yearly': 182,
        'yearly': 365
    }
    
    # Aggregation functions for different data types
    AGGREGATION_FUNCTIONS = {
        'temperature': 'mean',
        'humidity': 'mean',
        'wind_speed': 'mean',
        'pressure': 'mean',
        'precipitation': 'sum',
        'uv_index': 'mean',
        'concentration': 'mean'
    }
    
    def __init__(self, weather_api_key: Optional[str] = None, pollen_api_key: Optional[str] = None, 
                 max_retries: int = 3, timeout: int = 10, cache_manager: Optional[CacheManager] = None):
        """
        Initialize the DataService.
        
        Args:
            weather_api_key (Optional[str]): API key for weather data service (Weatherbit).
            pollen_api_key (Optional[str]): API key for pollen data service (AQICN).
            max_retries (int): Maximum number of API retry attempts. Defaults to 3.
            timeout (int): API request timeout in seconds. Defaults to 10.
            cache_manager (Optional[CacheManager]): Cache manager for fallback data. If not provided, a new one is created.
        """
        self.api_client = APIClient(weather_api_key=weather_api_key, pollen_api_key=pollen_api_key, 
                                   max_retries=max_retries, timeout=timeout)
        self.location_config = get_location_config()
        
        # Initialize cache manager for fallback data
        if cache_manager is None:
            self.cache_manager = CacheManager(default_ttl=3600)
        else:
            self.cache_manager = cache_manager
        
        logger.info("DataService initialized")
    
    def fetch_weather_data(self, country_code: str, state_code: str, district_name: str) -> Dict[str, Any]:
        """
        Fetch weather data for a specific location with fallback to cached data.
        
        Args:
            country_code (str): Country code (e.g., 'USA', 'India').
            state_code (str): State code (e.g., 'NY', 'CA').
            district_name (str): District name (e.g., 'Manhattan', 'Brooklyn').
        
        Returns:
            Dict[str, Any]: Weather data including temperature, humidity, wind speed, etc.
                           If API fails, returns cached data with 'cached_data' indicator.
        
        Raises:
            DataServiceError: If location is invalid or both API and cache fail.
        
        Example response:
            {
                "timestamp": "2024-01-15T14:30:00Z",
                "location": {"country": "USA", "state": "NY", "district": "Manhattan"},
                "temperature": 72.5,
                "humidity": 65,
                "wind_speed": 12,
                "pressure": 1013,
                "precipitation": 0,
                "uv_index": 6,
                "weather_code": 2,
                "cached_data": false
            }
        """
        logger.info(f"Fetching weather data for {country_code}/{state_code}/{district_name}")
        
        # Create cache key
        cache_key = f"weather_{country_code}_{state_code}_{district_name}"
        
        try:
            # Validate location
            if not self.location_config.validate_location(country_code, state_code, district_name):
                error_msg = f"Invalid location: {country_code}/{state_code}/{district_name}"
                logger.error(error_msg)
                raise DataServiceError(error_msg)
            
            # Get coordinates
            latitude, longitude = self.location_config.get_coordinates(country_code, state_code, district_name)
            
            # Fetch data from API
            try:
                api_data = self.api_client.fetch_all_data(latitude, longitude)
                
                if api_data.get('weather') is None:
                    error_msg = f"Failed to fetch weather data for {country_code}/{state_code}/{district_name}"
                    logger.error(error_msg)
                    raise DataServiceError(error_msg)
                
                # Add location information
                weather_data = api_data['weather']
                weather_data['location'] = {
                    'country': country_code,
                    'state': state_code,
                    'district': district_name,
                    'latitude': latitude,
                    'longitude': longitude
                }
                weather_data['cached_data'] = False
                
                # Cache the successful data
                try:
                    self.cache_manager.set(cache_key, weather_data, ttl=CacheManager.DEFAULT_WEATHER_TTL)
                    logger.debug(f"Cached weather data for {country_code}/{state_code}/{district_name}")
                except CacheManagerError as cache_error:
                    logger.warning(f"Failed to cache weather data: {cache_error}")
                    # Continue anyway - caching failure shouldn't prevent data return
                
                logger.info(f"Successfully fetched weather data for {country_code}/{state_code}/{district_name}")
                return weather_data
            
            except APIClientError as api_error:
                logger.warning(f"API error fetching weather data: {api_error}")
                
                # Try to get cached data as fallback
                try:
                    cached_data = self.cache_manager.get(cache_key)
                    if cached_data is not None:
                        logger.info(f"Using cached weather data for {country_code}/{state_code}/{district_name}")
                        cached_data['cached_data'] = True
                        cached_data['cache_error'] = str(api_error)
                        return cached_data
                except CacheManagerError as cache_error:
                    logger.error(f"Failed to retrieve cached weather data: {cache_error}")
                
                # Both API and cache failed
                error_msg = f"Failed to fetch weather data from API and no cached data available: {str(api_error)}"
                logger.error(error_msg)
                raise DataServiceError(error_msg) from api_error
        
        except (ValueError, DataServiceError) as e:
            logger.error(f"Error fetching weather data: {e}")
            raise DataServiceError(str(e)) from e
    
    def fetch_pollen_data(self, country_code: str, state_code: str, district_name: str) -> Dict[str, Any]:
        """
        Fetch pollen data for a specific location with fallback to cached data.
        
        Args:
            country_code (str): Country code (e.g., 'USA', 'India').
            state_code (str): State code (e.g., 'NY', 'CA').
            district_name (str): District name (e.g., 'Manhattan', 'Brooklyn').
        
        Returns:
            Dict[str, Any]: Pollen data including concentration levels for each pollen type.
                           If API fails, returns cached data with 'cached_data' indicator.
        
        Raises:
            DataServiceError: If location is invalid or both API and cache fail.
        
        Example response:
            {
                "timestamp": "2024-01-15T00:00:00Z",
                "location": {"country": "USA", "state": "NY", "district": "Manhattan"},
                "pollen_types": {
                    "grass": {"concentration": 850, "unit": "gr/m³", "severity": "HIGH"},
                    "tree": {"concentration": 450, "unit": "gr/m³", "severity": "MODERATE"},
                    ...
                },
                "cached_data": false
            }
        """
        logger.info(f"Fetching pollen data for {country_code}/{state_code}/{district_name}")
        
        # Create cache key
        cache_key = f"pollen_{country_code}_{state_code}_{district_name}"
        
        try:
            # Validate location
            if not self.location_config.validate_location(country_code, state_code, district_name):
                error_msg = f"Invalid location: {country_code}/{state_code}/{district_name}"
                logger.error(error_msg)
                raise DataServiceError(error_msg)
            
            # Get coordinates
            latitude, longitude = self.location_config.get_coordinates(country_code, state_code, district_name)
            
            # Fetch data from API
            try:
                api_data = self.api_client.fetch_all_data(latitude, longitude)
                
                if api_data.get('pollen') is None:
                    error_msg = f"Failed to fetch pollen data for {country_code}/{state_code}/{district_name}"
                    logger.error(error_msg)
                    raise DataServiceError(error_msg)
                
                # Add location information
                pollen_data = api_data['pollen']
                pollen_data['location'] = {
                    'country': country_code,
                    'state': state_code,
                    'district': district_name,
                    'latitude': latitude,
                    'longitude': longitude
                }
                pollen_data['cached_data'] = False
                
                # Cache the successful data
                try:
                    self.cache_manager.set(cache_key, pollen_data, ttl=CacheManager.DEFAULT_POLLEN_TTL)
                    logger.debug(f"Cached pollen data for {country_code}/{state_code}/{district_name}")
                except CacheManagerError as cache_error:
                    logger.warning(f"Failed to cache pollen data: {cache_error}")
                    # Continue anyway - caching failure shouldn't prevent data return
                
                logger.info(f"Successfully fetched pollen data for {country_code}/{state_code}/{district_name}")
                return pollen_data
            
            except APIClientError as api_error:
                logger.warning(f"API error fetching pollen data: {api_error}")
                
                # Try to get cached data as fallback
                try:
                    cached_data = self.cache_manager.get(cache_key)
                    if cached_data is not None:
                        logger.info(f"Using cached pollen data for {country_code}/{state_code}/{district_name}")
                        cached_data['cached_data'] = True
                        cached_data['cache_error'] = str(api_error)
                        return cached_data
                except CacheManagerError as cache_error:
                    logger.error(f"Failed to retrieve cached pollen data: {cache_error}")
                
                # Both API and cache failed
                error_msg = f"Failed to fetch pollen data from API and no cached data available: {str(api_error)}"
                logger.error(error_msg)
                raise DataServiceError(error_msg) from api_error
        
        except (ValueError, DataServiceError) as e:
            logger.error(f"Error fetching pollen data: {e}")
            raise DataServiceError(str(e)) from e
    
    def aggregate_data(self, data: List[Dict[str, Any]], period: str) -> List[Dict[str, Any]]:
        """
        Aggregate data by time period (weekly, monthly, half-yearly, yearly).
        
        Args:
            data (List[Dict[str, Any]]): List of data points with timestamps.
            period (str): Time period for aggregation ('weekly', 'monthly', 'half_yearly', 'yearly').
        
        Returns:
            List[Dict[str, Any]]: Aggregated data points.
        
        Raises:
            DataAggregationError: If aggregation fails or period is invalid.
        
        Example:
            Input: [
                {"timestamp": "2024-01-01T00:00:00Z", "temperature": 70, "humidity": 60},
                {"timestamp": "2024-01-02T00:00:00Z", "temperature": 72, "humidity": 65},
                ...
            ]
            
            Output (weekly aggregation): [
                {"timestamp": "2024-01-01", "temperature": 71.5, "humidity": 62.5, ...}
            ]
        """
        logger.info(f"Aggregating data for period: {period}")
        
        try:
            # Validate period
            if period not in self.TIME_PERIODS:
                error_msg = f"Invalid time period: {period}. Must be one of {list(self.TIME_PERIODS.keys())}"
                logger.error(error_msg)
                raise DataAggregationError(error_msg)
            
            # Handle empty data
            if not data or len(data) == 0:
                logger.warning("No data to aggregate")
                return []
            
            # Convert to DataFrame for easier aggregation
            df = pd.DataFrame(data)
            
            # Parse timestamps
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            else:
                logger.warning("No timestamp column found in data")
                return data
            
            # Set timestamp as index
            df.set_index('timestamp', inplace=True)
            
            # Determine frequency based on period
            freq_map = {
                'weekly': 'W',
                'monthly': 'ME',
                'half_yearly': '6ME',
                'yearly': 'YE'
            }
            freq = freq_map[period]
            
            # Build aggregation dict only for columns that exist
            agg_dict = {}
            for col, func in self.AGGREGATION_FUNCTIONS.items():
                if col in df.columns:
                    agg_dict[col] = func
            
            # Aggregate numeric columns
            if agg_dict:
                aggregated = df.resample(freq).agg(agg_dict, skipna=True)
            else:
                aggregated = df.resample(freq).first()
            
            # Reset index to get timestamp back as column
            aggregated.reset_index(inplace=True)
            
            # Convert back to list of dictionaries
            result = aggregated.to_dict('records')
            
            logger.info(f"Successfully aggregated {len(data)} data points into {len(result)} periods")
            return result
        
        except (KeyError, ValueError, TypeError) as e:
            error_msg = f"Error aggregating data: {str(e)}"
            logger.error(error_msg)
            raise DataAggregationError(error_msg) from e
    
    def combine_datasets(self, weather_data: Dict[str, Any], pollen_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine and merge weather and pollen datasets.
        
        Args:
            weather_data (Dict[str, Any]): Weather data from fetch_weather_data().
            pollen_data (Dict[str, Any]): Pollen data from fetch_pollen_data().
        
        Returns:
            Dict[str, Any]: Combined dataset with both weather and pollen information.
        
        Raises:
            DataCombinationError: If datasets cannot be combined.
        
        Example response:
            {
                "timestamp": "2024-01-15T14:30:00Z",
                "location": {"country": "USA", "state": "NY", "district": "Manhattan"},
                "weather": {
                    "temperature": 72.5,
                    "humidity": 65,
                    "wind_speed": 12,
                    ...
                },
                "pollen": {
                    "grass": {"concentration": 850, "severity": "HIGH"},
                    ...
                }
            }
        """
        logger.info("Combining weather and pollen datasets")
        
        try:
            # Validate inputs
            if not weather_data or not isinstance(weather_data, dict):
                raise DataCombinationError("Invalid weather data")
            
            if not pollen_data or not isinstance(pollen_data, dict):
                raise DataCombinationError("Invalid pollen data")
            
            # Verify locations match
            weather_location = weather_data.get('location', {})
            pollen_location = pollen_data.get('location', {})
            
            if weather_location != pollen_location:
                logger.warning("Weather and pollen locations do not match exactly")
            
            # Create combined dataset
            combined = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'location': weather_location or pollen_location,
                'weather': {
                    'temperature': weather_data.get('temperature'),
                    'humidity': weather_data.get('humidity'),
                    'wind_speed': weather_data.get('wind_speed'),
                    'pressure': weather_data.get('pressure'),
                    'precipitation': weather_data.get('precipitation'),
                    'uv_index': weather_data.get('uv_index'),
                    'weather_code': weather_data.get('weather_code')
                },
                'pollen': pollen_data.get('pollen_types', {})
            }
            
            logger.info("Successfully combined weather and pollen datasets")
            return combined
        
        except (KeyError, TypeError) as e:
            error_msg = f"Error combining datasets: {str(e)}"
            logger.error(error_msg)
            raise DataCombinationError(error_msg) from e
    
    def validate_weather_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate weather data for required fields and value ranges.
        
        Args:
            data (Dict[str, Any]): Weather data to validate.
        
        Returns:
            bool: True if data is valid, False otherwise.
        """
        logger.debug("Validating weather data")
        
        try:
            # Check required fields
            required_fields = ['temperature', 'humidity', 'wind_speed', 'pressure']
            for field in required_fields:
                if field not in data or data[field] is None:
                    logger.warning(f"Missing required field: {field}")
                    return False
            
            # Validate value ranges
            temperature = data.get('temperature')
            if temperature is not None and (temperature < -100 or temperature > 150):
                logger.warning(f"Temperature out of range: {temperature}")
                return False
            
            humidity = data.get('humidity')
            if humidity is not None and (humidity < 0 or humidity > 100):
                logger.warning(f"Humidity out of range: {humidity}")
                return False
            
            wind_speed = data.get('wind_speed')
            if wind_speed is not None and wind_speed < 0:
                logger.warning(f"Wind speed cannot be negative: {wind_speed}")
                return False
            
            pressure = data.get('pressure')
            if pressure is not None and (pressure < 800 or pressure > 1100):
                logger.warning(f"Pressure out of range: {pressure}")
                return False
            
            logger.debug("Weather data validation passed")
            return True
        
        except Exception as e:
            logger.error(f"Error validating weather data: {e}")
            return False
    
    def validate_pollen_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate pollen data for required fields and structure.
        
        Args:
            data (Dict[str, Any]): Pollen data to validate.
        
        Returns:
            bool: True if data is valid, False otherwise.
        """
        logger.debug("Validating pollen data")
        
        try:
            # Check required fields
            if 'pollen_types' not in data:
                logger.warning("Missing pollen_types field")
                return False
            
            pollen_types = data['pollen_types']
            if not isinstance(pollen_types, dict):
                logger.warning("pollen_types is not a dictionary")
                return False
            
            # Check for all required pollen types
            required_types = ['grass', 'tree', 'weed', 'ragweed', 'mold']
            for pollen_type in required_types:
                if pollen_type not in pollen_types:
                    logger.warning(f"Missing pollen type: {pollen_type}")
                    return False
                
                pollen_info = pollen_types[pollen_type]
                if not isinstance(pollen_info, dict):
                    logger.warning(f"Invalid pollen type structure: {pollen_type}")
                    return False
                
                # Check required fields in pollen type
                if 'concentration' not in pollen_info or 'severity' not in pollen_info:
                    logger.warning(f"Missing fields in pollen type: {pollen_type}")
                    return False
                
                # Validate concentration is non-negative
                concentration = pollen_info.get('concentration')
                if concentration is not None and concentration < 0:
                    logger.warning(f"Negative concentration for {pollen_type}: {concentration}")
                    return False
            
            logger.debug("Pollen data validation passed")
            return True
        
        except Exception as e:
            logger.error(f"Error validating pollen data: {e}")
            return False
    
    def get_aggregation_period_days(self, period: str) -> int:
        """
        Get the number of days for a given aggregation period.
        
        Args:
            period (str): Time period ('weekly', 'monthly', 'half_yearly', 'yearly').
        
        Returns:
            int: Number of days in the period.
        
        Raises:
            DataServiceError: If period is invalid.
        """
        if period not in self.TIME_PERIODS:
            raise DataServiceError(f"Invalid period: {period}")
        
        return self.TIME_PERIODS[period]
