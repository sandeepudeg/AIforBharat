"""
Search Service - Handles full-text search functionality
"""
import logging
from typing import List, Dict, Optional
from services.cache_service import get_cache_service

logger = logging.getLogger(__name__)

class SearchService:
    """Service for searching articles"""
    
    def __init__(self, data_service):
        """
        Initialize search service
        
        Args:
            data_service: DataService instance
        """
        self.data_service = data_service
        self.cache = get_cache_service()
        logger.info("SearchService initialized")
    
    def search(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Search articles by query
        
        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum number of results
            
        Returns:
            List of matching articles
        """
        if not query or len(query.strip()) < 2:
            logger.warning(f"Invalid search query: {query}")
            return []
        
        # Check cache first
        cache_key = f"search:{query}:{category}:{limit}"
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for search: {query}")
            return cached_result
        
        query_lower = query.lower().strip()
        query_words = query_lower.split()
        results = []
        
        try:
            articles = self.data_service.get_all_articles()
            
            for article in articles:
                # Filter by category if specified
                if category and article.get('category') != category:
                    continue
                
                # Check if article matches query (any word match)
                title = article.get('title', '').lower()
                description = article.get('description', '').lower()
                content = article.get('content', '').lower()
                tags = [tag.lower() for tag in article.get('tags', [])]
                category_field = article.get('category', '').lower()
                
                # Article matches if ANY query word is found in searchable fields
                matches = False
                for word in query_words:
                    if len(word) < 2:
                        continue
                    if (word in title or 
                        word in description or 
                        word in content or 
                        word in category_field or
                        any(word in tag for tag in tags)):
                        matches = True
                        break
                
                if matches:
                    # Calculate relevance score
                    score = self._calculate_relevance(article, query_lower)
                    
                    if score > 0:
                        article_copy = article.copy()
                        article_copy['relevance_score'] = score
                        results.append(article_copy)
            
            # Sort by relevance score
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Limit results
            results = results[:limit]
            
            # Cache the results (1 hour TTL)
            self.cache.set(cache_key, results, ttl=3600)
            
            logger.info(f"Search query '{query}' returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            return []
    
    def _calculate_relevance(self, article: Dict, query: str) -> float:
        """
        Calculate relevance score for an article
        
        Args:
            article: Article dict
            query: Search query (lowercase)
            
        Returns:
            Relevance score (0-100)
        """
        score = 0
        
        # Split query into individual words for multi-word search
        query_words = query.split()
        
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        content = article.get('content', '').lower()
        tags = [tag.lower() for tag in article.get('tags', [])]
        category = article.get('category', '').lower()
        
        # For each word in the query, calculate partial scores
        for word in query_words:
            if len(word) < 2:  # Skip very short words
                continue
            
            # Title match (highest weight)
            if word in title:
                score += 50
                # Exact word match in title gets bonus
                if word == title or f' {word} ' in f' {title} ':
                    score += 25
            
            # Category match (high weight)
            if word in category:
                score += 40
            
            # Description match (medium weight)
            if word in description:
                score += 30
            
            # Tags match (medium weight)
            if any(word in tag for tag in tags):
                score += 20
            
            # Content match (lower weight)
            if word in content:
                score += 10
        
        # Bonus for exact phrase match
        if query in title:
            score += 50
        elif query in description:
            score += 30
        elif query in content:
            score += 10
        
        return score
    
    def search_by_category(self, category: str) -> List[Dict]:
        """
        Search articles by category
        
        Args:
            category: Category name
            
        Returns:
            List of articles in category
        """
        try:
            # Check cache first
            cache_key = f"search_by_category:{category}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for category: {category}")
                return cached_result
            
            articles = self.data_service.get_articles_by_category(category)
            
            # Cache the results (1 hour TTL)
            self.cache.set(cache_key, articles, ttl=3600)
            
            logger.info(f"Found {len(articles)} articles in category '{category}'")
            return articles
        except Exception as e:
            logger.error(f"Error searching by category: {str(e)}")
            return []
    
    def get_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions based on query
        
        Args:
            query: Partial search query
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested search terms
        """
        if not query or len(query) < 2:
            return []
        
        # Check cache first
        cache_key = f"suggestions:{query}:{limit}"
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Cache hit for suggestions: {query}")
            return cached_result
        
        query_lower = query.lower()
        suggestions = set()
        
        try:
            articles = self.data_service.get_all_articles()
            
            for article in articles:
                title = article.get('title', '').lower()
                if query_lower in title:
                    suggestions.add(article.get('title', ''))
                
                tags = article.get('tags', [])
                for tag in tags:
                    if query_lower in tag.lower():
                        suggestions.add(tag)
            
            result = list(suggestions)[:limit]
            
            # Cache the results (1 hour TTL)
            self.cache.set(cache_key, result, ttl=3600)
            
            return result
        except Exception as e:
            logger.error(f"Error getting suggestions: {str(e)}")
            return []
