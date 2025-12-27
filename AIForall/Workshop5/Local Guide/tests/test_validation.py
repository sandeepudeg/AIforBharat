"""
Unit tests for validation service
"""
import pytest
from services.validation_service import ValidationService


class TestSearchQueryValidation:
    """Tests for search query validation"""
    
    def test_valid_search_query(self):
        """Test valid search query"""
        is_valid, error = ValidationService.validate_search_query("Misal Pav")
        assert is_valid is True
        assert error is None
    
    def test_empty_search_query(self):
        """Test empty search query"""
        is_valid, error = ValidationService.validate_search_query("")
        assert is_valid is False
        assert error is not None
    
    def test_search_query_too_short(self):
        """Test search query too short"""
        is_valid, error = ValidationService.validate_search_query("a")
        assert is_valid is False
        assert "at least" in error.lower()
    
    def test_search_query_too_long(self):
        """Test search query too long"""
        long_query = "a" * 201
        is_valid, error = ValidationService.validate_search_query(long_query)
        assert is_valid is False
        assert "exceed" in error.lower()
    
    def test_search_query_with_whitespace(self):
        """Test search query with extra whitespace"""
        is_valid, error = ValidationService.validate_search_query("  Pune  ")
        assert is_valid is True
        assert error is None
    
    def test_search_query_with_special_chars(self):
        """Test search query with valid special characters"""
        is_valid, error = ValidationService.validate_search_query("What's in Pune?")
        assert is_valid is True
        assert error is None
    
    def test_search_query_with_invalid_chars(self):
        """Test search query with invalid characters"""
        is_valid, error = ValidationService.validate_search_query("Pune@#$%")
        assert is_valid is False
        assert "invalid" in error.lower()


class TestChatMessageValidation:
    """Tests for chat message validation"""
    
    def test_valid_chat_message(self):
        """Test valid chat message"""
        is_valid, error = ValidationService.validate_chat_message("Tell me about Pune")
        assert is_valid is True
        assert error is None
    
    def test_empty_chat_message(self):
        """Test empty chat message"""
        is_valid, error = ValidationService.validate_chat_message("")
        assert is_valid is False
        assert error is not None
    
    def test_chat_message_too_long(self):
        """Test chat message too long"""
        long_message = "a" * 501
        is_valid, error = ValidationService.validate_chat_message(long_message)
        assert is_valid is False
        assert "exceed" in error.lower()
    
    def test_chat_message_with_whitespace(self):
        """Test chat message with extra whitespace"""
        is_valid, error = ValidationService.validate_chat_message("  Hello  ")
        assert is_valid is True
        assert error is None
    
    def test_chat_message_with_newlines(self):
        """Test chat message with newlines"""
        is_valid, error = ValidationService.validate_chat_message("Hello\nWorld")
        assert is_valid is True
        assert error is None
    
    def test_chat_message_with_invalid_chars(self):
        """Test chat message with invalid characters"""
        is_valid, error = ValidationService.validate_chat_message("Hello@#$%")
        assert is_valid is False
        assert "invalid" in error.lower()


class TestCategoryIdValidation:
    """Tests for category ID validation"""
    
    def test_valid_category_id(self):
        """Test valid category ID"""
        is_valid, error = ValidationService.validate_category_id("food")
        assert is_valid is True
        assert error is None
    
    def test_valid_category_id_with_underscore(self):
        """Test valid category ID with underscore"""
        is_valid, error = ValidationService.validate_category_id("folk_culture")
        assert is_valid is True
        assert error is None
    
    def test_valid_category_id_with_hyphen(self):
        """Test valid category ID with hyphen"""
        is_valid, error = ValidationService.validate_category_id("folk-culture")
        assert is_valid is True
        assert error is None
    
    def test_empty_category_id(self):
        """Test empty category ID"""
        is_valid, error = ValidationService.validate_category_id("")
        assert is_valid is False
        assert error is not None
    
    def test_category_id_too_long(self):
        """Test category ID too long"""
        long_id = "a" * 51
        is_valid, error = ValidationService.validate_category_id(long_id)
        assert is_valid is False
        assert "exceed" in error.lower()
    
    def test_category_id_with_invalid_chars(self):
        """Test category ID with invalid characters"""
        is_valid, error = ValidationService.validate_category_id("food@culture")
        assert is_valid is False
        assert "invalid" in error.lower()


class TestArticleIdValidation:
    """Tests for article ID validation"""
    
    def test_valid_article_id(self):
        """Test valid article ID"""
        is_valid, error = ValidationService.validate_article_id("misal_pav")
        assert is_valid is True
        assert error is None
    
    def test_valid_article_id_with_hyphen(self):
        """Test valid article ID with hyphen"""
        is_valid, error = ValidationService.validate_article_id("kasba-peth")
        assert is_valid is True
        assert error is None
    
    def test_empty_article_id(self):
        """Test empty article ID"""
        is_valid, error = ValidationService.validate_article_id("")
        assert is_valid is False
        assert error is not None
    
    def test_article_id_too_long(self):
        """Test article ID too long"""
        long_id = "a" * 51
        is_valid, error = ValidationService.validate_article_id(long_id)
        assert is_valid is False
        assert "exceed" in error.lower()
    
    def test_article_id_with_invalid_chars(self):
        """Test article ID with invalid characters"""
        is_valid, error = ValidationService.validate_article_id("misal@pav")
        assert is_valid is False
        assert "invalid" in error.lower()


class TestSanitization:
    """Tests for input sanitization"""
    
    def test_sanitize_search_query(self):
        """Test search query sanitization"""
        query = "  Pune   food  "
        sanitized = ValidationService.sanitize_search_query(query)
        assert sanitized == "Pune food"
    
    def test_sanitize_message(self):
        """Test message sanitization"""
        message = "  Hello   world  "
        sanitized = ValidationService.sanitize_message(message)
        assert sanitized == "Hello world"
    
    def test_sanitize_preserves_content(self):
        """Test sanitization preserves content"""
        query = "What's in Pune?"
        sanitized = ValidationService.sanitize_search_query(query)
        assert "What's" in sanitized
        assert "Pune" in sanitized
