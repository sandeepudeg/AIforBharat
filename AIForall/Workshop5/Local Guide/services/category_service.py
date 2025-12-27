"""
Category Service - Handles category-related operations
"""
import logging
from typing import List, Dict, Optional
from services.cache_service import get_cache_service

logger = logging.getLogger(__name__)

class CategoryService:
    """Service for managing categories"""
    
    def __init__(self, data_service):
        """
        Initialize category service
        
        Args:
            data_service: DataService instance
        """
        self.data_service = data_service
        self.cache = get_cache_service()
        logger.info("CategoryService initialized")
    
    def get_all_categories(self) -> List[Dict]:
        """
        Get all categories with article counts
        
        Returns:
            List of category dicts
        """
        try:
            # Check cache first
            cache_key = "all_categories"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug("Cache hit for all categories")
                return cached_result
            
            categories = self.data_service.get_all_categories()
            
            # Add article count to each category
            for category in categories:
                category_id = category.get('id')
                articles = self.data_service.get_articles_by_category(category_id)
                category['article_count'] = len(articles)
            
            # Cache the results (1 hour TTL)
            self.cache.set(cache_key, categories, ttl=3600)
            
            logger.info(f"Retrieved {len(categories)} categories")
            return categories
        except Exception as e:
            logger.error(f"Error getting all categories: {str(e)}")
            return []
    
    def get_category(self, category_id: str) -> Optional[Dict]:
        """
        Get category by ID with articles
        
        Args:
            category_id: Category ID
            
        Returns:
            Category dict with articles or None
        """
        try:
            # Check cache first
            cache_key = f"category:{category_id}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for category: {category_id}")
                return cached_result
            
            category = self.data_service.get_category(category_id)
            if not category:
                logger.warning(f"Category not found: {category_id}")
                return None
            
            # Get articles in category
            articles = self.data_service.get_articles_by_category(category_id)
            category['articles'] = articles
            category['article_count'] = len(articles)
            
            # Cache the results (1 hour TTL)
            self.cache.set(cache_key, category, ttl=3600)
            
            logger.info(f"Retrieved category '{category_id}' with {len(articles)} articles")
            return category
        except Exception as e:
            logger.error(f"Error getting category: {str(e)}")
            return None
    
    def get_category_articles(self, category_id: str, limit: int = None) -> List[Dict]:
        """
        Get articles in a category
        
        Args:
            category_id: Category ID
            limit: Maximum number of articles
            
        Returns:
            List of articles
        """
        try:
            # Check cache first
            cache_key = f"category_articles:{category_id}:{limit}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for category articles: {category_id}")
                return cached_result
            
            articles = self.data_service.get_articles_by_category(category_id)
            
            if limit:
                articles = articles[:limit]
            
            # Cache the results (1 hour TTL)
            self.cache.set(cache_key, articles, ttl=3600)
            
            logger.info(f"Retrieved {len(articles)} articles from category '{category_id}'")
            return articles
        except Exception as e:
            logger.error(f"Error getting category articles: {str(e)}")
            return []
    
    def get_category_stats(self, category_id: str) -> Dict:
        """
        Get statistics for a category
        
        Args:
            category_id: Category ID
            
        Returns:
            Category statistics dict
        """
        try:
            # Check cache first
            cache_key = f"category_stats:{category_id}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for category stats: {category_id}")
                return cached_result
            
            category = self.data_service.get_category(category_id)
            if not category:
                return {}
            
            articles = self.data_service.get_articles_by_category(category_id)
            
            stats = {
                'category_id': category_id,
                'category_name': category.get('name', ''),
                'article_count': len(articles),
                'tags': set(),
                'subcategories': set()
            }
            
            # Collect tags and subcategories
            for article in articles:
                stats['tags'].update(article.get('tags', []))
                subcategory = article.get('subcategory')
                if subcategory:
                    stats['subcategories'].add(subcategory)
            
            # Convert sets to lists
            stats['tags'] = list(stats['tags'])
            stats['subcategories'] = list(stats['subcategories'])
            
            # Cache the results (1 hour TTL)
            self.cache.set(cache_key, stats, ttl=3600)
            
            logger.info(f"Retrieved stats for category '{category_id}'")
            return stats
        except Exception as e:
            logger.error(f"Error getting category stats: {str(e)}")
            return {}
    
    def get_popular_categories(self, limit: int = 5) -> List[Dict]:
        """
        Get most popular categories by article count
        
        Args:
            limit: Maximum number of categories
            
        Returns:
            List of popular categories
        """
        try:
            # Check cache first
            cache_key = f"popular_categories:{limit}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for popular categories")
                return cached_result
            
            categories = self.get_all_categories()
            
            # Sort by article count
            categories.sort(key=lambda x: x.get('article_count', 0), reverse=True)
            
            result = categories[:limit]
            
            # Cache the results (1 hour TTL)
            self.cache.set(cache_key, result, ttl=3600)
            
            return result
        except Exception as e:
            logger.error(f"Error getting popular categories: {str(e)}")
            return []
    
    def get_article_count(self, category_id: str) -> int:
        """
        Get article count for a category
        
        Args:
            category_id: Category ID
            
        Returns:
            Number of articles in category
        """
        try:
            articles = self.data_service.get_articles_by_category(category_id)
            return len(articles)
        except Exception as e:
            logger.error(f"Error getting article count: {str(e)}")
            return 0
    
    def category_exists(self, category_id: str) -> bool:
        """
        Check if a category exists
        
        Args:
            category_id: Category ID
            
        Returns:
            True if category exists, False otherwise
        """
        try:
            category = self.data_service.get_category(category_id)
            return category is not None
        except Exception as e:
            logger.error(f"Error checking category existence: {str(e)}")
            return False
