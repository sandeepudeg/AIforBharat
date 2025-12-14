"""
Unit tests for the cache manager module (src/cache_manager.py).

Tests cache operations including get/set, invalidation, expiration checking,
and cache lifecycle management.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, timezone
from hypothesis import given, strategies as st, settings

from src.cache_manager import (
    CacheManager,
    CacheManagerError,
    CacheExpirationError
)


@pytest.fixture
def cache_manager():
    """Create a CacheManager instance for testing."""
    return CacheManager(cache=None, default_ttl=3600)


@pytest.fixture
def sample_data():
    """Create sample data for caching."""
    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'temperature': 72.5,
        'humidity': 65,
        'wind_speed': 12,
        'pressure': 1013
    }


class TestCacheManagerInitialization:
    """Test CacheManager initialization."""
    
    def test_cache_manager_initialization(self, cache_manager):
        """Test CacheManager initialization."""
        assert cache_manager.cache is not None
        assert cache_manager.default_ttl == 3600
        assert cache_manager._metadata == {}
    
    def test_cache_manager_custom_ttl(self):
        """Test CacheManager initialization with custom TTL."""
        manager = CacheManager(cache=None, default_ttl=1800)
        assert manager.default_ttl == 1800
    
    def test_cache_manager_default_ttl_values(self, cache_manager):
        """Test that default TTL values are defined."""
        assert cache_manager.DEFAULT_WEATHER_TTL == 1800
        assert cache_manager.DEFAULT_POLLEN_TTL == 86400
        assert cache_manager.DEFAULT_CORRELATION_TTL == 3600


class TestCacheSet:
    """Test cache set operations."""
    
    def test_set_cache_success(self, cache_manager, sample_data):
        """Test successful cache set operation."""
        result = cache_manager.set('test_key', sample_data, ttl=3600)
        
        assert result is True
        assert 'test_key' in cache_manager._metadata
    
    def test_set_cache_with_default_ttl(self, cache_manager, sample_data):
        """Test cache set with default TTL."""
        result = cache_manager.set('test_key', sample_data)
        
        assert result is True
        assert cache_manager._metadata['test_key']['ttl'] == 3600
    
    def test_set_cache_with_custom_ttl(self, cache_manager, sample_data):
        """Test cache set with custom TTL."""
        result = cache_manager.set('test_key', sample_data, ttl=1800)
        
        assert result is True
        assert cache_manager._metadata['test_key']['ttl'] == 1800
    
    def test_set_cache_stores_metadata(self, cache_manager, sample_data):
        """Test that cache set stores metadata correctly."""
        cache_manager.set('test_key', sample_data, ttl=3600)
        
        metadata = cache_manager._metadata['test_key']
        assert 'timestamp' in metadata
        assert 'ttl' in metadata
        assert 'expires_at' in metadata
        assert metadata['ttl'] == 3600
    
    def test_set_cache_invalid_ttl_zero(self, cache_manager, sample_data):
        """Test cache set with invalid TTL (zero)."""
        with pytest.raises(CacheManagerError):
            cache_manager.set('test_key', sample_data, ttl=0)
    
    def test_set_cache_invalid_ttl_negative(self, cache_manager, sample_data):
        """Test cache set with invalid TTL (negative)."""
        with pytest.raises(CacheManagerError):
            cache_manager.set('test_key', sample_data, ttl=-100)
    
    def test_set_cache_overwrites_existing(self, cache_manager, sample_data):
        """Test that cache set overwrites existing data."""
        cache_manager.set('test_key', sample_data, ttl=3600)
        
        new_data = {'temperature': 80.0}
        cache_manager.set('test_key', new_data, ttl=3600)
        
        # Verify new data is stored
        assert cache_manager.get('test_key') == new_data
    
    def test_set_cache_with_various_data_types(self, cache_manager):
        """Test cache set with various data types."""
        # Test with string
        assert cache_manager.set('string_key', 'test_string', ttl=3600) is True
        
        # Test with list
        assert cache_manager.set('list_key', [1, 2, 3], ttl=3600) is True
        
        # Test with dict
        assert cache_manager.set('dict_key', {'key': 'value'}, ttl=3600) is True
        
        # Test with number
        assert cache_manager.set('number_key', 42, ttl=3600) is True
        
        # Test with None
        assert cache_manager.set('none_key', None, ttl=3600) is True


class TestCacheGet:
    """Test cache get operations."""
    
    def test_get_cache_success(self, cache_manager, sample_data):
        """Test successful cache get operation."""
        cache_manager.set('test_key', sample_data, ttl=3600)
        
        result = cache_manager.get('test_key')
        
        assert result == sample_data
    
    def test_get_cache_miss(self, cache_manager):
        """Test cache get with non-existent key."""
        result = cache_manager.get('non_existent_key')
        
        assert result is None
    
    def test_get_cache_returns_correct_data(self, cache_manager):
        """Test that cache get returns the correct data."""
        test_data = {'temperature': 72.5, 'humidity': 65}
        cache_manager.set('test_key', test_data, ttl=3600)
        
        result = cache_manager.get('test_key')
        
        assert result['temperature'] == 72.5
        assert result['humidity'] == 65
    
    def test_get_cache_with_various_data_types(self, cache_manager):
        """Test cache get with various data types."""
        # Test with string
        cache_manager.set('string_key', 'test_string', ttl=3600)
        assert cache_manager.get('string_key') == 'test_string'
        
        # Test with list
        cache_manager.set('list_key', [1, 2, 3], ttl=3600)
        assert cache_manager.get('list_key') == [1, 2, 3]
        
        # Test with dict
        cache_manager.set('dict_key', {'key': 'value'}, ttl=3600)
        assert cache_manager.get('dict_key') == {'key': 'value'}
        
        # Test with number
        cache_manager.set('number_key', 42, ttl=3600)
        assert cache_manager.get('number_key') == 42


class TestCacheInvalidation:
    """Test cache invalidation operations."""
    
    def test_invalidate_cache_success(self, cache_manager, sample_data):
        """Test successful cache invalidation."""
        cache_manager.set('test_key', sample_data, ttl=3600)
        
        result = cache_manager.invalidate('test_key')
        
        assert result is True
        assert cache_manager.get('test_key') is None
    
    def test_invalidate_cache_non_existent_key(self, cache_manager):
        """Test invalidation of non-existent key."""
        result = cache_manager.invalidate('non_existent_key')
        
        assert result is False
    
    def test_invalidate_removes_metadata(self, cache_manager, sample_data):
        """Test that invalidation removes metadata."""
        cache_manager.set('test_key', sample_data, ttl=3600)
        
        cache_manager.invalidate('test_key')
        
        assert 'test_key' not in cache_manager._metadata
    
    def test_invalidate_multiple_keys(self, cache_manager, sample_data):
        """Test invalidation of multiple keys."""
        cache_manager.set('key1', sample_data, ttl=3600)
        cache_manager.set('key2', sample_data, ttl=3600)
        cache_manager.set('key3', sample_data, ttl=3600)
        
        cache_manager.invalidate('key1')
        cache_manager.invalidate('key2')
        
        assert cache_manager.get('key1') is None
        assert cache_manager.get('key2') is None
        assert cache_manager.get('key3') == sample_data


class TestCacheExpiration:
    """Test cache expiration checking."""
    
    def test_is_expired_non_existent_key(self, cache_manager):
        """Test expiration check for non-existent key."""
        result = cache_manager.is_expired('non_existent_key')
        
        assert result is True
    
    def test_is_expired_valid_cache(self, cache_manager, sample_data):
        """Test expiration check for valid cache."""
        cache_manager.set('test_key', sample_data, ttl=3600)
        
        result = cache_manager.is_expired('test_key')
        
        assert result is False
    
    def test_get_expired_cache_returns_none(self, cache_manager, sample_data):
        """Test that getting expired cache returns None."""
        # Set cache with very short TTL
        cache_manager.set('test_key', sample_data, ttl=1)
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Manually mark as expired by updating metadata
        cache_manager._metadata['test_key']['expires_at'] = datetime.now(timezone.utc) - timedelta(seconds=1)
        
        result = cache_manager.get('test_key')
        
        assert result is None
    
    def test_is_expired_after_ttl_passes(self, cache_manager, sample_data):
        """Test that cache is marked as expired after TTL passes."""
        cache_manager.set('test_key', sample_data, ttl=1)
        
        # Manually set expiration to past
        cache_manager._metadata['test_key']['expires_at'] = datetime.now(timezone.utc) - timedelta(seconds=1)
        
        result = cache_manager.is_expired('test_key')
        
        assert result is True


class TestClearAll:
    """Test cache clear all operations."""
    
    def test_clear_all_success(self, cache_manager, sample_data):
        """Test successful clear all operation."""
        cache_manager.set('key1', sample_data, ttl=3600)
        cache_manager.set('key2', sample_data, ttl=3600)
        cache_manager.set('key3', sample_data, ttl=3600)
        
        result = cache_manager.clear_all()
        
        assert result is True
        assert cache_manager.get('key1') is None
        assert cache_manager.get('key2') is None
        assert cache_manager.get('key3') is None
        assert cache_manager._metadata == {}
    
    def test_clear_all_empty_cache(self, cache_manager):
        """Test clear all on empty cache."""
        result = cache_manager.clear_all()
        
        assert result is True
        assert cache_manager._metadata == {}


class TestGetCacheInfo:
    """Test cache info retrieval."""
    
    def test_get_cache_info_success(self, cache_manager, sample_data):
        """Test successful cache info retrieval."""
        cache_manager.set('test_key', sample_data, ttl=3600)
        
        info = cache_manager.get_cache_info('test_key')
        
        assert info is not None
        assert 'timestamp' in info
        assert 'ttl' in info
        assert 'expires_at' in info
        assert info['ttl'] == 3600
    
    def test_get_cache_info_non_existent_key(self, cache_manager):
        """Test cache info retrieval for non-existent key."""
        info = cache_manager.get_cache_info('non_existent_key')
        
        assert info is None
    
    def test_get_cache_info_does_not_modify_metadata(self, cache_manager, sample_data):
        """Test that getting cache info doesn't modify metadata."""
        cache_manager.set('test_key', sample_data, ttl=3600)
        
        original_metadata = cache_manager._metadata['test_key'].copy()
        cache_manager.get_cache_info('test_key')
        
        assert cache_manager._metadata['test_key'] == original_metadata


class TestGetAllKeys:
    """Test getting all cache keys."""
    
    def test_get_all_keys_success(self, cache_manager, sample_data):
        """Test successful retrieval of all cache keys."""
        cache_manager.set('key1', sample_data, ttl=3600)
        cache_manager.set('key2', sample_data, ttl=3600)
        cache_manager.set('key3', sample_data, ttl=3600)
        
        keys = cache_manager.get_all_keys()
        
        assert len(keys) == 3
        assert 'key1' in keys
        assert 'key2' in keys
        assert 'key3' in keys
    
    def test_get_all_keys_empty_cache(self, cache_manager):
        """Test getting all keys from empty cache."""
        keys = cache_manager.get_all_keys()
        
        assert keys == []
    
    def test_get_all_keys_after_invalidation(self, cache_manager, sample_data):
        """Test getting all keys after invalidation."""
        cache_manager.set('key1', sample_data, ttl=3600)
        cache_manager.set('key2', sample_data, ttl=3600)
        
        cache_manager.invalidate('key1')
        
        keys = cache_manager.get_all_keys()
        
        assert len(keys) == 1
        assert 'key2' in keys


class TestCleanupExpired:
    """Test cleanup of expired cache entries."""
    
    def test_cleanup_expired_success(self, cache_manager, sample_data):
        """Test successful cleanup of expired entries."""
        cache_manager.set('key1', sample_data, ttl=3600)
        cache_manager.set('key2', sample_data, ttl=3600)
        cache_manager.set('key3', sample_data, ttl=3600)
        
        # Mark key1 and key2 as expired
        cache_manager._metadata['key1']['expires_at'] = datetime.now(timezone.utc) - timedelta(seconds=1)
        cache_manager._metadata['key2']['expires_at'] = datetime.now(timezone.utc) - timedelta(seconds=1)
        
        removed_count = cache_manager.cleanup_expired()
        
        assert removed_count == 2
        assert cache_manager.get('key1') is None
        assert cache_manager.get('key2') is None
        assert cache_manager.get('key3') == sample_data
    
    def test_cleanup_expired_no_expired_entries(self, cache_manager, sample_data):
        """Test cleanup when no entries are expired."""
        cache_manager.set('key1', sample_data, ttl=3600)
        cache_manager.set('key2', sample_data, ttl=3600)
        
        removed_count = cache_manager.cleanup_expired()
        
        assert removed_count == 0
        assert cache_manager.get('key1') == sample_data
        assert cache_manager.get('key2') == sample_data
    
    def test_cleanup_expired_empty_cache(self, cache_manager):
        """Test cleanup on empty cache."""
        removed_count = cache_manager.cleanup_expired()
        
        assert removed_count == 0


class TestCacheStats:
    """Test cache statistics retrieval."""
    
    def test_get_cache_stats_empty_cache(self, cache_manager):
        """Test cache stats on empty cache."""
        stats = cache_manager.get_cache_stats()
        
        assert stats['total_entries'] == 0
        assert stats['expired_entries'] == 0
        assert stats['valid_entries'] == 0
        assert stats['total_hits'] == 0
        assert stats['total_misses'] == 0
        assert stats['hit_rate'] == 0
        assert stats['miss_rate'] == 0
    
    def test_get_cache_stats_with_entries(self, cache_manager, sample_data):
        """Test cache stats with cached entries."""
        cache_manager.set('key1', sample_data, ttl=3600)
        cache_manager.set('key2', sample_data, ttl=3600)
        cache_manager.set('key3', sample_data, ttl=3600)
        
        stats = cache_manager.get_cache_stats()
        
        assert stats['total_entries'] == 3
        assert stats['valid_entries'] == 3
        assert stats['expired_entries'] == 0
    
    def test_get_cache_stats_with_expired_entries(self, cache_manager, sample_data):
        """Test cache stats with expired entries."""
        cache_manager.set('key1', sample_data, ttl=3600)
        cache_manager.set('key2', sample_data, ttl=3600)
        cache_manager.set('key3', sample_data, ttl=3600)
        
        # Mark one as expired
        cache_manager._metadata['key1']['expires_at'] = datetime.now(timezone.utc) - timedelta(seconds=1)
        
        stats = cache_manager.get_cache_stats()
        
        assert stats['total_entries'] == 3
        assert stats['expired_entries'] == 1
        assert stats['valid_entries'] == 2
    
    def test_get_cache_stats_hit_rate(self, cache_manager, sample_data):
        """Test cache stats hit rate calculation."""
        cache_manager.set('key1', sample_data, ttl=3600)
        
        # Simulate hits and misses
        cache_manager.get('key1')  # Hit
        cache_manager.get('key1')  # Hit
        cache_manager.get('non_existent')  # Miss
        
        stats = cache_manager.get_cache_stats()
        
        assert stats['total_hits'] == 2
        assert stats['total_misses'] == 1
        assert stats['hit_rate'] == pytest.approx(66.67, rel=0.1)
        assert stats['miss_rate'] == pytest.approx(33.33, rel=0.1)


class TestCacheWarming:
    """Test cache warming functionality."""
    
    def test_warm_cache_success(self, cache_manager):
        """Test successful cache warming."""
        warm_data = {
            'key1': ({'value': 1}, 3600),
            'key2': ({'value': 2}, 3600),
            'key3': ({'value': 3}, 3600)
        }
        
        warmed_count = cache_manager.warm_cache(warm_data)
        
        assert warmed_count == 3
        assert cache_manager.get('key1') == {'value': 1}
        assert cache_manager.get('key2') == {'value': 2}
        assert cache_manager.get('key3') == {'value': 3}
    
    def test_warm_cache_with_default_ttl(self, cache_manager):
        """Test cache warming with default TTL."""
        warm_data = {
            'key1': {'value': 1},  # No TTL specified, should use default
            'key2': {'value': 2}
        }
        
        warmed_count = cache_manager.warm_cache(warm_data)
        
        assert warmed_count == 2
        assert cache_manager.get('key1') == {'value': 1}
        assert cache_manager.get('key2') == {'value': 2}
    
    def test_warm_cache_mixed_ttl(self, cache_manager):
        """Test cache warming with mixed TTL specifications."""
        warm_data = {
            'key1': ({'value': 1}, 1800),  # Custom TTL
            'key2': {'value': 2},  # Default TTL
            'key3': ({'value': 3}, 7200)  # Custom TTL
        }
        
        warmed_count = cache_manager.warm_cache(warm_data)
        
        assert warmed_count == 3
        
        # Verify TTLs are set correctly
        info1 = cache_manager.get_cache_info('key1')
        info2 = cache_manager.get_cache_info('key2')
        info3 = cache_manager.get_cache_info('key3')
        
        assert info1['ttl'] == 1800
        assert info2['ttl'] == 3600  # Default
        assert info3['ttl'] == 7200
    
    def test_warm_cache_empty_data(self, cache_manager):
        """Test cache warming with empty data."""
        warm_data = {}
        
        warmed_count = cache_manager.warm_cache(warm_data)
        
        assert warmed_count == 0
    
    def test_warm_cache_overwrites_existing(self, cache_manager):
        """Test that cache warming overwrites existing entries."""
        cache_manager.set('key1', {'old': 'data'}, ttl=3600)
        
        warm_data = {
            'key1': ({'new': 'data'}, 3600)
        }
        
        warmed_count = cache_manager.warm_cache(warm_data)
        
        assert warmed_count == 1
        assert cache_manager.get('key1') == {'new': 'data'}


class TestCacheInvalidationProperty:
    """
    Property-based tests for cache invalidation.
    
    **Feature: data-mashup-dashboard, Property 9: Cache Invalidation**
    **Validates: Requirements 1.4, 9.2**
    """
    
    @given(
        key=st.text(min_size=1, max_size=100),
        ttl=st.integers(min_value=1, max_value=86400),
        data=st.dictionaries(st.text(min_size=1), st.integers())
    )
    @settings(max_examples=100, suppress_health_check=[])
    def test_cache_invalidation_removes_expired_data(self, key, ttl, data):
        """
        Property: For any cached data with a TTL, if the TTL has expired,
        the system should fetch fresh data from the API instead of returning stale cache.
        
        This property verifies that:
        1. When cache is set with a TTL, it can be retrieved
        2. When the TTL expires, the cache returns None
        3. Invalidation removes the cache entry
        4. After invalidation, the cache returns None
        
        **Validates: Requirements 1.4, 9.2**
        """
        cache_manager = CacheManager(cache=None, default_ttl=3600)
        
        # Set cache with specified TTL
        cache_manager.set(key, data, ttl=ttl)
        
        # Verify cache is set
        assert cache_manager.get(key) == data, "Cache should return data immediately after set"
        
        # Mark as expired
        cache_manager._metadata[key]['expires_at'] = datetime.now(timezone.utc) - timedelta(seconds=1)
        
        # Verify cache returns None when expired
        assert cache_manager.get(key) is None, "Cache should return None when expired"
        
        # Note: get() on expired cache automatically invalidates it, so we check if it's gone
        # Verify cache is gone after expiration
        assert cache_manager.get(key) is None, "Cache should return None after expiration"
    
    @given(
        key=st.text(min_size=1, max_size=100),
        ttl=st.integers(min_value=1, max_value=86400),
        data=st.dictionaries(st.text(min_size=1), st.integers())
    )
    @settings(max_examples=100, suppress_health_check=[])
    def test_cache_ttl_enforcement(self, key, ttl, data):
        """
        Property: For any cached data, the TTL should be correctly stored and enforced.
        
        This property verifies that:
        1. When cache is set with a TTL, the TTL is stored in metadata
        2. The expiration time is correctly calculated
        3. The cache is marked as expired after the TTL passes
        
        **Validates: Requirements 1.4, 9.2**
        """
        cache_manager = CacheManager(cache=None, default_ttl=3600)
        
        # Set cache with specified TTL
        cache_manager.set(key, data, ttl=ttl)
        
        # Verify TTL is stored
        metadata = cache_manager.get_cache_info(key)
        assert metadata is not None, "Metadata should exist after set"
        assert metadata['ttl'] == ttl, f"TTL should be {ttl}, got {metadata['ttl']}"
        
        # Verify expiration time is in the future
        assert metadata['expires_at'] > datetime.now(timezone.utc), "Expiration should be in the future"
        
        # Verify cache is not expired
        assert cache_manager.is_expired(key) is False, "Cache should not be expired immediately"
    
    @given(
        key=st.text(min_size=1, max_size=100),
        data=st.dictionaries(st.text(min_size=1), st.integers())
    )
    @settings(max_examples=100, suppress_health_check=[])
    def test_cache_invalidation_idempotent(self, key, data):
        """
        Property: For any cache entry, invalidating it multiple times should be safe
        and not raise errors.
        
        This property verifies that:
        1. Invalidating an existing cache entry succeeds
        2. Invalidating the same entry again returns False (already gone)
        3. Multiple invalidations don't cause errors
        
        **Validates: Requirements 1.4, 9.2**
        """
        cache_manager = CacheManager(cache=None, default_ttl=3600)
        
        # Set cache
        cache_manager.set(key, data, ttl=3600)
        
        # First invalidation should succeed
        assert cache_manager.invalidate(key) is True, "First invalidation should succeed"
        
        # Second invalidation should return False (already gone)
        assert cache_manager.invalidate(key) is False, "Second invalidation should return False"
        
        # Cache should be gone
        assert cache_manager.get(key) is None, "Cache should be None after invalidation"
    
    @given(
        num_entries=st.integers(min_value=1, max_value=50),
        ttl=st.integers(min_value=1, max_value=86400)
    )
    @settings(max_examples=100, suppress_health_check=[])
    def test_cache_cleanup_removes_only_expired(self, num_entries, ttl):
        """
        Property: For any set of cached entries, cleanup should only remove expired entries
        and leave valid entries intact.
        
        This property verifies that:
        1. Cleanup removes all expired entries
        2. Cleanup leaves non-expired entries intact
        3. The number of removed entries matches the number of expired entries
        
        **Validates: Requirements 1.4, 9.2**
        """
        cache_manager = CacheManager(cache=None, default_ttl=3600)
        
        # Create cache entries
        for i in range(num_entries):
            cache_manager.set(f'key_{i}', {'value': i}, ttl=ttl)
        
        # Mark half as expired
        expired_count = num_entries // 2
        for i in range(expired_count):
            cache_manager._metadata[f'key_{i}']['expires_at'] = datetime.now(timezone.utc) - timedelta(seconds=1)
        
        # Run cleanup
        removed_count = cache_manager.cleanup_expired()
        
        # Verify correct number removed
        assert removed_count == expired_count, f"Should remove {expired_count} entries, removed {removed_count}"
        
        # Verify expired entries are gone
        for i in range(expired_count):
            assert cache_manager.get(f'key_{i}') is None, f"Expired entry key_{i} should be gone"
        
        # Verify non-expired entries remain
        for i in range(expired_count, num_entries):
            assert cache_manager.get(f'key_{i}') == {'value': i}, f"Non-expired entry key_{i} should remain"
