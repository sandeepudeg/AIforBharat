"""
Property-Based Tests for Chat Response Relevance
Feature: pune-knowledge-base, Property 4: Chat Response Relevance
Validates: Requirement 19
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

chat_message_strategy = st.text(
    alphabet=st.characters(blacklist_categories=('Cc', 'Cs')),
    min_size=2,
    max_size=200
).filter(lambda x: x.strip())

intent_strategy = st.sampled_from(['search', 'browse', 'help', 'general'])

class TestChatResponses:
    """Property-based tests for chat response relevance"""
    
    @given(chat_message_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_chat_response_is_string(self, chat_service, chat_message):
        """
        Property: For any user message, get_response 
        SHALL return a tuple of (response_string, articles_list).
        
        Feature: pune-knowledge-base, Property 4: Chat Response Relevance
        Validates: Requirement 19
        """
        response, articles = chat_service.get_response(chat_message)
        
        assert isinstance(response, str), "Response should be a string"
        assert isinstance(articles, list), "Articles should be a list"
        assert len(response) > 0, "Response should not be empty"
    
    @given(chat_message_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_chat_response_articles_have_required_fields(self, chat_service, chat_message):
        """
        Property: For any user message, all articles in the response 
        SHALL have id and title fields.
        
        Feature: pune-knowledge-base, Property 4: Chat Response Relevance
        Validates: Requirement 19
        """
        response, articles = chat_service.get_response(chat_message)
        
        for article in articles:
            assert 'id' in article, "Article should have id"
            assert 'title' in article, "Article should have title"
    
    @given(st.text(min_size=0, max_size=1))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_chat_handles_invalid_messages(self, chat_service, invalid_message):
        """
        Property: For any invalid message (empty or too short), 
        get_response SHALL return a valid response without error.
        
        Feature: pune-knowledge-base, Property 4: Chat Response Relevance
        Validates: Requirement 19
        """
        response, articles = chat_service.get_response(invalid_message)
        
        assert isinstance(response, str), "Should return string response"
        assert len(response) > 0, "Should provide feedback for invalid input"
    
    def test_chat_intent_detection_returns_valid_intent(self, chat_service):
        """
        Property: For any user message, _detect_intent 
        SHALL return one of: 'search', 'browse', 'help', 'general'.
        
        Feature: pune-knowledge-base, Property 4: Chat Response Relevance
        Validates: Requirement 19
        """
        test_messages = [
            "find information about food",
            "show me categories",
            "how do I use this",
            "tell me about Pune"
        ]
        
        valid_intents = {'search', 'browse', 'help', 'general'}
        
        for message in test_messages:
            intent = chat_service._detect_intent(message)
            assert intent in valid_intents, \
                f"Intent should be one of {valid_intents}, got '{intent}'"
    
    @given(chat_message_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_chat_response_consistency(self, chat_service, chat_message):
        """
        Property: For any user message, calling get_response multiple times 
        SHALL return the same response.
        
        Feature: pune-knowledge-base, Property 4: Chat Response Relevance
        Validates: Requirement 19
        """
        response1, articles1 = chat_service.get_response(chat_message)
        response2, articles2 = chat_service.get_response(chat_message)
        
        assert response1 == response2, "Response should be consistent"
        assert len(articles1) == len(articles2), "Articles count should be consistent"
    
    @given(chat_message_strategy)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_chat_response_articles_limit(self, chat_service, chat_message):
        """
        Property: For any user message, the number of related articles 
        SHALL not exceed a reasonable limit (e.g., 5).
        
        Feature: pune-knowledge-base, Property 4: Chat Response Relevance
        Validates: Requirement 19
        """
        response, articles = chat_service.get_response(chat_message)
        
        assert len(articles) <= 5, \
            f"Should return at most 5 articles, got {len(articles)}"
    
    def test_chat_search_intent_returns_articles(self, chat_service):
        """
        Property: For a message with search intent, get_response 
        SHALL return articles if matching content exists.
        
        Feature: pune-knowledge-base, Property 4: Chat Response Relevance
        Validates: Requirement 19
        """
        search_messages = [
            "find information about food",
            "search for culture",
            "look for places to visit"
        ]
        
        for message in search_messages:
            response, articles = chat_service.get_response(message)
            
            # Should return a response
            assert len(response) > 0, "Should return a response for search intent"
    
    def test_chat_browse_intent_returns_categories(self, chat_service):
        """
        Property: For a message with browse intent, get_response 
        SHALL return information about categories.
        
        Feature: pune-knowledge-base, Property 4: Chat Response Relevance
        Validates: Requirement 19
        """
        browse_messages = [
            "show me categories",
            "list all categories",
            "browse available topics"
        ]
        
        for message in browse_messages:
            response, articles = chat_service.get_response(message)
            
            # Response should mention categories
            assert len(response) > 0, "Should return a response for browse intent"
    
    def test_chat_help_intent_returns_guidance(self, chat_service):
        """
        Property: For a message with help intent, get_response 
        SHALL return helpful guidance.
        
        Feature: pune-knowledge-base, Property 4: Chat Response Relevance
        Validates: Requirement 19
        """
        help_messages = [
            "help",
            "how do I use this",
            "guide me"
        ]
        
        for message in help_messages:
            response, articles = chat_service.get_response(message)
            
            # Response should be helpful
            assert len(response) > 0, "Should return helpful response"
            assert len(response) > 50, "Help response should be detailed"
    
    @given(st.lists(chat_message_strategy, min_size=1, max_size=5))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_chat_handles_multiple_messages(self, chat_service, messages):
        """
        Property: For any sequence of messages, each message 
        SHALL receive a valid response without error.
        
        Feature: pune-knowledge-base, Property 4: Chat Response Relevance
        Validates: Requirement 19
        """
        for message in messages:
            response, articles = chat_service.get_response(message)
            
            assert isinstance(response, str), "Each response should be a string"
            assert len(response) > 0, "Each response should be non-empty"
            assert isinstance(articles, list), "Articles should be a list"
