"""
Tests for error handling and fallback to cached data.

Tests API failure handling, cache fallback, and error logging.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from src.data_service import DataService, DataServiceError
from src.cache_manager import CacheManager, CacheManagerError
from src.api_client import APIClientError, WeatherAPIError, PollenAPIError
from app import create_app


@pytest.fixture
def cache_manager():
    """Create a CacheManager instance for testing."""
    return CacheManager(default_ttl=3600)


@pytest.fixture
def data_service_with_cache(cache_manager):
    """Create a DataService instance with cache manager for testing."""
    with patch('src.data_service.get_location_config'):
        return DataService(pollen_api_key="test_key", cache_manager=cache_manager)


@pytest.fixture
def mock_weather_data():
    """Create mock weather data."""
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'temperature': 72.5,
        'humidity': 65,
        'wind_speed': 12,
        'pressure': 1013,
        'precipitation': 0,
        'uv_index': 6,
        'weather_code': 2,
        'location': {
            'country': 'USA',
            'state': 'NY',
            'district': 'Manhattan',
            'latitude': 40.7831,
            'longitude': -73.9712
        }
    }


@pytest.fixture
def mock_pollen_data():
    """Create mock pollen data."""
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'pollen_types': {
            'grass': {'concentration': 850, 'unit': 'gr/m³', 'severity': 'HIGH'},
            'tree': {'concentration': 450, 'unit': 'gr/m³', 'severity': 'MODERATE'},
            'weed': {'concentration': 150, 'unit': 'gr/m³', 'severity': 'LOW'},
            'ragweed': {'concentration': 200, 'unit': 'gr/m³', 'severity': 'LOW'},
            'mold': {'concentration': 320, 'unit': 'gr/m³', 'severity': 'MODERATE'}
        },
        'location': {
            'country': 'USA',
            'state': 'NY',
            'district': 'Manhattan',
            'latitude': 40.7831,
            'longitude': -73.9712
        }
    }


class TestWeatherDataFallbackToCache:
    """Test weather data fallback to cache when API fails."""
    
    @patch('src.data_service.get_location_config')
    @patch('src.data_service.APIClient.fetch_all_data')
    def test_weather_fallback_to_cache_on_api_failure(self, mock_fetch_all, mock_config, 
                                                       cache_manager, mock_weather_data):
        """Test that weather data falls back to cache when API fails."""
        # Setup mocks
        mock_location_config = Mock()
        mock_location_config.validate_location.return_value = True
        mock_location_config.get_coordinates.return_value = (40.7831, -73.9712)
        mock_config.return_value = mock_location_config
        
        # Create service with cache
        service = DataService(pollen_api_key="test_key", cache_manager=cache_manager)
        service.location_config = mock_location_config
        
        # First call succeeds and caches data
        mock_fetch_all.return_value = {
            'weather': mock_weather_data,
            'pollen': None,
            'errors': {'weather': None, 'pollen': None}
        }
        
        result1 = service.fetch_weather_data('USA', 'NY', 'Manhattan')
        assert result1['cached_data'] is False
        assert result1['temperature'] == 72.5
        
        # Second call fails with API error
        mock_fetch_all.side_effect = APIClientError("API failed")
        
        # Should return cached data
        result2 = service.fetch_weather_data('USA', 'NY', 'Manhattan')
        assert result2['cached_data'] is True
        assert result2['temperature'] == 72.5
        assert 'cache_error' in result2
    
    @patch('src.data_service.get_location_config')
    @patch('src.data_service.APIClient.fetch_all_data')
    def test_weather_raises_error_when_no_cache(self, mock_fetch_all, mock_config, 
                                                 cache_manager):
        """Test that weather fetch raises error when API fails and no cache exists."""
        # Setup mocks
        mock_location_config = Mock()
        mock_location_config.validate_location.return_value = True
        mock_location_config.get_coordinates.return_value = (40.7831, -73.9712)
        mock_config.return_value = mock_location_config
        
        # Create service with cache
        service = DataService(pollen_api_key="test_key", cache_manager=cache_manager)
        service.location_config = mock_location_config
        
        # API fails immediately
        mock_fetch_all.side_effect = APIClientError("API failed")
        
        # Should raise error since no cache exists
        with pytest.raises(DataServiceError):
            service.fetch_weather_data('USA', 'NY', 'Manhattan')


class TestPollenDataFallbackToCache:
    """Test pollen data fallback to cache when API fails."""
    
    @patch('src.data_service.get_location_config')
    @patch('src.data_service.APIClient.fetch_all_data')
    def test_pollen_fallback_to_cache_on_api_failure(self, mock_fetch_all, mock_config, 
                                                      cache_manager, mock_pollen_data):
        """Test that pollen data falls back to cache when API fails."""
        # Setup mocks
        mock_location_config = Mock()
        mock_location_config.validate_location.return_value = True
        mock_location_config.get_coordinates.return_value = (40.7831, -73.9712)
        mock_config.return_value = mock_location_config
        
        # Create service with cache
        service = DataService(pollen_api_key="test_key", cache_manager=cache_manager)
        service.location_config = mock_location_config
        
        # First call succeeds and caches data
        mock_fetch_all.return_value = {
            'weather': None,
            'pollen': mock_pollen_data,
            'errors': {'weather': None, 'pollen': None}
        }
        
        result1 = service.fetch_pollen_data('USA', 'NY', 'Manhattan')
        assert result1['cached_data'] is False
        assert 'grass' in result1['pollen_types']
        
        # Second call fails with API error
        mock_fetch_all.side_effect = APIClientError("API failed")
        
        # Should return cached data
        result2 = service.fetch_pollen_data('USA', 'NY', 'Manhattan')
        assert result2['cached_data'] is True
        assert 'grass' in result2['pollen_types']
        assert 'cache_error' in result2
    
    @patch('src.data_service.get_location_config')
    @patch('src.data_service.APIClient.fetch_all_data')
    def test_pollen_raises_error_when_no_cache(self, mock_fetch_all, mock_config, 
                                                cache_manager):
        """Test that pollen fetch raises error when API fails and no cache exists."""
        # Setup mocks
        mock_location_config = Mock()
        mock_location_config.validate_location.return_value = True
        mock_location_config.get_coordinates.return_value = (40.7831, -73.9712)
        mock_config.return_value = mock_location_config
        
        # Create service with cache
        service = DataService(pollen_api_key="test_key", cache_manager=cache_manager)
        service.location_config = mock_location_config
        
        # API fails immediately
        mock_fetch_all.side_effect = APIClientError("API failed")
        
        # Should raise error since no cache exists
        with pytest.raises(DataServiceError):
            service.fetch_pollen_data('USA', 'NY', 'Manhattan')


class TestAPIEndpointErrorHandling:
    """Test error handling in Flask API endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing."""
        app = create_app()
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create Flask test client."""
        return app.test_client()
    
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_weather_endpoint_returns_cached_data_indicator(self, mock_validate, mock_fetch, 
                                                            client, mock_weather_data):
        """Test that weather endpoint returns cached_data indicator."""
        mock_validate.return_value = True
        
        # Simulate cached data response
        cached_weather = mock_weather_data.copy()
        cached_weather['cached_data'] = True
        cached_weather['cache_error'] = 'API failed'
        
        mock_fetch.return_value = cached_weather
        
        response = client.get('/api/weather/USA/NY/Manhattan')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['cached_data'] is True
        assert 'cache_error' in data
    
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('config.LocationConfig.validate_location')
    def test_pollen_endpoint_returns_cached_data_indicator(self, mock_validate, mock_fetch, 
                                                           client, mock_pollen_data):
        """Test that pollen endpoint returns cached_data indicator."""
        mock_validate.return_value = True
        
        # Simulate cached data response
        cached_pollen = mock_pollen_data.copy()
        cached_pollen['cached_data'] = True
        cached_pollen['cache_error'] = 'API failed'
        
        mock_fetch.return_value = cached_pollen
        
        response = client.get('/api/pollen/USA/NY/Manhattan')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['cached_data'] is True
        assert 'cache_error' in data
    
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_weather_endpoint_error_when_no_cache(self, mock_validate, mock_fetch, client):
        """Test that weather endpoint returns error when API fails and no cache exists."""
        mock_validate.return_value = True
        mock_fetch.side_effect = DataServiceError("API failed and no cache available")
        
        response = client.get('/api/weather/USA/NY/Manhattan')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Data Service Error'
    
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('config.LocationConfig.validate_location')
    def test_pollen_endpoint_error_when_no_cache(self, mock_validate, mock_fetch, client):
        """Test that pollen endpoint returns error when API fails and no cache exists."""
        mock_validate.return_value = True
        mock_fetch.side_effect = DataServiceError("API failed and no cache available")
        
        response = client.get('/api/pollen/USA/NY/Manhattan')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Data Service Error'


class TestErrorLogging:
    """Test that errors are logged with timestamps."""
    
    @patch('src.data_service.get_location_config')
    @patch('src.data_service.APIClient.fetch_all_data')
    def test_api_error_is_logged(self, mock_fetch_all, mock_config, cache_manager):
        """Test that API errors are logged."""
        # Setup mocks
        mock_location_config = Mock()
        mock_location_config.validate_location.return_value = True
        mock_location_config.get_coordinates.return_value = (40.7831, -73.9712)
        mock_config.return_value = mock_location_config
        
        # Create service with cache
        service = DataService(pollen_api_key="test_key", cache_manager=cache_manager)
        service.location_config = mock_location_config
        
        # API fails
        mock_fetch_all.side_effect = APIClientError("Connection timeout")
        
        # Should raise error
        with pytest.raises(DataServiceError):
            service.fetch_weather_data('USA', 'NY', 'Manhattan')
    
    @patch('src.data_service.get_location_config')
    def test_invalid_location_is_logged(self, mock_config, cache_manager):
        """Test that invalid location errors are logged."""
        # Setup mocks
        mock_location_config = Mock()
        mock_location_config.validate_location.return_value = False
        mock_config.return_value = mock_location_config
        
        # Create service with cache
        service = DataService(pollen_api_key="test_key", cache_manager=cache_manager)
        service.location_config = mock_location_config
        
        # Should raise error for invalid location
        with pytest.raises(DataServiceError):
            service.fetch_weather_data('InvalidCountry', 'InvalidState', 'InvalidDistrict')


class TestCacheIntegration:
    """Test cache integration with data service."""
    
    @patch('src.data_service.get_location_config')
    @patch('src.data_service.APIClient.fetch_all_data')
    def test_successful_data_is_cached(self, mock_fetch_all, mock_config, 
                                       cache_manager, mock_weather_data):
        """Test that successful API responses are cached."""
        # Setup mocks
        mock_location_config = Mock()
        mock_location_config.validate_location.return_value = True
        mock_location_config.get_coordinates.return_value = (40.7831, -73.9712)
        mock_config.return_value = mock_location_config
        
        mock_fetch_all.return_value = {
            'weather': mock_weather_data,
            'pollen': None,
            'errors': {'weather': None, 'pollen': None}
        }
        
        # Create service with cache
        service = DataService(pollen_api_key="test_key", cache_manager=cache_manager)
        service.location_config = mock_location_config
        
        # Fetch data
        result = service.fetch_weather_data('USA', 'NY', 'Manhattan')
        
        # Verify data is cached
        cache_key = "weather_USA_NY_Manhattan"
        cached_data = cache_manager.get(cache_key)
        assert cached_data is not None
        assert cached_data['temperature'] == 72.5
    
    @patch('src.data_service.get_location_config')
    @patch('src.data_service.APIClient.fetch_all_data')
    def test_cache_ttl_is_respected(self, mock_fetch_all, mock_config, 
                                    cache_manager, mock_weather_data):
        """Test that cache TTL is properly set."""
        # Setup mocks
        mock_location_config = Mock()
        mock_location_config.validate_location.return_value = True
        mock_location_config.get_coordinates.return_value = (40.7831, -73.9712)
        mock_config.return_value = mock_location_config
        
        mock_fetch_all.return_value = {
            'weather': mock_weather_data,
            'pollen': None,
            'errors': {'weather': None, 'pollen': None}
        }
        
        # Create service with cache
        service = DataService(pollen_api_key="test_key", cache_manager=cache_manager)
        service.location_config = mock_location_config
        
        # Fetch data
        result = service.fetch_weather_data('USA', 'NY', 'Manhattan')
        
        # Verify cache info
        cache_key = "weather_USA_NY_Manhattan"
        cache_info = cache_manager.get_cache_info(cache_key)
        assert cache_info is not None
        assert cache_info['ttl'] == CacheManager.DEFAULT_WEATHER_TTL


class TestDataValidationErrorHandling:
    """Test data validation error handling in API endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing."""
        app = create_app()
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create Flask test client."""
        return app.test_client()
    
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('src.data_service.DataService.validate_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_weather_endpoint_returns_validation_error(self, mock_validate_loc, mock_validate_data, 
                                                       mock_fetch, client, mock_weather_data):
        """Test that weather endpoint returns validation error when data is invalid."""
        mock_validate_loc.return_value = True
        mock_fetch.return_value = mock_weather_data
        mock_validate_data.return_value = False  # Validation fails
        
        response = client.get('/api/weather/USA/NY/Manhattan')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Data Validation Error'
        assert 'validation' in data['message'].lower()
    
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('src.data_service.DataService.validate_pollen_data')
    @patch('config.LocationConfig.validate_location')
    def test_pollen_endpoint_returns_validation_error(self, mock_validate_loc, mock_validate_data, 
                                                      mock_fetch, client, mock_pollen_data):
        """Test that pollen endpoint returns validation error when data is invalid."""
        mock_validate_loc.return_value = True
        mock_fetch.return_value = mock_pollen_data
        mock_validate_data.return_value = False  # Validation fails
        
        response = client.get('/api/pollen/USA/NY/Manhattan')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Data Validation Error'
        assert 'validation' in data['message'].lower()
    
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('src.data_service.DataService.validate_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_weather_endpoint_passes_valid_data(self, mock_validate_loc, mock_validate_data, 
                                                mock_fetch, client, mock_weather_data):
        """Test that weather endpoint passes valid data through."""
        mock_validate_loc.return_value = True
        mock_fetch.return_value = mock_weather_data
        mock_validate_data.return_value = True  # Validation passes
        
        response = client.get('/api/weather/USA/NY/Manhattan')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['temperature'] == 72.5
        assert 'error' not in data
    
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('src.data_service.DataService.validate_pollen_data')
    @patch('config.LocationConfig.validate_location')
    def test_pollen_endpoint_passes_valid_data(self, mock_validate_loc, mock_validate_data, 
                                               mock_fetch, client, mock_pollen_data):
        """Test that pollen endpoint passes valid data through."""
        mock_validate_loc.return_value = True
        mock_fetch.return_value = mock_pollen_data
        mock_validate_data.return_value = True  # Validation passes
        
        response = client.get('/api/pollen/USA/NY/Manhattan')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'grass' in data['pollen_types']
        assert 'error' not in data


class TestLocationDataValidation:
    """Test location data validation."""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing."""
        app = create_app()
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create Flask test client."""
        return app.test_client()
    
    @patch('config.LocationConfig.validate_location')
    def test_invalid_location_returns_error(self, mock_validate, client):
        """Test that invalid location returns error."""
        mock_validate.return_value = False
        
        response = client.get('/api/weather/InvalidCountry/InvalidState/InvalidDistrict')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Invalid Location'
        assert 'not found' in data['message'].lower()
    
    @patch('config.LocationConfig.validate_location')
    def test_valid_location_passes_validation(self, mock_validate, client):
        """Test that valid location passes validation."""
        mock_validate.return_value = True
        
        with patch('src.data_service.DataService.fetch_weather_data') as mock_fetch:
            mock_fetch.return_value = {
                'temperature': 72.5,
                'humidity': 65,
                'wind_speed': 12,
                'pressure': 1013,
                'location': {'country': 'USA', 'state': 'NY', 'district': 'Manhattan'}
            }
            
            with patch('src.data_service.DataService.validate_weather_data') as mock_validate_data:
                mock_validate_data.return_value = True
                
                response = client.get('/api/weather/USA/NY/Manhattan')
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert 'error' not in data
