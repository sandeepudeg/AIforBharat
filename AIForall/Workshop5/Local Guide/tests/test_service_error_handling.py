"""
Unit tests for service error handling
"""
import pytest
from services.search_service import SearchService
from services.category_service import CategoryService
from services.article_service import ArticleService
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


class TestSearchServiceErrorHandling:
    """Tests for search service error handling"""
    
    def test_search_with_none_query(self, search_service):
        """Test search with None query"""
        result = search_service.search(None)
        assert result == []
    
    def test_search_with_empty_query(self, search_service):
        """Test search with empty query"""
        result = search_service.search("")
        assert result == []
    
    def test_search_with_whitespace_query(self, search_service):
        """Test search with whitespace query"""
        result = search_service.search("   ")
        assert result == []
    
    def test_search_with_single_char_query(self, search_service):
        """Test search with single character query"""
        result = search_service.search("a")
        assert result == []
    
    def test_search_with_valid_query(self, search_service):
        """Test search with valid query"""
        result = search_service.search("pune")
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_search_with_invalid_category(self, search_service):
        """Test search with invalid category"""
        result = search_service.search("pune", category="nonexistent")
        assert result == []
    
    def test_search_suggestions_with_empty_query(self, search_service):
        """Test search suggestions with empty query"""
        result = search_service.get_suggestions("")
        assert result == []
    
    def test_search_suggestions_with_valid_query(self, search_service):
        """Test search suggestions with valid query"""
        result = search_service.get_suggestions("pu")
        assert isinstance(result, list)
    
    def test_search_by_category_with_valid_category(self, search_service):
        """Test search by category with valid category"""
        result = search_service.search_by_category("food")
        assert isinstance(result, list)
    
    def test_search_by_category_with_invalid_category(self, search_service):
        """Test search by category with invalid category"""
        result = search_service.search_by_category("nonexistent")
        assert result == []


class TestCategoryServiceErrorHandling:
    """Tests for category service error handling"""
    
    def test_get_all_categories(self, category_service):
        """Test get all categories"""
        result = category_service.get_all_categories()
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_get_category_with_valid_id(self, category_service):
        """Test get category with valid ID"""
        result = category_service.get_category("food")
        assert result is not None
        assert result.get('id') == "food"
    
    def test_get_category_with_invalid_id(self, category_service):
        """Test get category with invalid ID"""
        result = category_service.get_category("nonexistent")
        assert result is None
    
    def test_get_category_articles_with_valid_id(self, category_service):
        """Test get category articles with valid ID"""
        result = category_service.get_category_articles("food")
        assert isinstance(result, list)
    
    def test_get_category_articles_with_invalid_id(self, category_service):
        """Test get category articles with invalid ID"""
        result = category_service.get_category_articles("nonexistent")
        assert result == []
    
    def test_get_category_stats_with_valid_id(self, category_service):
        """Test get category stats with valid ID"""
        result = category_service.get_category_stats("food")
        assert isinstance(result, dict)
        assert result.get('category_id') == "food"
    
    def test_get_category_stats_with_invalid_id(self, category_service):
        """Test get category stats with invalid ID"""
        result = category_service.get_category_stats("nonexistent")
        assert result == {}
    
    def test_get_popular_categories(self, category_service):
        """Test get popular categories"""
        result = category_service.get_popular_categories()
        assert isinstance(result, list)
    
    def test_get_article_count_with_valid_id(self, category_service):
        """Test get article count with valid ID"""
        result = category_service.get_article_count("food")
        assert isinstance(result, int)
        assert result >= 0
    
    def test_get_article_count_with_invalid_id(self, category_service):
        """Test get article count with invalid ID"""
        result = category_service.get_article_count("nonexistent")
        assert result == 0
    
    def test_category_exists_with_valid_id(self, category_service):
        """Test category exists with valid ID"""
        result = category_service.category_exists("food")
        assert result is True
    
    def test_category_exists_with_invalid_id(self, category_service):
        """Test category exists with invalid ID"""
        result = category_service.category_exists("nonexistent")
        assert result is False


class TestArticleServiceErrorHandling:
    """Tests for article service error handling"""
    
    def test_get_article_with_valid_id(self, article_service):
        """Test get article with valid ID"""
        result = article_service.get_article("misal_pav")
        assert result is not None
        assert result.get('id') == "misal_pav"
    
    def test_get_article_with_invalid_id(self, article_service):
        """Test get article with invalid ID"""
        result = article_service.get_article("nonexistent")
        assert result is None
    
    def test_get_related_articles_with_valid_id(self, article_service):
        """Test get related articles with valid ID"""
        result = article_service.get_related_articles("misal_pav")
        assert isinstance(result, list)
    
    def test_get_related_articles_with_invalid_id(self, article_service):
        """Test get related articles with invalid ID"""
        result = article_service.get_related_articles("nonexistent")
        assert result == []
    
    def test_get_articles_by_category_with_valid_id(self, article_service):
        """Test get articles by category with valid ID"""
        result = article_service.get_articles_by_category("food")
        assert isinstance(result, list)
    
    def test_get_articles_by_category_with_invalid_id(self, article_service):
        """Test get articles by category with invalid ID"""
        result = article_service.get_articles_by_category("nonexistent")
        assert result == []
    
    def test_get_all_articles(self, article_service):
        """Test get all articles"""
        result = article_service.get_all_articles()
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_get_article_stats_with_valid_id(self, article_service):
        """Test get article stats with valid ID"""
        result = article_service.get_article_stats("misal_pav")
        assert isinstance(result, dict)
        assert result.get('article_id') == "misal_pav"
    
    def test_get_article_stats_with_invalid_id(self, article_service):
        """Test get article stats with invalid ID"""
        result = article_service.get_article_stats("nonexistent")
        assert result == {}
    
    def test_get_articles_by_tag_with_valid_tag(self, article_service):
        """Test get articles by tag with valid tag"""
        result = article_service.get_articles_by_tag("food")
        assert isinstance(result, list)
    
    def test_get_articles_by_tag_with_invalid_tag(self, article_service):
        """Test get articles by tag with invalid tag"""
        result = article_service.get_articles_by_tag("nonexistent_tag_xyz")
        assert result == []
    
    def test_get_featured_articles(self, article_service):
        """Test get featured articles"""
        result = article_service.get_featured_articles()
        assert isinstance(result, list)
    
    def test_get_breadcrumbs_with_valid_id(self, article_service):
        """Test get breadcrumbs with valid ID"""
        result = article_service.get_breadcrumbs("misal_pav")
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_get_breadcrumbs_with_invalid_id(self, article_service):
        """Test get breadcrumbs with invalid ID"""
        result = article_service.get_breadcrumbs("nonexistent")
        assert result == []


class TestErrorRecovery:
    """Tests for error recovery and graceful degradation"""
    
    def test_search_service_returns_empty_list_on_error(self, search_service):
        """Test search service returns empty list on error"""
        # All error cases should return empty list, not raise exceptions
        assert search_service.search(None) == []
        assert search_service.search("") == []
        assert search_service.search_by_category("nonexistent") == []
        assert search_service.get_suggestions("") == []
    
    def test_category_service_returns_empty_on_error(self, category_service):
        """Test category service returns empty on error"""
        # All error cases should return empty/None, not raise exceptions
        assert category_service.get_category("nonexistent") is None
        assert category_service.get_category_articles("nonexistent") == []
        assert category_service.get_category_stats("nonexistent") == {}
        assert category_service.get_article_count("nonexistent") == 0
        assert category_service.category_exists("nonexistent") is False
    
    def test_article_service_returns_empty_on_error(self, article_service):
        """Test article service returns empty on error"""
        # All error cases should return empty/None, not raise exceptions
        assert article_service.get_article("nonexistent") is None
        assert article_service.get_related_articles("nonexistent") == []
        assert article_service.get_articles_by_category("nonexistent") == []
        assert article_service.get_article_stats("nonexistent") == {}
        assert article_service.get_articles_by_tag("nonexistent_tag") == []
        assert article_service.get_breadcrumbs("nonexistent") == []
