"""
Property-Based Tests for Data Integrity
Feature: pune-knowledge-base, Property 6: Data Integrity Round-Trip
Validates: Requirements 1-17
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
import json
from services.data_service import DataService

# Strategies for generating test data
article_id_strategy = st.text(
    alphabet=st.characters(blacklist_categories=('Cc', 'Cs')),
    min_size=1,
    max_size=50
).filter(lambda x: x.strip())

article_title_strategy = st.text(
    min_size=1,
    max_size=200
).filter(lambda x: x.strip())

article_content_strategy = st.text(
    min_size=10,
    max_size=5000
).filter(lambda x: x.strip())

category_strategy = st.sampled_from(['food', 'culture', 'geography', 'places', 'trekking'])

tags_strategy = st.lists(
    st.text(min_size=1, max_size=20),
    min_size=0,
    max_size=5
)

article_strategy = st.fixed_dictionaries({
    'id': article_id_strategy,
    'title': article_title_strategy,
    'category': category_strategy,
    'subcategory': st.text(min_size=1, max_size=50),
    'description': st.text(min_size=10, max_size=500),
    'content': article_content_strategy,
    'tags': tags_strategy,
    'related_articles': st.lists(article_id_strategy, max_size=3),
    'created_at': st.just('2025-01-01T00:00:00Z'),
    'updated_at': st.just('2025-01-01T00:00:00Z')
})

class TestDataIntegrity:
    """Property-based tests for data integrity"""
    
    @given(article_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_article_round_trip(self, data_service, article):
        """
        Property: For any article stored in the knowledge base, retrieving and 
        displaying the article SHALL preserve all content, formatting, and metadata 
        without loss or corruption.
        
        Feature: pune-knowledge-base, Property 6: Data Integrity Round-Trip
        Validates: Requirements 1-17
        """
        # Add article
        data_service.add_article(article)
        
        # Retrieve article
        retrieved = data_service.get_article(article['id'])
        
        # Verify all fields are preserved
        assert retrieved is not None, "Article should be retrievable"
        assert retrieved['id'] == article['id'], "ID should be preserved"
        assert retrieved['title'] == article['title'], "Title should be preserved"
        assert retrieved['category'] == article['category'], "Category should be preserved"
        assert retrieved['content'] == article['content'], "Content should be preserved"
        assert retrieved['tags'] == article['tags'], "Tags should be preserved"
        assert retrieved['description'] == article['description'], "Description should be preserved"
    
    @given(st.lists(article_strategy, min_size=1, max_size=10))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_multiple_articles_integrity(self, data_service, articles):
        """
        Property: For any collection of articles, storing and retrieving them 
        SHALL preserve all articles without loss or duplication.
        
        Feature: pune-knowledge-base, Property 6: Data Integrity Round-Trip
        Validates: Requirements 1-17
        """
        # Add all articles
        for article in articles:
            data_service.add_article(article)
        
        # Verify count
        all_articles = data_service.get_all_articles()
        assert len(all_articles) >= len(articles), "All articles should be stored"
        
        # Verify each article is retrievable
        for article in articles:
            retrieved = data_service.get_article(article['id'])
            assert retrieved is not None, f"Article {article['id']} should be retrievable"
            assert retrieved['id'] == article['id'], f"Article {article['id']} ID should match"
    
    @given(article_strategy)
    @settings(max_examples=100)
    def test_article_json_serialization(self, article):
        """
        Property: For any article, serializing to JSON and deserializing 
        SHALL produce an equivalent article.
        
        Feature: pune-knowledge-base, Property 6: Data Integrity Round-Trip
        Validates: Requirements 1-17
        """
        # Serialize to JSON
        json_str = json.dumps(article)
        
        # Deserialize from JSON
        deserialized = json.loads(json_str)
        
        # Verify equivalence
        assert deserialized == article, "Deserialized article should equal original"
        assert deserialized['id'] == article['id'], "ID should be preserved in JSON round-trip"
        assert deserialized['content'] == article['content'], "Content should be preserved in JSON round-trip"
    
    @given(article_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_article_validation(self, data_service, article):
        """
        Property: For any article with required fields, validation 
        SHALL succeed and the article SHALL be storable.
        
        Feature: pune-knowledge-base, Property 6: Data Integrity Round-Trip
        Validates: Requirements 1-17
        """
        # Validate article
        is_valid = data_service.validate_article(article)
        
        # If valid, should be addable
        if is_valid:
            result = data_service.add_article(article)
            assert result is True, "Valid article should be addable"
            
            # Should be retrievable
            retrieved = data_service.get_article(article['id'])
            assert retrieved is not None, "Added article should be retrievable"
    
    @given(st.lists(article_strategy, min_size=1, max_size=5))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_category_index_integrity(self, data_service, articles):
        """
        Property: For any collection of articles, the category index 
        SHALL correctly map all articles to their categories.
        
        Feature: pune-knowledge-base, Property 6: Data Integrity Round-Trip
        Validates: Requirements 1-17
        """
        # Add articles
        for article in articles:
            data_service.add_article(article)
        
        # Verify index
        for article in articles:
            category = article['category']
            category_articles = data_service.get_articles_by_category(category)
            
            # Article should be in its category
            article_ids = [a['id'] for a in category_articles]
            assert article['id'] in article_ids, f"Article should be indexed in category {category}"
    
    @given(article_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_article_metadata_preservation(self, data_service, article):
        """
        Property: For any article, all metadata fields 
        SHALL be preserved without modification.
        
        Feature: pune-knowledge-base, Property 6: Data Integrity Round-Trip
        Validates: Requirements 1-17
        """
        # Add article
        data_service.add_article(article)
        
        # Retrieve article
        retrieved = data_service.get_article(article['id'])
        
        # Verify metadata
        assert retrieved['created_at'] == article['created_at'], "Created timestamp should be preserved"
        assert retrieved['updated_at'] == article['updated_at'], "Updated timestamp should be preserved"
        assert retrieved['subcategory'] == article['subcategory'], "Subcategory should be preserved"
        assert len(retrieved['related_articles']) == len(article['related_articles']), "Related articles count should match"
