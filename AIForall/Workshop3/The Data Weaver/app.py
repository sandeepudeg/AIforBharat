"""
Main Flask application for Weather & Pollen Dashboard.

This module initializes the Flask app, sets up configuration,
error handlers, and logging for the dashboard application.
"""

import logging
import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def create_app(config=None):
    """
    Create and configure the Flask application.
    
    Args:
        config (dict, optional): Configuration dictionary to override defaults
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Default configuration
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', False)
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # Override with provided config if any
    if config:
        app.config.update(config)
    
    logger.info("Flask application initialized with configuration: %s", app.config)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register routes
    register_routes(app)
    
    return app


def register_error_handlers(app):
    """
    Register error handlers for the Flask application.
    
    Args:
        app (Flask): Flask application instance
    """
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors."""
        logger.warning("404 error: %s", error)
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status': 404
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        logger.error("500 error: %s", error)
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred on the server',
            'status': 500
        }), 500
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request errors."""
        logger.warning("400 error: %s", error)
        return jsonify({
            'error': 'Bad Request',
            'message': 'The request was invalid or malformed',
            'status': 400
        }), 400
    
    logger.info("Error handlers registered")


def register_routes(app):
    """
    Register routes for the Flask application.
    
    Args:
        app (Flask): Flask application instance
    """
    from src.data_service import DataService, DataServiceError
    from src.correlation_calculator import CorrelationCalculator, CorrelationCalculatorError
    from config import get_location_config
    
    # Initialize services with API keys
    weather_api_key = os.getenv("WEATHERBIT_API_KEY", "ae394525c7444e92bd13494a7afc7518")
    pollen_api_key = os.getenv("AQICN_API_KEY")
    
    data_service = DataService(weather_api_key=weather_api_key, pollen_api_key=pollen_api_key)
    correlation_calculator = CorrelationCalculator()
    location_config = get_location_config()
    
    @app.route('/')
    def dashboard():
        """
        Serve the main dashboard HTML page.
        
        Returns:
            str: Rendered dashboard HTML template
        """
        logger.info("Dashboard page requested")
        try:
            return render_template('dashboard.html')
        except Exception as e:
            logger.error("Error rendering dashboard template: %s", e)
            return jsonify({
                'error': 'Template Error',
                'message': 'Failed to load dashboard template',
                'status': 500
            }), 500
    
    @app.route('/health')
    def health_check():
        """
        Health check endpoint for monitoring application status.
        
        Returns:
            dict: JSON response with health status
        """
        logger.debug("Health check requested")
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'Weather & Pollen Dashboard'
        }), 200
    
    @app.route('/api/weather/<country>/<state>/<district>')
    def get_weather(country, state, district):
        """
        Fetch weather data for a specific location.
        
        Args:
            country (str): Country code (e.g., 'USA', 'India')
            state (str): State code (e.g., 'NY', 'CA')
            district (str): District name (e.g., 'Manhattan', 'Brooklyn')
        
        Returns:
            dict: JSON response with weather data or error message
        
        Status Codes:
            200: Successfully retrieved weather data (fresh or cached)
            400: Invalid location provided or validation failed
            500: Server error during data fetch
        
        Example:
            GET /api/weather/USA/NY/Manhattan
            
            Response (200):
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
        logger.info(f"Weather data requested for {country}/{state}/{district}")
        
        try:
            # Validate location
            if not location_config.validate_location(country, state, district):
                logger.warning(f"Invalid location: {country}/{state}/{district}")
                return jsonify({
                    'error': 'Invalid Location',
                    'message': f'Location not found: {country}/{state}/{district}',
                    'status': 400
                }), 400
            
            # Fetch weather data (with fallback to cache if API fails)
            weather_data = data_service.fetch_weather_data(country, state, district)
            
            # Validate weather data ranges and required fields
            if not data_service.validate_weather_data(weather_data):
                logger.error(f"Weather data validation failed for {country}/{state}/{district}")
                return jsonify({
                    'error': 'Data Validation Error',
                    'message': 'Weather data failed validation checks. Data may be corrupted or out of range.',
                    'status': 400
                }), 400
            
            # Check if data is from cache
            if weather_data.get('cached_data'):
                logger.warning(f"Returning cached weather data for {country}/{state}/{district}: {weather_data.get('cache_error', 'Unknown error')}")
            else:
                logger.info(f"Successfully retrieved fresh weather data for {country}/{state}/{district}")
            
            return jsonify(weather_data), 200
        
        except DataServiceError as e:
            logger.error(f"Data service error: {e}")
            return jsonify({
                'error': 'Data Service Error',
                'message': str(e),
                'status': 500
            }), 500
        
        except Exception as e:
            logger.error(f"Unexpected error fetching weather data: {e}")
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred while fetching weather data',
                'status': 500
            }), 500
    
    @app.route('/api/pollen/<country>/<state>/<district>')
    def get_pollen(country, state, district):
        """
        Fetch pollen data for a specific location.
        
        Args:
            country (str): Country code (e.g., 'USA', 'India')
            state (str): State code (e.g., 'NY', 'CA')
            district (str): District name (e.g., 'Manhattan', 'Brooklyn')
        
        Returns:
            dict: JSON response with pollen data or error message
        
        Status Codes:
            200: Successfully retrieved pollen data (fresh or cached)
            400: Invalid location provided or validation failed
            500: Server error during data fetch
        
        Example:
            GET /api/pollen/USA/NY/Manhattan
            
            Response (200):
            {
                "timestamp": "2024-01-15T00:00:00Z",
                "location": {"country": "USA", "state": "NY", "district": "Manhattan"},
                "pollen_types": {
                    "grass": {"concentration": 850, "unit": "gr/m³", "severity": "HIGH"},
                    "tree": {"concentration": 450, "unit": "gr/m³", "severity": "MODERATE"},
                    "weed": {"concentration": 150, "unit": "gr/m³", "severity": "LOW"},
                    "ragweed": {"concentration": 200, "unit": "gr/m³", "severity": "LOW"},
                    "mold": {"concentration": 320, "unit": "gr/m³", "severity": "MODERATE"}
                },
                "cached_data": false
            }
        """
        logger.info(f"Pollen data requested for {country}/{state}/{district}")
        
        try:
            # Validate location
            if not location_config.validate_location(country, state, district):
                logger.warning(f"Invalid location: {country}/{state}/{district}")
                return jsonify({
                    'error': 'Invalid Location',
                    'message': f'Location not found: {country}/{state}/{district}',
                    'status': 400
                }), 400
            
            # Fetch pollen data (with fallback to cache if API fails)
            pollen_data = data_service.fetch_pollen_data(country, state, district)
            
            # Validate pollen data structure and required fields
            if not data_service.validate_pollen_data(pollen_data):
                logger.error(f"Pollen data validation failed for {country}/{state}/{district}")
                return jsonify({
                    'error': 'Data Validation Error',
                    'message': 'Pollen data failed validation checks. Missing pollen types or invalid structure.',
                    'status': 400
                }), 400
            
            # Check if data is from cache
            if pollen_data.get('cached_data'):
                logger.warning(f"Returning cached pollen data for {country}/{state}/{district}: {pollen_data.get('cache_error', 'Unknown error')}")
            else:
                logger.info(f"Successfully retrieved fresh pollen data for {country}/{state}/{district}")
            
            return jsonify(pollen_data), 200
        
        except DataServiceError as e:
            logger.error(f"Data service error: {e}")
            return jsonify({
                'error': 'Data Service Error',
                'message': str(e),
                'status': 500
            }), 500
        
        except Exception as e:
            logger.error(f"Unexpected error fetching pollen data: {e}")
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred while fetching pollen data',
                'status': 500
            }), 500
    
    @app.route('/api/correlation/<country>/<state>/<district>')
    def get_correlation(country, state, district):
        """
        Calculate and fetch correlation data between weather factors and pollen levels.
        
        Args:
            country (str): Country code (e.g., 'USA', 'India')
            state (str): State code (e.g., 'NY', 'CA')
            district (str): District name (e.g., 'Manhattan', 'Brooklyn')
        
        Returns:
            dict: JSON response with correlation data or error message
        
        Status Codes:
            200: Successfully calculated correlations
            400: Invalid location provided
            500: Server error during calculation
        
        Example:
            GET /api/correlation/USA/NY/Manhattan
            
            Response (200):
            {
                "location": {"country": "USA", "state": "NY", "district": "Manhattan"},
                "timestamp": "2024-01-15T14:30:00Z",
                "correlations": [
                    {
                        "weather_factor": "temperature",
                        "pollen_type": "grass",
                        "correlation_coefficient": 0.78,
                        "strength": "Strong Positive",
                        "explanation": "Higher temperatures increase grass pollen production..."
                    },
                    ...
                ]
            }
        """
        logger.info(f"Correlation data requested for {country}/{state}/{district}")
        
        try:
            # Validate location
            if not location_config.validate_location(country, state, district):
                logger.warning(f"Invalid location: {country}/{state}/{district}")
                return jsonify({
                    'error': 'Invalid Location',
                    'message': f'Location not found: {country}/{state}/{district}',
                    'status': 400
                }), 400
            
            # Fetch weather and pollen data
            weather_data = data_service.fetch_weather_data(country, state, district)
            pollen_data = data_service.fetch_pollen_data(country, state, district)
            
            # For correlation calculation, we need historical data
            # For now, we'll create a simple correlation response with the current data
            # In a production system, this would use historical data from a database
            
            # Create lists with single data point for correlation calculation
            weather_list = [weather_data]
            pollen_list = [pollen_data]
            
            # Calculate correlations
            correlations = correlation_calculator.calculate_all_correlations(weather_list, pollen_list)
            
            response = {
                'location': {
                    'country': country,
                    'state': state,
                    'district': district
                },
                'timestamp': datetime.utcnow().isoformat(),
                'correlations': correlations
            }
            
            logger.info(f"Successfully calculated correlations for {country}/{state}/{district}")
            return jsonify(response), 200
        
        except DataServiceError as e:
            logger.error(f"Data service error: {e}")
            return jsonify({
                'error': 'Data Service Error',
                'message': str(e),
                'status': 500
            }), 500
        
        except CorrelationCalculatorError as e:
            logger.error(f"Correlation calculator error: {e}")
            return jsonify({
                'error': 'Correlation Calculation Error',
                'message': str(e),
                'status': 500
            }), 500
        
        except Exception as e:
            logger.error(f"Unexpected error calculating correlations: {e}")
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred while calculating correlations',
                'status': 500
            }), 500
    
    @app.route('/api/export', methods=['POST'])
    def export_data():
        """
        Export current weather and pollen data with metadata as JSON.
        
        Request body should contain:
        {
            "country": "USA",
            "state": "NY",
            "district": "Manhattan"
        }
        
        Returns:
            dict: JSON response with exported data or error message
        
        Status Codes:
            200: Successfully exported data
            400: Invalid location or request body
            500: Server error during export
        
        Example:
            POST /api/export
            
            Request body:
            {
                "country": "USA",
                "state": "NY",
                "district": "Manhattan"
            }
            
            Response (200):
            {
                "export_timestamp": "2024-01-15T14:30:00Z",
                "location": {"country": "USA", "state": "NY", "district": "Manhattan"},
                "weather": {
                    "timestamp": "2024-01-15T14:30:00Z",
                    "temperature": 72.5,
                    "humidity": 65,
                    ...
                },
                "pollen": {
                    "timestamp": "2024-01-15T00:00:00Z",
                    "pollen_types": {...}
                },
                "correlations": [
                    {
                        "weather_factor": "temperature",
                        "pollen_type": "grass",
                        "correlation_coefficient": 0.78,
                        ...
                    }
                ],
                "metadata": {
                    "data_sources": ["Open-Meteo", "AQICN"],
                    "export_format": "JSON",
                    "version": "1.0"
                }
            }
        """
        logger.info("Export data requested")
        
        try:
            # Get request data
            request_data = request.get_json(silent=True)
            
            if not request_data:
                logger.warning("Export request missing JSON body")
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'Request body must contain JSON with country, state, and district',
                    'status': 400
                }), 400
            
            # Extract location parameters
            country = request_data.get('country')
            state = request_data.get('state')
            district = request_data.get('district')
            
            # Validate required fields
            if not country or not state or not district:
                logger.warning("Export request missing location parameters")
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'Request body must contain country, state, and district',
                    'status': 400
                }), 400
            
            # Validate location
            if not location_config.validate_location(country, state, district):
                logger.warning(f"Invalid location for export: {country}/{state}/{district}")
                return jsonify({
                    'error': 'Invalid Location',
                    'message': f'Location not found: {country}/{state}/{district}',
                    'status': 400
                }), 400
            
            # Fetch weather data
            weather_data = data_service.fetch_weather_data(country, state, district)
            
            # Fetch pollen data
            pollen_data = data_service.fetch_pollen_data(country, state, district)
            
            # Calculate correlations
            weather_list = [weather_data]
            pollen_list = [pollen_data]
            correlations = correlation_calculator.calculate_all_correlations(weather_list, pollen_list)
            
            # Create export data structure
            export_data = {
                'export_timestamp': datetime.utcnow().isoformat(),
                'location': {
                    'country': country,
                    'state': state,
                    'district': district
                },
                'weather': weather_data,
                'pollen': pollen_data,
                'correlations': correlations,
                'metadata': {
                    'data_sources': ['Open-Meteo', 'AQICN'],
                    'export_format': 'JSON',
                    'version': '1.0'
                }
            }
            
            logger.info(f"Successfully exported data for {country}/{state}/{district}")
            return jsonify(export_data), 200
        
        except DataServiceError as e:
            logger.error(f"Data service error during export: {e}")
            return jsonify({
                'error': 'Data Service Error',
                'message': str(e),
                'status': 500
            }), 500
        
        except CorrelationCalculatorError as e:
            logger.error(f"Correlation calculator error during export: {e}")
            return jsonify({
                'error': 'Correlation Calculation Error',
                'message': str(e),
                'status': 500
            }), 500
        
        except Exception as e:
            logger.error(f"Unexpected error during export: {e}")
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred while exporting data',
                'status': 500
            }), 500
    
    @app.route('/api/locations')
    def get_locations():
        """
        Get location hierarchy with optional filtering by country and state.
        
        Query Parameters:
            country (str, optional): Filter by country code (e.g., 'USA', 'India')
            state (str, optional): Filter by state code (e.g., 'NY', 'CA'). Requires country parameter.
        
        Returns:
            dict: JSON response with location hierarchy or filtered results
        
        Status Codes:
            200: Successfully retrieved locations
            400: Invalid query parameters
            404: Country or state not found
        
        Examples:
            GET /api/locations
            Response (200):
            {
                "countries": [
                    {"code": "USA", "name": "United States of America"},
                    {"code": "India", "name": "India"},
                    ...
                ]
            }
            
            GET /api/locations?country=USA
            Response (200):
            {
                "country": "USA",
                "states": [
                    {"code": "NY", "name": "New York"},
                    {"code": "CA", "name": "California"},
                    ...
                ]
            }
            
            GET /api/locations?country=USA&state=NY
            Response (200):
            {
                "country": "USA",
                "state": "NY",
                "districts": ["Manhattan", "Brooklyn", "Queens"]
            }
        """
        logger.info("Location hierarchy requested")
        
        try:
            # Get query parameters
            country_filter = request.args.get('country')
            state_filter = request.args.get('state')
            
            # If state filter is provided, country must also be provided
            if state_filter and not country_filter:
                logger.warning("State filter provided without country filter")
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'State filter requires country filter to be specified',
                    'status': 400
                }), 400
            
            # Return all countries if no filters
            if not country_filter:
                countries = location_config.get_countries()
                logger.info(f"Retrieved {len(countries)} countries")
                return jsonify({
                    'countries': countries
                }), 200
            
            # Return states for a specific country
            if country_filter and not state_filter:
                # Validate country exists
                countries = location_config.get_countries()
                country_codes = [c['code'] for c in countries]
                
                if country_filter not in country_codes:
                    logger.warning(f"Country not found: {country_filter}")
                    return jsonify({
                        'error': 'Not Found',
                        'message': f'Country not found: {country_filter}',
                        'status': 404
                    }), 404
                
                states = location_config.get_states(country_filter)
                logger.info(f"Retrieved {len(states)} states for country {country_filter}")
                return jsonify({
                    'country': country_filter,
                    'states': states
                }), 200
            
            # Return districts for a specific country and state
            if country_filter and state_filter:
                # Validate country exists
                countries = location_config.get_countries()
                country_codes = [c['code'] for c in countries]
                
                if country_filter not in country_codes:
                    logger.warning(f"Country not found: {country_filter}")
                    return jsonify({
                        'error': 'Not Found',
                        'message': f'Country not found: {country_filter}',
                        'status': 404
                    }), 404
                
                # Validate state exists
                states = location_config.get_states(country_filter)
                state_codes = [s['code'] for s in states]
                
                if state_filter not in state_codes:
                    logger.warning(f"State not found: {state_filter} in country {country_filter}")
                    return jsonify({
                        'error': 'Not Found',
                        'message': f'State not found: {state_filter} in country {country_filter}',
                        'status': 404
                    }), 404
                
                districts = location_config.get_districts(country_filter, state_filter)
                logger.info(f"Retrieved {len(districts)} districts for {country_filter}/{state_filter}")
                return jsonify({
                    'country': country_filter,
                    'state': state_filter,
                    'districts': districts
                }), 200
        
        except Exception as e:
            logger.error(f"Unexpected error retrieving locations: {e}")
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred while retrieving locations',
                'status': 500
            }), 500
    
    logger.info("Routes registered")


if __name__ == '__main__':
    app = create_app()
    logger.info("Starting Weather & Pollen Dashboard application")
    app.run(host='0.0.0.0', port=5000, debug=True)
