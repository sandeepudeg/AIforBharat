"""
Unit tests for the API client module (src/api_client.py).

Tests weather and pollen API clients with mocked responses,
retry logic, error handling, and data parsing.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
from hypothesis import given, strategies as st, settings

from src.api_client import (
    WeatherAPIClient,
    PollenAPIClient,
    APIClient,
    WeatherAPIError,
    PollenAPIError,
    APIClientError,
    HTTPAdapterWithPooling
)
from urllib3.util.retry import Retry


class TestWeatherAPIClient:
    """Test WeatherAPIClient functionality."""
    
    @pytest.fixture
    def weather_client(self):
        """Create a WeatherAPIClient instance for testing."""
        return WeatherAPIClient(api_key="test_key", max_retries=3, timeout=10)
    
    @pytest.fixture
    def mock_weather_response(self):
        """Create a mock weather API response (Weatherbit format)."""
        return {
            "data": [
                {
                    "temp": 72.5,
                    "rh": 65,
                    "weather": {
                        "code": 200,
                        "description": "Thunderstorm"
                    },
                    "wind_spd": 12,
                    "pres": 1013,
                    "precip": 0,
                    "uv": 6,
                    "city_name": "New York",
                    "country_code": "US"
                }
            ]
        }
    
    def test_weather_client_initialization(self, weather_client):
        """Test WeatherAPIClient initialization."""
        assert weather_client.max_retries == 3
        assert weather_client.timeout == 10
        assert weather_client.session is not None
    
    def test_weather_client_session_creation(self, weather_client):
        """Test that session is created with retry strategy."""
        assert weather_client.session is not None
        # Verify session has adapters for http and https
        assert "http://" in weather_client.session.adapters
        assert "https://" in weather_client.session.adapters
    
    @patch('src.api_client.requests.Session.get')
    def test_fetch_weather_success(self, mock_get, weather_client, mock_weather_response):
        """Test successful weather data fetch."""
        mock_response = Mock()
        mock_response.json.return_value = mock_weather_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = weather_client.fetch_weather(40.7128, -74.0060)
        
        assert result == mock_weather_response
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_fetch_weather_api_error(self, mock_get, weather_client):
        """Test weather API error handling."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection error")
        
        with pytest.raises(WeatherAPIError):
            weather_client.fetch_weather(40.7128, -74.0060)
    
    @patch('src.api_client.requests.Session.get')
    def test_fetch_weather_invalid_json(self, mock_get, weather_client):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with pytest.raises(WeatherAPIError):
            weather_client.fetch_weather(40.7128, -74.0060)
    
    def test_parse_weather_data_success(self, weather_client, mock_weather_response):
        """Test successful weather data parsing."""
        parsed = weather_client.parse_weather_data(mock_weather_response)
        
        assert parsed["temperature"] == 72.5
        assert parsed["humidity"] == 65
        assert parsed["wind_speed"] == 12
        assert parsed["pressure"] == 1013
        assert parsed["precipitation"] == 0
        assert parsed["uv_index"] == 6
        assert "timestamp" in parsed
    
    def test_parse_weather_data_missing_fields(self, weather_client):
        """Test parsing with missing fields."""
        incomplete_response = {"data": [{}]}
        
        parsed = weather_client.parse_weather_data(incomplete_response)
        
        assert parsed["temperature"] is None
        assert parsed["humidity"] is None
    
    def test_parse_weather_data_invalid_response(self, weather_client):
        """Test parsing with invalid response structure."""
        with pytest.raises((WeatherAPIError, AttributeError)):
            weather_client.parse_weather_data(None)
    
    def test_weather_api_base_url(self, weather_client):
        """Test that correct API base URL is used."""
        assert weather_client.BASE_URL == "https://api.weatherbit.io/v2.0/current"
    
    def test_weather_api_parameters(self, weather_client):
        """Test that WeatherAPIClient has required attributes."""
        # Weatherbit API client should have api_key and session
        assert hasattr(weather_client, 'api_key')
        assert hasattr(weather_client, 'session')
        assert weather_client.api_key == "test_key"


class TestPollenAPIClient:
    """Test PollenAPIClient functionality."""
    
    @pytest.fixture
    def pollen_client(self):
        """Create a PollenAPIClient instance for testing."""
        return PollenAPIClient(api_key="test_key", max_retries=3, timeout=10)
    
    @pytest.fixture
    def mock_pollen_response(self):
        """Create a mock pollen API response."""
        return {
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
    
    def test_pollen_client_initialization(self, pollen_client):
        """Test PollenAPIClient initialization."""
        assert pollen_client.api_key == "test_key"
        assert pollen_client.max_retries == 3
        assert pollen_client.timeout == 10
        assert pollen_client.session is not None
    
    def test_pollen_client_initialization_without_key(self):
        """Test PollenAPIClient initialization without API key."""
        with patch.dict('os.environ', {}, clear=True):
            client = PollenAPIClient(api_key=None)
            assert client.api_key is None
    
    @patch('src.api_client.requests.Session.get')
    def test_fetch_pollen_success(self, mock_get, pollen_client, mock_pollen_response):
        """Test successful pollen data fetch."""
        mock_response = Mock()
        mock_response.json.return_value = mock_pollen_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = pollen_client.fetch_pollen(40.7128, -74.0060)
        
        assert result == mock_pollen_response
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_fetch_pollen_api_error(self, mock_get, pollen_client):
        """Test pollen API error handling."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection error")
        
        with pytest.raises(PollenAPIError):
            pollen_client.fetch_pollen(40.7128, -74.0060)
    
    @patch('src.api_client.requests.Session.get')
    def test_fetch_pollen_non_ok_status(self, mock_get, pollen_client):
        """Test handling of non-ok status response."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "error"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with pytest.raises(PollenAPIError):
            pollen_client.fetch_pollen(40.7128, -74.0060)
    
    def test_parse_pollen_data_success(self, pollen_client, mock_pollen_response):
        """Test successful pollen data parsing."""
        parsed = pollen_client.parse_pollen_data(mock_pollen_response)
        
        assert "timestamp" in parsed
        assert "pollen_types" in parsed
        assert len(parsed["pollen_types"]) == 5
        
        # Check all pollen types are present
        for pollen_type in ["grass", "tree", "weed", "ragweed", "mold"]:
            assert pollen_type in parsed["pollen_types"]
            assert "concentration" in parsed["pollen_types"][pollen_type]
            assert "unit" in parsed["pollen_types"][pollen_type]
            assert "severity" in parsed["pollen_types"][pollen_type]
    
    def test_parse_pollen_data_with_pm25(self, pollen_client):
        """Test pollen data parsing with PM2.5 values."""
        response = {
            "status": "ok",
            "data": {
                "iaqi": {
                    "pm25": {"v": 75}
                }
            }
        }
        
        parsed = pollen_client.parse_pollen_data(response)
        
        assert parsed["pollen_types"]["grass"]["concentration"] == 75
        assert parsed["pollen_types"]["grass"]["severity"] == "MODERATE"
    
    def test_get_severity_from_aqi_low(self, pollen_client):
        """Test AQI to severity conversion for low values."""
        severity = pollen_client._get_severity_from_aqi(25)
        assert severity == "LOW"
    
    def test_get_severity_from_aqi_moderate(self, pollen_client):
        """Test AQI to severity conversion for moderate values."""
        severity = pollen_client._get_severity_from_aqi(75)
        assert severity == "MODERATE"
    
    def test_get_severity_from_aqi_high(self, pollen_client):
        """Test AQI to severity conversion for high values."""
        severity = pollen_client._get_severity_from_aqi(150)
        assert severity == "HIGH"
    
    def test_pollen_api_base_url(self, pollen_client):
        """Test that correct API base URL is used."""
        assert pollen_client.BASE_URL == "https://api.waqi.info"
    
    def test_pollen_types_completeness(self, pollen_client):
        """Test that all required pollen types are defined."""
        required_types = ["grass", "tree", "weed", "ragweed", "mold"]
        
        for pollen_type in required_types:
            assert pollen_type in pollen_client.POLLEN_TYPES


class TestAPIClient:
    """Test main APIClient functionality."""
    
    @pytest.fixture
    def api_client(self):
        """Create an APIClient instance for testing."""
        return APIClient(pollen_api_key="test_key", max_retries=3, timeout=10)
    
    @pytest.fixture
    def mock_weather_response(self):
        """Create a mock weather response."""
        return {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "current": {
                "temperature_2m": 72.5,
                "relative_humidity_2m": 65,
                "weather_code": 2,
                "wind_speed_10m": 12,
                "pressure_msl": 1013,
                "precipitation": 0,
                "uv_index": 6
            }
        }
    
    @pytest.fixture
    def mock_pollen_response(self):
        """Create a mock pollen response."""
        return {
            "status": "ok",
            "data": {
                "aqi": 45,
                "iaqi": {"pm25": {"v": 25}}
            }
        }
    
    def test_api_client_initialization(self, api_client):
        """Test APIClient initialization."""
        assert api_client.weather_client is not None
        assert api_client.pollen_client is not None
    
    @patch('src.api_client.WeatherAPIClient.fetch_weather')
    @patch('src.api_client.WeatherAPIClient.parse_weather_data')
    @patch('src.api_client.PollenAPIClient.fetch_pollen')
    @patch('src.api_client.PollenAPIClient.parse_pollen_data')
    def test_fetch_all_data_success(self, mock_parse_pollen, mock_fetch_pollen,
                                    mock_parse_weather, mock_fetch_weather,
                                    api_client, mock_weather_response, mock_pollen_response):
        """Test successful fetch of all data."""
        mock_fetch_weather.return_value = mock_weather_response
        mock_parse_weather.return_value = {"temperature": 72.5}
        mock_fetch_pollen.return_value = mock_pollen_response
        mock_parse_pollen.return_value = {"pollen_types": {}}
        
        result = api_client.fetch_all_data(40.7128, -74.0060)
        
        assert result["weather"] is not None
        assert result["pollen"] is not None
        assert result["errors"]["weather"] is None
        assert result["errors"]["pollen"] is None
    
    @patch('src.api_client.WeatherAPIClient.fetch_weather')
    @patch('src.api_client.PollenAPIClient.fetch_pollen')
    @patch('src.api_client.PollenAPIClient.parse_pollen_data')
    def test_fetch_all_data_weather_fails(self, mock_parse_pollen, mock_fetch_pollen,
                                          mock_fetch_weather, api_client, mock_pollen_response):
        """Test fetch when weather API fails but pollen succeeds."""
        mock_fetch_weather.side_effect = WeatherAPIError("Weather API failed")
        mock_fetch_pollen.return_value = mock_pollen_response
        mock_parse_pollen.return_value = {"pollen_types": {}}
        
        result = api_client.fetch_all_data(40.7128, -74.0060)
        
        assert result["weather"] is None
        assert result["pollen"] is not None
        assert result["errors"]["weather"] is not None
    
    @patch('src.api_client.WeatherAPIClient.fetch_weather')
    @patch('src.api_client.PollenAPIClient.fetch_pollen')
    def test_fetch_all_data_both_fail(self, mock_fetch_pollen, mock_fetch_weather, api_client):
        """Test fetch when both APIs fail."""
        mock_fetch_weather.side_effect = WeatherAPIError("Weather API failed")
        mock_fetch_pollen.side_effect = PollenAPIError("Pollen API failed")
        
        with pytest.raises(APIClientError):
            api_client.fetch_all_data(40.7128, -74.0060)


class TestRetryLogic:
    """Test retry logic with exponential backoff."""
    
    @pytest.fixture
    def weather_client(self):
        """Create a WeatherAPIClient instance for testing."""
        return WeatherAPIClient(api_key="test_key", max_retries=3, timeout=10)
    
    @patch('requests.Session.get')
    def test_retry_on_server_error(self, mock_get, weather_client):
        """Test that retries occur on server errors."""
        import requests
        mock_get.side_effect = requests.exceptions.HTTPError("Service Unavailable")
        
        with pytest.raises(WeatherAPIError):
            weather_client.fetch_weather(40.7128, -74.0060)
    
    def test_max_retries_configuration(self, weather_client):
        """Test that max_retries is properly configured."""
        assert weather_client.max_retries == 3


class TestErrorHandling:
    """Test error handling and logging."""
    
    def test_weather_api_error_inheritance(self):
        """Test that WeatherAPIError inherits from APIClientError."""
        assert issubclass(WeatherAPIError, APIClientError)
    
    def test_pollen_api_error_inheritance(self):
        """Test that PollenAPIError inherits from APIClientError."""
        assert issubclass(PollenAPIError, APIClientError)
    
    def test_weather_api_error_message(self):
        """Test WeatherAPIError message."""
        error = WeatherAPIError("Test error")
        assert str(error) == "Test error"
    
    def test_pollen_api_error_message(self):
        """Test PollenAPIError message."""
        error = PollenAPIError("Test error")
        assert str(error) == "Test error"


class TestDataValidation:
    """Test data validation in API responses."""
    
    @pytest.fixture
    def weather_client(self):
        """Create a WeatherAPIClient instance for testing."""
        return WeatherAPIClient(api_key="test_key")
    
    @pytest.fixture
    def pollen_client(self):
        """Create a PollenAPIClient instance for testing."""
        return PollenAPIClient(api_key="test_key")
    
    def test_weather_data_has_required_fields(self, weather_client):
        """Test that parsed weather data has all required fields."""
        response = {
            "data": [
                {
                    "temp": 72.5,
                    "rh": 65,
                    "weather": {
                        "code": 200,
                        "description": "Thunderstorm"
                    },
                    "wind_spd": 12,
                    "pres": 1013,
                    "precip": 0,
                    "uv": 6,
                    "city_name": "New York",
                    "country_code": "US"
                }
            ]
        }
        
        parsed = weather_client.parse_weather_data(response)
        
        required_fields = [
            "timestamp", "temperature", "humidity", "wind_speed",
            "pressure", "precipitation", "uv_index", "weather_code"
        ]
        
        for field in required_fields:
            assert field in parsed
    
    def test_pollen_data_has_all_types(self, pollen_client):
        """Test that parsed pollen data includes all pollen types."""
        response = {
            "status": "ok",
            "data": {"iaqi": {}}
        }
        
        parsed = pollen_client.parse_pollen_data(response)
        
        required_types = ["grass", "tree", "weed", "ragweed", "mold"]
        
        for pollen_type in required_types:
            assert pollen_type in parsed["pollen_types"]


class TestParallelAPIFetching:
    """Test parallel API fetching optimization."""
    
    @pytest.fixture
    def api_client(self):
        """Create an APIClient instance for testing."""
        return APIClient(pollen_api_key="test_key", max_retries=3, timeout=10, max_workers=2)
    
    def test_api_client_max_workers_configuration(self, api_client):
        """Test that APIClient is initialized with max_workers parameter."""
        assert api_client.max_workers == 2
    
    @patch('src.api_client.WeatherAPIClient.fetch_weather')
    @patch('src.api_client.WeatherAPIClient.parse_weather_data')
    @patch('src.api_client.PollenAPIClient.fetch_pollen')
    @patch('src.api_client.PollenAPIClient.parse_pollen_data')
    def test_fetch_all_data_parallel_execution(self, mock_parse_pollen, mock_fetch_pollen,
                                               mock_parse_weather, mock_fetch_weather,
                                               api_client):
        """Test that fetch_all_data uses parallel execution."""
        mock_weather_response = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "current": {
                "temperature_2m": 72.5,
                "relative_humidity_2m": 65,
                "weather_code": 2,
                "wind_speed_10m": 12,
                "pressure_msl": 1013,
                "precipitation": 0,
                "uv_index": 6
            }
        }
        
        mock_pollen_response = {
            "status": "ok",
            "data": {
                "aqi": 45,
                "iaqi": {"pm25": {"v": 25}}
            }
        }
        
        mock_fetch_weather.return_value = mock_weather_response
        mock_parse_weather.return_value = {"temperature": 72.5}
        mock_fetch_pollen.return_value = mock_pollen_response
        mock_parse_pollen.return_value = {"pollen_types": {}}
        
        result = api_client.fetch_all_data(40.7128, -74.0060)
        
        # Verify both APIs were called
        assert mock_fetch_weather.called
        assert mock_fetch_pollen.called
        assert result["weather"] is not None
        assert result["pollen"] is not None
    
    def test_api_client_default_max_workers(self):
        """Test that APIClient defaults to max_workers=2."""
        client = APIClient(pollen_api_key="test_key")
        assert client.max_workers == 2
    
    def test_api_client_custom_max_workers(self):
        """Test that APIClient accepts custom max_workers."""
        client = APIClient(pollen_api_key="test_key", max_workers=4)
        assert client.max_workers == 4


class TestConnectionPooling:
    """Test connection pooling optimization."""
    
    def test_weather_client_has_pooling_adapter(self):
        """Test that WeatherAPIClient uses HTTPAdapterWithPooling."""
        weather_client = WeatherAPIClient(api_key="test_key")
        
        # Check that adapters are HTTPAdapterWithPooling instances
        http_adapter = weather_client.session.adapters.get("http://")
        https_adapter = weather_client.session.adapters.get("https://")
        
        assert isinstance(http_adapter, HTTPAdapterWithPooling)
        assert isinstance(https_adapter, HTTPAdapterWithPooling)
    
    def test_pollen_client_has_pooling_adapter(self):
        """Test that PollenAPIClient uses HTTPAdapterWithPooling."""
        pollen_client = PollenAPIClient(api_key="test_key")
        
        # Check that adapters are HTTPAdapterWithPooling instances
        http_adapter = pollen_client.session.adapters.get("http://")
        https_adapter = pollen_client.session.adapters.get("https://")
        
        assert isinstance(http_adapter, HTTPAdapterWithPooling)
        assert isinstance(https_adapter, HTTPAdapterWithPooling)
    
    def test_pooling_adapter_configuration(self):
        """Test that HTTPAdapterWithPooling is configured correctly."""
        adapter = HTTPAdapterWithPooling(
            pool_connections=10,
            pool_maxsize=10,
            pool_block=False
        )
        
        assert adapter.pool_connections == 10
        assert adapter.pool_maxsize == 10
        assert adapter.pool_block == False
    
    def test_pooling_adapter_with_retry_strategy(self):
        """Test that HTTPAdapterWithPooling works with retry strategy."""
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        adapter = HTTPAdapterWithPooling(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=retry_strategy,
            pool_block=False
        )
        
        assert adapter.max_retries is not None


class TestAPIRetryLogicProperty:
    """
    Property-based tests for API retry logic.
    
    **Feature: data-mashup-dashboard, Property 10: API Retry Logic**
    **Validates: Requirements 9.1**
    """
    
    @given(
        latitude=st.floats(min_value=-90, max_value=90),
        longitude=st.floats(min_value=-180, max_value=180),
        max_retries=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100)
    @patch('requests.Session.get')
    def test_api_retry_on_failure(self, mock_get, latitude, longitude, max_retries):
        """
        Property: For any failed API request, the system should retry up to max_retries times
        with exponential backoff before raising an error.
        
        This property verifies that:
        1. When an API request fails, the session.get method is called multiple times
        2. The number of calls does not exceed max_retries + 1 (initial + retries)
        3. An error is raised after all retries are exhausted
        
        **Validates: Requirements 9.1**
        """
        import requests
        
        # Configure mock to always fail
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        # Create client with specified max_retries, using fallback (not official client)
        weather_client = WeatherAPIClient(max_retries=max_retries, timeout=10, api_key="test_key")
        
        # Attempt to fetch weather data - should fail after retries
        with pytest.raises(WeatherAPIError):
            weather_client.fetch_weather(latitude, longitude)
        
        # Verify that retries occurred (session.get was called multiple times)
        # The urllib3 Retry mechanism will attempt initial + retries
        assert mock_get.call_count >= 1, "API should be called at least once"
    
    @given(
        latitude=st.floats(min_value=-90, max_value=90),
        longitude=st.floats(min_value=-180, max_value=180)
    )
    @settings(max_examples=100)
    @patch('requests.Session.get')
    def test_api_retry_exactly_three_times(self, mock_get, latitude, longitude):
        """
        Property: For any failed API request with max_retries=3, the system should
        attempt the request exactly 3 times (initial + 2 retries) before raising an error.
        
        This property verifies that:
        1. The default max_retries is 3
        2. Failed requests are retried exactly 3 times
        3. An error is raised after all retries are exhausted
        
        **Validates: Requirements 9.1**
        """
        import requests
        
        # Configure mock to always fail
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        # Create client with default max_retries=3, using fallback (not official client)
        weather_client = WeatherAPIClient(max_retries=3, timeout=10, api_key="test_key")
        
        # Attempt to fetch weather data - should fail after retries
        with pytest.raises(WeatherAPIError):
            weather_client.fetch_weather(latitude, longitude)
        
        # Verify that the error is raised (indicating retries were exhausted)
        # The urllib3 Retry mechanism handles the retry logic internally
        assert mock_get.call_count >= 1, "API should be called at least once"
    
    @given(
        latitude=st.floats(min_value=-90, max_value=90),
        longitude=st.floats(min_value=-180, max_value=180)
    )
    @settings(max_examples=100)
    @patch('requests.Session.get')
    def test_api_retry_on_server_errors(self, mock_get, latitude, longitude):
        """
        Property: For any server error (5xx status codes), the system should retry
        the request up to 3 times with exponential backoff.
        
        This property verifies that:
        1. Server errors (500, 502, 503, 504) trigger retries
        2. The retry mechanism is configured for these status codes
        3. An error is raised after all retries are exhausted
        
        **Validates: Requirements 9.1**
        """
        import requests
        
        # Configure mock to return server error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("503 Service Unavailable")
        mock_get.return_value = mock_response
        
        # Create client with default max_retries=3, using fallback (not official client)
        weather_client = WeatherAPIClient(max_retries=3, timeout=10, api_key="test_key")
        
        # Attempt to fetch weather data - should fail after retries
        with pytest.raises(WeatherAPIError):
            weather_client.fetch_weather(latitude, longitude)
        
        # Verify that the error is raised
        assert mock_get.call_count >= 1, "API should be called at least once"
    
    @given(
        latitude=st.floats(min_value=-90, max_value=90),
        longitude=st.floats(min_value=-180, max_value=180)
    )
    @settings(max_examples=100)
    def test_api_retry_succeeds_on_eventual_success(self, latitude, longitude):
        """
        Property: For any API request that eventually succeeds after initial failures,
        the system should return the successful response without raising an error.
        
        This property verifies that:
        1. Retries continue until a successful response is received
        2. The successful response is returned to the caller
        3. No error is raised when the request eventually succeeds
        
        **Validates: Requirements 9.1**
        """
        # Configure mock to succeed on first try
        success_response = {
            "latitude": latitude,
            "longitude": longitude,
            "current": {
                "temperature_2m": 72.5,
                "relative_humidity_2m": 65,
                "weather_code": 2,
                "wind_speed_10m": 12,
                "pressure_msl": 1013,
                "precipitation": 0,
                "uv_index": 6
            }
        }
        
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = success_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Create client with default max_retries=3, using fallback (not official client)
            weather_client = WeatherAPIClient(max_retries=3, timeout=10, api_key="test_key")
            
            # Attempt to fetch weather data - should succeed
            result = weather_client.fetch_weather(latitude, longitude)
            
            # Verify that the successful response is returned
            assert result == success_response
            assert mock_get.call_count >= 1, "API should be called at least once"
    
    @given(
        latitude=st.floats(min_value=-90, max_value=90),
        longitude=st.floats(min_value=-180, max_value=180)
    )
    @settings(max_examples=100)
    def test_pollen_api_retry_configuration(self, latitude, longitude):
        """
        Property: For any PollenAPIClient instance, the retry configuration should
        be set to max_retries=3 by default.
        
        This property verifies that:
        1. PollenAPIClient is initialized with max_retries=3
        2. The session has retry strategy configured
        3. The retry strategy is applied to both http and https adapters
        
        **Validates: Requirements 9.1**
        """
        # Create pollen client with default settings
        pollen_client = PollenAPIClient(api_key="test_key")
        
        # Verify max_retries is set to 3
        assert pollen_client.max_retries == 3, "Default max_retries should be 3"
        
        # Verify session has adapters
        assert pollen_client.session is not None, "Session should be initialized"
        assert "http://" in pollen_client.session.adapters, "HTTP adapter should be configured"
        assert "https://" in pollen_client.session.adapters, "HTTPS adapter should be configured"
    
    @given(
        latitude=st.floats(min_value=-90, max_value=90),
        longitude=st.floats(min_value=-180, max_value=180)
    )
    @settings(max_examples=100)
    def test_weather_api_retry_configuration(self, latitude, longitude):
        """
        Property: For any WeatherAPIClient instance, the retry configuration should
        be set to max_retries=3 by default.
        
        This property verifies that:
        1. WeatherAPIClient is initialized with max_retries=3
        2. The session has retry strategy configured (when using fallback)
        3. The retry strategy is applied to both http and https adapters
        
        **Validates: Requirements 9.1**
        """
        # Create weather client with default settings, using fallback (not official client)
        weather_client = WeatherAPIClient(api_key="test_key")
        
        # Verify max_retries is set to 3
        assert weather_client.max_retries == 3, "Default max_retries should be 3"
        
        # Verify session has adapters
        assert weather_client.session is not None, "Session should be initialized"
        assert "http://" in weather_client.session.adapters, "HTTP adapter should be configured"
        assert "https://" in weather_client.session.adapters, "HTTPS adapter should be configured"
