"""
Unit tests for the configuration management module (config.py).

Tests location hierarchy loading, validation, and coordinate retrieval.
"""

import json
import os
import pytest
import tempfile
from hypothesis import given, strategies as st, settings
from config import LocationConfig, get_location_config


@pytest.fixture
def sample_location_config():
    """Create a sample location configuration for testing."""
    return {
        "countries": {
            "USA": {
                "name": "United States of America",
                "states": {
                    "NY": {
                        "name": "New York",
                        "latitude": 42.1657,
                        "longitude": -74.9481,
                        "districts": {
                            "Manhattan": {
                                "latitude": 40.7831,
                                "longitude": -73.9712
                            },
                            "Brooklyn": {
                                "latitude": 40.6501,
                                "longitude": -73.9496
                            }
                        }
                    },
                    "CA": {
                        "name": "California",
                        "latitude": 36.1162,
                        "longitude": -119.6816,
                        "districts": {
                            "Los Angeles": {
                                "latitude": 34.0522,
                                "longitude": -118.2437
                            }
                        }
                    }
                }
            },
            "India": {
                "name": "India",
                "states": {
                    "MH": {
                        "name": "Maharashtra",
                        "latitude": 19.7515,
                        "longitude": 75.7139,
                        "districts": {
                            "Mumbai": {
                                "latitude": 19.0760,
                                "longitude": 72.8777
                            }
                        }
                    }
                }
            }
        }
    }


@pytest.fixture
def temp_config_file(sample_location_config):
    """Create a temporary configuration file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_location_config, f)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    if os.path.exists(temp_file):
        os.remove(temp_file)


class TestLocationConfigInitialization:
    """Test LocationConfig initialization and file loading."""
    
    def test_load_valid_config_file(self, temp_config_file):
        """Test loading a valid configuration file."""
        config = LocationConfig(temp_config_file)
        assert config.location_data is not None
        assert 'countries' in config.location_data
    
    def test_load_nonexistent_file(self):
        """Test that FileNotFoundError is raised for nonexistent file."""
        with pytest.raises(FileNotFoundError):
            LocationConfig('nonexistent_file.json')
    
    def test_load_invalid_json(self):
        """Test that JSONDecodeError is raised for invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_file = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                LocationConfig(temp_file)
        finally:
            os.remove(temp_file)


class TestGetCountries:
    """Test get_countries method."""
    
    def test_get_countries_returns_list(self, temp_config_file):
        """Test that get_countries returns a list of countries."""
        config = LocationConfig(temp_config_file)
        countries = config.get_countries()
        
        assert isinstance(countries, list)
        assert len(countries) == 2
    
    def test_get_countries_structure(self, temp_config_file):
        """Test that countries have correct structure with code and name."""
        config = LocationConfig(temp_config_file)
        countries = config.get_countries()
        
        for country in countries:
            assert 'code' in country
            assert 'name' in country
            assert isinstance(country['code'], str)
            assert isinstance(country['name'], str)
    
    def test_get_countries_contains_expected_countries(self, temp_config_file):
        """Test that expected countries are in the list."""
        config = LocationConfig(temp_config_file)
        countries = config.get_countries()
        country_codes = [c['code'] for c in countries]
        
        assert 'USA' in country_codes
        assert 'India' in country_codes


class TestGetStates:
    """Test get_states method."""
    
    def test_get_states_for_valid_country(self, temp_config_file):
        """Test getting states for a valid country."""
        config = LocationConfig(temp_config_file)
        states = config.get_states('USA')
        
        assert isinstance(states, list)
        assert len(states) == 2
    
    def test_get_states_structure(self, temp_config_file):
        """Test that states have correct structure."""
        config = LocationConfig(temp_config_file)
        states = config.get_states('USA')
        
        for state in states:
            assert 'code' in state
            assert 'name' in state
    
    def test_get_states_for_invalid_country(self, temp_config_file):
        """Test that empty list is returned for invalid country."""
        config = LocationConfig(temp_config_file)
        states = config.get_states('InvalidCountry')
        
        assert states == []
    
    def test_get_states_contains_expected_states(self, temp_config_file):
        """Test that expected states are in the list."""
        config = LocationConfig(temp_config_file)
        states = config.get_states('USA')
        state_codes = [s['code'] for s in states]
        
        assert 'NY' in state_codes
        assert 'CA' in state_codes


class TestGetDistricts:
    """Test get_districts method."""
    
    def test_get_districts_for_valid_location(self, temp_config_file):
        """Test getting districts for a valid country and state."""
        config = LocationConfig(temp_config_file)
        districts = config.get_districts('USA', 'NY')
        
        assert isinstance(districts, list)
        assert len(districts) == 2
    
    def test_get_districts_contains_expected_districts(self, temp_config_file):
        """Test that expected districts are in the list."""
        config = LocationConfig(temp_config_file)
        districts = config.get_districts('USA', 'NY')
        
        assert 'Manhattan' in districts
        assert 'Brooklyn' in districts
    
    def test_get_districts_for_invalid_country(self, temp_config_file):
        """Test that empty list is returned for invalid country."""
        config = LocationConfig(temp_config_file)
        districts = config.get_districts('InvalidCountry', 'NY')
        
        assert districts == []
    
    def test_get_districts_for_invalid_state(self, temp_config_file):
        """Test that empty list is returned for invalid state."""
        config = LocationConfig(temp_config_file)
        districts = config.get_districts('USA', 'InvalidState')
        
        assert districts == []


class TestValidateLocation:
    """Test validate_location method."""
    
    def test_validate_valid_location(self, temp_config_file):
        """Test validation of a valid location."""
        config = LocationConfig(temp_config_file)
        is_valid = config.validate_location('USA', 'NY', 'Manhattan')
        
        assert is_valid is True
    
    def test_validate_invalid_country(self, temp_config_file):
        """Test validation with invalid country."""
        config = LocationConfig(temp_config_file)
        is_valid = config.validate_location('InvalidCountry', 'NY', 'Manhattan')
        
        assert is_valid is False
    
    def test_validate_invalid_state(self, temp_config_file):
        """Test validation with invalid state."""
        config = LocationConfig(temp_config_file)
        is_valid = config.validate_location('USA', 'InvalidState', 'Manhattan')
        
        assert is_valid is False
    
    def test_validate_invalid_district(self, temp_config_file):
        """Test validation with invalid district."""
        config = LocationConfig(temp_config_file)
        is_valid = config.validate_location('USA', 'NY', 'InvalidDistrict')
        
        assert is_valid is False
    
    def test_validate_all_valid_locations(self, temp_config_file):
        """Test validation of all valid locations in config."""
        config = LocationConfig(temp_config_file)
        
        # Test USA locations
        assert config.validate_location('USA', 'NY', 'Manhattan') is True
        assert config.validate_location('USA', 'NY', 'Brooklyn') is True
        assert config.validate_location('USA', 'CA', 'Los Angeles') is True
        
        # Test India locations
        assert config.validate_location('India', 'MH', 'Mumbai') is True


class TestGetCoordinates:
    """Test get_coordinates method."""
    
    def test_get_coordinates_for_valid_location(self, temp_config_file):
        """Test getting coordinates for a valid location."""
        config = LocationConfig(temp_config_file)
        lat, lon = config.get_coordinates('USA', 'NY', 'Manhattan')
        
        assert isinstance(lat, float)
        assert isinstance(lon, float)
        assert lat == 40.7831
        assert lon == -73.9712
    
    def test_get_coordinates_returns_tuple(self, temp_config_file):
        """Test that get_coordinates returns a tuple."""
        config = LocationConfig(temp_config_file)
        result = config.get_coordinates('USA', 'NY', 'Manhattan')
        
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_get_coordinates_for_invalid_location(self, temp_config_file):
        """Test that ValueError is raised for invalid location."""
        config = LocationConfig(temp_config_file)
        
        with pytest.raises(ValueError):
            config.get_coordinates('InvalidCountry', 'NY', 'Manhattan')
    
    def test_get_coordinates_for_invalid_state(self, temp_config_file):
        """Test that ValueError is raised for invalid state."""
        config = LocationConfig(temp_config_file)
        
        with pytest.raises(ValueError):
            config.get_coordinates('USA', 'InvalidState', 'Manhattan')
    
    def test_get_coordinates_for_invalid_district(self, temp_config_file):
        """Test that ValueError is raised for invalid district."""
        config = LocationConfig(temp_config_file)
        
        with pytest.raises(ValueError):
            config.get_coordinates('USA', 'NY', 'InvalidDistrict')
    
    def test_get_coordinates_all_valid_locations(self, temp_config_file):
        """Test getting coordinates for all valid locations."""
        config = LocationConfig(temp_config_file)
        
        # Test USA locations
        lat, lon = config.get_coordinates('USA', 'NY', 'Manhattan')
        assert lat == 40.7831 and lon == -73.9712
        
        lat, lon = config.get_coordinates('USA', 'CA', 'Los Angeles')
        assert lat == 34.0522 and lon == -118.2437
        
        # Test India locations
        lat, lon = config.get_coordinates('India', 'MH', 'Mumbai')
        assert lat == 19.0760 and lon == 72.8777


class TestGetLocationHierarchy:
    """Test get_location_hierarchy method."""
    
    def test_get_location_hierarchy_returns_dict(self, temp_config_file):
        """Test that get_location_hierarchy returns the full hierarchy."""
        config = LocationConfig(temp_config_file)
        hierarchy = config.get_location_hierarchy()
        
        assert isinstance(hierarchy, dict)
        assert 'countries' in hierarchy
    
    def test_get_location_hierarchy_contains_all_data(self, temp_config_file):
        """Test that hierarchy contains all countries and states."""
        config = LocationConfig(temp_config_file)
        hierarchy = config.get_location_hierarchy()
        
        assert 'USA' in hierarchy['countries']
        assert 'India' in hierarchy['countries']
        assert 'NY' in hierarchy['countries']['USA']['states']


class TestLocationConfigSingleton:
    """Test the singleton pattern for LocationConfig."""
    
    def test_get_location_config_returns_instance(self, temp_config_file):
        """Test that get_location_config returns a LocationConfig instance."""
        config = get_location_config(temp_config_file)
        
        assert isinstance(config, LocationConfig)
    
    def test_get_location_config_singleton_behavior(self, temp_config_file):
        """Test that get_location_config returns the same instance."""
        config1 = get_location_config(temp_config_file)
        config2 = get_location_config(temp_config_file)
        
        assert config1 is config2



class TestLocationHierarchyConsistency:
    """
    Property-based tests for location hierarchy consistency.
    
    **Feature: data-mashup-dashboard, Property 5: Location Hierarchy Consistency**
    **Validates: Requirements 5.2, 5.3**
    """
    
    @given(
        country_code=st.sampled_from(['USA', 'India']),
        state_code=st.just(None),  # Will be determined based on country
    )
    @settings(max_examples=100)
    def test_states_belong_to_selected_country(self, country_code, state_code):
        """
        Property: For any country selection, the state dropdown should contain 
        only states that belong to that country.
        
        This tests that when a country is selected, all returned states are 
        actually part of that country in the configuration.
        """
        config = LocationConfig('location_config.json')
        
        # Get all states for the selected country
        states = config.get_states(country_code)
        
        # Verify that all returned states are valid for this country
        for state in states:
            state_code = state['code']
            # Verify the state exists in the country's states
            assert state_code in config.location_data['countries'][country_code]['states'], \
                f"State {state_code} should belong to country {country_code}"
    
    @given(
        country_code=st.sampled_from(['USA', 'India']),
        state_code=st.just(None),  # Will be determined based on country
    )
    @settings(max_examples=100)
    def test_districts_belong_to_selected_state(self, country_code, state_code):
        """
        Property: For any state selection, the district dropdown should contain 
        only districts that belong to that state.
        
        This tests that when a country and state are selected, all returned 
        districts are actually part of that state in the configuration.
        """
        config = LocationConfig('location_config.json')
        
        # Get all states for the country
        states = config.get_states(country_code)
        
        # For each state in the country, verify districts belong to it
        for state in states:
            state_code = state['code']
            districts = config.get_districts(country_code, state_code)
            
            # Verify that all returned districts are valid for this state
            for district_name in districts:
                assert district_name in config.location_data['countries'][country_code]['states'][state_code]['districts'], \
                    f"District {district_name} should belong to state {state_code} in country {country_code}"
    
    @given(
        country_code=st.sampled_from(['USA', 'India']),
    )
    @settings(max_examples=100)
    def test_no_cross_country_state_contamination(self, country_code):
        """
        Property: For any country, the states returned should not include 
        states from other countries.
        
        This tests that the state dropdown for one country does not accidentally 
        include states from other countries.
        """
        config = LocationConfig('location_config.json')
        
        # Get all states for the selected country
        states = config.get_states(country_code)
        state_codes = [s['code'] for s in states]
        
        # Get all other countries
        all_countries = config.get_countries()
        other_countries = [c['code'] for c in all_countries if c['code'] != country_code]
        
        # Verify no state from other countries appears in this country's states
        for other_country in other_countries:
            other_states = config.get_states(other_country)
            other_state_codes = [s['code'] for s in other_states]
            
            for state_code in state_codes:
                assert state_code not in other_state_codes, \
                    f"State {state_code} from {country_code} should not appear in {other_country}"
    
    @given(
        country_code=st.sampled_from(['USA', 'India']),
    )
    @settings(max_examples=100)
    def test_no_cross_state_district_contamination(self, country_code):
        """
        Property: For any state, the districts returned should not include 
        districts from other states in the same country.
        
        This tests that the district dropdown for one state does not accidentally 
        include districts from other states.
        """
        config = LocationConfig('location_config.json')
        
        # Get all states for the country
        states = config.get_states(country_code)
        
        # For each state, verify districts don't include districts from other states
        for state in states:
            state_code = state['code']
            districts = config.get_districts(country_code, state_code)
            district_names = set(districts)
            
            # Get all other states in the same country
            other_states = [s for s in states if s['code'] != state_code]
            
            for other_state in other_states:
                other_state_code = other_state['code']
                other_districts = config.get_districts(country_code, other_state_code)
                other_district_names = set(other_districts)
                
                # Verify no overlap between districts
                overlap = district_names & other_district_names
                assert len(overlap) == 0, \
                    f"Districts {overlap} appear in both {state_code} and {other_state_code}"
