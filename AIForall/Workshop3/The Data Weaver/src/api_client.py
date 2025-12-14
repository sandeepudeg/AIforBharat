"""
API Client module for Weather & Pollen Dashboard.

This module provides clients for fetching weather and pollen data from external APIs
with retry logic, error handling, and comprehensive logging.

APIs Used:
- Weather: Open-Meteo (https://open-meteo.com/)
- Pollen: AQICN (https://aqicn.org/)
"""

import logging
import time
from typing import Dict, Optional, Any
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.poolmanager import PoolManager

try:
    import openmeteo_requests
except ImportError:
    openmeteo_requests = None

logger = logging.getLogger(__name__)


class HTTPAdapterWithPooling(HTTPAdapter):
    """
    Custom HTTPAdapter with connection pooling configuration.
    
    This adapter configures connection pooling to reuse connections
    and improve performance for multiple API requests.
    """
    
    def __init__(self, pool_connections: int = 10, pool_maxsize: int = 10, 
                 max_retries: Optional[Retry] = None, pool_block: bool = False):
        """
        Initialize HTTPAdapter with pooling configuration.
        
        Args:
            pool_connections (int): Number of connection pools to cache. Defaults to 10.
            pool_maxsize (int): Maximum number of connections to save in the pool. Defaults to 10.
            max_retries (Optional[Retry]): Retry strategy. Defaults to None.
            pool_block (bool): Whether to block when pool is exhausted. Defaults to False.
        """
        self.pool_connections = pool_connections
        self.pool_maxsize = pool_maxsize
        self.pool_block = pool_block
        super().__init__(max_retries=max_retries, pool_connections=pool_connections, 
                         pool_maxsize=pool_maxsize, pool_block=pool_block)


class APIClientError(Exception):
    """Base exception for API client errors."""
    pass


class WeatherAPIError(APIClientError):
    """Exception raised for weather API errors."""
    pass


class PollenAPIError(APIClientError):
    """Exception raised for pollen API errors."""
    pass


class WeatherAPIClient:
    """
    Client for fetching weather data from Weatherbit API.
    
    Weatherbit provides current weather and forecast data for any location.
    Requires an API key for access.
    """
    
    BASE_URL = "https://api.weatherbit.io/v2.0/current"
    
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3, timeout: int = 10):
        """
        Initialize the Weather API client.
        
        Args:
            api_key (Optional[str]): Weatherbit API key. If not provided, will attempt to use
                                    environment variable WEATHERBIT_API_KEY.
            max_retries (int): Maximum number of retry attempts. Defaults to 3.
            timeout (int): Request timeout in seconds. Defaults to 10.
        """
        import os
        
        self.api_key = api_key or os.getenv("WEATHERBIT_API_KEY")
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = self._create_session()
        
        if not self.api_key:
            logger.warning("Weatherbit API key not provided. Weather API calls may fail.")
        
        logger.info(f"WeatherAPIClient initialized with max_retries={max_retries}, timeout={timeout}s")
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry strategy and connection pooling.
        
        Returns:
            requests.Session: Configured session with retry logic and pooling.
        """
        session = requests.Session()
        
        # Configure retry strategy with exponential backoff
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,  # 1s, 2s, 4s for retries
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        # Use custom adapter with connection pooling
        adapter = HTTPAdapterWithPooling(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=retry_strategy,
            pool_block=False
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        logger.debug("Requests session created with retry strategy and connection pooling")
        return session
    
    def fetch_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Fetch current weather data for a location.
        
        Args:
            latitude (float): Location latitude.
            longitude (float): Location longitude.
        
        Returns:
            Dict[str, Any]: Weather data including temperature, humidity, wind speed, etc.
        
        Raises:
            WeatherAPIError: If the API request fails after retries.
        
        Example response:
            {
                "data": [
                    {
                        "temp": 72.5,
                        "rh": 65,
                        "wind_spd": 12,
                        "pres": 1013,
                        "precip": 0,
                        "uv": 6,
                        "weather": {"code": 200, "description": "Thunderstorm"}
                    }
                ]
            }
        """
        logger.info(f"Fetching weather data for lat={latitude}, lon={longitude}")
        
        try:
            return self._fetch_with_requests(latitude, longitude)
        
        except Exception as e:
            error_msg = f"Weather API request failed for lat={latitude}, lon={longitude}: {str(e)}"
            logger.error(error_msg)
            raise WeatherAPIError(error_msg) from e
    

    def _fetch_with_requests(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Fetch weather data using the requests library.
        
        Args:
            latitude (float): Location latitude.
            longitude (float): Location longitude.
        
        Returns:
            Dict[str, Any]: Weather data from API.
        
        Raises:
            WeatherAPIError: If the API request fails.
        """
        try:
            params = {
                "lat": latitude,
                "lon": longitude,
                "key": self.api_key,
                "units": "I"  # Imperial units (Fahrenheit, mph)
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched weather data for lat={latitude}, lon={longitude}")
            return data
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Requests library failed: {str(e)}"
            logger.error(error_msg)
            raise WeatherAPIError(error_msg) from e
        
        except ValueError as e:
            error_msg = f"Failed to parse weather API response: {str(e)}"
            logger.error(error_msg)
            raise WeatherAPIError(error_msg) from e
    
    def parse_weather_data(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and normalize weather API response into standard format.
        
        Args:
            api_response (Dict[str, Any]): Raw response from Weatherbit API.
        
        Returns:
            Dict[str, Any]: Normalized weather data.
        
        Raises:
            WeatherAPIError: If response is missing required fields.
        """
        try:
            if api_response is None:
                raise WeatherAPIError("API response is None")
            
            # Weatherbit returns data as a list
            data_list = api_response.get("data", [])
            if not data_list:
                raise WeatherAPIError("No weather data in API response")
            
            current = data_list[0]
            
            parsed_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "temperature": current.get("temp"),
                "humidity": current.get("rh"),
                "wind_speed": current.get("wind_spd"),
                "pressure": current.get("pres"),
                "precipitation": current.get("precip"),
                "uv_index": current.get("uv"),
                "weather_code": current.get("weather", {}).get("code"),
                "weather_description": current.get("weather", {}).get("description"),
                "city_name": current.get("city_name"),
                "country_code": current.get("country_code")
            }
            
            logger.debug(f"Parsed weather data: {parsed_data}")
            return parsed_data
        
        except (KeyError, TypeError, IndexError) as e:
            error_msg = f"Error parsing weather data: {str(e)}"
            logger.error(error_msg)
            raise WeatherAPIError(error_msg) from e


class PollenAPIClient:
    """
    Client for fetching pollen data from AQICN API.
    
    AQICN provides air quality and pollen data for various locations.
    Requires an API key for access.
    """
    
    BASE_URL = "https://api.waqi.info"
    
    # Pollen types to track
    POLLEN_TYPES = ["grass", "tree", "weed", "ragweed", "mold"]
    
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3, timeout: int = 10):
        """
        Initialize the Pollen API client.
        
        Args:
            api_key (Optional[str]): AQICN API key. If not provided, will attempt to use
                                    environment variable AQICN_API_KEY.
            max_retries (int): Maximum number of retry attempts. Defaults to 3.
            timeout (int): Request timeout in seconds. Defaults to 10.
        """
        import os
        
        self.api_key = api_key or os.getenv("AQICN_API_KEY")
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = self._create_session()
        
        if not self.api_key:
            logger.warning("AQICN API key not provided. Pollen API calls may fail.")
        
        logger.info(f"PollenAPIClient initialized with max_retries={max_retries}, timeout={timeout}s")
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry strategy and connection pooling.
        
        Returns:
            requests.Session: Configured session with retry logic and pooling.
        """
        session = requests.Session()
        
        # Configure retry strategy with exponential backoff
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,  # 1s, 2s, 4s for retries
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        # Use custom adapter with connection pooling
        adapter = HTTPAdapterWithPooling(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=retry_strategy,
            pool_block=False
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        logger.debug("Requests session created with retry strategy and connection pooling")
        return session
    
    def fetch_pollen(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Fetch pollen data for a location.
        
        Args:
            latitude (float): Location latitude.
            longitude (float): Location longitude.
        
        Returns:
            Dict[str, Any]: Pollen data including concentration levels for each pollen type.
        
        Raises:
            PollenAPIError: If the API request fails after retries.
        
        Example response:
            {
                "status": "ok",
                "data": {
                    "aqi": 45,
                    "dominentpol": "pm25",
                    "iaqi": {
                        "pm25": {"v": 25},
                        "pm10": {"v": 35},
                        "o3": {"v": 45}
                    }
                }
            }
        """
        params = {
            "lat": latitude,
            "lon": longitude,
            "token": self.api_key
        }
        
        logger.info(f"Fetching pollen data for lat={latitude}, lon={longitude}")
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/feed/geo:{latitude};{longitude}/?token={self.api_key}",
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "ok":
                error_msg = f"Pollen API returned non-ok status: {data.get('status')}"
                logger.error(error_msg)
                raise PollenAPIError(error_msg)
            
            logger.info(f"Successfully fetched pollen data for lat={latitude}, lon={longitude}")
            return data
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Pollen API request failed for lat={latitude}, lon={longitude}: {str(e)}"
            logger.error(error_msg)
            raise PollenAPIError(error_msg) from e
        
        except ValueError as e:
            error_msg = f"Failed to parse pollen API response: {str(e)}"
            logger.error(error_msg)
            raise PollenAPIError(error_msg) from e
    
    def parse_pollen_data(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and normalize pollen API response into standard format.
        
        Args:
            api_response (Dict[str, Any]): Raw response from AQICN API.
        
        Returns:
            Dict[str, Any]: Normalized pollen data with all five pollen types.
        
        Raises:
            PollenAPIError: If response is missing required fields.
        """
        try:
            data = api_response.get("data", {})
            iaqi = data.get("iaqi", {})
            
            # Map AQICN pollutants to pollen types
            # Note: AQICN doesn't directly provide pollen data, so we use PM2.5 as proxy
            # In production, you might use a different API or data source for pollen
            pollen_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "pollen_types": {}
            }
            
            # Initialize all pollen types with default values
            for pollen_type in self.POLLEN_TYPES:
                pollen_data["pollen_types"][pollen_type] = {
                    "concentration": 0,
                    "unit": "gr/m³",
                    "severity": "LOW"
                }
            
            # Extract available data from AQICN response
            # This is a simplified mapping - in production, use actual pollen API
            if "pm25" in iaqi:
                pm25_value = iaqi["pm25"].get("v", 0)
                # Map PM2.5 to pollen severity
                severity = self._get_severity_from_aqi(pm25_value)
                pollen_data["pollen_types"]["grass"]["concentration"] = pm25_value
                pollen_data["pollen_types"]["grass"]["severity"] = severity
            
            logger.debug(f"Parsed pollen data: {pollen_data}")
            return pollen_data
        
        except (KeyError, TypeError) as e:
            error_msg = f"Error parsing pollen data: {str(e)}"
            logger.error(error_msg)
            raise PollenAPIError(error_msg) from e
    
    @staticmethod
    def _get_severity_from_aqi(aqi_value: float) -> str:
        """
        Convert AQI value to severity level.
        
        Args:
            aqi_value (float): AQI value.
        
        Returns:
            str: Severity level (LOW, MODERATE, HIGH).
        """
        if aqi_value < 50:
            return "LOW"
        elif aqi_value < 100:
            return "MODERATE"
        else:
            return "HIGH"


class APIClient:
    """
    Main API client that coordinates weather and pollen data fetching.
    
    This class provides a unified interface for fetching and parsing
    both weather and pollen data with error handling, retry logic,
    and parallel API calls for improved performance.
    """
    
    def __init__(self, weather_api_key: Optional[str] = None, pollen_api_key: Optional[str] = None, 
                 max_retries: int = 3, timeout: int = 10, max_workers: int = 2):
        """
        Initialize the main API client.
        
        Args:
            weather_api_key (Optional[str]): Weatherbit API key for weather data.
            pollen_api_key (Optional[str]): AQICN API key for pollen data.
            max_retries (int): Maximum number of retry attempts. Defaults to 3.
            timeout (int): Request timeout in seconds. Defaults to 10.
            max_workers (int): Maximum number of worker threads for parallel requests. Defaults to 2.
        """
        self.weather_client = WeatherAPIClient(api_key=weather_api_key, max_retries=max_retries, timeout=timeout)
        self.pollen_client = PollenAPIClient(api_key=pollen_api_key, max_retries=max_retries, timeout=timeout)
        self.max_workers = max_workers
        logger.info(f"APIClient initialized with max_workers={max_workers}")
    
    def _fetch_weather_task(self, latitude: float, longitude: float) -> tuple:
        """
        Task for fetching and parsing weather data.
        
        Args:
            latitude (float): Location latitude.
            longitude (float): Location longitude.
        
        Returns:
            tuple: (weather_data, error_message) where one will be None
        """
        try:
            raw_weather = self.weather_client.fetch_weather(latitude, longitude)
            weather_data = self.weather_client.parse_weather_data(raw_weather)
            return weather_data, None
        except WeatherAPIError as e:
            error_msg = str(e)
            logger.error(f"Failed to fetch weather data: {error_msg}")
            return None, error_msg
    
    def _fetch_pollen_task(self, latitude: float, longitude: float) -> tuple:
        """
        Task for fetching and parsing pollen data.
        
        Args:
            latitude (float): Location latitude.
            longitude (float): Location longitude.
        
        Returns:
            tuple: (pollen_data, error_message) where one will be None
        """
        try:
            raw_pollen = self.pollen_client.fetch_pollen(latitude, longitude)
            pollen_data = self.pollen_client.parse_pollen_data(raw_pollen)
            return pollen_data, None
        except PollenAPIError as e:
            error_msg = str(e)
            logger.error(f"Failed to fetch pollen data: {error_msg}")
            return None, error_msg
    
    def fetch_all_data(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Fetch both weather and pollen data for a location using parallel requests.
        
        This method uses ThreadPoolExecutor to fetch weather and pollen data
        concurrently, improving performance by reducing total request time.
        
        Args:
            latitude (float): Location latitude.
            longitude (float): Location longitude.
        
        Returns:
            Dict[str, Any]: Combined weather and pollen data.
        
        Raises:
            APIClientError: If both weather and pollen fetches fail.
        """
        logger.info(f"Fetching all data for lat={latitude}, lon={longitude} using parallel requests")
        
        weather_data = None
        pollen_data = None
        weather_error = None
        pollen_error = None
        
        # Use ThreadPoolExecutor for parallel API calls
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit both tasks concurrently
            weather_future = executor.submit(self._fetch_weather_task, latitude, longitude)
            pollen_future = executor.submit(self._fetch_pollen_task, latitude, longitude)
            
            # Collect results as they complete
            for future in as_completed([weather_future, pollen_future]):
                try:
                    data, error = future.result()
                    
                    # Determine which task completed
                    if future == weather_future:
                        weather_data = data
                        weather_error = error
                    else:
                        pollen_data = data
                        pollen_error = error
                
                except Exception as e:
                    logger.error(f"Unexpected error in parallel fetch: {str(e)}")
                    # Determine which task failed
                    if future == weather_future:
                        weather_error = str(e)
                    else:
                        pollen_error = str(e)
        
        # If both failed, raise error
        if weather_data is None and pollen_data is None:
            error_msg = f"Failed to fetch both weather and pollen data. Weather: {weather_error}, Pollen: {pollen_error}"
            logger.error(error_msg)
            raise APIClientError(error_msg)
        
        # Return combined data
        result = {
            "weather": weather_data,
            "pollen": pollen_data,
            "errors": {
                "weather": weather_error,
                "pollen": pollen_error
            }
        }
        
        logger.info(f"Successfully fetched data for lat={latitude}, lon={longitude}")
        return result
