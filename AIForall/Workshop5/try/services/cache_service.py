"""
Cache Service - Implements caching for frequently accessed data
"""
import logging
import time
from typing import Any, Optional, Callable, Dict
from functools import wraps

logger = logging.getLogger(__name__)


class CacheService:
    """Service for managing application-level caching"""
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize cache service
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        logger.info(f"CacheService initialized with default TTL: {default_ttl}s")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if entry['expires_at'] < time.time():
            del self.cache[key]
            logger.debug(f"Cache entry expired: {key}")
            return None
        
        logger.debug(f"Cache hit: {key}")
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        self.cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
        logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
    
    def delete(self, key: str) -> None:
        """
        Delete value from cache
        
        Args:
            key: Cache key
        """
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache deleted: {key}")
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        total_entries = len(self.cache)
        expired_entries = 0
        current_time = time.time()
        
        for entry in self.cache.values():
            if entry['expires_at'] < current_time:
                expired_entries += 1
        
        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'active_entries': total_entries - expired_entries
        }
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache
        
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry['expires_at'] < current_time
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)


# Global cache service instance
_cache_service = None


def get_cache_service(default_ttl: int = 3600) -> CacheService:
    """
    Get or create global cache service instance
    
    Args:
        default_ttl: Default time-to-live in seconds
        
    Returns:
        CacheService instance
    """
    global _cache_service
    
    if _cache_service is None:
        _cache_service = CacheService(default_ttl)
    
    return _cache_service


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            cache = get_cache_service()
            
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    
    return decorator
