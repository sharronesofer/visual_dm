"""
Event system middleware components for Visual DM.

This module provides middleware components that can be added to the EventDispatcher
to process events before they are sent to handlers.
"""

# Import middleware functions/components that actually exist
from .logging_middleware import logging_middleware
from .error_handler import handle_component_error, ErrorSeverity
from .error_middleware import error_handling_middleware as error_middleware
from .analytics_middleware import analytics_middleware
from .debugging_middleware import debug_middleware

# Import classes from files that have them
from .analytics import AnalyticsService

__all__ = [
    # Middleware functions
    'logging_middleware',
    'error_handling_middleware', 
    'error_middleware',
    'analytics_middleware',
    'debug_middleware',
    
    # Middleware classes
    'AnalyticsService',
    
    # Error handling
    'handle_component_error',
    'ErrorSeverity',
]
