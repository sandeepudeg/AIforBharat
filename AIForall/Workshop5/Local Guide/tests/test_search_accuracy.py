"""
Property-Based Tests for Search Accuracy
Feature: pune-knowledge-base, Property 2: Search Result Accuracy
Validates: Requirement 18
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from services.search_service import SearchService

# Strategies for generating test data
search_query_strategy = st.text(
    alphabet=st.characters(blacklist_categories=('Cc', 'Cs')),
    min_size=2,
    max_size=50
).filter(lambda x: x.strip())

category_filter_strategy = st.one_of(
    st.none(),
    st.sampled_from(['food', 'culture', 'geography', 'places', 'trekking'])
)

class TestSearchAccuracy:
    """Property-based tests for search accuracy"""
    
    @given(search_query_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_search_results_contain_query_terms(self, search_service, search_query):
        """
        Property: For any search query, all returned results 
        SHALL contain the search terms in title, description, content, or tags.
        
        Feature: pune-knowledge-base, Property 2: Search Result Accuracy
        Validates: Requirement 18
        """
        results = search_service.search(search_query)
        
        query_lower = search_query.lower()
        
        for result in results:
            # Check if query appears in any searchable field
            title = result.get('title', '').lower()
            description = result.get('description', '').lower()
            content = result.get('content', '').lower()
            tags = [tag.lower() for tag in result.get('tags', [])]
            
            found = (
                query_lower in title or
                query_lower in description or
                query_lower in content or
                any(query_lower in tag for tag in tags)
            )
            
            assert found, f"Query '{search_query}' should appear in result '{result.get('title', '')}'"
    
    @given(search_query_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_search_results_ranked_by_relevance(self, search_service, search_query):
        """
        Property: For any search query, results SHALL be ranked 
        by relevance score in descending order.
        
        Feature: pune-knowledge-base, Property 2: Search Result Accuracy
        Validates: Requirement 18
        """
        results = search_service.search(search_query)
        
        if len(results) > 1:
            # Check that scores are in descending order
            scores = [r.get('relevance_score', 0) for r in results]
            
            for i in range(len(scores) - 1):
                assert scores[i] >= scores[i + 1], \
                    f"Results should be ranked by relevance (score {scores[i]} should be >= {scores[i + 1]})"
    
    @given(search_query_strategy, category_filter_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_search_respects_category_filter(self, search_service, search_query, category_filter):
        """
        Property: For any search query with category filter, 
        all results SHALL belong to the specified category.
        
        Feature: pune-knowledge-base, Property 2: Search Result Accuracy
        Validates: Requirement 18
        """
        results = search_service.search(search_query, category=category_filter)
        
        if category_filter:
            for result in results:
                assert result.get('category') == category_filter, \
                    f"Result category should match filter '{category_filter}'"
    
    @given(st.text(min_size=0, max_size=1))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_search_handles_invalid_queries(self, search_service, invalid_query):
        """
        Property: For any invalid search query (empty or too short), 
        search SHALL return empty results without error.
        
        Feature: pune-knowledge-base, Property 2: Search Result Accuracy
        Validates: Requirement 18
        """
        results = search_service.search(invalid_query)
        
        # Should return empty list for invalid queries
        assert isinstance(results, list), "Search should return a list"
        assert len(results) == 0, "Invalid queries should return no results"
    
    @given(search_query_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_search_respects_result_limit(self, search_service, search_query):
        """
        Property: For any search query with limit parameter, 
        results SHALL not exceed the specified limit.
        
        Feature: pune-knowledge-base, Property 2: Search Result Accuracy
        Validates: Requirement 18
        """
        limit = 5
        results = search_service.search(search_query, limit=limit)
        
        assert len(results) <= limit, \
            f"Results should not exceed limit of {limit}, got {len(results)}"
    
    @given(search_query_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_search_results_have_relevance_scores(self, search_service, search_query):
        """
        Property: For any search query that returns results, 
        each result SHALL have a relevance score.
        
        Feature: pune-knowledge-base, Property 2: Search Result Accuracy
        Validates: Requirement 18
        """
        results = search_service.search(search_query)
        
        for result in results:
            assert 'relevance_score' in result, "Each result should have a relevance_score"
            assert isinstance(result['relevance_score'], (int, float)), \
                "Relevance score should be numeric"
            assert result['relevance_score'] > 0, "Relevance score should be positive"
    
    @given(st.lists(search_query_strategy, min_size=1, max_size=3))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_search_consistency(self, search_service, queries):
        """
        Property: For any search query, running the search multiple times 
        SHALL return the same results in the same order.
        
        Feature: pune-knowledge-base, Property 2: Search Result Accuracy
        Validates: Requirement 18
        """
        query = queries[0]
        
        # Run search twice
        results1 = search_service.search(query)
        results2 = search_service.search(query)
        
        # Results should be identical
        assert len(results1) == len(results2), "Search should return consistent result count"
        
        for r1, r2 in zip(results1, results2):
            assert r1['id'] == r2['id'], "Search results should be in consistent order"
            assert r1['relevance_score'] == r2['relevance_score'], \
                "Relevance scores should be consistent"
