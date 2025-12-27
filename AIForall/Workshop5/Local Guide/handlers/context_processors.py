"""
Context Processors - Injects data into templates
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def register_context_processors(app):
    """
    Register context processors with Flask app
    
    Args:
        app: Flask application instance
    """
    
    @app.context_processor
    def inject_app_info():
        """Inject application information into templates"""
        return {
            'app_name': 'Pune Knowledge Base',
            'app_version': '1.0.0',
            'current_year': datetime.now().year,
            'app_description': 'Your comprehensive guide to Pune'
        }
    
    @app.context_processor
    def inject_datetime():
        """Inject datetime utilities into templates"""
        return {
            'now': datetime.now(),
            'current_date': datetime.now().strftime('%Y-%m-%d'),
            'current_time': datetime.now().strftime('%H:%M:%S')
        }
