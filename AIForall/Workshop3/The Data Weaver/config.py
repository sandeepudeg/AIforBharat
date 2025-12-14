"""
Configuration management module for Weather & Pollen Dashboard.

This module handles loading location hierarchy from JSON configuration,
validating locations, and retrieving coordinates for API calls.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class LocationConfig:
    """
    Manages location hierarchy and coordinate retrieval.
    
    Loads location data from a JSON configuration file and provides
    methods to validate locations and retrieve their coordinates.
    """
    
    def __init__(self, config_file: str = 'location_config.json'):
        """
        Initialize LocationConfig by loading location hierarchy.
        
        Args:
            config_file (str): Path to the location configuration JSON file.
                             Defaults to 'location_config.json' in the current directory.
        
        Raises:
            FileNotFoundError: If the configuration file does not exist.
            json.JSONDecodeError: If the configuration file is not valid JSON.
        """
        self.config_file = config_file
        self.location_data = {}
        self._load_location_hierarchy()
    
    def _load_location_hierarchy(self) -> None:
        """
        Load location hierarchy from JSON configuration file.
        
        The JSON file should have the following structure:
        {
            "countries": {
                "COUNTRY_CODE": {
                    "name": "Country Name",
                    "states": {
                        "STATE_CODE": {
                            "name": "State Name",
                            "latitude": float,
                            "longitude": float,
                            "districts": {
                                "DISTRICT_NAME": {
                                    "latitude": float,
                                    "longitude": float
                                }
                            }
                        }
                    }
                }
            }
        }
        
        Raises:
            FileNotFoundError: If the configuration file does not exist.
            json.JSONDecodeError: If the configuration file is not valid JSON.
        """
        if not os.path.exists(self.config_file):
            logger.error(f"Configuration file not found: {self.config_file}")
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.location_data = json.load(f)
            logger.info(f"Location hierarchy loaded from {self.config_file}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            raise
    
    def get_countries(self) -> List[Dict[str, str]]:
        """
        Get list of all available countries.
        
        Returns:
            List[Dict[str, str]]: List of dictionaries with 'code' and 'name' keys.
                                 Example: [{'code': 'USA', 'name': 'United States of America'}, ...]
        """
        countries = []
        if 'countries' in self.location_data:
            for code, country_info in self.location_data['countries'].items():
                countries.append({
                    'code': code,
                    'name': country_info.get('name', code)
                })
        logger.debug(f"Retrieved {len(countries)} countries")
        return countries
    
    def get_states(self, country_code: str) -> List[Dict[str, str]]:
        """
        Get list of all states for a given country.
        
        Args:
            country_code (str): The country code (e.g., 'USA', 'India').
        
        Returns:
            List[Dict[str, str]]: List of dictionaries with 'code' and 'name' keys.
                                 Example: [{'code': 'NY', 'name': 'New York'}, ...]
                                 Returns empty list if country not found.
        """
        states = []
        if 'countries' in self.location_data:
            country = self.location_data['countries'].get(country_code)
            if country and 'states' in country:
                for state_code, state_info in country['states'].items():
                    states.append({
                        'code': state_code,
                        'name': state_info.get('name', state_code)
                    })
        logger.debug(f"Retrieved {len(states)} states for country {country_code}")
        return states
    
    def get_districts(self, country_code: str, state_code: str) -> List[Dict[str, str]]:
        """
        Get list of all districts for a given country and state.
        
        Args:
            country_code (str): The country code (e.g., 'USA', 'India').
            state_code (str): The state code (e.g., 'NY', 'CA').
        
        Returns:
            List[Dict[str, str]]: List of district names.
                                 Example: ['Manhattan', 'Brooklyn', 'Queens']
                                 Returns empty list if country or state not found.
        """
        districts = []
        if 'countries' in self.location_data:
            country = self.location_data['countries'].get(country_code)
            if country and 'states' in country:
                state = country['states'].get(state_code)
                if state and 'districts' in state:
                    districts = list(state['districts'].keys())
        logger.debug(f"Retrieved {len(districts)} districts for {country_code}/{state_code}")
        return districts
    
    def validate_location(self, country_code: str, state_code: str, district_name: str) -> bool:
        """
        Validate that a location (country, state, district) exists in the configuration.
        
        Args:
            country_code (str): The country code (e.g., 'USA', 'India').
            state_code (str): The state code (e.g., 'NY', 'CA').
            district_name (str): The district name (e.g., 'Manhattan', 'Brooklyn').
        
        Returns:
            bool: True if the location exists, False otherwise.
        """
        if 'countries' not in self.location_data:
            logger.warning("No countries found in location data")
            return False
        
        country = self.location_data['countries'].get(country_code)
        if not country:
            logger.warning(f"Country not found: {country_code}")
            return False
        
        if 'states' not in country:
            logger.warning(f"No states found for country: {country_code}")
            return False
        
        state = country['states'].get(state_code)
        if not state:
            logger.warning(f"State not found: {state_code} in country {country_code}")
            return False
        
        if 'districts' not in state:
            logger.warning(f"No districts found for state: {state_code}")
            return False
        
        if district_name not in state['districts']:
            logger.warning(f"District not found: {district_name} in state {state_code}")
            return False
        
        logger.debug(f"Location validated: {country_code}/{state_code}/{district_name}")
        return True
    
    def get_coordinates(self, country_code: str, state_code: str, district_name: str) -> Optional[Tuple[float, float]]:
        """
        Get latitude and longitude coordinates for a specific location.
        
        Args:
            country_code (str): The country code (e.g., 'USA', 'India').
            state_code (str): The state code (e.g., 'NY', 'CA').
            district_name (str): The district name (e.g., 'Manhattan', 'Brooklyn').
        
        Returns:
            Optional[Tuple[float, float]]: A tuple of (latitude, longitude) if the location exists,
                                          None otherwise.
        
        Raises:
            ValueError: If the location is invalid or coordinates are missing.
        """
        if not self.validate_location(country_code, state_code, district_name):
            logger.error(f"Invalid location: {country_code}/{state_code}/{district_name}")
            raise ValueError(f"Invalid location: {country_code}/{state_code}/{district_name}")
        
        try:
            district = self.location_data['countries'][country_code]['states'][state_code]['districts'][district_name]
            
            latitude = district.get('latitude')
            longitude = district.get('longitude')
            
            if latitude is None or longitude is None:
                logger.error(f"Missing coordinates for {country_code}/{state_code}/{district_name}")
                raise ValueError(f"Missing coordinates for location: {country_code}/{state_code}/{district_name}")
            
            logger.debug(f"Retrieved coordinates for {country_code}/{state_code}/{district_name}: ({latitude}, {longitude})")
            return (latitude, longitude)
        
        except (KeyError, TypeError) as e:
            logger.error(f"Error retrieving coordinates: {e}")
            raise ValueError(f"Error retrieving coordinates for {country_code}/{state_code}/{district_name}") from e
    
    def get_location_hierarchy(self) -> Dict:
        """
        Get the complete location hierarchy structure.
        
        Returns:
            Dict: The complete location hierarchy from the configuration file.
        """
        logger.debug("Retrieved complete location hierarchy")
        return self.location_data


# Global instance for easy access
_config_instance: Optional[LocationConfig] = None


def get_location_config(config_file: str = 'location_config.json') -> LocationConfig:
    """
    Get or create a singleton instance of LocationConfig.
    
    Args:
        config_file (str): Path to the location configuration JSON file.
                          Only used on first call.
    
    Returns:
        LocationConfig: The LocationConfig instance.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = LocationConfig(config_file)
    return _config_instance
