"""
Article Service - Handles article-related operations
"""
import logging
from typing import List, Dict, Optional
from services.cache_service import get_cache_service

logger = logging.getLogger(__name__)

class ArticleService:
    """Service for managing articles"""
    
    def __init__(self, data_service):
        """
        Initialize article service
        
        Args:
            data_service: DataService instance
        """
        self.data_service = data_service
        self.cache = get_cache_service()
        logger.info("ArticleService initialized")
    
    def get_article(self, article_id: str) -> Optional[Dict]:
        """
        Get article by ID with related articles
        
        Args:
            article_id: Article ID
            
        Returns:
            Article dict or None
        """
        try:
            # Check cache first
            cache_key = f"article:{article_id}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for article: {article_id}")
                return cached_result
            
            article = self.data_service.get_article(article_id)
            if not article:
                logger.warning(f"Article not found: {article_id}")
                return None
            
            # Get related articles
            related = self.data_service.get_related_articles(article_id)
            article['related_articles_data'] = related
            
            # Cache the results (1 hour TTL)
            self.cache.set(cache_key, article, ttl=3600)
            
            logger.info(f"Retrieved article '{article_id}'")
            return article
        except Exception as e:
            logger.error(f"Error getting article: {str(e)}")
            return None
    
    def get_related_articles(self, article_id: str, limit: int = 5) -> List[Dict]:
        """
        Get related articles
        
        Args:
            article_id: Article ID
            limit: Maximum number of related articles
            
        Returns:
            List of related articles
        """
        try:
            # Check cache first
            cache_key = f"related_articles:{article_id}:{limit}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for related articles: {article_id}")
                return cached_result
            
            related = self.data_service.get_related_articles(article_id, limit)
            
            # Cache the results (1 hour TTL)
            self.cache.set(cache_key, related, ttl=3600)
            
            logger.info(f"Retrieved {len(related)} related articles for '{article_id}'")
            return related
        except Exception as e:
            logger.error(f"Error getting related articles: {str(e)}")
            return []
    
    def get_articles_by_category(self, category_id: str) -> List[Dict]:
        """
        Get all articles in a category
        
        Args:
            category_id: Category ID
            
        Returns:
            List of articles
        """
        try:
            # Check cache first
            cache_key = f"articles_by_category:{category_id}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for articles by category: {category_id}")
                return cached_result
            
            articles = self.data_service.get_articles_by_category(category_id)
            
            # Cache the results (1 hour TTL)
            self.cache.set(cache_key, articles, ttl=3600)
            
            logger.info(f"Retrieved {len(articles)} articles from category '{category_id}'")
            return articles
        except Exception as e:
            logger.error(f"Error getting articles by category: {str(e)}")
            return []
    
    def get_all_articles(self) -> List[Dict]:
        """
        Get all articles
        
        Returns:
            List of all articles
        """
        try:
            # Check cache first
            cache_key = "all_articles"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug("Cache hit for all articles")
                return cached_result
            
            articles = self.data_service.get_all_articles()
            
            # Cache the results (1 hour TTL)
            self.cache.set(cache_key, articles, ttl=3600)
            
            logger.info(f"Retrieved {len(articles)} total articles")
            return articles
        except Exception as e:
            logger.error(f"Error getting all articles: {str(e)}")
            return []
    
    def get_article_stats(self, article_id: str) -> Dict:
        """
        Get statistics for an article
        
        Args:
            article_id: Article ID
            
        Returns:
            Article statistics dict
        """
        try:
            # Check cache first
            cache_key = f"article_stats:{article_id}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for article stats: {article_id}")
                return cached_result
            
            article = self.data_service.get_article(article_id)
            if not article:
                return {}
            
            stats = {
                'article_id': article_id,
                'title': article.get('title', ''),
                'category': article.get('category', ''),
                'subcategory': article.get('subcategory', ''),
                'tags_count': len(article.get('tags', [])),
                'related_count': len(article.get('related_articles', [])),
                'content_length': len(article.get('content', '')),
                'description_length': len(article.get('description', ''))
            }
            
            # Cache the results (1 hour TTL)
            self.cache.set(cache_key, stats, ttl=3600)
            
            logger.info(f"Retrieved stats for article '{article_id}'")
            return stats
        except Exception as e:
            logger.error(f"Error getting article stats: {str(e)}")
            return {}
    
    def get_articles_by_tag(self, tag: str) -> List[Dict]:
        """
        Get articles by tag
        
        Args:
            tag: Tag name
            
        Returns:
            List of articles with tag
        """
        try:
            # Check cache first
            cache_key = f"articles_by_tag:{tag}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for articles by tag: {tag}")
                return cached_result
            
            articles = self.data_service.get_all_articles()
            tag_lower = tag.lower()
            
            matching_articles = [
                article for article in articles
                if any(t.lower() == tag_lower for t in article.get('tags', []))
            ]
            
            # Cache the results (1 hour TTL)
            self.cache.set(cache_key, matching_articles, ttl=3600)
            
            logger.info(f"Found {len(matching_articles)} articles with tag '{tag}'")
            return matching_articles
        except Exception as e:
            logger.error(f"Error getting articles by tag: {str(e)}")
            return []
    
    def get_featured_articles(self, limit: int = 5) -> List[Dict]:
        """
        Get featured articles (articles with most related articles)
        
        Args:
            limit: Maximum number of articles
            
        Returns:
            List of featured articles
        """
        try:
            # Check cache first
            cache_key = f"featured_articles:{limit}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for featured articles")
                return cached_result
            
            articles = self.data_service.get_all_articles()
            
            # Sort by number of related articles
            articles.sort(
                key=lambda x: len(x.get('related_articles', [])),
                reverse=True
            )
            
            featured = articles[:limit]
            
            # Cache the results (1 hour TTL)
            self.cache.set(cache_key, featured, ttl=3600)
            
            logger.info(f"Retrieved {len(featured)} featured articles")
            return featured
        except Exception as e:
            logger.error(f"Error getting featured articles: {str(e)}")
            return []
    
    def get_breadcrumbs(self, article_id: str) -> List[Dict]:
        """
        Get breadcrumb navigation for an article
        
        Args:
            article_id: Article ID
            
        Returns:
            List of breadcrumb items with name and link
        """
        try:
            # Check cache first
            cache_key = f"breadcrumbs:{article_id}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for breadcrumbs: {article_id}")
                return cached_result
            
            article = self.data_service.get_article(article_id)
            if not article:
                return []
            
            breadcrumbs = [
                {'name': 'Home', 'link': '/'},
                {
                    'name': article.get('category', '').title(),
                    'link': f"/category/{article.get('category', '')}"
                },
                {
                    'name': article.get('title', ''),
                    'link': f"/article/{article_id}"
                }
            ]
            
            # Cache the results (1 hour TTL)
            self.cache.set(cache_key, breadcrumbs, ttl=3600)
            
            logger.info(f"Generated breadcrumbs for article '{article_id}'")
            return breadcrumbs
        except Exception as e:
            logger.error(f"Error getting breadcrumbs: {str(e)}")
            return []
