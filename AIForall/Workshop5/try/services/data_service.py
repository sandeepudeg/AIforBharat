"""
Data Service - Manages knowledge base data loading and caching
"""
import os
import json
import logging
from typing import List, Dict, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

class DataService:
    """Service for managing knowledge base data"""
    
    def __init__(self, data_dir: str):
        """
        Initialize data service
        
        Args:
            data_dir: Path to knowledge base data directory
        """
        self.data_dir = data_dir
        self.articles = {}
        self.categories = {}
        self.index = {}
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        logger.info(f"DataService initialized with data_dir: {data_dir}")
    
    def load_all_data(self) -> bool:
        """
        Load all data from JSON files
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Loading all knowledge base data...")
            
            # Load categories
            self._load_categories()
            
            # Load articles
            self._load_articles()
            
            # Build index
            self._build_index()
            
            logger.info(f"Successfully loaded {len(self.articles)} articles from {len(self.categories)} categories")
            return True
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False
    
    def _load_categories(self):
        """Load categories from JSON files"""
        categories_file = os.path.join(self.data_dir, 'categories.json')
        
        if os.path.exists(categories_file):
            try:
                with open(categories_file, 'r', encoding='utf-8') as f:
                    self.categories = json.load(f)
                logger.info(f"Loaded {len(self.categories)} categories")
            except Exception as e:
                logger.error(f"Error loading categories: {str(e)}")
        else:
            logger.warning(f"Categories file not found: {categories_file}")
    
    def _load_articles(self):
        """Load articles from JSON files"""
        articles_file = os.path.join(self.data_dir, 'articles.json')
        
        if os.path.exists(articles_file):
            try:
                with open(articles_file, 'r', encoding='utf-8') as f:
                    articles_list = json.load(f)
                    # Convert list to dict with ID as key
                    self.articles = {article['id']: article for article in articles_list}
                logger.info(f"Loaded {len(self.articles)} articles")
            except Exception as e:
                logger.error(f"Error loading articles: {str(e)}")
        else:
            logger.warning(f"Articles file not found: {articles_file}")
    
    def _build_index(self):
        """Build search index"""
        self.index = {}
        for article_id, article in self.articles.items():
            # Index by category
            category = article.get('category', 'uncategorized')
            if category not in self.index:
                self.index[category] = []
            self.index[category].append(article_id)
        
        logger.info(f"Built index with {len(self.index)} categories")
    
    def get_article(self, article_id: str) -> Optional[Dict]:
        """
        Get article by ID
        
        Args:
            article_id: Article ID
            
        Returns:
            Article dict or None if not found
        """
        return self.articles.get(article_id)
    
    def get_articles_by_category(self, category: str) -> List[Dict]:
        """
        Get all articles in a category
        
        Args:
            category: Category name
            
        Returns:
            List of articles in category
        """
        article_ids = self.index.get(category, [])
        return [self.articles[aid] for aid in article_ids if aid in self.articles]
    
    def get_all_categories(self) -> List[Dict]:
        """
        Get all categories
        
        Returns:
            List of category dicts
        """
        return list(self.categories.values())
    
    def get_category(self, category_id: str) -> Optional[Dict]:
        """
        Get category by ID
        
        Args:
            category_id: Category ID
            
        Returns:
            Category dict or None if not found
        """
        return self.categories.get(category_id)
    
    def get_related_articles(self, article_id: str, limit: int = 5) -> List[Dict]:
        """
        Get related articles
        
        Args:
            article_id: Article ID
            limit: Maximum number of related articles
            
        Returns:
            List of related articles
        """
        article = self.get_article(article_id)
        if not article:
            return []
        
        related_ids = article.get('related_articles', [])
        related = []
        for rid in related_ids[:limit]:
            related_article = self.get_article(rid)
            if related_article:
                related.append(related_article)
        
        return related
    
    def search_articles(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """
        Search articles by query
        
        Args:
            query: Search query
            category: Optional category filter
            
        Returns:
            List of matching articles
        """
        query_lower = query.lower()
        results = []
        
        for article in self.articles.values():
            # Filter by category if specified
            if category and article.get('category') != category:
                continue
            
            # Search in title, description, and tags
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            tags = [tag.lower() for tag in article.get('tags', [])]
            
            if (query_lower in title or 
                query_lower in description or 
                any(query_lower in tag for tag in tags)):
                results.append(article)
        
        return results
    
    def get_all_articles(self) -> List[Dict]:
        """
        Get all articles
        
        Returns:
            List of all articles
        """
        return list(self.articles.values())
    
    def validate_article(self, article: Dict) -> bool:
        """
        Validate article structure
        
        Args:
            article: Article dict to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['id', 'title', 'category', 'description', 'content']
        
        for field in required_fields:
            if field not in article:
                logger.warning(f"Article missing required field: {field}")
                return False
        
        return True
    
    def add_article(self, article: Dict) -> bool:
        """
        Add article to knowledge base
        
        Args:
            article: Article dict
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.validate_article(article):
            return False
        
        article_id = article['id']
        self.articles[article_id] = article
        
        # Update index
        category = article.get('category', 'uncategorized')
        if category not in self.index:
            self.index[category] = []
        if article_id not in self.index[category]:
            self.index[category].append(article_id)
        
        logger.info(f"Added article: {article_id}")
        return True
    
    def save_data(self) -> bool:
        """
        Save data to JSON files
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Save articles
            articles_file = os.path.join(self.data_dir, 'articles.json')
            with open(articles_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.articles.values()), f, ensure_ascii=False, indent=2)
            
            # Save categories
            categories_file = os.path.join(self.data_dir, 'categories.json')
            with open(categories_file, 'w', encoding='utf-8') as f:
                json.dump(self.categories, f, ensure_ascii=False, indent=2)
            
            logger.info("Data saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            return False


# Global data service instance
_data_service = None

def get_data_service(data_dir: str = None) -> DataService:
    """
    Get or create global data service instance
    
    Args:
        data_dir: Path to knowledge base data directory
        
    Returns:
        DataService instance
    """
    global _data_service
    
    if _data_service is None:
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'knowledge_base')
        _data_service = DataService(data_dir)
    
    return _data_service
