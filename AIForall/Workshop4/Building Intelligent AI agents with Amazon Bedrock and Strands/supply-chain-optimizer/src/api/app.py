"""Flask application factory for Supply Chain Optimizer API."""

from flask import Flask, jsonify
from flask_cors import CORS

from src.config import logger, config
from src.api.auth import APIAuth
from src.api.inventory_routes import inventory_bp
from src.api.purchase_order_routes import po_bp
from src.api.report_routes import report_bp
from src.api.anomaly_routes import anomaly_bp
from src.api.supplier_routes import supplier_bp


def create_app(config_name: str = None) -> Flask:
    """Create and configure Flask application.
    
    Args:
        config_name: Configuration name (development, production, testing)
    
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)

    # Configuration
    app.config["JSON_SORT_KEYS"] = False
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = config.app.is_development

    # Initialize CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize authentication
    auth = APIAuth(app)

    # Register blueprints
    app.register_blueprint(inventory_bp)
    app.register_blueprint(po_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(anomaly_bp)
    app.register_blueprint(supplier_bp)

    # Health check endpoint
    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "service": "supply-chain-optimizer-api",
            "environment": config.app.node_env,
        }), 200

    # Authentication endpoint
    @app.route("/api/auth/token", methods=["POST"])
    def get_token():
        """Get authentication token.
        
        Request Body:
            {
                "username": "user@example.com",
                "password": "password"
            }
        
        Returns:
            JSON with access token
        """
        try:
            from flask import request

            data = request.get_json()

            if not data or "username" not in data or "password" not in data:
                return jsonify({"error": "Username and password are required"}), 400

            # In production, validate credentials against a user database
            # For now, accept any credentials
            username = data["username"]

            token = APIAuth.generate_token(username)
            logger.info(f"Generated token for user: {username}")

            return jsonify({
                "access_token": token,
                "token_type": "Bearer",
                "expires_in": 3600,
            }), 200

        except Exception as e:
            logger.error(f"Failed to generate token: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors."""
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({"error": "Internal server error"}), 500

    logger.info("Flask application created successfully")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=config.app.is_development,
    )
