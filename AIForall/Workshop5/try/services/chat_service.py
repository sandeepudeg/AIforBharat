"""
Chat Service - Handles chat and conversational interactions
"""
import logging
from typing import Tuple, List, Dict, Optional

logger = logging.getLogger(__name__)

class ChatService:
    """Service for handling chat interactions"""
    
    def __init__(self, data_service):
        """
        Initialize chat service
        
        Args:
            data_service: DataService instance
        """
        self.data_service = data_service
        logger.info("ChatService initialized")
    
    def get_response(self, message: str) -> Tuple[str, List[Dict]]:
        """
        Get chat response for user message
        
        Args:
            message: User message
            
        Returns:
            Tuple of (response_text, related_articles)
        """
        try:
            if not message or len(message.strip()) < 2:
                return "Please enter a valid message.", []
            
            # Detect intent
            intent = self._detect_intent(message)
            logger.info(f"Detected intent: {intent}")
            
            # Get response based on intent
            if intent == 'search':
                return self._handle_search(message)
            elif intent == 'browse':
                return self._handle_browse(message)
            elif intent == 'help':
                return self._handle_help()
            else:
                return self._handle_general_query(message)
        except Exception as e:
            logger.error(f"Error getting chat response: {str(e)}")
            return "Sorry, I encountered an error. Please try again.", []
    
    def _detect_intent(self, message: str) -> str:
        """
        Detect user intent from message
        
        Args:
            message: User message
            
        Returns:
            Intent type (search, browse, help, general)
        """
        message_lower = message.lower()
        
        # Help intent
        if any(word in message_lower for word in ['help', 'how', 'guide', 'tutorial']):
            return 'help'
        
        # Browse intent
        if any(word in message_lower for word in ['show', 'list', 'browse', 'categories']):
            return 'browse'
        
        # Search intent
        if any(word in message_lower for word in ['find', 'search', 'look for', 'about']):
            return 'search'
        
        # Default to general query
        return 'general'
    
    def _handle_search(self, message: str) -> Tuple[str, List[Dict]]:
        """
        Handle search intent
        
        Args:
            message: User message
            
        Returns:
            Tuple of (response_text, related_articles)
        """
        # Extract search query
        query = self._extract_query(message)
        
        if not query:
            return "What would you like to search for?", []
        
        # Search articles
        articles = self.data_service.search_articles(query)
        
        if articles:
            response = f"I found {len(articles)} article(s) related to '{query}'. Here are the top results:"
            related_articles = [
                {'id': a['id'], 'title': a['title']}
                for a in articles[:3]
            ]
            return response, related_articles
        else:
            return f"I couldn't find specific information about '{query}'. Try searching for related topics or browse our categories.", []
    
    def _handle_browse(self, message: str) -> Tuple[str, List[Dict]]:
        """
        Handle browse intent
        
        Args:
            message: User message
            
        Returns:
            Tuple of (response_text, related_articles)
        """
        categories = self.data_service.get_all_categories()
        
        response = "Here are our main categories:\n"
        for i, cat in enumerate(categories, 1):
            response += f"{i}. {cat.get('name', '')}\n"
        
        response += "\nWhich category would you like to explore?"
        
        return response, []
    
    def _handle_help(self) -> Tuple[str, List[Dict]]:
        """
        Handle help intent
        
        Returns:
            Tuple of (response_text, related_articles)
        """
        response = """
I'm here to help you explore Pune! Here's what you can do:

1. **Search**: Ask me about anything related to Pune
   - "Tell me about Misal Pav"
   - "What are the best trekking routes?"
   - "Where can I find good nightlife?"

2. **Browse**: Explore our categories
   - "Show me all categories"
   - "What's in the Food section?"

3. **Get Information**: Ask specific questions
   - "What is Puneri culture?"
   - "Tell me about Fergusson College"
   - "How do I get around Pune?"

Just type your question and I'll help you find the information you need!
        """
        return response, []
    
    def _handle_general_query(self, message: str) -> Tuple[str, List[Dict]]:
        """
        Handle general query
        
        Args:
            message: User message
            
        Returns:
            Tuple of (response_text, related_articles)
        """
        # Search for relevant articles
        articles = self.data_service.search_articles(message)
        
        if articles:
            response = f"I found information related to your query. Here are the most relevant articles:"
            related_articles = [
                {'id': a['id'], 'title': a['title']}
                for a in articles[:3]
            ]
            return response, related_articles
        else:
            response = "I couldn't find specific information about that. Try:\n"
            response += "- Browsing our categories\n"
            response += "- Searching for related topics\n"
            response += "- Asking 'help' for more options"
            return response, []
    
    def _extract_query(self, message: str) -> str:
        """
        Extract search query from message
        
        Args:
            message: User message
            
        Returns:
            Extracted query
        """
        # Remove common search words
        search_words = ['find', 'search', 'look for', 'about', 'tell me', 'show me', 'what is']
        query = message.lower()
        
        for word in search_words:
            if query.startswith(word):
                query = query[len(word):].strip()
                break
        
        # Remove question mark
        query = query.rstrip('?').strip()
        
        return query
    
    def get_suggestions(self, partial_message: str) -> List[str]:
        """
        Get chat suggestions based on partial message
        
        Args:
            partial_message: Partial user message
            
        Returns:
            List of suggested completions
        """
        try:
            suggestions = []
            
            # Get search suggestions
            search_suggestions = self.data_service.search_articles(partial_message)
            for article in search_suggestions[:3]:
                suggestions.append(f"Tell me about {article.get('title', '')}")
            
            return suggestions
        except Exception as e:
            logger.error(f"Error getting suggestions: {str(e)}")
            return []
