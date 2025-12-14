"""
Cache Warming Strategy module for Weather & Pollen Dashboard.

This module provides strategies for pre-loading cache with frequently accessed data
at application startup or during scheduled maintenance to improve performance.

Key responsibilities:
- Define cache warming strategies for different data types
- Implement cache warming with appropriate TTLs
- Schedule periodic cache warming
- Monitor cache warming effectiveness
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone
from src.cache_manager import CacheManager, CacheManagerError

logger = logging.getLogger(__name__)


class CacheWarmingStrategy:
    """
    Strategy for warming cache with frequently accessed data.
    
    This class provides methods to:
    - Define cache warming strategies
    - Execute cache warming with appropriate TTLs
    - Track cache warming effectiveness
    """
    
    # TTL configurations for different data types (in seconds)
    TTL_CONFIG = {
        'weather': 1800,  # 30 minutes - weather changes frequently
        'pollen': 86400,  # 24 hours - pollen data updates daily
        'correlation': 3600,  # 1 hour - correlations update hourly
        'location': 604800,  # 7 days - location data rarely changes
        'config': 604800  # 7 days - configuration data rarely changes
    }
    
    def __init__(self, cache_manager: CacheManager):
        """
        Initialize the CacheWarmingStrategy.
        
        Args:
            cache_manager (CacheManager): CacheManager instance to use for warming.
        
        Raises:
            ValueError: If cache_manager is None.
        """
        if cache_manager is None:
            raise ValueError("cache_manager cannot be None")
        
        self.cache_manager = cache_manager
        self.warming_history = []  # Track warming operations
        
        logger.info("CacheWarmingStrategy initialized")
    
    def get_ttl_for_data_type(self, data_type: str) -> int:
        """
        Get the appropriate TTL for a given data type.
        
        Args:
            data_type (str): Type of data ('weather', 'pollen', 'correlation', 'location', 'config').
        
        Returns:
            int: TTL in seconds for the data type.
        
        Raises:
            ValueError: If data_type is not recognized.
        
        Example:
            >>> strategy = CacheWarmingStrategy(cache_manager)
            >>> ttl = strategy.get_ttl_for_data_type('weather')
            >>> print(f"Weather TTL: {ttl} seconds")
        """
        if data_type not in self.TTL_CONFIG:
            raise ValueError(f"Unknown data type: {data_type}. Must be one of {list(self.TTL_CONFIG.keys())}")
        
        return self.TTL_CONFIG[data_type]
    
    def warm_weather_data(self, weather_data_list: List[Dict[str, Any]]) -> int:
        """
        Warm cache with weather data.
        
        Args:
            weather_data_list (List[Dict[str, Any]]): List of weather data dictionaries.
                                                      Each should have location info.
        
        Returns:
            int: Number of weather cache entries warmed.
        
        Raises:
            CacheManagerError: If cache warming fails.
        
        Example:
            >>> strategy = CacheWarmingStrategy(cache_manager)
            >>> weather_list = [
            ...     {'location': {'country': 'USA', 'state': 'NY', 'district': 'Manhattan'}, ...},
            ...     {'location': {'country': 'USA', 'state': 'CA', 'district': 'Los Angeles'}, ...}
            ... ]
            >>> warmed = strategy.warm_weather_data(weather_list)
            >>> print(f"Warmed {warmed} weather entries")
        """
        logger.info(f"Warming cache with {len(weather_data_list)} weather data entries")
        
        try:
            cache_data = {}
            
            for weather_data in weather_data_list:
                location = weather_data.get('location', {})
                country = location.get('country', 'unknown')
                state = location.get('state', 'unknown')
                district = location.get('district', 'unknown')
                
                # Create cache key
                cache_key = f"weather_{country}_{state}_{district}"
                
                # Add to cache data with weather TTL
                cache_data[cache_key] = (weather_data, self.TTL_CONFIG['weather'])
            
            # Warm cache
            warmed_count = self.cache_manager.warm_cache(cache_data)
            
            # Record warming operation
            self._record_warming('weather', len(weather_data_list), warmed_count)
            
            logger.info(f"Successfully warmed {warmed_count} weather cache entries")
            return warmed_count
        
        except Exception as e:
            error_msg = f"Error warming weather cache: {str(e)}"
            logger.error(error_msg)
            raise CacheManagerError(error_msg) from e
    
    def warm_pollen_data(self, pollen_data_list: List[Dict[str, Any]]) -> int:
        """
        Warm cache with pollen data.
        
        Args:
            pollen_data_list (List[Dict[str, Any]]): List of pollen data dictionaries.
                                                     Each should have location info.
        
        Returns:
            int: Number of pollen cache entries warmed.
        
        Raises:
            CacheManagerError: If cache warming fails.
        
        Example:
            >>> strategy = CacheWarmingStrategy(cache_manager)
            >>> pollen_list = [
            ...     {'location': {'country': 'USA', 'state': 'NY', 'district': 'Manhattan'}, ...},
            ...     {'location': {'country': 'USA', 'state': 'CA', 'district': 'Los Angeles'}, ...}
            ... ]
            >>> warmed = strategy.warm_pollen_data(pollen_list)
            >>> print(f"Warmed {warmed} pollen entries")
        """
        logger.info(f"Warming cache with {len(pollen_data_list)} pollen data entries")
        
        try:
            cache_data = {}
            
            for pollen_data in pollen_data_list:
                location = pollen_data.get('location', {})
                country = location.get('country', 'unknown')
                state = location.get('state', 'unknown')
                district = location.get('district', 'unknown')
                
                # Create cache key
                cache_key = f"pollen_{country}_{state}_{district}"
                
                # Add to cache data with pollen TTL
                cache_data[cache_key] = (pollen_data, self.TTL_CONFIG['pollen'])
            
            # Warm cache
            warmed_count = self.cache_manager.warm_cache(cache_data)
            
            # Record warming operation
            self._record_warming('pollen', len(pollen_data_list), warmed_count)
            
            logger.info(f"Successfully warmed {warmed_count} pollen cache entries")
            return warmed_count
        
        except Exception as e:
            error_msg = f"Error warming pollen cache: {str(e)}"
            logger.error(error_msg)
            raise CacheManagerError(error_msg) from e
    
    def warm_correlation_data(self, correlation_data_list: List[Dict[str, Any]]) -> int:
        """
        Warm cache with correlation data.
        
        Args:
            correlation_data_list (List[Dict[str, Any]]): List of correlation data dictionaries.
                                                          Each should have location info.
        
        Returns:
            int: Number of correlation cache entries warmed.
        
        Raises:
            CacheManagerError: If cache warming fails.
        
        Example:
            >>> strategy = CacheWarmingStrategy(cache_manager)
            >>> correlation_list = [
            ...     {'location': {'country': 'USA', 'state': 'NY', 'district': 'Manhattan'}, ...},
            ...     {'location': {'country': 'USA', 'state': 'CA', 'district': 'Los Angeles'}, ...}
            ... ]
            >>> warmed = strategy.warm_correlation_data(correlation_list)
            >>> print(f"Warmed {warmed} correlation entries")
        """
        logger.info(f"Warming cache with {len(correlation_data_list)} correlation data entries")
        
        try:
            cache_data = {}
            
            for correlation_data in correlation_data_list:
                location = correlation_data.get('location', {})
                country = location.get('country', 'unknown')
                state = location.get('state', 'unknown')
                district = location.get('district', 'unknown')
                
                # Create cache key
                cache_key = f"correlation_{country}_{state}_{district}"
                
                # Add to cache data with correlation TTL
                cache_data[cache_key] = (correlation_data, self.TTL_CONFIG['correlation'])
            
            # Warm cache
            warmed_count = self.cache_manager.warm_cache(cache_data)
            
            # Record warming operation
            self._record_warming('correlation', len(correlation_data_list), warmed_count)
            
            logger.info(f"Successfully warmed {warmed_count} correlation cache entries")
            return warmed_count
        
        except Exception as e:
            error_msg = f"Error warming correlation cache: {str(e)}"
            logger.error(error_msg)
            raise CacheManagerError(error_msg) from e
    
    def warm_location_data(self, location_data: Dict[str, Any]) -> int:
        """
        Warm cache with location configuration data.
        
        Args:
            location_data (Dict[str, Any]): Location hierarchy data.
        
        Returns:
            int: Number of location cache entries warmed.
        
        Raises:
            CacheManagerError: If cache warming fails.
        
        Example:
            >>> strategy = CacheWarmingStrategy(cache_manager)
            >>> location_data = {'countries': [...], 'states': {...}, ...}
            >>> warmed = strategy.warm_location_data(location_data)
            >>> print(f"Warmed {warmed} location entries")
        """
        logger.info("Warming cache with location data")
        
        try:
            cache_data = {
                'location_hierarchy': (location_data, self.TTL_CONFIG['location'])
            }
            
            # Warm cache
            warmed_count = self.cache_manager.warm_cache(cache_data)
            
            # Record warming operation
            self._record_warming('location', 1, warmed_count)
            
            logger.info(f"Successfully warmed {warmed_count} location cache entries")
            return warmed_count
        
        except Exception as e:
            error_msg = f"Error warming location cache: {str(e)}"
            logger.error(error_msg)
            raise CacheManagerError(error_msg) from e
    
    def warm_all(self, data_provider: Callable) -> Dict[str, int]:
        """
        Warm all cache types using a data provider function.
        
        Args:
            data_provider (Callable): Function that returns a dictionary with keys:
                                     'weather', 'pollen', 'correlation', 'location'
                                     Each value should be a list of data dictionaries.
        
        Returns:
            Dict[str, int]: Dictionary with warming results for each data type.
                           Example: {'weather': 5, 'pollen': 5, 'correlation': 5, 'location': 1}
        
        Raises:
            CacheManagerError: If cache warming fails.
        
        Example:
            >>> def get_data():
            ...     return {
            ...         'weather': [...],
            ...         'pollen': [...],
            ...         'correlation': [...],
            ...         'location': {...}
            ...     }
            >>> strategy = CacheWarmingStrategy(cache_manager)
            >>> results = strategy.warm_all(get_data)
            >>> print(f"Warming results: {results}")
        """
        logger.info("Starting comprehensive cache warming")
        
        try:
            results = {}
            
            # Get data from provider
            data = data_provider()
            
            # Warm each data type
            if 'weather' in data and data['weather']:
                results['weather'] = self.warm_weather_data(data['weather'])
            else:
                results['weather'] = 0
            
            if 'pollen' in data and data['pollen']:
                results['pollen'] = self.warm_pollen_data(data['pollen'])
            else:
                results['pollen'] = 0
            
            if 'correlation' in data and data['correlation']:
                results['correlation'] = self.warm_correlation_data(data['correlation'])
            else:
                results['correlation'] = 0
            
            if 'location' in data and data['location']:
                results['location'] = self.warm_location_data(data['location'])
            else:
                results['location'] = 0
            
            total_warmed = sum(results.values())
            logger.info(f"Comprehensive cache warming completed. Total entries warmed: {total_warmed}")
            
            return results
        
        except Exception as e:
            error_msg = f"Error during comprehensive cache warming: {str(e)}"
            logger.error(error_msg)
            raise CacheManagerError(error_msg) from e
    
    def _record_warming(self, data_type: str, requested: int, warmed: int):
        """
        Record a cache warming operation for tracking.
        
        Args:
            data_type (str): Type of data warmed.
            requested (int): Number of entries requested to warm.
            warmed (int): Number of entries actually warmed.
        """
        record = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data_type': data_type,
            'requested': requested,
            'warmed': warmed,
            'success_rate': (warmed / requested * 100) if requested > 0 else 0
        }
        
        self.warming_history.append(record)
        logger.debug(f"Recorded warming operation: {record}")
    
    def get_warming_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get the history of cache warming operations.
        
        Args:
            limit (Optional[int]): Maximum number of records to return. If None, returns all.
        
        Returns:
            List[Dict[str, Any]]: List of warming operation records.
        
        Example:
            >>> strategy = CacheWarmingStrategy(cache_manager)
            >>> history = strategy.get_warming_history(limit=10)
            >>> for record in history:
            ...     print(f"{record['timestamp']}: {record['data_type']} - {record['warmed']} entries")
        """
        if limit is None:
            return self.warming_history.copy()
        else:
            return self.warming_history[-limit:].copy()
    
    def get_warming_stats(self) -> Dict[str, Any]:
        """
        Get statistics about cache warming operations.
        
        Returns:
            Dict[str, Any]: Statistics including:
                - total_operations: Total number of warming operations
                - total_entries_warmed: Total entries warmed across all operations
                - average_success_rate: Average success rate across all operations
                - by_data_type: Statistics broken down by data type
        
        Example:
            >>> strategy = CacheWarmingStrategy(cache_manager)
            >>> stats = strategy.get_warming_stats()
            >>> print(f"Total operations: {stats['total_operations']}")
        """
        if not self.warming_history:
            return {
                'total_operations': 0,
                'total_entries_warmed': 0,
                'average_success_rate': 0,
                'by_data_type': {}
            }
        
        total_operations = len(self.warming_history)
        total_entries_warmed = sum(r['warmed'] for r in self.warming_history)
        average_success_rate = sum(r['success_rate'] for r in self.warming_history) / total_operations
        
        # Group by data type
        by_data_type = {}
        for record in self.warming_history:
            data_type = record['data_type']
            if data_type not in by_data_type:
                by_data_type[data_type] = {
                    'operations': 0,
                    'entries_warmed': 0,
                    'average_success_rate': 0
                }
            
            by_data_type[data_type]['operations'] += 1
            by_data_type[data_type]['entries_warmed'] += record['warmed']
        
        # Calculate average success rate per data type
        for data_type in by_data_type:
            type_records = [r for r in self.warming_history if r['data_type'] == data_type]
            by_data_type[data_type]['average_success_rate'] = sum(r['success_rate'] for r in type_records) / len(type_records)
        
        return {
            'total_operations': total_operations,
            'total_entries_warmed': total_entries_warmed,
            'average_success_rate': average_success_rate,
            'by_data_type': by_data_type
        }
