"""
Tests for Flask API endpoints.

Tests the weather, pollen, and correlation API endpoints.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from app import create_app


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


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


class TestDashboardRoute:
    """Test dashboard route."""
    
    def test_dashboard_route_returns_200(self, client):
        """Test that dashboard route returns 200 status."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_dashboard_route_returns_html(self, client):
        """Test that dashboard route returns HTML content."""
        response = client.get('/')
        assert response.status_code == 200
        # Should contain HTML content
        assert b'<!DOCTYPE' in response.data or b'<html' in response.data or b'<body' in response.data


class TestHealthCheckRoute:
    """Test health check route."""
    
    def test_health_check_returns_200(self, client):
        """Test that health check returns 200 status."""
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_health_check_returns_json(self, client):
        """Test that health check returns JSON."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'
    
    def test_health_check_contains_timestamp(self, client):
        """Test that health check response contains timestamp."""
        response = client.get('/health')
        data = json.loads(response.data)
        assert 'timestamp' in data


class TestWeatherEndpoint:
    """Test weather API endpoint."""
    
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_weather_endpoint_success(self, mock_validate, mock_fetch, client, mock_weather_data):
        """Test successful weather endpoint call."""
        mock_validate.return_value = True
        mock_fetch.return_value = mock_weather_data
        
        response = client.get('/api/weather/USA/NY/Manhattan')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['temperature'] == 72.5
        assert data['humidity'] == 65
    
    @patch('config.LocationConfig.validate_location')
    def test_weather_endpoint_invalid_location(self, mock_validate, client):
        """Test weather endpoint with invalid location."""
        mock_validate.return_value = False
        
        response = client.get('/api/weather/InvalidCountry/InvalidState/InvalidDistrict')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Invalid Location'
    
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_weather_endpoint_api_error(self, mock_validate, mock_fetch, client):
        """Test weather endpoint when API fails."""
        from src.data_service import DataServiceError
        
        mock_validate.return_value = True
        mock_fetch.side_effect = DataServiceError("API failed")
        
        response = client.get('/api/weather/USA/NY/Manhattan')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data


class TestPollenEndpoint:
    """Test pollen API endpoint."""
    
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('config.LocationConfig.validate_location')
    def test_pollen_endpoint_success(self, mock_validate, mock_fetch, client, mock_pollen_data):
        """Test successful pollen endpoint call."""
        mock_validate.return_value = True
        mock_fetch.return_value = mock_pollen_data
        
        response = client.get('/api/pollen/USA/NY/Manhattan')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'pollen_types' in data
        assert 'grass' in data['pollen_types']
    
    @patch('config.LocationConfig.validate_location')
    def test_pollen_endpoint_invalid_location(self, mock_validate, client):
        """Test pollen endpoint with invalid location."""
        mock_validate.return_value = False
        
        response = client.get('/api/pollen/InvalidCountry/InvalidState/InvalidDistrict')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Invalid Location'
    
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('config.LocationConfig.validate_location')
    def test_pollen_endpoint_api_error(self, mock_validate, mock_fetch, client):
        """Test pollen endpoint when API fails."""
        from src.data_service import DataServiceError
        
        mock_validate.return_value = True
        mock_fetch.side_effect = DataServiceError("API failed")
        
        response = client.get('/api/pollen/USA/NY/Manhattan')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data


class TestCorrelationEndpoint:
    """Test correlation API endpoint."""
    
    @patch('src.correlation_calculator.CorrelationCalculator.calculate_all_correlations')
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_correlation_endpoint_success(self, mock_validate, mock_fetch_weather, mock_fetch_pollen, 
                                         mock_calc_corr, client, mock_weather_data, mock_pollen_data):
        """Test successful correlation endpoint call."""
        mock_validate.return_value = True
        mock_fetch_weather.return_value = mock_weather_data
        mock_fetch_pollen.return_value = mock_pollen_data
        mock_calc_corr.return_value = [
            {
                'weather_factor': 'temperature',
                'pollen_type': 'grass',
                'correlation_coefficient': 0.78,
                'strength': 'Strong Positive',
                'explanation': 'Higher temperatures increase grass pollen production'
            }
        ]
        
        response = client.get('/api/correlation/USA/NY/Manhattan')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'correlations' in data
        assert 'location' in data
        assert len(data['correlations']) > 0
    
    @patch('config.LocationConfig.validate_location')
    def test_correlation_endpoint_invalid_location(self, mock_validate, client):
        """Test correlation endpoint with invalid location."""
        mock_validate.return_value = False
        
        response = client.get('/api/correlation/InvalidCountry/InvalidState/InvalidDistrict')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Invalid Location'
    
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_correlation_endpoint_api_error(self, mock_validate, mock_fetch_weather, mock_fetch_pollen, client):
        """Test correlation endpoint when API fails."""
        from src.data_service import DataServiceError
        
        mock_validate.return_value = True
        mock_fetch_weather.side_effect = DataServiceError("API failed")
        
        response = client.get('/api/correlation/USA/NY/Manhattan')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data


class TestExportEndpoint:
    """Test export API endpoint."""
    
    @patch('src.correlation_calculator.CorrelationCalculator.calculate_all_correlations')
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_export_endpoint_success(self, mock_validate, mock_fetch_weather, mock_fetch_pollen,
                                     mock_calc_corr, client, mock_weather_data, mock_pollen_data):
        """Test successful export endpoint call."""
        mock_validate.return_value = True
        mock_fetch_weather.return_value = mock_weather_data
        mock_fetch_pollen.return_value = mock_pollen_data
        mock_calc_corr.return_value = [
            {
                'weather_factor': 'temperature',
                'pollen_type': 'grass',
                'correlation_coefficient': 0.78,
                'strength': 'Strong Positive',
                'explanation': 'Higher temperatures increase grass pollen production'
            }
        ]
        
        request_body = {
            'country': 'USA',
            'state': 'NY',
            'district': 'Manhattan'
        }
        
        response = client.post('/api/export', json=request_body)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'export_timestamp' in data
        assert 'location' in data
        assert 'weather' in data
        assert 'pollen' in data
        assert 'correlations' in data
        assert 'metadata' in data
        assert data['location']['country'] == 'USA'
        assert data['location']['state'] == 'NY'
        assert data['location']['district'] == 'Manhattan'
    
    @patch('config.LocationConfig.validate_location')
    def test_export_endpoint_invalid_location(self, mock_validate, client):
        """Test export endpoint with invalid location."""
        mock_validate.return_value = False
        
        request_body = {
            'country': 'InvalidCountry',
            'state': 'InvalidState',
            'district': 'InvalidDistrict'
        }
        
        response = client.post('/api/export', json=request_body)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Invalid Location'
    
    def test_export_endpoint_missing_body(self, client):
        """Test export endpoint with missing request body."""
        response = client.post('/api/export')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Bad Request'
    
    def test_export_endpoint_missing_country(self, client):
        """Test export endpoint with missing country parameter."""
        request_body = {
            'state': 'NY',
            'district': 'Manhattan'
        }
        
        response = client.post('/api/export', json=request_body)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Bad Request'
    
    def test_export_endpoint_missing_state(self, client):
        """Test export endpoint with missing state parameter."""
        request_body = {
            'country': 'USA',
            'district': 'Manhattan'
        }
        
        response = client.post('/api/export', json=request_body)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Bad Request'
    
    def test_export_endpoint_missing_district(self, client):
        """Test export endpoint with missing district parameter."""
        request_body = {
            'country': 'USA',
            'state': 'NY'
        }
        
        response = client.post('/api/export', json=request_body)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Bad Request'
    
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_export_endpoint_api_error(self, mock_validate, mock_fetch_weather, client):
        """Test export endpoint when API fails."""
        from src.data_service import DataServiceError
        
        mock_validate.return_value = True
        mock_fetch_weather.side_effect = DataServiceError("API failed")
        
        request_body = {
            'country': 'USA',
            'state': 'NY',
            'district': 'Manhattan'
        }
        
        response = client.post('/api/export', json=request_body)
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('src.correlation_calculator.CorrelationCalculator.calculate_all_correlations')
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_export_endpoint_contains_all_required_fields(self, mock_validate, mock_fetch_weather,
                                                          mock_fetch_pollen, mock_calc_corr, client,
                                                          mock_weather_data, mock_pollen_data):
        """Test that export endpoint returns all required fields."""
        mock_validate.return_value = True
        mock_fetch_weather.return_value = mock_weather_data
        mock_fetch_pollen.return_value = mock_pollen_data
        mock_calc_corr.return_value = []
        
        request_body = {
            'country': 'USA',
            'state': 'NY',
            'district': 'Manhattan'
        }
        
        response = client.post('/api/export', json=request_body)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify all required top-level fields
        assert 'export_timestamp' in data
        assert 'location' in data
        assert 'weather' in data
        assert 'pollen' in data
        assert 'correlations' in data
        assert 'metadata' in data
        
        # Verify metadata structure
        metadata = data['metadata']
        assert 'data_sources' in metadata
        assert 'export_format' in metadata
        assert 'version' in metadata
        assert metadata['export_format'] == 'JSON'
        
        # Verify weather data is included
        weather = data['weather']
        assert 'temperature' in weather
        assert 'humidity' in weather
        assert 'wind_speed' in weather
        
        # Verify pollen data is included
        pollen = data['pollen']
        assert 'pollen_types' in pollen
        assert 'grass' in pollen['pollen_types']


class TestLocationsEndpoint:
    """Test locations API endpoint."""
    
    def test_locations_endpoint_returns_all_countries(self, client):
        """Test that locations endpoint returns all countries when no filters provided."""
        response = client.get('/api/locations')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'countries' in data
        assert isinstance(data['countries'], list)
        assert len(data['countries']) > 0
        
        # Verify country structure
        for country in data['countries']:
            assert 'code' in country
            assert 'name' in country
    
    def test_locations_endpoint_filter_by_country(self, client):
        """Test locations endpoint with country filter."""
        response = client.get('/api/locations?country=USA')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'country' in data
        assert data['country'] == 'USA'
        assert 'states' in data
        assert isinstance(data['states'], list)
        assert len(data['states']) > 0
        
        # Verify state structure
        for state in data['states']:
            assert 'code' in state
            assert 'name' in state
    
    def test_locations_endpoint_filter_by_country_and_state(self, client):
        """Test locations endpoint with country and state filters."""
        response = client.get('/api/locations?country=USA&state=NY')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'country' in data
        assert data['country'] == 'USA'
        assert 'state' in data
        assert data['state'] == 'NY'
        assert 'districts' in data
        assert isinstance(data['districts'], list)
        assert len(data['districts']) > 0
    
    def test_locations_endpoint_invalid_country(self, client):
        """Test locations endpoint with invalid country."""
        response = client.get('/api/locations?country=InvalidCountry')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Not Found'
    
    def test_locations_endpoint_invalid_state(self, client):
        """Test locations endpoint with invalid state."""
        response = client.get('/api/locations?country=USA&state=InvalidState')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Not Found'
    
    def test_locations_endpoint_state_without_country(self, client):
        """Test locations endpoint with state filter but no country filter."""
        response = client.get('/api/locations?state=NY')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Bad Request'
    
    def test_locations_endpoint_returns_valid_countries(self, client):
        """Test that locations endpoint returns expected countries."""
        response = client.get('/api/locations')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        countries = data['countries']
        country_codes = [c['code'] for c in countries]
        
        # Verify expected countries are present
        assert 'USA' in country_codes
        assert 'India' in country_codes
        assert 'UK' in country_codes
        assert 'Canada' in country_codes
    
    def test_locations_endpoint_returns_valid_states_for_usa(self, client):
        """Test that locations endpoint returns expected states for USA."""
        response = client.get('/api/locations?country=USA')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        states = data['states']
        state_codes = [s['code'] for s in states]
        
        # Verify expected states are present
        assert 'NY' in state_codes
        assert 'CA' in state_codes
        assert 'TX' in state_codes
    
    def test_locations_endpoint_returns_valid_districts_for_ny(self, client):
        """Test that locations endpoint returns expected districts for NY."""
        response = client.get('/api/locations?country=USA&state=NY')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        districts = data['districts']
        
        # Verify expected districts are present
        assert 'Manhattan' in districts
        assert 'Brooklyn' in districts
        assert 'Queens' in districts
    
    def test_locations_endpoint_returns_valid_districts_for_india(self, client):
        """Test that locations endpoint returns expected districts for India."""
        response = client.get('/api/locations?country=India&state=MH')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        districts = data['districts']
        
        # Verify expected districts are present
        assert 'Mumbai' in districts
        assert 'Pune' in districts
        assert 'Nagpur' in districts


class TestErrorHandling:
    """Test error handling in endpoints."""
    
    def test_404_not_found(self, client):
        """Test 404 error handling."""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_weather_endpoint_url_format(self, client):
        """Test weather endpoint URL format validation."""
        # Missing district parameter
        response = client.get('/api/weather/USA/NY')
        assert response.status_code == 404
    
    def test_pollen_endpoint_url_format(self, client):
        """Test pollen endpoint URL format validation."""
        # Missing district parameter
        response = client.get('/api/pollen/USA/NY')
        assert response.status_code == 404
    
    def test_correlation_endpoint_url_format(self, client):
        """Test correlation endpoint URL format validation."""
        # Missing district parameter
        response = client.get('/api/correlation/USA/NY')
        assert response.status_code == 404


# Property-Based Tests using Hypothesis
from hypothesis import given, strategies as st, settings, assume
from hypothesis.strategies import composite


@composite
def weather_data_strategy(draw):
    """Generate random weather data for property-based testing."""
    return {
        'timestamp': draw(st.datetimes(timezones=st.just(timezone.utc))).isoformat(),
        'temperature': draw(st.floats(min_value=-50, max_value=130)),
        'humidity': draw(st.integers(min_value=0, max_value=100)),
        'wind_speed': draw(st.floats(min_value=0, max_value=100)),
        'pressure': draw(st.floats(min_value=800, max_value=1100)),
        'precipitation': draw(st.floats(min_value=0, max_value=50)),
        'uv_index': draw(st.integers(min_value=0, max_value=20)),
        'weather_code': draw(st.integers(min_value=0, max_value=99)),
        'location': {
            'country': 'USA',
            'state': 'NY',
            'district': 'Manhattan',
            'latitude': 40.7831,
            'longitude': -73.9712
        }
    }


@composite
def pollen_data_strategy(draw):
    """Generate random pollen data for property-based testing."""
    return {
        'timestamp': draw(st.datetimes(timezones=st.just(timezone.utc))).isoformat(),
        'pollen_types': {
            'grass': {
                'concentration': draw(st.floats(min_value=0, max_value=5000)),
                'unit': 'gr/m³',
                'severity': draw(st.sampled_from(['LOW', 'MODERATE', 'HIGH']))
            },
            'tree': {
                'concentration': draw(st.floats(min_value=0, max_value=5000)),
                'unit': 'gr/m³',
                'severity': draw(st.sampled_from(['LOW', 'MODERATE', 'HIGH']))
            },
            'weed': {
                'concentration': draw(st.floats(min_value=0, max_value=5000)),
                'unit': 'gr/m³',
                'severity': draw(st.sampled_from(['LOW', 'MODERATE', 'HIGH']))
            },
            'ragweed': {
                'concentration': draw(st.floats(min_value=0, max_value=5000)),
                'unit': 'gr/m³',
                'severity': draw(st.sampled_from(['LOW', 'MODERATE', 'HIGH']))
            },
            'mold': {
                'concentration': draw(st.floats(min_value=0, max_value=5000)),
                'unit': 'gr/m³',
                'severity': draw(st.sampled_from(['LOW', 'MODERATE', 'HIGH']))
            }
        },
        'location': {
            'country': 'USA',
            'state': 'NY',
            'district': 'Manhattan',
            'latitude': 40.7831,
            'longitude': -73.9712
        }
    }


class TestExportDataIntegrityProperty:
    """
    Property-based tests for export data integrity.
    
    **Feature: data-mashup-dashboard, Property 7: Export Data Integrity**
    **Validates: Requirements 6.1, 6.2, 6.4**
    """
    
    @given(weather_data=weather_data_strategy(), pollen_data=pollen_data_strategy())
    @settings(max_examples=100, deadline=None)
    def test_export_contains_all_weather_metrics(self, weather_data, pollen_data):
        """
        Property: For any weather data, the export should contain all weather metrics.
        
        Validates: Requirements 6.1, 6.4
        """
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        with patch('config.LocationConfig.validate_location', return_value=True), \
             patch('src.data_service.DataService.fetch_weather_data', return_value=weather_data), \
             patch('src.data_service.DataService.fetch_pollen_data', return_value=pollen_data), \
             patch('src.correlation_calculator.CorrelationCalculator.calculate_all_correlations', return_value=[]):
            
            request_body = {
                'country': 'USA',
                'state': 'NY',
                'district': 'Manhattan'
            }
            
            response = client.post('/api/export', json=request_body)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            # Verify all weather metrics are present
            weather = data['weather']
            assert 'temperature' in weather
            assert 'humidity' in weather
            assert 'wind_speed' in weather
            assert 'pressure' in weather
            assert 'precipitation' in weather
            assert 'uv_index' in weather
            assert 'weather_code' in weather
            
            # Verify weather values match input
            assert weather['temperature'] == weather_data['temperature']
            assert weather['humidity'] == weather_data['humidity']
            assert weather['wind_speed'] == weather_data['wind_speed']
            assert weather['pressure'] == weather_data['pressure']
            assert weather['precipitation'] == weather_data['precipitation']
            assert weather['uv_index'] == weather_data['uv_index']
    
    @given(weather_data=weather_data_strategy(), pollen_data=pollen_data_strategy())
    @settings(max_examples=100)
    def test_export_contains_all_pollen_types(self, weather_data, pollen_data):
        """
        Property: For any pollen data, the export should contain all five pollen types.
        
        Validates: Requirements 6.1, 6.4
        """
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        with patch('config.LocationConfig.validate_location', return_value=True), \
             patch('src.data_service.DataService.fetch_weather_data', return_value=weather_data), \
             patch('src.data_service.DataService.fetch_pollen_data', return_value=pollen_data), \
             patch('src.correlation_calculator.CorrelationCalculator.calculate_all_correlations', return_value=[]):
            
            request_body = {
                'country': 'USA',
                'state': 'NY',
                'district': 'Manhattan'
            }
            
            response = client.post('/api/export', json=request_body)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            # Verify all pollen types are present
            pollen = data['pollen']
            assert 'pollen_types' in pollen
            pollen_types = pollen['pollen_types']
            
            required_pollen_types = ['grass', 'tree', 'weed', 'ragweed', 'mold']
            for pollen_type in required_pollen_types:
                assert pollen_type in pollen_types
                assert 'concentration' in pollen_types[pollen_type]
                assert 'severity' in pollen_types[pollen_type]
                assert 'unit' in pollen_types[pollen_type]
    
    @given(weather_data=weather_data_strategy(), pollen_data=pollen_data_strategy())
    @settings(max_examples=100)
    def test_export_contains_required_metadata(self, weather_data, pollen_data):
        """
        Property: For any export operation, the response should contain all required metadata.
        
        Validates: Requirements 6.2
        """
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        with patch('config.LocationConfig.validate_location', return_value=True), \
             patch('src.data_service.DataService.fetch_weather_data', return_value=weather_data), \
             patch('src.data_service.DataService.fetch_pollen_data', return_value=pollen_data), \
             patch('src.correlation_calculator.CorrelationCalculator.calculate_all_correlations', return_value=[
                 {
                     'weather_factor': 'temperature',
                     'pollen_type': 'grass',
                     'correlation_coefficient': 0.78,
                     'strength': 'Strong Positive',
                     'explanation': 'Higher temperatures increase grass pollen production'
                 }
             ]):
            
            request_body = {
                'country': 'USA',
                'state': 'NY',
                'district': 'Manhattan'
            }
            
            response = client.post('/api/export', json=request_body)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            # Verify export_timestamp is present
            assert 'export_timestamp' in data
            assert isinstance(data['export_timestamp'], str)
            
            # Verify location is present
            assert 'location' in data
            location = data['location']
            assert location['country'] == 'USA'
            assert location['state'] == 'NY'
            assert location['district'] == 'Manhattan'
            
            # Verify metadata is present
            assert 'metadata' in data
            metadata = data['metadata']
            assert 'data_sources' in metadata
            assert 'export_format' in metadata
            assert 'version' in metadata
            assert isinstance(metadata['data_sources'], list)
            assert len(metadata['data_sources']) > 0
            assert metadata['export_format'] == 'JSON'
    
    @given(weather_data=weather_data_strategy(), pollen_data=pollen_data_strategy())
    @settings(max_examples=100)
    def test_export_contains_correlations(self, weather_data, pollen_data):
        """
        Property: For any export operation, the response should include correlation coefficients.
        
        Validates: Requirements 6.2
        """
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        with patch('config.LocationConfig.validate_location', return_value=True), \
             patch('src.data_service.DataService.fetch_weather_data', return_value=weather_data), \
             patch('src.data_service.DataService.fetch_pollen_data', return_value=pollen_data), \
             patch('src.correlation_calculator.CorrelationCalculator.calculate_all_correlations', return_value=[
                 {
                     'weather_factor': 'temperature',
                     'pollen_type': 'grass',
                     'correlation_coefficient': 0.78,
                     'strength': 'Strong Positive',
                     'explanation': 'Higher temperatures increase grass pollen production'
                 },
                 {
                     'weather_factor': 'humidity',
                     'pollen_type': 'mold',
                     'correlation_coefficient': 0.85,
                     'strength': 'Strong Positive',
                     'explanation': 'Higher humidity increases mold spore production'
                 }
             ]):
            
            request_body = {
                'country': 'USA',
                'state': 'NY',
                'district': 'Manhattan'
            }
            
            response = client.post('/api/export', json=request_body)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            # Verify correlations are present
            assert 'correlations' in data
            correlations = data['correlations']
            assert isinstance(correlations, list)
            
            # Verify each correlation has required fields
            for correlation in correlations:
                assert 'weather_factor' in correlation
                assert 'pollen_type' in correlation
                assert 'correlation_coefficient' in correlation
                assert 'strength' in correlation
                assert 'explanation' in correlation
                
                # Verify correlation coefficient is in valid range
                coeff = correlation['correlation_coefficient']
                assert -1 <= coeff <= 1
    
    @given(weather_data=weather_data_strategy(), pollen_data=pollen_data_strategy())
    @settings(max_examples=100)
    def test_export_data_integrity_structure(self, weather_data, pollen_data):
        """
        Property: For any export operation, the exported JSON should have a valid structure.
        
        Validates: Requirements 6.1, 6.2, 6.4
        """
        app = create_app()
        app.config['TESTING'] = True
        client = app.test_client()
        
        with patch('config.LocationConfig.validate_location', return_value=True), \
             patch('src.data_service.DataService.fetch_weather_data', return_value=weather_data), \
             patch('src.data_service.DataService.fetch_pollen_data', return_value=pollen_data), \
             patch('src.correlation_calculator.CorrelationCalculator.calculate_all_correlations', return_value=[]):
            
            request_body = {
                'country': 'USA',
                'state': 'NY',
                'district': 'Manhattan'
            }
            
            response = client.post('/api/export', json=request_body)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            # Verify top-level structure
            required_top_level_fields = [
                'export_timestamp',
                'location',
                'weather',
                'pollen',
                'correlations',
                'metadata'
            ]
            
            for field in required_top_level_fields:
                assert field in data, f"Missing required field: {field}"
            
            # Verify data types
            assert isinstance(data['export_timestamp'], str)
            assert isinstance(data['location'], dict)
            assert isinstance(data['weather'], dict)
            assert isinstance(data['pollen'], dict)
            assert isinstance(data['correlations'], list)
            assert isinstance(data['metadata'], dict)
            
            # Verify location structure
            location = data['location']
            assert 'country' in location
            assert 'state' in location
            assert 'district' in location
            
            # Verify metadata structure
            metadata = data['metadata']
            assert 'data_sources' in metadata
            assert 'export_format' in metadata
            assert 'version' in metadata
