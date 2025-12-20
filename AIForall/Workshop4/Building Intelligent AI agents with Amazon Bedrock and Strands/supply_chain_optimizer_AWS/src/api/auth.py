"""Authentication and authorization utilities for API."""

import os
from functools import wraps
from typing import Callable, Any

from flask import request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from src.config import logger


class APIAuth:
    """API authentication and authorization handler."""

    def __init__(self, app=None):
        """Initialize authentication."""
        self.app = app
        self.jwt = JWTManager()

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize JWT with Flask app."""
        app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
        app.config["JWT_ALGORITHM"] = "HS256"
        self.jwt.init_app(app)

    @staticmethod
    def generate_token(identity: str) -> str:
        """Generate JWT token for API access."""
        try:
            token = create_access_token(identity=identity)
            logger.info(f"Generated access token for identity: {identity}")
            return token
        except Exception as e:
            logger.error(f"Failed to generate token: {str(e)}")
            raise

    @staticmethod
    def require_auth(f: Callable) -> Callable:
        """Decorator to require JWT authentication."""
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs) -> Any:
            identity = get_jwt_identity()
            logger.debug(f"Authenticated request from: {identity}")
            return f(*args, **kwargs)

        return decorated_function

    @staticmethod
    def require_role(required_role: str) -> Callable:
        """Decorator to require specific role."""
        def decorator(f: Callable) -> Callable:
            @wraps(f)
            @jwt_required()
            def decorated_function(*args, **kwargs) -> Any:
                identity = get_jwt_identity()
                # In production, fetch user role from database
                # For now, we'll use a simple check
                user_role = request.headers.get("X-User-Role", "user")

                if user_role != required_role:
                    logger.warning(f"Unauthorized access attempt by {identity} with role {user_role}")
                    return jsonify({"error": "Insufficient permissions"}), 403

                return f(*args, **kwargs)

            return decorated_function

        return decorator


def validate_api_key(f: Callable) -> Callable:
    """Decorator to validate API key from header."""
    @wraps(f)
    def decorated_function(*args, **kwargs) -> Any:
        api_key = request.headers.get("X-API-Key")
        expected_key = os.getenv("API_KEY", "dev-api-key")

        if not api_key or api_key != expected_key:
            logger.warning("Invalid API key provided")
            return jsonify({"error": "Invalid API key"}), 401

        return f(*args, **kwargs)

    return decorated_function
