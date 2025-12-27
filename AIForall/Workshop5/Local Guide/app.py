"""
Pune Local Intelligence Knowledge Base - Main Flask Application
"""
import os
import logging
from flask import Flask
from datetime import datetime
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """
    Application factory function
    
    Args:
        config_name: Configuration name (development, testing, production)
        
    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config.get(config_name, config['development']))
    
    logger.info(f"Flask app initialized with {config_name} configuration")
    
    # Register blueprints
    from routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register error handlers
    from handlers import register_error_handlers
    register_error_handlers(app)
    
    # Register context processors
    from handlers import register_context_processors
    register_context_processors(app)
    
    # Initialize data service
    from services.data_service import get_data_service
    with app.app_context():
        data_service = get_data_service()
        if not data_service.load_all_data():
            logger.warning("Failed to load knowledge base data")
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    logger.info("Starting Pune Knowledge Base application")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
