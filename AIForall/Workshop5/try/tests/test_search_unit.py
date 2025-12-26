"""
Unit Tests for Search Functionality
Tests specific examples and edge cases for search functionality
Requirement: 18
"""
import pytest
from services.search_service import SearchService


class TestSearchExactMatches:
    """Test search with exact matches"""
    
    def test_search_exact_match_in_title(self, search_service):
        """Test that exact match in title is found"""
        results = search_service.search("Test Article 1")
        
        assert len(results) > 0, "Should find exact match in title"
        assert results[0]['id'] == "test_article_1"
        assert results[0]['title'] == "Test Article 1"
    
    def test_search_exact_match_in_tags(self, search_service):
        """Test that exact match in tags is found"""
        results = search_service.search("food")
        
        assert len(results) > 0, "Should find articles with 'food' tag"
        # Should find test_article_1 which has 'food' tag
        article_ids = [r['id'] for r in results]
        assert "test_article_1" in article_ids
    
    def test_search_exact_match_returns_highest_score(self, search_service):
        """Test that exact matches have highest relevance score"""
        results = search_service.search("Test Article 1")
        
        assert len(results) > 0
        # Exact title match should be first
        assert results[0]['id'] == "test_article_1"
        assert results[0]['relevance_score'] > 0


class TestSearchPartialMatches:
    """Test search with partial matches"""
    
    def test_search_partial_match_in_title(self, search_service):
        """Test that partial match in title is found"""
        results = search_service.search("Test Article")
        
        assert len(results) > 0, "Should find partial match in title"
        # Should find both test articles
        article_ids = [r['id'] for r in results]
        assert "test_article_1" in article_ids
        assert "test_article_2" in article_ids
    
    def test_search_partial_match_in_description(self, search_service):
        """Test that partial match in description is found"""
        results = search_service.search("test description")
        
        assert len(results) > 0, "Should find partial match in description"
        article_ids = [r['id'] for r in results]
        assert "test_article_1" in article_ids
    
    def test_search_partial_match_in_content(self, search_service):
        """Test that partial match in content is found"""
        results = search_service.search("content")
        
        assert len(results) > 0, "Should find partial match in content"
        article_ids = [r['id'] for r in results]
        assert "test_article_1" in article_ids or "test_article_2" in article_ids
    
    def test_search_case_insensitive(self, search_service):
        """Test that search is case insensitive"""
        results_lower = search_service.search("test article")
        results_upper = search_service.search("TEST ARTICLE")
        results_mixed = search_service.search("TeSt ArTiClE")
        
        assert len(results_lower) > 0
        assert len(results_upper) > 0
        assert len(results_mixed) > 0
        
        # All should return same articles
        ids_lower = {r['id'] for r in results_lower}
        ids_upper = {r['id'] for r in results_upper}
        ids_mixed = {r['id'] for r in results_mixed}
        
        assert ids_lower == ids_upper == ids_mixed


class TestCategoryFiltering:
    """Test search with category filtering"""
    
    def test_search_with_category_filter(self, search_service):
        """Test that category filter works"""
        results = search_service.search("test", category="food")
        
        # All results should be from food category
        for result in results:
            assert result['category'] == "food"
    
    def test_search_with_category_filter_excludes_other_categories(self, search_service):
        """Test that category filter excludes other categories"""
        results = search_service.search("test", category="food")
        
        article_ids = [r['id'] for r in results]
        # test_article_1 is in food category, test_article_2 is in culture
        assert "test_article_1" in article_ids
        assert "test_article_2" not in article_ids
    
    def test_search_with_nonexistent_category(self, search_service):
        """Test search with category that has no matching articles"""
        results = search_service.search("test", category="nonexistent")
        
        assert len(results) == 0, "Should return no results for nonexistent category"
    
    def test_search_culture_category(self, search_service):
        """Test search in culture category"""
        results = search_service.search("test", category="culture")
        
        article_ids = [r['id'] for r in results]
        assert "test_article_2" in article_ids
        assert "test_article_1" not in article_ids


class TestEmptySearchResults:
    """Test search with empty or no results"""
    
    def test_search_no_matches(self, search_service):
        """Test search that returns no results"""
        results = search_service.search("nonexistent_query_xyz")
        
        assert len(results) == 0, "Should return empty list for no matches"
        assert isinstance(results, list)
    
    def test_search_empty_query(self, search_service):
        """Test search with empty query"""
        results = search_service.search("")
        
        assert len(results) == 0, "Should return empty list for empty query"
    
    def test_search_single_character_query(self, search_service):
        """Test search with single character (too short)"""
        results = search_service.search("a")
        
        assert len(results) == 0, "Should return empty list for single character query"
    
    def test_search_whitespace_only_query(self, search_service):
        """Test search with whitespace only"""
        results = search_service.search("   ")
        
        assert len(results) == 0, "Should return empty list for whitespace-only query"
    
    def test_search_special_characters_no_match(self, search_service):
        """Test search with special characters that don't match"""
        results = search_service.search("@#$%^&*()")
        
        assert len(results) == 0, "Should return empty list for special characters with no match"


class TestSearchResultProperties:
    """Test properties of search results"""
    
    def test_search_results_have_required_fields(self, search_service):
        """Test that search results have all required fields"""
        results = search_service.search("test")
        
        assert len(results) > 0
        
        for result in results:
            assert 'id' in result
            assert 'title' in result
            assert 'category' in result
            assert 'description' in result
            assert 'content' in result
            assert 'relevance_score' in result
    
    def test_search_results_relevance_scores_are_positive(self, search_service):
        """Test that all relevance scores are positive"""
        results = search_service.search("test")
        
        for result in results:
            assert result['relevance_score'] > 0, "Relevance score should be positive"
    
    def test_search_results_are_sorted_by_relevance(self, search_service):
        """Test that results are sorted by relevance score"""
        results = search_service.search("test")
        
        if len(results) > 1:
            scores = [r['relevance_score'] for r in results]
            # Check descending order
            for i in range(len(scores) - 1):
                assert scores[i] >= scores[i + 1], \
                    f"Results should be sorted by relevance (descending)"


class TestSearchLimitParameter:
    """Test search limit parameter"""
    
    def test_search_with_limit(self, search_service):
        """Test that limit parameter works"""
        results = search_service.search("test", limit=1)
        
        assert len(results) <= 1, "Should respect limit parameter"
    
    def test_search_with_large_limit(self, search_service):
        """Test search with limit larger than results"""
        results = search_service.search("test", limit=100)
        
        # Should return all matching results (not more than available)
        assert len(results) <= 100
    
    def test_search_default_limit(self, search_service):
        """Test that default limit is applied"""
        results = search_service.search("test")
        
        # Default limit is 10
        assert len(results) <= 10


class TestSearchByCategory:
    """Test search_by_category method"""
    
    def test_search_by_category_returns_articles(self, search_service):
        """Test that search_by_category returns articles"""
        results = search_service.search_by_category("food")
        
        assert len(results) > 0, "Should find articles in food category"
        for result in results:
            assert result['category'] == "food"
    
    def test_search_by_category_nonexistent(self, search_service):
        """Test search_by_category with nonexistent category"""
        results = search_service.search_by_category("nonexistent")
        
        assert len(results) == 0, "Should return empty list for nonexistent category"


class TestSearchSuggestions:
    """Test search suggestions"""
    
    def test_get_suggestions_returns_list(self, search_service):
        """Test that get_suggestions returns a list"""
        suggestions = search_service.get_suggestions("test")
        
        assert isinstance(suggestions, list)
    
    def test_get_suggestions_respects_limit(self, search_service):
        """Test that suggestions respect limit parameter"""
        suggestions = search_service.get_suggestions("test", limit=1)
        
        assert len(suggestions) <= 1
    
    def test_get_suggestions_empty_query(self, search_service):
        """Test suggestions with empty query"""
        suggestions = search_service.get_suggestions("")
        
        assert len(suggestions) == 0
    
    def test_get_suggestions_single_character(self, search_service):
        """Test suggestions with single character"""
        suggestions = search_service.get_suggestions("a")
        
        assert len(suggestions) == 0
