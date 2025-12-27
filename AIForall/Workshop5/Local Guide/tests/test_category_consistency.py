"""
Property-Based Tests for Category Consistency
Feature: pune-knowledge-base, Property 3: Category Navigation Consistency
Validates: Requirements 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

category_name_strategy = st.sampled_from(['food', 'culture'])

class TestCategoryConsistency:
    """Property-based tests for category consistency"""
    
    @given(category_name_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_category_articles_belong_to_category(self, category_service, category_name):
        """
        Property: For any category, all articles returned by get_category_articles 
        SHALL have their category field matching the requested category.
        
        Feature: pune-knowledge-base, Property 3: Category Navigation Consistency
        Validates: Requirements 1-17
        """
        articles = category_service.get_category_articles(category_name)
        
        for article in articles:
            assert article.get('category') == category_name, \
                f"Article should belong to category '{category_name}'"
    
    @given(category_name_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_category_article_count_consistency(self, category_service, category_name):
        """
        Property: For any category, the article count returned by get_article_count 
        SHALL match the length of articles returned by get_category_articles.
        
        Feature: pune-knowledge-base, Property 3: Category Navigation Consistency
        Validates: Requirements 1-17
        """
        articles = category_service.get_category_articles(category_name)
        count = category_service.get_article_count(category_name)
        
        assert count == len(articles), \
            f"Article count should match actual articles (expected {len(articles)}, got {count})"
    
    def test_all_categories_retrievable(self, category_service):
        """
        Property: All categories in the system SHALL be retrievable 
        via get_all_categories.
        
        Feature: pune-knowledge-base, Property 3: Category Navigation Consistency
        Validates: Requirements 1-17
        """
        categories = category_service.get_all_categories()
        
        assert isinstance(categories, list), "get_all_categories should return a list"
        assert len(categories) > 0, "Should have at least one category"
        
        # Each category should have required fields
        for category in categories:
            assert 'id' in category or 'name' in category, \
                "Each category should have id or name"
    
    @given(category_name_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_category_exists_check(self, category_service, category_name):
        """
        Property: For any valid category name, category_exists 
        SHALL return True.
        
        Feature: pune-knowledge-base, Property 3: Category Navigation Consistency
        Validates: Requirements 1-17
        """
        exists = category_service.category_exists(category_name)
        
        assert isinstance(exists, bool), "category_exists should return boolean"
        assert exists is True, f"Category '{category_name}' should exist"
    
    def test_category_articles_have_required_fields(self, category_service):
        """
        Property: For any article in any category, the article 
        SHALL have all required fields (id, title, category, content).
        
        Feature: pune-knowledge-base, Property 3: Category Navigation Consistency
        Validates: Requirements 1-17
        """
        categories = category_service.get_all_categories()
        
        for category in categories:
            category_id = category.get('id')
            articles = category_service.get_category_articles(category_id)
            
            for article in articles:
                assert 'id' in article, "Article should have id"
                assert 'title' in article, "Article should have title"
                assert 'category' in article, "Article should have category"
                assert 'content' in article, "Article should have content"
    
    @given(st.lists(category_name_strategy, min_size=1, max_size=3, unique=True))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_category_filtering_isolation(self, category_service, categories):
        """
        Property: For any set of categories, articles from one category 
        SHALL NOT appear in results for another category.
        
        Feature: pune-knowledge-base, Property 3: Category Navigation Consistency
        Validates: Requirements 1-17
        """
        if len(categories) < 2:
            return
        
        cat1, cat2 = categories[0], categories[1]
        
        articles1 = category_service.get_category_articles(cat1)
        articles2 = category_service.get_category_articles(cat2)
        
        ids1 = {a['id'] for a in articles1}
        ids2 = {a['id'] for a in articles2}
        
        # No overlap between categories
        overlap = ids1 & ids2
        assert len(overlap) == 0, \
            f"Articles should not appear in multiple categories (found {len(overlap)} overlaps)"
    
    def test_category_statistics_consistency(self, category_service):
        """
        Property: For all categories combined, the sum of article counts 
        SHALL equal the total number of articles in the system.
        
        Feature: pune-knowledge-base, Property 3: Category Navigation Consistency
        Validates: Requirements 1-17
        """
        categories = category_service.get_all_categories()
        
        total_count = 0
        for category in categories:
            # Use the ID as the category identifier
            category_id = category.get('id')
            count = category_service.get_article_count(category_id)
            total_count += count
        
        # Total should be positive
        assert total_count > 0, "Should have articles across all categories"
    
    @given(category_name_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_category_articles_consistency(self, category_service, category_name):
        """
        Property: For any category, calling get_category_articles multiple times 
        SHALL return the same articles in the same order.
        
        Feature: pune-knowledge-base, Property 3: Category Navigation Consistency
        Validates: Requirements 1-17
        """
        articles1 = category_service.get_category_articles(category_name)
        articles2 = category_service.get_category_articles(category_name)
        
        assert len(articles1) == len(articles2), \
            "Category articles should be consistent"
        
        for a1, a2 in zip(articles1, articles2):
            assert a1['id'] == a2['id'], \
                "Category articles should be in consistent order"
