"""
Handlers package - Contains error handlers and context processors
"""
from .error_handlers import register_error_handlers
from .context_processors import register_context_processors

__all__ = ['register_error_handlers', 'register_context_processors']
