"""
Integration tests for Weather & Pollen Dashboard.

Tests end-to-end workflows including:
- Location selection to chart display
- Export functionality
- Error scenarios and recovery
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from app import create_app
from src.data_service import DataService, DataServiceError
from src.correlation_calculator import CorrelationCalculator


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


@pytest.fixture
def mock_correlations():
    """Create mock correlation data."""
    return [
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
        },
        {
            'weather_factor': 'wind_speed',
            'pollen_type': 'grass',
            'correlation_coefficient': 0.65,
            'strength': 'Moderate Positive',
            'explanation': 'Higher wind speeds increase pollen dispersion'
        },
        {
            'weather_factor': 'precipitation',
            'pollen_type': 'grass',
            'correlation_coefficient': -0.72,
            'strength': 'Strong Negative',
            'explanation': 'Rain reduces airborne pollen'
        }
    ]


class TestLocationSelectionToChartDisplay:
    """
    Integration tests for end-to-end workflow from location selection to chart display.
    
    **Feature: data-mashup-dashboard, Requirements 1.1, 5.4**
    """
    
    @patch('src.correlation_calculator.CorrelationCalculator.calculate_all_correlations')
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_complete_workflow_location_selection_to_display(self, mock_validate, mock_fetch_weather,
                                                             mock_fetch_pollen, mock_calc_corr,
                                                             client, mock_weather_data, mock_pollen_data,
                                                             mock_correlations):
        """
        Test complete workflow: user selects location -> system fetches data -> displays on dashboard.
        
        Validates: Requirements 1.1, 5.4
        """
        # Setup mocks
        mock_validate.return_value = True
        mock_fetch_weather.return_value = mock_weather_data
        mock_fetch_pollen.return_value = mock_pollen_data
        mock_calc_corr.return_value = mock_correlations
        
        # Step 1: User loads dashboard
        response = client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE' in response.data or b'<html' in response.data
        
        # Step 2: User gets available locations
        response = client.get('/api/locations')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'countries' in data
        assert len(data['countries']) > 0
        
        # Step 3: User selects a country and gets states
        response = client.get('/api/locations?country=USA')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['country'] == 'USA'
        assert 'states' in data
        assert len(data['states']) > 0
        
        # Step 4: User selects a state and gets districts
        response = client.get('/api/locations?country=USA&state=NY')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['country'] == 'USA'
        assert data['state'] == 'NY'
        assert 'districts' in data
        assert 'Manhattan' in data['districts']
        
        # Step 5: User selects a district and fetches weather data
        response = client.get('/api/weather/USA/NY/Manhattan')
        assert response.status_code == 200
        weather = json.loads(response.data)
        assert weather['temperature'] == 72.5
        assert weather['humidity'] == 65
        assert weather['wind_speed'] == 12
        
        # Step 6: System fetches pollen data for the same location
        response = client.get('/api/pollen/USA/NY/Manhattan')
        assert response.status_code == 200
        pollen = json.loads(response.data)
        assert 'pollen_types' in pollen
        assert 'grass' in pollen['pollen_types']
        assert pollen['pollen_types']['grass']['concentration'] == 850
        
        # Step 7: System calculates correlations
        response = client.get('/api/correlation/USA/NY/Manhattan')
        assert response.status_code == 200
        correlations = json.loads(response.data)
        assert 'correlations' in correlations
        assert len(correlations['correlations']) > 0
        
        # Verify correlation structure
        for corr in correlations['correlations']:
            assert 'weather_factor' in corr
            assert 'pollen_type' in corr
            assert 'correlation_coefficient' in corr
            assert -1 <= corr['correlation_coefficient'] <= 1
    
    @patch('src.correlation_calculator.CorrelationCalculator.calculate_all_correlations')
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_workflow_with_location_change(self, mock_validate, mock_fetch_weather,
                                          mock_fetch_pollen, mock_calc_corr,
                                          client, mock_weather_data, mock_pollen_data,
                                          mock_correlations):
        """
        Test workflow where user changes location and system updates all data.
        
        Validates: Requirements 1.1, 5.4
        """
        mock_validate.return_value = True
        mock_fetch_weather.return_value = mock_weather_data
        mock_fetch_pollen.return_value = mock_pollen_data
        mock_calc_corr.return_value = mock_correlations
        
        # First location: USA/NY/Manhattan
        response = client.get('/api/weather/USA/NY/Manhattan')
        assert response.status_code == 200
        weather1 = json.loads(response.data)
        assert weather1['location']['district'] == 'Manhattan'
        
        # Change location: USA/CA/Los Angeles
        # Update mock to return different data
        mock_weather_data_ca = mock_weather_data.copy()
        mock_weather_data_ca['location'] = {
            'country': 'USA',
            'state': 'CA',
            'district': 'Los Angeles',
            'latitude': 34.0522,
            'longitude': -118.2437
        }
        mock_weather_data_ca['temperature'] = 75.0
        
        mock_fetch_weather.return_value = mock_weather_data_ca
        
        response = client.get('/api/weather/USA/CA/Los Angeles')
        assert response.status_code == 200
        weather2 = json.loads(response.data)
        assert weather2['location']['district'] == 'Los Angeles'
        assert weather2['temperature'] == 75.0
        
        # Verify pollen data also updates
        mock_pollen_data_ca = mock_pollen_data.copy()
        mock_pollen_data_ca['location'] = {
            'country': 'USA',
            'state': 'CA',
            'district': 'Los Angeles',
            'latitude': 34.0522,
            'longitude': -118.2437
        }
        mock_fetch_pollen.return_value = mock_pollen_data_ca
        
        response = client.get('/api/pollen/USA/CA/Los Angeles')
        assert response.status_code == 200
        pollen2 = json.loads(response.data)
        assert pollen2['location']['district'] == 'Los Angeles'
    
    @patch('src.correlation_calculator.CorrelationCalculator.calculate_all_correlations')
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_workflow_with_multiple_locations(self, mock_validate, mock_fetch_weather,
                                             mock_fetch_pollen, mock_calc_corr,
                                             client, mock_weather_data, mock_pollen_data,
                                             mock_correlations):
        """
        Test workflow where user compares data from multiple locations.
        
        Validates: Requirements 1.1, 5.4
        """
        mock_validate.return_value = True
        mock_calc_corr.return_value = mock_correlations
        
        locations = [
            ('USA', 'NY', 'Manhattan'),
            ('USA', 'CA', 'Los Angeles'),
            ('India', 'MH', 'Mumbai')
        ]
        
        all_weather_data = []
        all_pollen_data = []
        
        for country, state, district in locations:
            # Create location-specific mock data
            weather_data = mock_weather_data.copy()
            weather_data['location'] = {
                'country': country,
                'state': state,
                'district': district,
                'latitude': 40.7831,
                'longitude': -73.9712
            }
            
            pollen_data = mock_pollen_data.copy()
            pollen_data['location'] = {
                'country': country,
                'state': state,
                'district': district,
                'latitude': 40.7831,
                'longitude': -73.9712
            }
            
            mock_fetch_weather.return_value = weather_data
            mock_fetch_pollen.return_value = pollen_data
            
            # Fetch weather for each location
            response = client.get(f'/api/weather/{country}/{state}/{district}')
            assert response.status_code == 200
            weather = json.loads(response.data)
            all_weather_data.append(weather)
            
            # Fetch pollen for each location
            response = client.get(f'/api/pollen/{country}/{state}/{district}')
            assert response.status_code == 200
            pollen = json.loads(response.data)
            all_pollen_data.append(pollen)
        
        # Verify we have data from all locations
        assert len(all_weather_data) == 3
        assert len(all_pollen_data) == 3
        
        # Verify each location has correct data
        for i, (country, state, district) in enumerate(locations):
            assert all_weather_data[i]['location']['country'] == country
            assert all_weather_data[i]['location']['state'] == state
            assert all_weather_data[i]['location']['district'] == district


class TestExportFunctionality:
    """
    Integration tests for export functionality.
    
    **Feature: data-mashup-dashboard, Requirements 6.1**
    """
    
    @patch('src.correlation_calculator.CorrelationCalculator.calculate_all_correlations')
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_export_complete_workflow(self, mock_validate, mock_fetch_weather,
                                     mock_fetch_pollen, mock_calc_corr,
                                     client, mock_weather_data, mock_pollen_data,
                                     mock_correlations):
        """
        Test complete export workflow: fetch data -> calculate correlations -> export.
        
        Validates: Requirements 6.1
        """
        mock_validate.return_value = True
        mock_fetch_weather.return_value = mock_weather_data
        mock_fetch_pollen.return_value = mock_pollen_data
        mock_calc_corr.return_value = mock_correlations
        
        # Step 1: Fetch weather data
        response = client.get('/api/weather/USA/NY/Manhattan')
        assert response.status_code == 200
        weather = json.loads(response.data)
        
        # Step 2: Fetch pollen data
        response = client.get('/api/pollen/USA/NY/Manhattan')
        assert response.status_code == 200
        pollen = json.loads(response.data)
        
        # Step 3: Calculate correlations
        response = client.get('/api/correlation/USA/NY/Manhattan')
        assert response.status_code == 200
        correlations = json.loads(response.data)
        
        # Step 4: Export all data
        request_body = {
            'country': 'USA',
            'state': 'NY',
            'district': 'Manhattan'
        }
        
        response = client.post('/api/export', json=request_body)
        assert response.status_code == 200
        export_data = json.loads(response.data)
        
        # Verify export contains all required data
        assert 'export_timestamp' in export_data
        assert 'location' in export_data
        assert 'weather' in export_data
        assert 'pollen' in export_data
        assert 'correlations' in export_data
        assert 'metadata' in export_data
        
        # Verify exported weather data matches fetched data
        assert export_data['weather']['temperature'] == weather['temperature']
        assert export_data['weather']['humidity'] == weather['humidity']
        
        # Verify exported pollen data matches fetched data
        assert export_data['pollen']['pollen_types']['grass']['concentration'] == \
               pollen['pollen_types']['grass']['concentration']
        
        # Verify exported correlations are present
        assert len(export_data['correlations']) > 0
        
        # Verify metadata
        assert export_data['metadata']['export_format'] == 'JSON'
        assert 'data_sources' in export_data['metadata']
        assert 'version' in export_data['metadata']
    
    @patch('src.correlation_calculator.CorrelationCalculator.calculate_all_correlations')
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_export_data_consistency(self, mock_validate, mock_fetch_weather,
                                    mock_fetch_pollen, mock_calc_corr,
                                    client, mock_weather_data, mock_pollen_data,
                                    mock_correlations):
        """
        Test that exported data is consistent with fetched data.
        
        Validates: Requirements 6.1, 6.4
        """
        mock_validate.return_value = True
        mock_fetch_weather.return_value = mock_weather_data
        mock_fetch_pollen.return_value = mock_pollen_data
        mock_calc_corr.return_value = mock_correlations
        
        # Export data
        request_body = {
            'country': 'USA',
            'state': 'NY',
            'district': 'Manhattan'
        }
        
        response = client.post('/api/export', json=request_body)
        assert response.status_code == 200
        export_data = json.loads(response.data)
        
        # Verify all weather metrics are present in export
        weather = export_data['weather']
        required_weather_fields = [
            'temperature', 'humidity', 'wind_speed', 'pressure',
            'precipitation', 'uv_index', 'weather_code'
        ]
        for field in required_weather_fields:
            assert field in weather, f"Missing weather field: {field}"
        
        # Verify all pollen types are present in export
        pollen = export_data['pollen']
        required_pollen_types = ['grass', 'tree', 'weed', 'ragweed', 'mold']
        for pollen_type in required_pollen_types:
            assert pollen_type in pollen['pollen_types'], f"Missing pollen type: {pollen_type}"
            assert 'concentration' in pollen['pollen_types'][pollen_type]
            assert 'severity' in pollen['pollen_types'][pollen_type]
            assert 'unit' in pollen['pollen_types'][pollen_type]
        
        # Verify correlations are present
        assert len(export_data['correlations']) > 0
        for corr in export_data['correlations']:
            assert 'weather_factor' in corr
            assert 'pollen_type' in corr
            assert 'correlation_coefficient' in corr
            assert -1 <= corr['correlation_coefficient'] <= 1
    
    @patch('src.correlation_calculator.CorrelationCalculator.calculate_all_correlations')
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_export_multiple_locations(self, mock_validate, mock_fetch_weather,
                                      mock_fetch_pollen, mock_calc_corr,
                                      client, mock_weather_data, mock_pollen_data,
                                      mock_correlations):
        """
        Test exporting data from multiple locations.
        
        Validates: Requirements 6.1
        """
        mock_validate.return_value = True
        mock_fetch_weather.return_value = mock_weather_data
        mock_fetch_pollen.return_value = mock_pollen_data
        mock_calc_corr.return_value = mock_correlations
        
        locations = [
            {'country': 'USA', 'state': 'NY', 'district': 'Manhattan'},
            {'country': 'USA', 'state': 'CA', 'district': 'Los Angeles'},
            {'country': 'India', 'state': 'MH', 'district': 'Mumbai'}
        ]
        
        all_exports = []
        
        for location in locations:
            response = client.post('/api/export', json=location)
            assert response.status_code == 200
            export_data = json.loads(response.data)
            all_exports.append(export_data)
            
            # Verify location in export matches request
            assert export_data['location']['country'] == location['country']
            assert export_data['location']['state'] == location['state']
            assert export_data['location']['district'] == location['district']
        
        # Verify we have exports from all locations
        assert len(all_exports) == 3


class TestErrorScenariosAndRecovery:
    """
    Integration tests for error scenarios and recovery mechanisms.
    
    **Feature: data-mashup-dashboard, Requirements 9.1, 9.2, 9.3, 9.4**
    """
    
    @patch('config.LocationConfig.validate_location')
    def test_invalid_location_error_handling(self, mock_validate, client):
        """
        Test error handling when user selects invalid location.
        
        Validates: Requirements 9.3, 9.4
        """
        mock_validate.return_value = False
        
        # Try to fetch weather for invalid location
        response = client.get('/api/weather/InvalidCountry/InvalidState/InvalidDistrict')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Invalid Location'
        
        # Try to fetch pollen for invalid location
        response = client.get('/api/pollen/InvalidCountry/InvalidState/InvalidDistrict')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Invalid Location'
        
        # Try to export for invalid location
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
    
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_api_failure_error_handling(self, mock_validate, mock_fetch_weather, client):
        """
        Test error handling when external API fails.
        
        Validates: Requirements 9.1, 9.3, 9.4
        """
        mock_validate.return_value = True
        mock_fetch_weather.side_effect = DataServiceError("API failed")
        
        # Try to fetch weather when API fails
        response = client.get('/api/weather/USA/NY/Manhattan')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Data Service Error'
    
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_partial_api_failure_recovery(self, mock_validate, mock_fetch_weather,
                                         mock_fetch_pollen, client, mock_weather_data,
                                         mock_pollen_data):
        """
        Test recovery when one API fails but other succeeds.
        
        Validates: Requirements 9.1, 9.2
        """
        mock_validate.return_value = True
        
        # Weather API succeeds
        mock_fetch_weather.return_value = mock_weather_data
        
        # Pollen API fails
        mock_fetch_pollen.side_effect = DataServiceError("Pollen API failed")
        
        # Weather should succeed
        response = client.get('/api/weather/USA/NY/Manhattan')
        assert response.status_code == 200
        weather = json.loads(response.data)
        assert weather['temperature'] == 72.5
        
        # Pollen should fail
        response = client.get('/api/pollen/USA/NY/Manhattan')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('src.correlation_calculator.CorrelationCalculator.calculate_all_correlations')
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_export_with_api_failure(self, mock_validate, mock_fetch_weather,
                                    mock_fetch_pollen, mock_calc_corr, client):
        """
        Test export error handling when API fails.
        
        Validates: Requirements 9.1, 9.3, 9.4
        """
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
        assert data['error'] == 'Data Service Error'
    
    @patch('config.LocationConfig.validate_location')
    def test_missing_export_parameters(self, mock_validate, client):
        """
        Test export error handling with missing parameters.
        
        Validates: Requirements 9.3, 9.4
        """
        # Missing all parameters
        response = client.post('/api/export', json={})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Bad Request'
        
        # Missing state
        request_body = {'country': 'USA', 'district': 'Manhattan'}
        response = client.post('/api/export', json=request_body)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Bad Request'
        
        # Missing district
        request_body = {'country': 'USA', 'state': 'NY'}
        response = client.post('/api/export', json=request_body)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Bad Request'
    
    def test_malformed_request_body(self, client):
        """
        Test error handling with malformed request body.
        
        Validates: Requirements 9.3, 9.4
        """
        # Send invalid JSON
        response = client.post('/api/export', data='invalid json', 
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('config.LocationConfig.validate_location')
    def test_invalid_location_hierarchy(self, mock_validate, client):
        """
        Test error handling with invalid location hierarchy.
        
        Validates: Requirements 5.2, 5.3
        """
        mock_validate.return_value = False
        
        # Try to get states for invalid country
        response = client.get('/api/locations?country=InvalidCountry')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Not Found'
        
        # Try to get districts for invalid state
        response = client.get('/api/locations?country=USA&state=InvalidState')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Not Found'


class TestDataValidationInWorkflow:
    """
    Integration tests for data validation throughout the workflow.
    
    **Feature: data-mashup-dashboard, Requirements 1.5, 3.2**
    """
    
    @patch('src.data_service.DataService.validate_weather_data')
    @patch('src.data_service.DataService.fetch_weather_data')
    @patch('config.LocationConfig.validate_location')
    def test_weather_data_validation_in_workflow(self, mock_validate_loc, mock_fetch_weather,
                                                 mock_validate_data, client, mock_weather_data):
        """
        Test that weather data is validated in the workflow.
        
        Validates: Requirements 1.5
        """
        mock_validate_loc.return_value = True
        mock_fetch_weather.return_value = mock_weather_data
        mock_validate_data.return_value = True
        
        # Valid data should pass
        response = client.get('/api/weather/USA/NY/Manhattan')
        assert response.status_code == 200
        
        # Invalid data should fail
        mock_validate_data.return_value = False
        response = client.get('/api/weather/USA/NY/Manhattan')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Data Validation Error'
    
    @patch('src.data_service.DataService.validate_pollen_data')
    @patch('src.data_service.DataService.fetch_pollen_data')
    @patch('config.LocationConfig.validate_location')
    def test_pollen_data_validation_in_workflow(self, mock_validate_loc, mock_fetch_pollen,
                                               mock_validate_data, client, mock_pollen_data):
        """
        Test that pollen data is validated in the workflow.
        
        Validates: Requirements 3.2
        """
        mock_validate_loc.return_value = True
        mock_fetch_pollen.return_value = mock_pollen_data
        mock_validate_data.return_value = True
        
        # Valid data should pass
        response = client.get('/api/pollen/USA/NY/Manhattan')
        assert response.status_code == 200
        
        # Invalid data should fail
        mock_validate_data.return_value = False
        response = client.get('/api/pollen/USA/NY/Manhattan')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Data Validation Error'
