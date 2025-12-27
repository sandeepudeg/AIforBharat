"""
Validation Service - Handles input validation for the application
"""
import logging
import re
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class ValidationService:
    """Service for validating user inputs"""
    
    # Constants
    MIN_SEARCH_LENGTH = 2
    MAX_SEARCH_LENGTH = 200
    MIN_MESSAGE_LENGTH = 1
    MAX_MESSAGE_LENGTH = 500
    MIN_CATEGORY_LENGTH = 1
    MAX_CATEGORY_LENGTH = 50
    
    # Patterns
    SEARCH_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-\'\".,?!&()]+$')
    MESSAGE_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-\'\".,?!&()\n]+$')
    CATEGORY_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]+$')
    
    @staticmethod
    def validate_search_query(query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate search query
        
        Args:
            query: Search query string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not query:
            return False, "Search query cannot be empty"
        
        query = query.strip()
        
        if len(query) < ValidationService.MIN_SEARCH_LENGTH:
            return False, f"Search query must be at least {ValidationService.MIN_SEARCH_LENGTH} characters"
        
        if len(query) > ValidationService.MAX_SEARCH_LENGTH:
            return False, f"Search query cannot exceed {ValidationService.MAX_SEARCH_LENGTH} characters"
        
        # Check for valid characters
        if not ValidationService.SEARCH_PATTERN.match(query):
            return False, "Search query contains invalid characters"
        
        logger.info(f"Search query validated: {query[:50]}...")
        return True, None
    
    @staticmethod
    def validate_chat_message(message: str) -> Tuple[bool, Optional[str]]:
        """
        Validate chat message
        
        Args:
            message: Chat message string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not message:
            return False, "Message cannot be empty"
        
        message = message.strip()
        
        if len(message) < ValidationService.MIN_MESSAGE_LENGTH:
            return False, f"Message must be at least {ValidationService.MIN_MESSAGE_LENGTH} character"
        
        if len(message) > ValidationService.MAX_MESSAGE_LENGTH:
            return False, f"Message cannot exceed {ValidationService.MAX_MESSAGE_LENGTH} characters"
        
        # Check for valid characters
        if not ValidationService.MESSAGE_PATTERN.match(message):
            return False, "Message contains invalid characters"
        
        logger.info(f"Chat message validated: {message[:50]}...")
        return True, None
    
    @staticmethod
    def validate_category_id(category_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate category ID
        
        Args:
            category_id: Category ID string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not category_id:
            return False, "Category ID cannot be empty"
        
        category_id = category_id.strip()
        
        if len(category_id) < ValidationService.MIN_CATEGORY_LENGTH:
            return False, f"Category ID must be at least {ValidationService.MIN_CATEGORY_LENGTH} character"
        
        if len(category_id) > ValidationService.MAX_CATEGORY_LENGTH:
            return False, f"Category ID cannot exceed {ValidationService.MAX_CATEGORY_LENGTH} characters"
        
        # Check for valid characters (alphanumeric, underscore, hyphen)
        if not ValidationService.CATEGORY_PATTERN.match(category_id):
            return False, "Category ID contains invalid characters"
        
        logger.info(f"Category ID validated: {category_id}")
        return True, None
    
    @staticmethod
    def validate_article_id(article_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate article ID
        
        Args:
            article_id: Article ID string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not article_id:
            return False, "Article ID cannot be empty"
        
        article_id = article_id.strip()
        
        if len(article_id) < ValidationService.MIN_CATEGORY_LENGTH:
            return False, f"Article ID must be at least {ValidationService.MIN_CATEGORY_LENGTH} character"
        
        if len(article_id) > ValidationService.MAX_CATEGORY_LENGTH:
            return False, f"Article ID cannot exceed {ValidationService.MAX_CATEGORY_LENGTH} characters"
        
        # Check for valid characters (alphanumeric, underscore, hyphen)
        if not ValidationService.CATEGORY_PATTERN.match(article_id):
            return False, "Article ID contains invalid characters"
        
        logger.info(f"Article ID validated: {article_id}")
        return True, None
    
    @staticmethod
    def sanitize_search_query(query: str) -> str:
        """
        Sanitize search query by removing extra whitespace
        
        Args:
            query: Search query string
            
        Returns:
            Sanitized query
        """
        # Remove extra whitespace
        query = ' '.join(query.split())
        return query.strip()
    
    @staticmethod
    def sanitize_message(message: str) -> str:
        """
        Sanitize chat message by removing extra whitespace
        
        Args:
            message: Chat message string
            
        Returns:
            Sanitized message
        """
        # Remove extra whitespace
        message = ' '.join(message.split())
        return message.strip()
