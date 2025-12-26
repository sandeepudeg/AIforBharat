"""
API routes - RESTful API endpoints
"""
import logging
from flask import Blueprint, request, jsonify
from services.data_service import get_data_service
from services.chat_service import ChatService
from services.search_service import SearchService
from services.category_service import CategoryService
from services.article_service import ArticleService
from services.validation_service import ValidationService

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

# Services will be initialized lazily on first use
_services = {}

def _get_services():
    """Get or initialize services"""
    global _services
    
    if not _services:
        data_service = get_data_service()
        # Ensure data is loaded
        if not data_service.articles:
            data_service.load_all_data()
        
        _services = {
            'data': data_service,
            'chat': ChatService(data_service),
            'search': SearchService(data_service),
            'category': CategoryService(data_service),
            'article': ArticleService(data_service)
        }
    
    return _services

# ============================================================================
# CATEGORIES ENDPOINTS
# ============================================================================

@api_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        services = _get_services()
        category_service = services['category']
        categories = category_service.get_all_categories()
        return jsonify({
            'success': True,
            'data': categories,
            'count': len(categories)
        }), 200
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/categories/<category_id>', methods=['GET'])
def get_category(category_id):
    """Get category by ID"""
    try:
        # Validate category ID
        is_valid, error_msg = ValidationService.validate_category_id(category_id)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        services = _get_services()
        category_service = services['category']
        category = category_service.get_category(category_id)
        if not category:
            return jsonify({'success': False, 'error': 'Category not found'}), 404
        
        return jsonify({
            'success': True,
            'data': category
        }), 200
    except Exception as e:
        logger.error(f"Error getting category: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/categories/<category_id>/articles', methods=['GET'])
def get_category_articles(category_id):
    """Get articles in a category"""
    try:
        # Validate category ID
        is_valid, error_msg = ValidationService.validate_category_id(category_id)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        services = _get_services()
        category_service = services['category']
        articles = category_service.get_category_articles(category_id)
        return jsonify({
            'success': True,
            'data': articles,
            'count': len(articles)
        }), 200
    except Exception as e:
        logger.error(f"Error getting category articles: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# ARTICLES ENDPOINTS
# ============================================================================

@api_bp.route('/articles/<article_id>', methods=['GET'])
def get_article(article_id):
    """Get article by ID"""
    try:
        # Validate article ID
        is_valid, error_msg = ValidationService.validate_article_id(article_id)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        services = _get_services()
        article_service = services['article']
        article = article_service.get_article(article_id)
        if not article:
            return jsonify({'success': False, 'error': 'Article not found'}), 404
        
        return jsonify({
            'success': True,
            'data': article
        }), 200
    except Exception as e:
        logger.error(f"Error getting article: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# SEARCH ENDPOINTS
# ============================================================================

@api_bp.route('/search', methods=['GET'])
def search():
    """Search articles"""
    try:
        services = _get_services()
        search_service = services['search']
        
        query = request.args.get('q', '').strip()
        category = request.args.get('category', None)
        
        # Validate search query
        is_valid, error_msg = ValidationService.validate_search_query(query)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Sanitize query
        query = ValidationService.sanitize_search_query(query)
        
        # Validate category if provided
        if category:
            is_valid, error_msg = ValidationService.validate_category_id(category)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': f"Invalid category: {error_msg}"
                }), 400
        
        results = search_service.search(query, category)
        
        return jsonify({
            'success': True,
            'data': results,
            'count': len(results),
            'query': query
        }), 200
    except Exception as e:
        logger.error(f"Error searching: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# CHAT ENDPOINTS
# ============================================================================

@api_bp.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint"""
    try:
        services = _get_services()
        chat_service = services['chat']
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body must be JSON'
            }), 400
        
        message = data.get('message', '').strip()
        
        # Validate chat message
        is_valid, error_msg = ValidationService.validate_chat_message(message)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Sanitize message
        message = ValidationService.sanitize_message(message)
        
        # Get chat response
        response, articles = chat_service.get_response(message)
        
        return jsonify({
            'success': True,
            'response': response,
            'articles': articles
        }), 200
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
