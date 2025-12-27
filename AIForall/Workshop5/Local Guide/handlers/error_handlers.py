"""
Error Handlers - Handles application errors
"""
import logging
from flask import render_template, jsonify

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """
    Register error handlers with Flask app
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        logger.warning(f"400 error: {str(error)}")
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        logger.warning(f"404 error: {error}")
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors"""
        logger.warning(f"405 error: {str(error)}")
        return jsonify({
            'success': False,
            'error': 'Method not allowed',
            'message': str(error)
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors"""
        logger.error(f"500 error: {str(error)}")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all unhandled exceptions"""
        logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
