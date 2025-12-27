"""
Main routes - Web pages and general routes
"""
import logging
from flask import Blueprint, render_template, abort
from services.data_service import get_data_service

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage"""
    logger.info("Homepage accessed")
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """About page"""
    logger.info("About page accessed")
    return render_template('about.html')

@main_bp.route('/categories')
def categories_list():
    """Categories listing page"""
    try:
        data_service = get_data_service()
        if not data_service.articles:
            data_service.load_all_data()
        
        from services.category_service import CategoryService
        category_service = CategoryService(data_service)
        categories = category_service.get_all_categories()
        
        logger.info("Categories listing page accessed")
        return render_template('categories.html', categories=categories)
    except Exception as e:
        logger.error(f"Error loading categories: {str(e)}")
        abort(500)

@main_bp.route('/categories/<category_id>')
def category_detail(category_id):
    """Category detail page"""
    try:
        data_service = get_data_service()
        if not data_service.articles:
            data_service.load_all_data()
        
        from services.category_service import CategoryService
        category_service = CategoryService(data_service)
        category = category_service.get_category(category_id)
        
        if not category:
            logger.warning(f"Category not found: {category_id}")
            abort(404)
        
        articles = category_service.get_category_articles(category_id)
        
        logger.info(f"Category detail page accessed: {category_id}")
        return render_template('category_detail.html', category=category, articles=articles)
    except Exception as e:
        logger.error(f"Error loading category: {str(e)}")
        abort(500)

@main_bp.route('/search')
def search_results():
    """Search results page"""
    try:
        from flask import request
        from services.validation_service import ValidationService
        
        query = request.args.get('q', '').strip()
        
        # Validate search query
        is_valid, error_msg = ValidationService.validate_search_query(query)
        if not is_valid:
            return render_template('search_results.html', results=[], query=query, error=error_msg)
        
        # Sanitize query
        query = ValidationService.sanitize_search_query(query)
        
        data_service = get_data_service()
        if not data_service.articles:
            data_service.load_all_data()
        
        from services.search_service import SearchService
        search_service = SearchService(data_service)
        results = search_service.search(query)
        
        logger.info(f"Search results page accessed: {query} ({len(results)} results)")
        return render_template('search_results.html', results=results, query=query)
    except Exception as e:
        logger.error(f"Error in search results: {str(e)}")
        return render_template('search_results.html', results=[], query='', error=str(e))

@main_bp.route('/articles/<article_id>')
def article_detail(article_id):
    """Article detail page"""
    try:
        data_service = get_data_service()
        if not data_service.articles:
            data_service.load_all_data()
        
        article = data_service.get_article(article_id)
        if not article:
            logger.warning(f"Article not found: {article_id}")
            return render_template('errors/404.html'), 404
        
        logger.info(f"Article detail page accessed: {article_id}")
        return render_template('article.html', article=article)
    except Exception as e:
        logger.error(f"Error loading article: {str(e)}")
        return render_template('errors/500.html'), 500

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    from datetime import datetime
    from flask import jsonify
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200
