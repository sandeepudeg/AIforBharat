"""
Performance tests for caching and optimization
"""
import pytest
import time
from services.search_service import SearchService
from services.category_service import CategoryService
from services.article_service import ArticleService
from services.cache_service import get_cache_service
from services.data_service import get_data_service


@pytest.fixture
def data_service():
    """Get data service"""
    service = get_data_service()
    if not service.articles:
        service.load_all_data()
    return service


@pytest.fixture
def search_service(data_service):
    """Get search service"""
    return SearchService(data_service)


@pytest.fixture
def category_service(data_service):
    """Get category service"""
    return CategoryService(data_service)


@pytest.fixture
def article_service(data_service):
    """Get article service"""
    return ArticleService(data_service)


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test"""
    cache = get_cache_service()
    cache.clear()
    yield
    cache.clear()


class TestSearchPerformance:
    """Tests for search performance"""
    
    def test_search_first_call_performance(self, search_service):
        """Test first search call performance (no cache)"""
        start = time.time()
        results = search_service.search("pune")
        elapsed = time.time() - start
        
        assert len(results) > 0
        assert elapsed < 1.0, f"First search took {elapsed}s, should be < 1s"
    
    def test_search_cached_call_performance(self, search_service):
        """Test cached search call performance"""
        # First call (no cache)
        search_service.search("pune")
        
        # Second call (cached)
        start = time.time()
        results = search_service.search("pune")
        elapsed = time.time() - start
        
        assert len(results) > 0
        assert elapsed < 0.1, f"Cached search took {elapsed}s, should be < 0.1s"
    
    def test_search_cache_speedup(self, search_service):
        """Test cache provides significant speedup"""
        # First call (no cache)
        start = time.time()
        search_service.search("pune")
        first_time = time.time() - start
        
        # Second call (cached)
        start = time.time()
        search_service.search("pune")
        cached_time = time.time() - start
        
        # Cached should be at least 2x faster
        speedup = first_time / cached_time if cached_time > 0 else float('inf')
        assert speedup >= 2, f"Cache speedup only {speedup}x, should be >= 2x"
    
    def test_search_suggestions_performance(self, search_service):
        """Test search suggestions performance"""
        start = time.time()
        suggestions = search_service.get_suggestions("pu")
        elapsed = time.time() - start
        
        assert isinstance(suggestions, list)
        assert elapsed < 1.0, f"Suggestions took {elapsed}s, should be < 1s"
    
    def test_search_by_category_performance(self, search_service):
        """Test search by category performance"""
        start = time.time()
        results = search_service.search_by_category("food")
        elapsed = time.time() - start
        
        assert isinstance(results, list)
        assert elapsed < 1.0, f"Search by category took {elapsed}s, should be < 1s"


class TestCategoryPerformance:
    """Tests for category service performance"""
    
    def test_get_all_categories_performance(self, category_service):
        """Test get all categories performance"""
        start = time.time()
        categories = category_service.get_all_categories()
        elapsed = time.time() - start
        
        assert len(categories) > 0
        assert elapsed < 1.0, f"Get all categories took {elapsed}s, should be < 1s"
    
    def test_get_category_performance(self, category_service):
        """Test get category performance"""
        start = time.time()
        category = category_service.get_category("food")
        elapsed = time.time() - start
        
        assert category is not None
        assert elapsed < 1.0, f"Get category took {elapsed}s, should be < 1s"
    
    def test_get_category_cached_performance(self, category_service):
        """Test cached get category performance"""
        # First call
        category_service.get_category("food")
        
        # Second call (cached)
        start = time.time()
        category = category_service.get_category("food")
        elapsed = time.time() - start
        
        assert category is not None
        assert elapsed < 0.1, f"Cached get category took {elapsed}s, should be < 0.1s"
    
    def test_get_popular_categories_performance(self, category_service):
        """Test get popular categories performance"""
        start = time.time()
        categories = category_service.get_popular_categories()
        elapsed = time.time() - start
        
        assert len(categories) > 0
        assert elapsed < 1.0, f"Get popular categories took {elapsed}s, should be < 1s"


class TestArticlePerformance:
    """Tests for article service performance"""
    
    def test_get_article_performance(self, article_service):
        """Test get article performance"""
        start = time.time()
        article = article_service.get_article("misal_pav")
        elapsed = time.time() - start
        
        assert article is not None
        assert elapsed < 1.0, f"Get article took {elapsed}s, should be < 1s"
    
    def test_get_article_cached_performance(self, article_service):
        """Test cached get article performance"""
        # First call
        article_service.get_article("misal_pav")
        
        # Second call (cached)
        start = time.time()
        article = article_service.get_article("misal_pav")
        elapsed = time.time() - start
        
        assert article is not None
        assert elapsed < 0.1, f"Cached get article took {elapsed}s, should be < 0.1s"
    
    def test_get_all_articles_performance(self, article_service):
        """Test get all articles performance"""
        start = time.time()
        articles = article_service.get_all_articles()
        elapsed = time.time() - start
        
        assert len(articles) > 0
        assert elapsed < 1.0, f"Get all articles took {elapsed}s, should be < 1s"
    
    def test_get_featured_articles_performance(self, article_service):
        """Test get featured articles performance"""
        start = time.time()
        articles = article_service.get_featured_articles()
        elapsed = time.time() - start
        
        assert len(articles) > 0
        assert elapsed < 1.0, f"Get featured articles took {elapsed}s, should be < 1s"


class TestCacheService:
    """Tests for cache service functionality"""
    
    def test_cache_get_set(self):
        """Test cache get and set"""
        cache = get_cache_service()
        cache.clear()
        
        cache.set("test_key", "test_value")
        value = cache.get("test_key")
        
        assert value == "test_value"
    
    def test_cache_expiration(self):
        """Test cache expiration"""
        cache = get_cache_service()
        cache.clear()
        
        # Set with 1 second TTL
        cache.set("test_key", "test_value", ttl=1)
        
        # Should be available immediately
        assert cache.get("test_key") == "test_value"
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        assert cache.get("test_key") is None
    
    def test_cache_delete(self):
        """Test cache delete"""
        cache = get_cache_service()
        cache.clear()
        
        cache.set("test_key", "test_value")
        cache.delete("test_key")
        
        assert cache.get("test_key") is None
    
    def test_cache_stats(self):
        """Test cache statistics"""
        cache = get_cache_service()
        cache.clear()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        stats = cache.get_stats()
        
        assert stats['total_entries'] == 2
        assert stats['active_entries'] == 2
        assert stats['expired_entries'] == 0
    
    def test_cache_cleanup_expired(self):
        """Test cache cleanup of expired entries"""
        cache = get_cache_service()
        cache.clear()
        
        # Add entries with different TTLs
        cache.set("key1", "value1", ttl=1)
        cache.set("key2", "value2", ttl=3600)
        
        # Wait for first to expire
        time.sleep(1.1)
        
        # Cleanup
        removed = cache.cleanup_expired()
        
        assert removed == 1
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"


class TestCacheConsistency:
    """Tests for cache consistency"""
    
    def test_search_cache_consistency(self, search_service):
        """Test search results are consistent across cache hits"""
        result1 = search_service.search("pune")
        result2 = search_service.search("pune")
        
        assert len(result1) == len(result2)
        assert result1[0]['id'] == result2[0]['id']
    
    def test_category_cache_consistency(self, category_service):
        """Test category results are consistent across cache hits"""
        result1 = category_service.get_category("food")
        result2 = category_service.get_category("food")
        
        assert result1['id'] == result2['id']
        assert len(result1['articles']) == len(result2['articles'])
    
    def test_article_cache_consistency(self, article_service):
        """Test article results are consistent across cache hits"""
        result1 = article_service.get_article("misal_pav")
        result2 = article_service.get_article("misal_pav")
        
        assert result1['id'] == result2['id']
        assert result1['title'] == result2['title']
