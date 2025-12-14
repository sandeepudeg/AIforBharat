"""
Unit tests for the cache warming strategy module (src/cache_warming_strategy.py).

Tests cache warming strategies, TTL configurations, and warming effectiveness.
"""

import pytest
from datetime import datetime, timezone
from src.cache_manager import CacheManager
from src.cache_warming_strategy import CacheWarmingStrategy


@pytest.fixture
def cache_manager():
    """Create a CacheManager instance for testing."""
    return CacheManager(cache=None, default_ttl=3600)


@pytest.fixture
def warming_strategy(cache_manager):
    """Create a CacheWarmingStrategy instance for testing."""
    return CacheWarmingStrategy(cache_manager)


@pytest.fixture
def sample_weather_data():
    """Create sample weather data."""
    return [
        {
            'location': {'country': 'USA', 'state': 'NY', 'district': 'Manhattan'},
            'temperature': 72.5,
            'humidity': 65,
            'wind_speed': 12
        },
        {
            'location': {'country': 'USA', 'state': 'CA', 'district': 'Los Angeles'},
            'temperature': 85.0,
            'humidity': 45,
            'wind_speed': 8
        }
    ]


@pytest.fixture
def sample_pollen_data():
    """Create sample pollen data."""
    return [
        {
            'location': {'country': 'USA', 'state': 'NY', 'district': 'Manhattan'},
            'pollen_types': {
                'grass': {'concentration': 850, 'severity': 'HIGH'},
                'tree': {'concentration': 450, 'severity': 'MODERATE'},
                'weed': {'concentration': 150, 'severity': 'LOW'},
                'ragweed': {'concentration': 200, 'severity': 'LOW'},
                'mold': {'concentration': 320, 'severity': 'MODERATE'}
            }
        },
        {
            'location': {'country': 'USA', 'state': 'CA', 'district': 'Los Angeles'},
            'pollen_types': {
                'grass': {'concentration': 450, 'severity': 'MODERATE'},
                'tree': {'concentration': 250, 'severity': 'LOW'},
                'weed': {'concentration': 50, 'severity': 'LOW'},
                'ragweed': {'concentration': 100, 'severity': 'LOW'},
                'mold': {'concentration': 150, 'severity': 'LOW'}
            }
        }
    ]


@pytest.fixture
def sample_correlation_data():
    """Create sample correlation data."""
    return [
        {
            'location': {'country': 'USA', 'state': 'NY', 'district': 'Manhattan'},
            'correlations': [
                {'weather_factor': 'temperature', 'pollen_type': 'grass', 'coefficient': 0.78},
                {'weather_factor': 'humidity', 'pollen_type': 'grass', 'coefficient': -0.45}
            ]
        }
    ]


@pytest.fixture
def sample_location_data():
    """Create sample location data."""
    return {
        'countries': [
            {'code': 'USA', 'name': 'United States'},
            {'code': 'India', 'name': 'India'}
        ],
        'states': {
            'USA': [
                {'code': 'NY', 'name': 'New York'},
                {'code': 'CA', 'name': 'California'}
            ]
        }
    }


class TestCacheWarmingStrategyInitialization:
    """Test CacheWarmingStrategy initialization."""
    
    def test_initialization_success(self, cache_manager):
        """Test successful initialization."""
        strategy = CacheWarmingStrategy(cache_manager)
        
        assert strategy.cache_manager is cache_manager
        assert strategy.warming_history == []
    
    def test_initialization_with_none_cache_manager(self):
        """Test initialization with None cache manager."""
        with pytest.raises(ValueError):
            CacheWarmingStrategy(None)
    
    def test_ttl_config_defined(self, warming_strategy):
        """Test that TTL configuration is defined."""
        assert warming_strategy.TTL_CONFIG['weather'] == 1800
        assert warming_strategy.TTL_CONFIG['pollen'] == 86400
        assert warming_strategy.TTL_CONFIG['correlation'] == 3600
        assert warming_strategy.TTL_CONFIG['location'] == 604800
        assert warming_strategy.TTL_CONFIG['config'] == 604800


class TestGetTTLForDataType:
    """Test getting TTL for data types."""
    
    def test_get_ttl_weather(self, warming_strategy):
        """Test getting TTL for weather data."""
        ttl = warming_strategy.get_ttl_for_data_type('weather')
        assert ttl == 1800
    
    def test_get_ttl_pollen(self, warming_strategy):
        """Test getting TTL for pollen data."""
        ttl = warming_strategy.get_ttl_for_data_type('pollen')
        assert ttl == 86400
    
    def test_get_ttl_correlation(self, warming_strategy):
        """Test getting TTL for correlation data."""
        ttl = warming_strategy.get_ttl_for_data_type('correlation')
        assert ttl == 3600
    
    def test_get_ttl_location(self, warming_strategy):
        """Test getting TTL for location data."""
        ttl = warming_strategy.get_ttl_for_data_type('location')
        assert ttl == 604800
    
    def test_get_ttl_invalid_type(self, warming_strategy):
        """Test getting TTL for invalid data type."""
        with pytest.raises(ValueError):
            warming_strategy.get_ttl_for_data_type('invalid_type')


class TestWarmWeatherData:
    """Test warming weather data."""
    
    def test_warm_weather_data_success(self, warming_strategy, sample_weather_data):
        """Test successful weather data warming."""
        warmed_count = warming_strategy.warm_weather_data(sample_weather_data)
        
        assert warmed_count == 2
        
        # Verify data is cached
        cached = warming_strategy.cache_manager.get('weather_USA_NY_Manhattan')
        assert cached is not None
        assert cached['temperature'] == 72.5
    
    def test_warm_weather_data_ttl(self, warming_strategy, sample_weather_data):
        """Test that weather data is warmed with correct TTL."""
        warming_strategy.warm_weather_data(sample_weather_data)
        
        info = warming_strategy.cache_manager.get_cache_info('weather_USA_NY_Manhattan')
        assert info['ttl'] == 1800  # Weather TTL
    
    def test_warm_weather_data_empty_list(self, warming_strategy):
        """Test warming with empty weather data list."""
        warmed_count = warming_strategy.warm_weather_data([])
        
        assert warmed_count == 0
    
    def test_warm_weather_data_records_history(self, warming_strategy, sample_weather_data):
        """Test that warming records history."""
        warming_strategy.warm_weather_data(sample_weather_data)
        
        assert len(warming_strategy.warming_history) == 1
        record = warming_strategy.warming_history[0]
        assert record['data_type'] == 'weather'
        assert record['requested'] == 2
        assert record['warmed'] == 2


class TestWarmPollenData:
    """Test warming pollen data."""
    
    def test_warm_pollen_data_success(self, warming_strategy, sample_pollen_data):
        """Test successful pollen data warming."""
        warmed_count = warming_strategy.warm_pollen_data(sample_pollen_data)
        
        assert warmed_count == 2
        
        # Verify data is cached
        cached = warming_strategy.cache_manager.get('pollen_USA_NY_Manhattan')
        assert cached is not None
        assert 'pollen_types' in cached
    
    def test_warm_pollen_data_ttl(self, warming_strategy, sample_pollen_data):
        """Test that pollen data is warmed with correct TTL."""
        warming_strategy.warm_pollen_data(sample_pollen_data)
        
        info = warming_strategy.cache_manager.get_cache_info('pollen_USA_NY_Manhattan')
        assert info['ttl'] == 86400  # Pollen TTL
    
    def test_warm_pollen_data_empty_list(self, warming_strategy):
        """Test warming with empty pollen data list."""
        warmed_count = warming_strategy.warm_pollen_data([])
        
        assert warmed_count == 0


class TestWarmCorrelationData:
    """Test warming correlation data."""
    
    def test_warm_correlation_data_success(self, warming_strategy, sample_correlation_data):
        """Test successful correlation data warming."""
        warmed_count = warming_strategy.warm_correlation_data(sample_correlation_data)
        
        assert warmed_count == 1
        
        # Verify data is cached
        cached = warming_strategy.cache_manager.get('correlation_USA_NY_Manhattan')
        assert cached is not None
        assert 'correlations' in cached
    
    def test_warm_correlation_data_ttl(self, warming_strategy, sample_correlation_data):
        """Test that correlation data is warmed with correct TTL."""
        warming_strategy.warm_correlation_data(sample_correlation_data)
        
        info = warming_strategy.cache_manager.get_cache_info('correlation_USA_NY_Manhattan')
        assert info['ttl'] == 3600  # Correlation TTL


class TestWarmLocationData:
    """Test warming location data."""
    
    def test_warm_location_data_success(self, warming_strategy, sample_location_data):
        """Test successful location data warming."""
        warmed_count = warming_strategy.warm_location_data(sample_location_data)
        
        assert warmed_count == 1
        
        # Verify data is cached
        cached = warming_strategy.cache_manager.get('location_hierarchy')
        assert cached is not None
        assert 'countries' in cached
    
    def test_warm_location_data_ttl(self, warming_strategy, sample_location_data):
        """Test that location data is warmed with correct TTL."""
        warming_strategy.warm_location_data(sample_location_data)
        
        info = warming_strategy.cache_manager.get_cache_info('location_hierarchy')
        assert info['ttl'] == 604800  # Location TTL


class TestWarmAll:
    """Test comprehensive cache warming."""
    
    def test_warm_all_success(self, warming_strategy, sample_weather_data, sample_pollen_data, 
                              sample_correlation_data, sample_location_data):
        """Test successful comprehensive warming."""
        def data_provider():
            return {
                'weather': sample_weather_data,
                'pollen': sample_pollen_data,
                'correlation': sample_correlation_data,
                'location': sample_location_data
            }
        
        results = warming_strategy.warm_all(data_provider)
        
        assert results['weather'] == 2
        assert results['pollen'] == 2
        assert results['correlation'] == 1
        assert results['location'] == 1
    
    def test_warm_all_partial_data(self, warming_strategy, sample_weather_data):
        """Test comprehensive warming with partial data."""
        def data_provider():
            return {
                'weather': sample_weather_data,
                'pollen': None,
                'correlation': None,
                'location': None
            }
        
        results = warming_strategy.warm_all(data_provider)
        
        assert results['weather'] == 2
        assert results['pollen'] == 0
        assert results['correlation'] == 0
        assert results['location'] == 0
    
    def test_warm_all_empty_data(self, warming_strategy):
        """Test comprehensive warming with empty data."""
        def data_provider():
            return {
                'weather': [],
                'pollen': [],
                'correlation': [],
                'location': None
            }
        
        results = warming_strategy.warm_all(data_provider)
        
        assert results['weather'] == 0
        assert results['pollen'] == 0
        assert results['correlation'] == 0
        assert results['location'] == 0


class TestWarmingHistory:
    """Test warming history tracking."""
    
    def test_get_warming_history_empty(self, warming_strategy):
        """Test getting history when no warming has occurred."""
        history = warming_strategy.get_warming_history()
        
        assert history == []
    
    def test_get_warming_history_with_operations(self, warming_strategy, sample_weather_data, 
                                                  sample_pollen_data):
        """Test getting history after warming operations."""
        warming_strategy.warm_weather_data(sample_weather_data)
        warming_strategy.warm_pollen_data(sample_pollen_data)
        
        history = warming_strategy.get_warming_history()
        
        assert len(history) == 2
        assert history[0]['data_type'] == 'weather'
        assert history[1]['data_type'] == 'pollen'
    
    def test_get_warming_history_with_limit(self, warming_strategy, sample_weather_data, 
                                             sample_pollen_data):
        """Test getting history with limit."""
        warming_strategy.warm_weather_data(sample_weather_data)
        warming_strategy.warm_pollen_data(sample_pollen_data)
        
        history = warming_strategy.get_warming_history(limit=1)
        
        assert len(history) == 1
        assert history[0]['data_type'] == 'pollen'  # Most recent


class TestWarmingStats:
    """Test warming statistics."""
    
    def test_get_warming_stats_empty(self, warming_strategy):
        """Test getting stats when no warming has occurred."""
        stats = warming_strategy.get_warming_stats()
        
        assert stats['total_operations'] == 0
        assert stats['total_entries_warmed'] == 0
        assert stats['average_success_rate'] == 0
        assert stats['by_data_type'] == {}
    
    def test_get_warming_stats_with_operations(self, warming_strategy, sample_weather_data, 
                                                sample_pollen_data):
        """Test getting stats after warming operations."""
        warming_strategy.warm_weather_data(sample_weather_data)
        warming_strategy.warm_pollen_data(sample_pollen_data)
        
        stats = warming_strategy.get_warming_stats()
        
        assert stats['total_operations'] == 2
        assert stats['total_entries_warmed'] == 4  # 2 weather + 2 pollen
        assert stats['average_success_rate'] == 100.0
        assert 'weather' in stats['by_data_type']
        assert 'pollen' in stats['by_data_type']
    
    def test_get_warming_stats_by_data_type(self, warming_strategy, sample_weather_data):
        """Test warming stats breakdown by data type."""
        warming_strategy.warm_weather_data(sample_weather_data)
        warming_strategy.warm_weather_data(sample_weather_data)
        
        stats = warming_strategy.get_warming_stats()
        
        assert stats['by_data_type']['weather']['operations'] == 2
        assert stats['by_data_type']['weather']['entries_warmed'] == 4
        assert stats['by_data_type']['weather']['average_success_rate'] == 100.0
