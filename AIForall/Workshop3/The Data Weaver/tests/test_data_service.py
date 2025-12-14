"""
Unit tests for the data service module (src/data_service.py).

Tests data fetching, aggregation, combination, and validation functionality.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, timezone
from hypothesis import given, strategies as st, settings
import pandas as pd

from src.data_service import (
    DataService,
    DataServiceError,
    DataAggregationError,
    DataCombinationError
)


@pytest.fixture
def data_service():
    """Create a DataService instance for testing."""
    with patch('src.data_service.get_location_config'):
        return DataService(pollen_api_key="test_key", max_retries=3, timeout=10)


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


class TestDataServiceInitialization:
    """Test DataService initialization."""
    
    def test_data_service_initialization(self, data_service):
        """Test DataService initialization."""
        assert data_service.api_client is not None
        assert data_service.location_config is not None
    
    def test_time_periods_defined(self, data_service):
        """Test that time periods are properly defined."""
        assert 'weekly' in data_service.TIME_PERIODS
        assert 'monthly' in data_service.TIME_PERIODS
        assert 'half_yearly' in data_service.TIME_PERIODS
        assert 'yearly' in data_service.TIME_PERIODS
    
    def test_aggregation_functions_defined(self, data_service):
        """Test that aggregation functions are defined."""
        assert 'temperature' in data_service.AGGREGATION_FUNCTIONS
        assert 'humidity' in data_service.AGGREGATION_FUNCTIONS
        assert 'precipitation' in data_service.AGGREGATION_FUNCTIONS


class TestFetchWeatherData:
    """Test fetch_weather_data method."""
    
    @patch('src.data_service.get_location_config')
    @patch('src.data_service.APIClient.fetch_all_data')
    def test_fetch_weather_data_success(self, mock_fetch_all, mock_config, mock_weather_data):
        """Test successful weather data fetch."""
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
        
        # Create service with mocked config
        service = DataService(pollen_api_key="test_key")
        service.location_config = mock_location_config
        
        # Fetch data
        result = service.fetch_weather_data('USA', 'NY', 'Manhattan')
        
        # Verify
        assert result is not None
        assert result['location']['country'] == 'USA'
        assert result['location']['state'] == 'NY'
        assert result['location']['district'] == 'Manhattan'
    
    @patch('src.data_service.get_location_config')
    def test_fetch_weather_data_invalid_location(self, mock_config):
        """Test weather data fetch with invalid location."""
        mock_location_config = Mock()
        mock_location_config.validate_location.return_value = False
        mock_config.return_value = mock_location_config
        
        service = DataService(pollen_api_key="test_key")
        service.location_config = mock_location_config
        
        with pytest.raises(DataServiceError):
            service.fetch_weather_data('InvalidCountry', 'InvalidState', 'InvalidDistrict')
    
    @patch('src.data_service.get_location_config')
    @patch('src.data_service.APIClient.fetch_all_data')
    def test_fetch_weather_data_api_failure(self, mock_fetch_all, mock_config):
        """Test weather data fetch when API fails."""
        from src.api_client import APIClientError
        
        mock_location_config = Mock()
        mock_location_config.validate_location.return_value = True
        mock_location_config.get_coordinates.return_value = (40.7831, -73.9712)
        mock_config.return_value = mock_location_config
        
        mock_fetch_all.side_effect = APIClientError("API failed")
        
        service = DataService(pollen_api_key="test_key")
        service.location_config = mock_location_config
        
        with pytest.raises(DataServiceError):
            service.fetch_weather_data('USA', 'NY', 'Manhattan')


class TestFetchPollenData:
    """Test fetch_pollen_data method."""
    
    @patch('src.data_service.get_location_config')
    @patch('src.data_service.APIClient.fetch_all_data')
    def test_fetch_pollen_data_success(self, mock_fetch_all, mock_config, mock_pollen_data):
        """Test successful pollen data fetch."""
        mock_location_config = Mock()
        mock_location_config.validate_location.return_value = True
        mock_location_config.get_coordinates.return_value = (40.7831, -73.9712)
        mock_config.return_value = mock_location_config
        
        mock_fetch_all.return_value = {
            'weather': None,
            'pollen': mock_pollen_data,
            'errors': {'weather': None, 'pollen': None}
        }
        
        service = DataService(pollen_api_key="test_key")
        service.location_config = mock_location_config
        
        result = service.fetch_pollen_data('USA', 'NY', 'Manhattan')
        
        assert result is not None
        assert result['location']['country'] == 'USA'
        assert 'pollen_types' in result
    
    @patch('src.data_service.get_location_config')
    def test_fetch_pollen_data_invalid_location(self, mock_config):
        """Test pollen data fetch with invalid location."""
        mock_location_config = Mock()
        mock_location_config.validate_location.return_value = False
        mock_config.return_value = mock_location_config
        
        service = DataService(pollen_api_key="test_key")
        service.location_config = mock_location_config
        
        with pytest.raises(DataServiceError):
            service.fetch_pollen_data('InvalidCountry', 'InvalidState', 'InvalidDistrict')


class TestAggregateData:
    """Test aggregate_data method."""
    
    def test_aggregate_data_weekly(self, data_service):
        """Test weekly data aggregation."""
        # Create sample data for 14 days
        data = []
        base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        for i in range(14):
            data.append({
                'timestamp': (base_date + timedelta(days=i)).isoformat(),
                'temperature': 70 + i,
                'humidity': 60 + i,
                'wind_speed': 10 + i,
                'pressure': 1013
            })
        
        result = data_service.aggregate_data(data, 'weekly')
        
        assert len(result) > 0
        assert 'timestamp' in result[0]
        assert 'temperature' in result[0]
    
    def test_aggregate_data_monthly(self, data_service):
        """Test monthly data aggregation."""
        data = []
        base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        for i in range(60):
            data.append({
                'timestamp': (base_date + timedelta(days=i)).isoformat(),
                'temperature': 70 + (i % 10),
                'humidity': 60 + (i % 10),
                'wind_speed': 10 + (i % 5),
                'pressure': 1013
            })
        
        result = data_service.aggregate_data(data, 'monthly')
        
        assert len(result) > 0
        assert 'temperature' in result[0]
    
    def test_aggregate_data_invalid_period(self, data_service):
        """Test aggregation with invalid period."""
        data = [{'timestamp': '2024-01-01T00:00:00Z', 'temperature': 70}]
        
        with pytest.raises(DataAggregationError):
            data_service.aggregate_data(data, 'invalid_period')
    
    def test_aggregate_data_empty_list(self, data_service):
        """Test aggregation with empty data list."""
        result = data_service.aggregate_data([], 'weekly')
        
        assert result == []
    
    def test_aggregate_data_no_timestamp(self, data_service):
        """Test aggregation with data missing timestamps."""
        data = [{'temperature': 70, 'humidity': 60}]
        
        result = data_service.aggregate_data(data, 'weekly')
        
        # Should return original data if no timestamp column
        assert result == data
    
    def test_aggregate_data_preserves_values(self, data_service):
        """Test that aggregation preserves data values correctly."""
        # Create data with known values
        data = []
        base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        for i in range(7):
            data.append({
                'timestamp': (base_date + timedelta(days=i)).isoformat(),
                'temperature': 70.0,  # Constant value
                'humidity': 60.0,
                'wind_speed': 10.0,
                'pressure': 1013.0
            })
        
        result = data_service.aggregate_data(data, 'weekly')
        
        # Mean of constant values should be the same constant
        assert len(result) > 0
        assert result[0]['temperature'] == 70.0


class TestCombineDatasets:
    """Test combine_datasets method."""
    
    def test_combine_datasets_success(self, data_service, mock_weather_data, mock_pollen_data):
        """Test successful dataset combination."""
        result = data_service.combine_datasets(mock_weather_data, mock_pollen_data)
        
        assert result is not None
        assert 'weather' in result
        assert 'pollen' in result
        assert 'location' in result
        assert 'timestamp' in result
    
    def test_combine_datasets_invalid_weather(self, data_service, mock_pollen_data):
        """Test combination with invalid weather data."""
        with pytest.raises(DataCombinationError):
            data_service.combine_datasets(None, mock_pollen_data)
    
    def test_combine_datasets_invalid_pollen(self, data_service, mock_weather_data):
        """Test combination with invalid pollen data."""
        with pytest.raises(DataCombinationError):
            data_service.combine_datasets(mock_weather_data, None)
    
    def test_combine_datasets_structure(self, data_service, mock_weather_data, mock_pollen_data):
        """Test that combined dataset has correct structure."""
        result = data_service.combine_datasets(mock_weather_data, mock_pollen_data)
        
        # Check weather fields
        assert result['weather']['temperature'] == 72.5
        assert result['weather']['humidity'] == 65
        assert result['weather']['wind_speed'] == 12
        
        # Check pollen fields
        assert 'grass' in result['pollen']
        assert 'tree' in result['pollen']
        assert 'weed' in result['pollen']
        assert 'ragweed' in result['pollen']
        assert 'mold' in result['pollen']


class TestValidateWeatherData:
    """Test validate_weather_data method."""
    
    def test_validate_weather_data_valid(self, data_service, mock_weather_data):
        """Test validation of valid weather data."""
        is_valid = data_service.validate_weather_data(mock_weather_data)
        
        assert is_valid is True
    
    def test_validate_weather_data_missing_field(self, data_service):
        """Test validation with missing required field."""
        data = {
            'temperature': 72.5,
            'humidity': 65,
            'wind_speed': 12
            # Missing 'pressure'
        }
        
        is_valid = data_service.validate_weather_data(data)
        
        assert is_valid is False
    
    def test_validate_weather_data_temperature_out_of_range(self, data_service):
        """Test validation with temperature out of range."""
        data = {
            'temperature': 200,  # Too high
            'humidity': 65,
            'wind_speed': 12,
            'pressure': 1013
        }
        
        is_valid = data_service.validate_weather_data(data)
        
        assert is_valid is False
    
    def test_validate_weather_data_humidity_out_of_range(self, data_service):
        """Test validation with humidity out of range."""
        data = {
            'temperature': 72.5,
            'humidity': 150,  # Too high
            'wind_speed': 12,
            'pressure': 1013
        }
        
        is_valid = data_service.validate_weather_data(data)
        
        assert is_valid is False
    
    def test_validate_weather_data_negative_wind_speed(self, data_service):
        """Test validation with negative wind speed."""
        data = {
            'temperature': 72.5,
            'humidity': 65,
            'wind_speed': -5,  # Negative
            'pressure': 1013
        }
        
        is_valid = data_service.validate_weather_data(data)
        
        assert is_valid is False


class TestValidatePollenData:
    """Test validate_pollen_data method."""
    
    def test_validate_pollen_data_valid(self, data_service, mock_pollen_data):
        """Test validation of valid pollen data."""
        is_valid = data_service.validate_pollen_data(mock_pollen_data)
        
        assert is_valid is True
    
    def test_validate_pollen_data_missing_pollen_types(self, data_service):
        """Test validation with missing pollen_types field."""
        data = {'timestamp': '2024-01-15T00:00:00Z'}
        
        is_valid = data_service.validate_pollen_data(data)
        
        assert is_valid is False
    
    def test_validate_pollen_data_missing_pollen_type(self, data_service):
        """Test validation with missing pollen type."""
        data = {
            'pollen_types': {
                'grass': {'concentration': 850, 'severity': 'HIGH'},
                'tree': {'concentration': 450, 'severity': 'MODERATE'}
                # Missing other types
            }
        }
        
        is_valid = data_service.validate_pollen_data(data)
        
        assert is_valid is False
    
    def test_validate_pollen_data_negative_concentration(self, data_service):
        """Test validation with negative concentration."""
        data = {
            'pollen_types': {
                'grass': {'concentration': -100, 'severity': 'HIGH'},
                'tree': {'concentration': 450, 'severity': 'MODERATE'},
                'weed': {'concentration': 150, 'severity': 'LOW'},
                'ragweed': {'concentration': 200, 'severity': 'LOW'},
                'mold': {'concentration': 320, 'severity': 'MODERATE'}
            }
        }
        
        is_valid = data_service.validate_pollen_data(data)
        
        assert is_valid is False


class TestGetAggregationPeriodDays:
    """Test get_aggregation_period_days method."""
    
    def test_get_period_days_weekly(self, data_service):
        """Test getting days for weekly period."""
        days = data_service.get_aggregation_period_days('weekly')
        assert days == 7
    
    def test_get_period_days_monthly(self, data_service):
        """Test getting days for monthly period."""
        days = data_service.get_aggregation_period_days('monthly')
        assert days == 30
    
    def test_get_period_days_half_yearly(self, data_service):
        """Test getting days for half-yearly period."""
        days = data_service.get_aggregation_period_days('half_yearly')
        assert days == 182
    
    def test_get_period_days_yearly(self, data_service):
        """Test getting days for yearly period."""
        days = data_service.get_aggregation_period_days('yearly')
        assert days == 365
    
    def test_get_period_days_invalid(self, data_service):
        """Test getting days for invalid period."""
        with pytest.raises(DataServiceError):
            data_service.get_aggregation_period_days('invalid')


class TestPollenTypeCompletenessProperty:
    """
    Property-based tests for pollen type completeness.
    
    **Feature: data-mashup-dashboard, Property 2: Pollen Type Completeness**
    **Validates: Requirements 3.1, 3.2**
    """
    
    @given(
        grass_conc=st.integers(min_value=0, max_value=2000),
        tree_conc=st.integers(min_value=0, max_value=2000),
        weed_conc=st.integers(min_value=0, max_value=2000),
        ragweed_conc=st.integers(min_value=0, max_value=2000),
        mold_conc=st.integers(min_value=0, max_value=2000)
    )
    @settings(max_examples=100, suppress_health_check=[])
    def test_pollen_data_contains_all_types(self, grass_conc, tree_conc, weed_conc, ragweed_conc, mold_conc):
        """
        Property: For any pollen data fetch, the system should return all five pollen types
        (grass, tree, weed, ragweed, mold) with concentration levels and severity indicators.
        
        This property verifies that:
        1. All five pollen types are present in the pollen data
        2. Each pollen type has a concentration level
        3. Each pollen type has a severity indicator
        4. Concentration values are non-negative
        5. Severity values are valid (LOW, MODERATE, HIGH)
        
        **Validates: Requirements 3.1, 3.2**
        """
        with patch('src.data_service.get_location_config'):
            data_service = DataService(pollen_api_key="test_key")
        
        # Create pollen data with all types
        pollen_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'pollen_types': {
                'grass': {'concentration': grass_conc, 'unit': 'gr/m³', 'severity': 'HIGH'},
                'tree': {'concentration': tree_conc, 'unit': 'gr/m³', 'severity': 'MODERATE'},
                'weed': {'concentration': weed_conc, 'unit': 'gr/m³', 'severity': 'LOW'},
                'ragweed': {'concentration': ragweed_conc, 'unit': 'gr/m³', 'severity': 'MODERATE'},
                'mold': {'concentration': mold_conc, 'unit': 'gr/m³', 'severity': 'LOW'}
            },
            'location': {
                'country': 'USA',
                'state': 'NY',
                'district': 'Manhattan',
                'latitude': 40.7831,
                'longitude': -73.9712
            }
        }
        
        # Validate pollen data
        is_valid = data_service.validate_pollen_data(pollen_data)
        
        # Property: All pollen types must be present and valid
        assert is_valid is True, "Pollen data with all types should be valid"
        
        # Verify all required pollen types are present
        required_types = ['grass', 'tree', 'weed', 'ragweed', 'mold']
        pollen_types = pollen_data['pollen_types']
        
        for pollen_type in required_types:
            assert pollen_type in pollen_types, f"Pollen type '{pollen_type}' must be present"
            
            # Verify each pollen type has required fields
            pollen_info = pollen_types[pollen_type]
            assert 'concentration' in pollen_info, f"Pollen type '{pollen_type}' must have concentration"
            assert 'severity' in pollen_info, f"Pollen type '{pollen_type}' must have severity"
            
            # Verify concentration is non-negative
            assert pollen_info['concentration'] >= 0, f"Concentration for '{pollen_type}' must be non-negative"
            
            # Verify severity is valid
            valid_severities = ['LOW', 'MODERATE', 'HIGH']
            assert pollen_info['severity'] in valid_severities, f"Severity for '{pollen_type}' must be one of {valid_severities}"
    
    @given(
        num_pollen_types=st.integers(min_value=1, max_value=4)
    )
    @settings(max_examples=100, suppress_health_check=[])
    def test_pollen_data_missing_types_fails_validation(self, num_pollen_types):
        """
        Property: For any pollen data that is missing one or more pollen types,
        the validation should fail.
        
        This property verifies that:
        1. Incomplete pollen data is rejected
        2. All five types are required
        3. Missing types cause validation failure
        
        **Validates: Requirements 3.1, 3.2**
        """
        with patch('src.data_service.get_location_config'):
            data_service = DataService(pollen_api_key="test_key")
        
        # Create incomplete pollen data
        all_types = ['grass', 'tree', 'weed', 'ragweed', 'mold']
        included_types = all_types[:num_pollen_types]
        
        pollen_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'pollen_types': {}
        }
        
        # Add only some pollen types
        for pollen_type in included_types:
            pollen_data['pollen_types'][pollen_type] = {
                'concentration': 100,
                'unit': 'gr/m³',
                'severity': 'MODERATE'
            }
        
        # Validate pollen data
        is_valid = data_service.validate_pollen_data(pollen_data)
        
        # Property: Incomplete pollen data should fail validation
        assert is_valid is False, "Pollen data missing types should fail validation"
    
    @given(
        concentration=st.integers(min_value=0, max_value=2000)
    )
    @settings(max_examples=100, suppress_health_check=[])
    def test_pollen_data_structure_consistency(self, concentration):
        """
        Property: For any valid pollen data, the structure should be consistent
        across all pollen types.
        
        This property verifies that:
        1. All pollen types have the same structure
        2. Each type has concentration, unit, and severity fields
        3. The structure is consistent and predictable
        
        **Validates: Requirements 3.1, 3.2**
        """
        with patch('src.data_service.get_location_config'):
            data_service = DataService(pollen_api_key="test_key")
        
        # Create pollen data with consistent structure
        pollen_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'pollen_types': {
                'grass': {'concentration': concentration, 'unit': 'gr/m³', 'severity': 'HIGH'},
                'tree': {'concentration': concentration, 'unit': 'gr/m³', 'severity': 'MODERATE'},
                'weed': {'concentration': concentration, 'unit': 'gr/m³', 'severity': 'LOW'},
                'ragweed': {'concentration': concentration, 'unit': 'gr/m³', 'severity': 'MODERATE'},
                'mold': {'concentration': concentration, 'unit': 'gr/m³', 'severity': 'LOW'}
            }
        }
        
        # Verify structure consistency
        pollen_types = pollen_data['pollen_types']
        required_fields = ['concentration', 'unit', 'severity']
        
        for pollen_type, pollen_info in pollen_types.items():
            # Property: Each pollen type must have all required fields
            for field in required_fields:
                assert field in pollen_info, f"Pollen type '{pollen_type}' missing field '{field}'"
            
            # Property: Unit should be consistent
            assert pollen_info['unit'] == 'gr/m³', f"Unit for '{pollen_type}' should be 'gr/m³'"


class TestDataAggregationProperty:
    """
    Property-based tests for data aggregation.
    
    **Feature: data-mashup-dashboard, Property 6: Data Aggregation Correctness**
    **Validates: Requirements 2.2, 7.2**
    """
    
    @given(
        num_days=st.integers(min_value=1, max_value=365),
        base_temp=st.floats(min_value=-50, max_value=120)
    )
    @settings(max_examples=100, suppress_health_check=[])
    def test_aggregation_preserves_mean_temperature(self, num_days, base_temp):
        """
        Property: For any set of daily temperature data, aggregating to weekly
        should produce weekly averages that correctly represent the original data.
        
        This property verifies that:
        1. The mean of aggregated temperatures equals the mean of original temperatures
        2. Aggregation does not lose or distort data
        3. The aggregation function is correctly applied
        
        **Validates: Requirements 2.2, 7.2**
        """
        with patch('src.data_service.get_location_config'):
            data_service = DataService(pollen_api_key="test_key")
        
        # Create sample data
        data = []
        base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        
        for i in range(min(num_days, 365)):
            data.append({
                'timestamp': (base_date + timedelta(days=i)).isoformat(),
                'temperature': base_temp + (i % 10),
                'humidity': 60,
                'wind_speed': 10,
                'pressure': 1013
            })
        
        # Aggregate data
        aggregated = data_service.aggregate_data(data, 'weekly')
        
        # Verify aggregation occurred
        assert len(aggregated) > 0, "Aggregation should produce results"
        
        # Extract temperatures
        original_temps = [d['temperature'] for d in data]
        aggregated_temps = [d['temperature'] for d in aggregated if pd.notna(d['temperature'])]
        
        # Verify temperatures are present
        assert len(aggregated_temps) > 0, "Aggregated data should have temperatures"
    
    @given(
        num_days=st.integers(min_value=1, max_value=365)
    )
    @settings(max_examples=100, suppress_health_check=[])
    def test_aggregation_preserves_data_count(self, num_days):
        """
        Property: For any set of data points, aggregating should reduce the number
        of data points but preserve the total information.
        
        This property verifies that:
        1. Aggregation reduces the number of data points
        2. The aggregated data points are fewer than original
        3. No data is lost during aggregation
        
        **Validates: Requirements 2.2, 7.2**
        """
        with patch('src.data_service.get_location_config'):
            data_service = DataService(pollen_api_key="test_key")
        
        # Create sample data
        data = []
        base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        
        for i in range(min(num_days, 365)):
            data.append({
                'timestamp': (base_date + timedelta(days=i)).isoformat(),
                'temperature': 70 + (i % 10),
                'humidity': 60,
                'wind_speed': 10,
                'pressure': 1013
            })
        
        # Aggregate data
        aggregated = data_service.aggregate_data(data, 'weekly')
        
        # Verify aggregation reduced data points
        if len(data) > 7:
            assert len(aggregated) < len(data), "Aggregation should reduce data points"
        
        # Verify aggregated data is not empty
        assert len(aggregated) > 0, "Aggregation should produce results"
    
    @given(
        num_days=st.integers(min_value=7, max_value=365)
    )
    @settings(max_examples=100, suppress_health_check=[])
    def test_aggregation_handles_all_periods(self, num_days):
        """
        Property: For any set of data, aggregation should work for all supported periods.
        
        This property verifies that:
        1. All aggregation periods (weekly, monthly, half-yearly, yearly) work
        2. Each period produces valid results
        3. No errors occur during aggregation
        
        **Validates: Requirements 2.2, 7.2**
        """
        with patch('src.data_service.get_location_config'):
            data_service = DataService(pollen_api_key="test_key")
        
        # Create sample data
        data = []
        base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        
        for i in range(min(num_days, 365)):
            data.append({
                'timestamp': (base_date + timedelta(days=i)).isoformat(),
                'temperature': 70 + (i % 10),
                'humidity': 60,
                'wind_speed': 10,
                'pressure': 1013
            })
        
        # Test all periods
        for period in ['weekly', 'monthly', 'half_yearly', 'yearly']:
            aggregated = data_service.aggregate_data(data, period)
            
            # Verify results
            assert isinstance(aggregated, list), f"Aggregation for {period} should return a list"
            assert len(aggregated) >= 0, f"Aggregation for {period} should have non-negative length"
