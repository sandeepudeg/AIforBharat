# Weather & Pollen Dashboard

A Python-based web application that combines real-time weather data with pollen forecasts to help users understand how environmental conditions affect allergen levels. The dashboard provides interactive visualizations showing correlations between weather patterns and pollen concentrations.

## Features

- **Real-time Weather Data**: Current temperature, humidity, wind speed, pressure, precipitation, and UV index
- **Pollen Tracking**: Monitor five pollen types (grass, tree, weed, ragweed, mold spores) with concentration levels
- **Interactive Visualizations**: Chart.js-powered charts showing weather trends and pollen levels
- **Correlation Analysis**: Statistical analysis showing relationships between weather factors and pollen
- **Multi-location Support**: Hierarchical location selection (country → state → district)
- **Time Range Filtering**: View data for weekly, monthly, half-yearly, or yearly periods
- **Metric System Selection**: Toggle between Metric (°C, km/h) and Imperial (°F, mph) units
- **Data Export**: Export weather and pollen data as JSON with metadata
- **Resilient Caching**: Automatic fallback to cached data when APIs are unavailable
- **Responsive Design**: Works on desktop and tablet devices

## Technology Stack

- **Backend**: Python 3.8+, Flask 2.0+
- **Frontend**: HTML5, CSS3, JavaScript with Chart.js
- **Data Processing**: Pandas, NumPy
- **API Integration**: Requests library
- **Caching**: Flask-Caching
- **Testing**: pytest, Hypothesis (property-based testing)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)

### Step 1: Clone or Download the Project

```bash
git clone <repository-url>
cd weather-pollen-dashboard
```

Or download and extract the project files manually.

### Step 2: Create a Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` file includes:
- Flask 2.3.0+
- Pandas 1.5.0+
- NumPy 1.24.0+
- Requests 2.28.0+
- Flask-Caching 2.0.0+
- pytest 7.0.0+ (for testing)
- Hypothesis 6.0.0+ (for property-based testing)

### Step 4: Verify Installation

```bash
python -c "import flask, pandas, numpy, requests; print('All dependencies installed successfully!')"
```

## Configuration

### Location Configuration

The dashboard uses a JSON-based location hierarchy. Edit `location_config.json` to add or modify locations:

```json
{
  "countries": [
    {
      "name": "USA",
      "code": "US",
      "states": [
        {
          "name": "New York",
          "code": "NY",
          "districts": [
            {
              "name": "Manhattan",
              "latitude": 40.7831,
              "longitude": -73.9712
            }
          ]
        }
      ]
    }
  ]
}
```

**Fields**:
- `name`: Display name of the location
- `code`: ISO code (optional)
- `latitude`: Decimal latitude coordinate
- `longitude`: Decimal longitude coordinate

### Application Configuration

Edit `config.py` to customize application settings:

```python
# Cache TTL (Time To Live) in seconds
WEATHER_CACHE_TTL = 1800  # 30 minutes
POLLEN_CACHE_TTL = 86400  # 1 day

# API Configuration
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
POLLEN_API_URL = "https://api.waqi.info/feed"

# Retry Configuration
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 2  # Exponential backoff: 1s, 2s, 4s
```

### Environment Variables

Set these environment variables for production deployment:

```bash
# Flask Configuration
export FLASK_ENV=production
export FLASK_DEBUG=0
export SECRET_KEY=your-secret-key-here

# API Keys (if required by your data sources)
export WEATHER_API_KEY=your-api-key
export POLLEN_API_KEY=your-api-key

# Cache Configuration
export CACHE_TYPE=simple  # or 'redis' for production
export CACHE_REDIS_URL=redis://localhost:6379/0
```

## Usage

### Starting the Application

```bash
# Development mode
python app.py

# Production mode (with Gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

The dashboard will be available at `http://localhost:5000`

### Using the Dashboard

1. **Select Location**: Use the country, state, and district dropdowns to choose your location
2. **View Weather Data**: Current weather conditions are displayed in the top panel
3. **View Pollen Levels**: Pollen concentrations by type are shown in the middle panel
4. **Analyze Trends**: Use the time range buttons (Weekly, Monthly, Half-Yearly, Yearly) to view trends
5. **Select Parameters**: Check/uncheck weather parameters to display them on the trend chart
6. **View Correlations**: See how weather factors correlate with pollen levels
7. **Change Units**: Toggle between Metric and Imperial units using the selector
8. **Export Data**: Click the export button to download current data as JSON

### Keyboard Shortcuts

- `R`: Refresh data manually
- `E`: Export current data
- `M`: Toggle metric system
- `?`: Show help

## API Documentation

### Weather Endpoint

**GET** `/api/weather/<location>`

Returns current weather data for the specified location.

**Parameters**:
- `location` (string): Location identifier in format "country/state/district"

**Response**:
```json
{
  "timestamp": "2024-01-15T14:30:00Z",
  "location": {
    "country": "USA",
    "state": "NY",
    "district": "Manhattan"
  },
  "temperature": 72.5,
  "humidity": 65,
  "wind_speed": 12,
  "pressure": 1013,
  "precipitation": 0,
  "uv_index": 6,
  "conditions": "Partly Cloudy"
}
```

### Pollen Endpoint

**GET** `/api/pollen/<location>`

Returns pollen data for the specified location.

**Parameters**:
- `location` (string): Location identifier in format "country/state/district"

**Response**:
```json
{
  "timestamp": "2024-01-15T00:00:00Z",
  "location": {
    "country": "USA",
    "state": "NY",
    "district": "Manhattan"
  },
  "pollen_types": {
    "grass": {
      "concentration": 850,
      "unit": "gr/m³",
      "severity": "HIGH"
    },
    "tree": {
      "concentration": 450,
      "unit": "gr/m³",
      "severity": "MODERATE"
    },
    "weed": {
      "concentration": 150,
      "unit": "gr/m³",
      "severity": "LOW"
    },
    "ragweed": {
      "concentration": 200,
      "unit": "gr/m³",
      "severity": "LOW"
    },
    "mold": {
      "concentration": 320,
      "unit": "gr/m³",
      "severity": "MODERATE"
    }
  }
}
```

### Correlation Endpoint

**GET** `/api/correlation/<location>`

Returns correlation coefficients between weather factors and pollen levels.

**Parameters**:
- `location` (string): Location identifier in format "country/state/district"

**Response**:
```json
{
  "correlations": [
    {
      "weather_factor": "wind_speed",
      "pollen_type": "grass",
      "correlation_coefficient": 0.78,
      "strength": "Strong Positive",
      "explanation": "Higher wind speeds increase pollen dispersion in the air..."
    }
  ]
}
```

### Locations Endpoint

**GET** `/api/locations`

Returns the complete location hierarchy.

**Query Parameters**:
- `country` (optional): Filter by country code
- `state` (optional): Filter by state code

**Response**:
```json
{
  "countries": [
    {
      "name": "USA",
      "code": "US",
      "states": [
        {
          "name": "New York",
          "code": "NY",
          "districts": [
            {
              "name": "Manhattan",
              "latitude": 40.7831,
              "longitude": -73.9712
            }
          ]
        }
      ]
    }
  ]
}
```

### Export Endpoint

**POST** `/api/export`

Exports current weather and pollen data as JSON.

**Request Body**:
```json
{
  "location": "USA/NY/Manhattan",
  "include_metadata": true
}
```

**Response**:
```json
{
  "export_timestamp": "2024-01-15T14:30:00Z",
  "location": {
    "country": "USA",
    "state": "NY",
    "district": "Manhattan"
  },
  "weather_data": { ... },
  "pollen_data": { ... },
  "correlations": [ ... ],
  "metadata": {
    "data_sources": ["Open-Meteo", "AQICN"],
    "cache_status": "fresh"
  }
}
```

### Error Responses

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid location or parameters
- `404 Not Found`: Location not found
- `500 Internal Server Error`: Server error (check logs)
- `503 Service Unavailable`: External API unavailable (cached data returned if available)

**Error Response Format**:
```json
{
  "error": "Invalid location",
  "message": "Location 'USA/XX/Unknown' not found in configuration",
  "timestamp": "2024-01-15T14:30:00Z"
}
```

## Project Structure

```
weather-pollen-dashboard/
├── app.py                          # Main Flask application
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── location_config.json            # Location hierarchy data
├── README.md                       # This file
├── templates/
│   └── dashboard.html              # Main dashboard template
├── static/
│   ├── css/
│   │   ├── style.css               # Dashboard styling
│   │   └── style.min.css           # Minified CSS
│   └── js/
│       ├── dashboard.js            # Frontend logic
│       └── dashboard.min.js        # Minified JavaScript
├── src/
│   ├── __init__.py
│   ├── data_service.py             # Data fetching & processing
│   ├── cache_manager.py            # Caching logic
│   ├── correlation_calculator.py   # Correlation calculations
│   ├── api_client.py               # External API clients
│   └── utils.py                    # Utility functions
└── tests/
    ├── __init__.py
    ├── test_data_service.py        # Data service tests
    ├── test_correlation_calculator.py  # Correlation tests
    ├── test_cache_manager.py       # Cache tests
    ├── test_api_client.py          # API client tests
    ├── test_utils.py               # Utility function tests
    ├── test_config.py              # Configuration tests
    ├── test_error_handling.py      # Error handling tests
    ├── test_integration.py         # Integration tests
    └── test_api_endpoints.py       # API endpoint tests
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_data_service.py

# Run with coverage report
pytest --cov=src tests/
```

### Running Property-Based Tests

Property-based tests use Hypothesis to generate random inputs and verify correctness properties:

```bash
# Run all property-based tests
pytest tests/ -k "property"

# Run specific property test
pytest tests/test_correlation_calculator.py::test_correlation_coefficient_range -v
```

### Test Coverage

The project aims for 80%+ test coverage:

```bash
pytest --cov=src --cov-report=html tests/
# Open htmlcov/index.html in browser to view coverage report
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: "Location not found" error

**Solution**: Verify the location exists in `location_config.json` and use the correct format:
```
country/state/district
```

### Issue: API requests timing out

**Solution**: Check internet connection and API availability. The dashboard will automatically fall back to cached data if available.

### Issue: Charts not displaying

**Solution**: 
1. Check browser console for JavaScript errors (F12)
2. Verify Chart.js is loaded correctly
3. Clear browser cache and reload

### Issue: Metric conversion not working

**Solution**: Ensure JavaScript is enabled and the metric system selector is visible in the UI.

## Performance Optimization

### Caching Strategy

- **Weather Data**: Cached for 30 minutes (configurable)
- **Pollen Data**: Cached for 1 day (configurable)
- **Location Data**: Cached indefinitely (loaded once at startup)

### Frontend Optimization

- CSS and JavaScript are minified for production
- Charts use lazy loading to improve initial page load
- Data is fetched asynchronously to prevent UI blocking

### Backend Optimization

- Parallel API calls for weather and pollen data
- Connection pooling for HTTP requests
- Efficient data aggregation using Pandas

## Data Sources

- **Weather Data**: [Open-Meteo](https://open-meteo.com/) - Free weather API
- **Pollen Data**: [AQICN](https://aqicn.org/) or [OpenWeather](https://openweathermap.org/) - Air quality and pollen data

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or suggestions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review existing GitHub issues
3. Create a new issue with detailed information
4. Contact the development team

## Changelog

### Version 1.0.0 (Initial Release)
- Initial dashboard implementation
- Weather and pollen data integration
- Interactive visualizations
- Correlation analysis
- Multi-location support
- Data export functionality
- Comprehensive test suite

## Roadmap

- [ ] Database integration for historical data storage
- [ ] User accounts and preference saving
- [ ] Mobile application
- [ ] Real-time WebSocket updates
- [ ] Machine learning-based pollen prediction
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] API rate limiting and authentication

## Acknowledgments

- Open-Meteo for weather data
- AQICN for air quality and pollen data
- Chart.js for visualization library
- Flask community for the excellent web framework
- Pandas and NumPy for data processing

---

**Last Updated**: January 2024
**Version**: 1.0.0
**Status**: Active Development
