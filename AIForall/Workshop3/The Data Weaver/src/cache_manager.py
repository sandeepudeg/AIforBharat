"""
Cache Manager module for Weather & Pollen Dashboard.

This module provides caching functionality with TTL (Time-To-Live) support,
cache invalidation, and expiration checking using Flask-Caching backend.

Key responsibilities:
- Store and retrieve cached data with TTL
- Invalidate cache entries
- Check cache expiration
- Manage cache lifecycle
"""

import logging
from typing import Any, Optional
from datetime import datetime, timedelta, timezone
from flask_caching import Cache

logger = logging.getLogger(__name__)


class CacheManagerError(Exception):
    """Base exception for cache manager errors."""
    pass


class CacheExpirationError(CacheManagerError):
    """Exception raised for cache expiration errors."""
    pass


class CacheManager:
    """
    Manager for caching data with TTL and expiration checking.
    
    This class provides methods to:
    - Store data with TTL
    - Retrieve cached data
    - Invalidate cache entries
    - Check cache expiration
    - Manage cache lifecycle
    """
    
    # Default TTL values in seconds
    DEFAULT_WEATHER_TTL = 1800  # 30 minutes
    DEFAULT_POLLEN_TTL = 86400  # 24 hours
    DEFAULT_CORRELATION_TTL = 3600  # 1 hour
    
    def __init__(self, cache: Optional[Cache] = None, default_ttl: int = 3600):
        """
        Initialize the CacheManager.
        
        Args:
            cache (Optional[Cache]): Flask-Caching Cache instance. If not provided,
                                    a simple in-memory cache will be used.
            default_ttl (int): Default TTL in seconds for cache entries. Defaults to 3600 (1 hour).
        
        Raises:
            CacheManagerError: If cache initialization fails.
        """
        try:
            if cache is None:
                # Create a simple in-memory cache if not provided
                from flask import Flask
                app = Flask(__name__)
                app.config['CACHE_TYPE'] = 'simple'
                self.cache = Cache(app)
            else:
                self.cache = cache
            
            self.default_ttl = default_ttl
            self._metadata = {}  # Store metadata about cached items (timestamps, TTL)
            self._total_hits = 0  # Track cache hits for statistics
            self._total_misses = 0  # Track cache misses for statistics
            
            logger.info(f"CacheManager initialized with default_ttl={default_ttl}s")
        
        except Exception as e:
            error_msg = f"Failed to initialize CacheManager: {str(e)}"
            logger.error(error_msg)
            raise CacheManagerError(error_msg) from e
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve cached data by key.
        
        Args:
            key (str): Cache key to retrieve.
        
        Returns:
            Optional[Any]: Cached data if found and not expired, None otherwise.
        
        Raises:
            CacheManagerError: If retrieval fails.
        
        Example:
            >>> cache_manager = CacheManager()
            >>> data = cache_manager.get('weather_data_USA_NY_Manhattan')
            >>> if data:
            ...     print(f"Found cached data: {data}")
        """
        logger.debug(f"Retrieving cache for key: {key}")
        
        try:
            # Check if cache entry has expired
            if self._is_expired(key):
                logger.debug(f"Cache entry expired for key: {key}")
                self.invalidate(key)
                self._record_miss()
                return None
            
            # Retrieve data from cache
            data = self.cache.get(key)
            
            if data is not None:
                logger.debug(f"Cache hit for key: {key}")
                self._record_hit()
            else:
                logger.debug(f"Cache miss for key: {key}")
                self._record_miss()
            
            return data
        
        except Exception as e:
            error_msg = f"Error retrieving cache for key {key}: {str(e)}"
            logger.error(error_msg)
            raise CacheManagerError(error_msg) from e
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store data in cache with TTL.
        
        Args:
            key (str): Cache key to store data under.
            value (Any): Data to cache.
            ttl (Optional[int]): Time-to-live in seconds. If not provided, uses default_ttl.
        
        Returns:
            bool: True if data was successfully cached, False otherwise.
        
        Raises:
            CacheManagerError: If caching fails.
        
        Example:
            >>> cache_manager = CacheManager()
            >>> success = cache_manager.set('weather_data_USA_NY_Manhattan', weather_data, ttl=1800)
            >>> if success:
            ...     print("Data cached successfully")
        """
        logger.debug(f"Setting cache for key: {key} with ttl={ttl or self.default_ttl}s")
        
        try:
            # Use provided TTL or default
            cache_ttl = ttl if ttl is not None else self.default_ttl
            
            # Validate TTL
            if cache_ttl <= 0:
                error_msg = f"Invalid TTL: {cache_ttl}. TTL must be positive."
                logger.error(error_msg)
                raise CacheManagerError(error_msg)
            
            # Store data in cache
            self.cache.set(key, value, timeout=cache_ttl)
            
            # Store metadata (timestamp and TTL)
            self._metadata[key] = {
                'timestamp': datetime.now(timezone.utc),
                'ttl': cache_ttl,
                'expires_at': datetime.now(timezone.utc) + timedelta(seconds=cache_ttl)
            }
            
            logger.info(f"Successfully cached data for key: {key} with ttl={cache_ttl}s")
            return True
        
        except Exception as e:
            error_msg = f"Error setting cache for key {key}: {str(e)}"
            logger.error(error_msg)
            raise CacheManagerError(error_msg) from e
    
    def invalidate(self, key: str) -> bool:
        """
        Invalidate (remove) a cache entry.
        
        Args:
            key (str): Cache key to invalidate.
        
        Returns:
            bool: True if cache entry was invalidated, False if key didn't exist.
        
        Raises:
            CacheManagerError: If invalidation fails.
        
        Example:
            >>> cache_manager = CacheManager()
            >>> success = cache_manager.invalidate('weather_data_USA_NY_Manhattan')
            >>> if success:
            ...     print("Cache entry removed")
        """
        logger.debug(f"Invalidating cache for key: {key}")
        
        try:
            # Check if key exists
            if self.cache.get(key) is None and key not in self._metadata:
                logger.debug(f"Cache key does not exist: {key}")
                return False
            
            # Delete from cache
            self.cache.delete(key)
            
            # Remove metadata
            if key in self._metadata:
                del self._metadata[key]
            
            logger.info(f"Successfully invalidated cache for key: {key}")
            return True
        
        except Exception as e:
            error_msg = f"Error invalidating cache for key {key}: {str(e)}"
            logger.error(error_msg)
            raise CacheManagerError(error_msg) from e
    
    def is_expired(self, key: str) -> bool:
        """
        Check if a cache entry has expired.
        
        Args:
            key (str): Cache key to check.
        
        Returns:
            bool: True if cache entry has expired or doesn't exist, False otherwise.
        
        Raises:
            CacheManagerError: If check fails.
        
        Example:
            >>> cache_manager = CacheManager()
            >>> if cache_manager.is_expired('weather_data_USA_NY_Manhattan'):
            ...     print("Cache entry has expired")
        """
        logger.debug(f"Checking expiration for cache key: {key}")
        
        try:
            return self._is_expired(key)
        
        except Exception as e:
            error_msg = f"Error checking cache expiration for key {key}: {str(e)}"
            logger.error(error_msg)
            raise CacheManagerError(error_msg) from e
    
    def _is_expired(self, key: str) -> bool:
        """
        Internal method to check if a cache entry has expired.
        
        Args:
            key (str): Cache key to check.
        
        Returns:
            bool: True if cache entry has expired or doesn't exist, False otherwise.
        """
        # Check if metadata exists for this key
        if key not in self._metadata:
            logger.debug(f"No metadata found for key: {key}")
            return True
        
        metadata = self._metadata[key]
        expires_at = metadata.get('expires_at')
        
        if expires_at is None:
            logger.debug(f"No expiration time found for key: {key}")
            return True
        
        # Check if current time is past expiration time
        current_time = datetime.now(timezone.utc)
        is_expired = current_time > expires_at
        
        if is_expired:
            logger.debug(f"Cache entry expired for key: {key} (expired at {expires_at})")
        
        return is_expired
    
    def clear_all(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            bool: True if cache was successfully cleared, False otherwise.
        
        Raises:
            CacheManagerError: If clearing fails.
        
        Example:
            >>> cache_manager = CacheManager()
            >>> success = cache_manager.clear_all()
            >>> if success:
            ...     print("All cache entries cleared")
        """
        logger.debug("Clearing all cache entries")
        
        try:
            self.cache.clear()
            self._metadata.clear()
            
            logger.info("Successfully cleared all cache entries")
            return True
        
        except Exception as e:
            error_msg = f"Error clearing cache: {str(e)}"
            logger.error(error_msg)
            raise CacheManagerError(error_msg) from e
    
    def get_cache_info(self, key: str) -> Optional[dict]:
        """
        Get metadata information about a cached entry.
        
        Args:
            key (str): Cache key to get info for.
        
        Returns:
            Optional[dict]: Metadata dictionary with timestamp, ttl, and expires_at,
                          or None if key doesn't exist.
        
        Raises:
            CacheManagerError: If retrieval fails.
        
        Example:
            >>> cache_manager = CacheManager()
            >>> info = cache_manager.get_cache_info('weather_data_USA_NY_Manhattan')
            >>> if info:
            ...     print(f"Cache expires at: {info['expires_at']}")
        """
        logger.debug(f"Getting cache info for key: {key}")
        
        try:
            if key not in self._metadata:
                logger.debug(f"No cache info found for key: {key}")
                return None
            
            metadata = self._metadata[key].copy()
            logger.debug(f"Retrieved cache info for key: {key}")
            return metadata
        
        except Exception as e:
            error_msg = f"Error getting cache info for key {key}: {str(e)}"
            logger.error(error_msg)
            raise CacheManagerError(error_msg) from e
    
    def get_all_keys(self) -> list:
        """
        Get all cache keys currently in the cache.
        
        Returns:
            list: List of all cache keys.
        
        Raises:
            CacheManagerError: If retrieval fails.
        
        Example:
            >>> cache_manager = CacheManager()
            >>> keys = cache_manager.get_all_keys()
            >>> print(f"Cached keys: {keys}")
        """
        logger.debug("Getting all cache keys")
        
        try:
            keys = list(self._metadata.keys())
            logger.debug(f"Retrieved {len(keys)} cache keys")
            return keys
        
        except Exception as e:
            error_msg = f"Error getting cache keys: {str(e)}"
            logger.error(error_msg)
            raise CacheManagerError(error_msg) from e
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired cache entries.
        
        Returns:
            int: Number of cache entries that were removed.
        
        Raises:
            CacheManagerError: If cleanup fails.
        
        Example:
            >>> cache_manager = CacheManager()
            >>> removed_count = cache_manager.cleanup_expired()
            >>> print(f"Removed {removed_count} expired cache entries")
        """
        logger.debug("Cleaning up expired cache entries")
        
        try:
            expired_keys = []
            
            # Find all expired keys
            for key in list(self._metadata.keys()):
                if self._is_expired(key):
                    expired_keys.append(key)
            
            # Remove expired keys
            for key in expired_keys:
                self.invalidate(key)
            
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            return len(expired_keys)
        
        except Exception as e:
            error_msg = f"Error cleaning up expired cache entries: {str(e)}"
            logger.error(error_msg)
            raise CacheManagerError(error_msg) from e
    
    def get_cache_stats(self) -> dict:
        """
        Get cache statistics including hit rate, miss rate, and entry count.
        
        Returns:
            dict: Cache statistics with keys:
                - total_entries: Total number of cached entries
                - expired_entries: Number of expired entries
                - valid_entries: Number of valid (non-expired) entries
                - total_hits: Total number of cache hits
                - total_misses: Total number of cache misses
                - hit_rate: Cache hit rate as percentage (0-100)
                - miss_rate: Cache miss rate as percentage (0-100)
        
        Raises:
            CacheManagerError: If stats retrieval fails.
        
        Example:
            >>> cache_manager = CacheManager()
            >>> stats = cache_manager.get_cache_stats()
            >>> print(f"Cache hit rate: {stats['hit_rate']:.2f}%")
        """
        logger.debug("Retrieving cache statistics")
        
        try:
            total_entries = len(self._metadata)
            expired_entries = sum(1 for key in self._metadata.keys() if self._is_expired(key))
            valid_entries = total_entries - expired_entries
            
            total_hits = getattr(self, '_total_hits', 0)
            total_misses = getattr(self, '_total_misses', 0)
            total_requests = total_hits + total_misses
            
            # Calculate hit rate
            hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
            miss_rate = (total_misses / total_requests * 100) if total_requests > 0 else 0
            
            stats = {
                'total_entries': total_entries,
                'expired_entries': expired_entries,
                'valid_entries': valid_entries,
                'total_hits': total_hits,
                'total_misses': total_misses,
                'hit_rate': hit_rate,
                'miss_rate': miss_rate
            }
            
            logger.debug(f"Cache stats: {stats}")
            return stats
        
        except Exception as e:
            error_msg = f"Error retrieving cache statistics: {str(e)}"
            logger.error(error_msg)
            raise CacheManagerError(error_msg) from e
    
    def warm_cache(self, cache_data: dict) -> int:
        """
        Warm the cache by pre-loading data with specified TTLs.
        
        This method is useful for pre-loading frequently accessed data
        at application startup or during scheduled maintenance.
        
        Args:
            cache_data (dict): Dictionary where keys are cache keys and values are
                             tuples of (data, ttl) or just data (uses default TTL).
                             Example: {
                                 'weather_USA_NY_Manhattan': (weather_data, 1800),
                                 'pollen_USA_NY_Manhattan': (pollen_data, 86400)
                             }
        
        Returns:
            int: Number of cache entries that were warmed.
        
        Raises:
            CacheManagerError: If cache warming fails.
        
        Example:
            >>> cache_manager = CacheManager()
            >>> warm_data = {
            ...     'weather_USA_NY_Manhattan': (weather_data, 1800),
            ...     'pollen_USA_NY_Manhattan': (pollen_data, 86400)
            ... }
            >>> warmed_count = cache_manager.warm_cache(warm_data)
            >>> print(f"Warmed {warmed_count} cache entries")
        """
        logger.info(f"Warming cache with {len(cache_data)} entries")
        
        try:
            warmed_count = 0
            
            for key, value in cache_data.items():
                try:
                    # Handle both (data, ttl) tuples and plain data
                    if isinstance(value, tuple) and len(value) == 2:
                        data, ttl = value
                    else:
                        data = value
                        ttl = self.default_ttl
                    
                    # Set cache entry
                    if self.set(key, data, ttl=ttl):
                        warmed_count += 1
                        logger.debug(f"Warmed cache entry: {key} with ttl={ttl}s")
                
                except Exception as e:
                    logger.warning(f"Failed to warm cache entry {key}: {str(e)}")
                    # Continue warming other entries even if one fails
                    continue
            
            logger.info(f"Successfully warmed {warmed_count} cache entries")
            return warmed_count
        
        except Exception as e:
            error_msg = f"Error warming cache: {str(e)}"
            logger.error(error_msg)
            raise CacheManagerError(error_msg) from e
    
    def _record_hit(self):
        """Record a cache hit for statistics tracking."""
        if not hasattr(self, '_total_hits'):
            self._total_hits = 0
        self._total_hits += 1
    
    def _record_miss(self):
        """Record a cache miss for statistics tracking."""
        if not hasattr(self, '_total_misses'):
            self._total_misses = 0
        self._total_misses += 1
