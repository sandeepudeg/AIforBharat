# Design Document: Weather & Pollen Dashboard

## Overview

The Weather & Pollen Dashboard is a Python-based web application that combines real-time weather data with pollen forecasts to help users understand environmental impacts on allergen levels. The system uses Flask as the web framework, integrates with free weather and pollen APIs, and provides interactive visualizations using Chart.js on the frontend.

**Technology Stack:**
- **Backend**: Python 3.8+, Flask
- **Frontend**: HTML5, CSS3, JavaScript (Chart.js)
- **Data Processing**: Pandas, NumPy
- **API Integration**: Requests library
- **Caching**: Flask-Caching
- **Configuration**: JSON-based config files

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Browser (Frontend)                   │
│  HTML/CSS/JavaScript with Chart.js for visualizations       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/JSON
┌────────────────────────▼────────────────────────────────────┐
│                    Flask Web Server                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Routes & Controllers                                 │   │
│  │ - Dashboard route                                    │   │
│  │ - API endpoints for data fetching                    │   │
│  │ - Export endpoints                                   │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼──────────┐ ┌──▼──────────────┐
│ Data Service   │ │ Cache Manager │ │ Config Manager  │
│ - Fetch data   │ │ - Store data  │ │ - Load configs  │
│ - Process data │ │ - Retrieve    │ │ - Manage locs   │
│ - Calculate    │ │ - Invalidate  │ │ - Validate      │
│   correlations │ └───────────────┘ └─────────────────┘
└───────┬────────┘
        │
        ├─────────────────────┬──────────────────┐
        │                     │                  │
┌───────▼──────────┐ ┌────────▼────────┐ ┌─────▼──────────┐
│ Weather API      │ │ Pollen API      │ │ Location Config│
│ (Open-Meteo)     │ │ (AQICN/OpenWeather)│ │ (JSON file)    │
└──────────────────┘ └─────────────────┘ └────────────────┘
```

### Module Structure

```
weather-pollen-dashboard/
├── app.py                          # Main Flask application
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── location_config.json            # Location hierarchy data
├── templates/
│   └── dashboard.html              # Main dashboard template
├── static/
│   ├── css/
│   │   └── style.css               # Dashboard styling
│   └── js/
│       └── dashboard.js            # Frontend logic
├── src/
│   ├── __init__.py
│   ├── data_service.py             # Data fetching & processing
│   ├── cache_manager.py            # Caching logic
│   ├── correlation_calculator.py   # Correlation calculations
│   ├── api_client.py               # External API clients
│   └── utils.py                    # Utility functions
└── tests/
    ├── __init__.py
    ├── test_data_service.py
    ├── test_correlation_calculator.py
    └── test_api_client.py
```

## Components and Interfaces

### 1. Flask Application (app.py)
**Responsibility**: Main entry point, route handling, request/response management

**Key Routes**:
- `GET /` - Serve dashboard HTML
- `GET /api/weather/<location>` - Fetch weather data
- `GET /api/pollen/<location>` - Fetch pollen data
- `GET /api/correlation/<location>` - Calculate correlations
- `POST /api/export` - Export data as JSON
- `GET /api/locations` - Get location hierarchy

### 2. Data Service (data_service.py)
**Responsibility**: Fetch, process, and aggregate data from external APIs

**Key Methods**:
- `fetch_weather_data(location, time_range)` - Get weather data
- `fetch_pollen_data(location, time_range)` - Get pollen data
- `aggregate_data(data, period)` - Aggregate by time period
- `combine_datasets(weather, pollen)` - Merge datasets

### 3. Correlation Calculator (correlation_calculator.py)
**Responsibility**: Calculate statistical correlations between weather and pollen

**Key Methods**:
- `calculate_pearson_correlation(x, y)` - Calculate Pearson correlation
- `calculate_all_correlations(weather_data, pollen_data)` - Calculate all correlations
- `get_correlation_strength(coefficient)` - Classify correlation strength

### 4. Cache Manager (cache_manager.py)
**Responsibility**: Manage data caching with TTL and invalidation

**Key Methods**:
- `get(key)` - Retrieve cached data
- `set(key, value, ttl)` - Store data with TTL
- `invalidate(key)` - Remove cached data
- `is_expired(key)` - Check if cache expired

### 5. API Client (api_client.py)
**Responsibility**: Handle external API calls with retry logic

**Key Methods**:
- `fetch_weather(lat, lon)` - Call weather API
- `fetch_pollen(lat, lon)` - Call pollen API
- `retry_request(url, max_retries)` - Retry with exponential backoff

### 6. Configuration Manager (config.py)
**Responsibility**: Load and manage application configuration

**Key Methods**:
- `load_location_hierarchy()` - Load location data
- `get_location_coordinates(country, state, district)` - Get lat/lon
- `validate_location(location)` - Validate location exists

## Data Models

### Weather Data
```python
{
    "timestamp": "2024-01-15T14:30:00Z",
    "location": {"country": "USA", "state": "NY", "district": "Manhattan"},
    "temperature": 72.5,  # Fahrenheit
    "humidity": 65,  # Percentage
    "wind_speed": 12,  # mph
    "pressure": 1013,  # mb
    "precipitation": 0,  # mm
    "uv_index": 6,
    "conditions": "Partly Cloudy"
}
```

### Pollen Data
```python
{
    "timestamp": "2024-01-15T00:00:00Z",
    "location": {"country": "USA", "state": "NY", "district": "Manhattan"},
    "pollen_types": {
        "grass": {"concentration": 850, "unit": "gr/m³", "severity": "HIGH"},
        "tree": {"concentration": 450, "unit": "gr/m³", "severity": "MODERATE"},
        "weed": {"concentration": 150, "unit": "gr/m³", "severity": "LOW"},
        "ragweed": {"concentration": 200, "unit": "gr/m³", "severity": "LOW"},
        "mold": {"concentration": 320, "unit": "gr/m³", "severity": "MODERATE"}
    }
}
```

### Correlation Data
```python
{
    "weather_factor": "wind_speed",
    "pollen_type": "grass",
    "correlation_coefficient": 0.78,
    "strength": "Strong Positive",
    "explanation": "Higher wind speeds increase pollen dispersion in the air..."
}
```

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Data Freshness
**For any** location and time range, the dashboard should display data that is no older than the specified refresh interval (30 minutes for weather, 1 day for pollen).
**Validates: Requirements 1.4**

### Property 2: Pollen Type Completeness
**For any** pollen data fetch, the system should return all five pollen types (grass, tree, weed, ragweed, mold) with concentration levels and severity indicators.
**Validates: Requirements 3.1, 3.2**

### Property 3: Correlation Coefficient Range
**For any** calculated correlation coefficient, the value should be between -1 and +1 (inclusive).
**Validates: Requirements 4.2**

### Property 4: Parameter Visibility
**For any** selected weather parameter, when added to the chart, the parameter should be visible with a distinct color and proper Y-axis scaling.
**Validates: Requirements 2.4, 2.6, 2.8**

### Property 5: Location Hierarchy Consistency
**For any** country selection, the state dropdown should contain only states that belong to that country. **For any** state selection, the district dropdown should contain only districts that belong to that state.
**Validates: Requirements 5.2, 5.3**

### Property 6: Data Aggregation Correctness
**For any** time range selection, the aggregated data should correctly represent the original data (e.g., daily averages for monthly view should equal the sum of hourly values divided by 24).
**Validates: Requirements 2.2, 7.2**

### Property 7: Export Data Integrity
**For any** export operation, the exported JSON should contain all current weather and pollen data points with metadata (timestamps, location, correlation coefficients).
**Validates: Requirements 6.1, 6.2, 6.4**

### Property 8: Metric Conversion Accuracy
**For any** temperature value in Fahrenheit, converting to Celsius and back should produce the original value (within rounding tolerance).
**Validates: Requirements 8.2, 8.3**

### Property 9: Cache Invalidation
**For any** cached data, if the TTL has expired, the system should fetch fresh data from the API instead of returning stale cache.
**Validates: Requirements 1.4, 9.2**

### Property 10: API Retry Logic
**For any** failed API request, the system should retry up to 3 times with exponential backoff before falling back to cached data.
**Validates: Requirements 9.1**

## Error Handling

### API Failures
- **Retry Strategy**: Exponential backoff (1s, 2s, 4s)
- **Fallback**: Display cached data with "cached data" indicator
- **User Notification**: Show error message if both API and cache fail

### Invalid Locations
- **Validation**: Check location exists in configuration
- **Error Response**: Return 400 Bad Request with error message
- **Fallback**: Retain last valid location data

### Data Processing Errors
- **Logging**: Log all errors with timestamp and details
- **Recovery**: Return partial data if available
- **User Notification**: Display warning message

### Cache Errors
- **Handling**: Continue without cache if cache fails
- **Logging**: Log cache errors for debugging
- **Recovery**: Fetch fresh data from API

## Testing Strategy

### Unit Testing
- Test individual functions in isolation
- Mock external API calls
- Test data processing and aggregation
- Test correlation calculations
- Test cache operations

**Test Framework**: pytest
**Coverage Target**: 80%+

### Property-Based Testing
- Use Hypothesis library for property-based tests
- Generate random weather and pollen data
- Verify properties hold across all generated inputs
- Test edge cases (extreme values, missing data)

**Minimum Iterations**: 100 per property

**Property Tests**:
1. **Data Freshness Property** - Verify data timestamps are within acceptable range
2. **Pollen Completeness Property** - Verify all pollen types are present
3. **Correlation Range Property** - Verify correlation values are in [-1, 1]
4. **Parameter Visibility Property** - Verify selected parameters appear in chart
5. **Location Hierarchy Property** - Verify location dropdowns are correctly populated
6. **Data Aggregation Property** - Verify aggregated data matches original data
7. **Export Integrity Property** - Verify exported data contains all required fields
8. **Metric Conversion Property** - Verify temperature conversions are accurate
9. **Cache Invalidation Property** - Verify expired cache is refreshed
10. **API Retry Property** - Verify retry logic works correctly

### Integration Testing
- Test end-to-end workflows
- Test API integration with real (or mocked) external APIs
- Test database/cache operations
- Test error scenarios

### Performance Testing
- Verify data loads within 5 seconds
- Verify chart rendering is smooth
- Verify no memory leaks with long-running dashboard

## Deployment

### Requirements
- Python 3.8+
- Flask 2.0+
- Pandas, NumPy
- Requests library
- Flask-Caching

### Configuration
- Set environment variables for API keys
- Configure cache backend (Redis or in-memory)
- Load location configuration from JSON file

### Running the Application
```bash
python app.py
```

The dashboard will be available at `http://localhost:5000`

## Future Enhancements

1. **Database Integration**: Store historical data in PostgreSQL
2. **User Accounts**: Allow users to save preferences
3. **Mobile App**: Native mobile application
4. **Real-time Updates**: WebSocket for live data updates
5. **Advanced Analytics**: Machine learning for pollen prediction
6. **Multi-language Support**: Internationalization
7. **API Rate Limiting**: Implement rate limiting for API endpoints
