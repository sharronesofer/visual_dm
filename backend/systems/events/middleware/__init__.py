"""
Event system middleware components for Visual DM.

This module provides middleware components that can be added to the EventDispatcher
to process events before they are sent to handlers.
"""

# Import middleware components
from .logging import LoggingMiddleware, logging_middleware
from .error_handler import ErrorHandlingMiddleware, error_handling_middleware
from .analytics import AnalyticsMiddleware, analytics_middleware
from .debugging import DebugMiddleware, debug_middleware

# Backward compatibility for older filenames
from .logging_middleware import LoggingMiddleware as LoggingMiddlewareLegacy
from .error_middleware import ErrorHandlingMiddleware as ErrorHandlingMiddlewareLegacy
from .analytics_middleware import AnalyticsMiddleware as AnalyticsMiddlewareLegacy
from .debugging_middleware import DebugMiddleware as DebugMiddlewareLegacy

__all__ = [
    # Modern middleware classes
    'LoggingMiddleware',
    'ErrorHandlingMiddleware',
    'AnalyticsMiddleware',
    'DebugMiddleware',
    
    # Singleton instances
    'logging_middleware',
    'error_handling_middleware',
    'analytics_middleware',
    'debug_middleware',
    
    # Legacy middleware classes
    'LoggingMiddlewareLegacy',
    'ErrorHandlingMiddlewareLegacy',
    'AnalyticsMiddlewareLegacy',
    'DebugMiddlewareLegacy',
]
