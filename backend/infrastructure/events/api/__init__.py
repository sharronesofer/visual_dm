"""
Event System API Package
-----------------------
Provides REST APIs for the event system components.
"""

from backend.infrastructure.events.plugin_api import router as plugin_router

__all__ = ["plugin_router"] 