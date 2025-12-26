"""
Property-Based Tests for Navigation and Related Articles
Feature: pune-knowledge-base, Property 7: Navigation Breadcrumb Accuracy
Feature: pune-knowledge-base, Property 8: Related Articles Validity
Validates: Requirement 19
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

article_id_strategy = st.text(
    alphabet=st.characters(blacklist_categories=('Cc', 'Cs')),
    min_size=1,
    max_size=50
).filter(lambda x: x.strip())

class TestNavigation:
    """Property-based tests for navigation and breadcrumbs"""
    
    def test_breadcrumb_structure_valid(self, article_service):
        """
        Property: For any article, get_breadcrumbs 
        SHALL return a list of breadcrumb items with name and link.
        
        Feature: pune-knowledge-base, Property 7: Navigation Breadcrumb Accuracy
        Validates: Requirement 19
        """
        articles = article_service.get_all_articles()
        
        if articles:
            article = articles[0]
            breadcrumbs = article_service.get_breadcrumbs(article['id'])
            
            assert isinstance(breadcrumbs, list), "Breadcrumbs should be a list"
            
            for breadcrumb in breadcrumbs:
                assert 'name' in breadcrumb, "Breadcrumb should have name"
                assert 'link' in breadcrumb, "Breadcrumb should have link"
    
    def test_breadcrumb_includes_home(self, article_service):
        """
        Property: For any article, breadcrumbs 
        SHALL include a home link as the first item.
        
        Feature: pune-knowledge-base, Property 7: Navigation Breadcrumb Accuracy
        Validates: Requirement 19
        """
        articles = article_service.get_all_articles()
        
        if articles:
            article = articles[0]
            breadcrumbs = article_service.get_breadcrumbs(article['id'])
            
            assert len(breadcrumbs) > 0, "Should have at least home breadcrumb"
            assert breadcrumbs[0]['name'].lower() == 'home', \
                "First breadcrumb should be home"
    
    def test_breadcrumb_includes_category(self, article_service):
        """
        Property: For any article, breadcrumbs 
        SHALL include the article's category.
        
        Feature: pune-knowledge-base, Property 7: Navigation Breadcrumb Accuracy
        Validates: Requirement 19
        """
        articles = article_service.get_all_articles()
        
        if articles:
            article = articles[0]
            breadcrumbs = article_service.get_breadcrumbs(article['id'])
            
            breadcrumb_names = [b['name'].lower() for b in breadcrumbs]
            category = article.get('category', '').lower()
            
            assert category in breadcrumb_names, \
                f"Breadcrumbs should include category '{category}'"
    
    def test_breadcrumb_includes_article_title(self, article_service):
        """
        Property: For any article, breadcrumbs 
        SHALL include the article's title as the last item.
        
        Feature: pune-knowledge-base, Property 7: Navigation Breadcrumb Accuracy
        Validates: Requirement 19
        """
        articles = article_service.get_all_articles()
        
        if articles:
            article = articles[0]
            breadcrumbs = article_service.get_breadcrumbs(article['id'])
            
            assert len(breadcrumbs) > 0, "Should have breadcrumbs"
            assert breadcrumbs[-1]['name'] == article['title'], \
                "Last breadcrumb should be article title"
    
    def test_breadcrumb_links_are_valid(self, article_service):
        """
        Property: For any article, all breadcrumb links 
        SHALL be non-empty strings.
        
        Feature: pune-knowledge-base, Property 7: Navigation Breadcrumb Accuracy
        Validates: Requirement 19
        """
        articles = article_service.get_all_articles()
        
        if articles:
            article = articles[0]
            breadcrumbs = article_service.get_breadcrumbs(article['id'])
            
            for breadcrumb in breadcrumbs:
                assert isinstance(breadcrumb['link'], str), \
                    "Breadcrumb link should be a string"
                assert len(breadcrumb['link']) > 0, \
                    "Breadcrumb link should not be empty"


class TestRelatedArticles:
    """Property-based tests for related articles validity"""
    
    def test_related_articles_exist(self, article_service):
        """
        Property: For any article with related_articles field, 
        all referenced article IDs SHALL exist in the knowledge base.
        
        Feature: pune-knowledge-base, Property 8: Related Articles Validity
        Validates: Requirement 19
        """
        articles = article_service.get_all_articles()
        all_article_ids = {a['id'] for a in articles}
        
        for article in articles:
            related_ids = article.get('related_articles', [])
            
            for related_id in related_ids:
                assert related_id in all_article_ids, \
                    f"Related article '{related_id}' should exist in knowledge base"
    
    def test_related_articles_are_different(self, article_service):
        """
        Property: For any article, related articles 
        SHALL NOT include the article itself.
        
        Feature: pune-knowledge-base, Property 8: Related Articles Validity
        Validates: Requirement 19
        """
        articles = article_service.get_all_articles()
        
        for article in articles:
            related_ids = article.get('related_articles', [])
            
            assert article['id'] not in related_ids, \
                "Article should not be related to itself"
    
    def test_get_related_articles_returns_valid_articles(self, article_service):
        """
        Property: For any article, get_related_articles 
        SHALL return articles with all required fields.
        
        Feature: pune-knowledge-base, Property 8: Related Articles Validity
        Validates: Requirement 19
        """
        articles = article_service.get_all_articles()
        
        if articles:
            article = articles[0]
            related = article_service.get_related_articles(article['id'])
            
            for rel_article in related:
                assert 'id' in rel_article, "Related article should have id"
                assert 'title' in rel_article, "Related article should have title"
                assert 'category' in rel_article, "Related article should have category"
    
    def test_related_articles_count_matches(self, article_service):
        """
        Property: For any article, the count of related articles 
        SHALL match the length of related_articles field.
        
        Feature: pune-knowledge-base, Property 8: Related Articles Validity
        Validates: Requirement 19
        """
        articles = article_service.get_all_articles()
        
        for article in articles:
            expected_count = len(article.get('related_articles', []))
            related = article_service.get_related_articles(article['id'])
            
            assert len(related) == expected_count, \
                f"Related articles count should match (expected {expected_count}, got {len(related)})"
    
    def test_related_articles_are_from_knowledge_base(self, article_service):
        """
        Property: For any article, all related articles 
        SHALL be retrievable from the knowledge base.
        
        Feature: pune-knowledge-base, Property 8: Related Articles Validity
        Validates: Requirement 19
        """
        articles = article_service.get_all_articles()
        
        for article in articles:
            related = article_service.get_related_articles(article['id'])
            
            for rel_article in related:
                # Should be retrievable by ID
                retrieved = article_service.get_article(rel_article['id'])
                assert retrieved is not None, \
                    f"Related article {rel_article['id']} should be retrievable"
    
    def test_related_articles_consistency(self, article_service):
        """
        Property: For any article, calling get_related_articles multiple times 
        SHALL return the same articles in the same order.
        
        Feature: pune-knowledge-base, Property 8: Related Articles Validity
        Validates: Requirement 19
        """
        articles = article_service.get_all_articles()
        
        if articles:
            article = articles[0]
            
            related1 = article_service.get_related_articles(article['id'])
            related2 = article_service.get_related_articles(article['id'])
            
            assert len(related1) == len(related2), \
                "Related articles should be consistent"
            
            for r1, r2 in zip(related1, related2):
                assert r1['id'] == r2['id'], \
                    "Related articles should be in consistent order"
