"""Events system - Infrastructure component for cross-cutting event concerns"""

# Auto-generated imports
from . import events
from . import models
from . import repositories
from . import routers
from . import schemas
from . import services
from . import utils

# Canonical exports for proper import resolution
from .services.event_dispatcher import EventDispatcher
from .events.canonical_events import EventBase
from .events.event_types import *

# Create EventBus wrapper for backward compatibility
class EventBus:
    """
    Event bus wrapper around EventDispatcher for simpler string-based events.
    Provides backward compatibility for systems expecting this interface.
    """
    
    def __init__(self):
        self._dispatcher = EventDispatcher.get_instance()
    
    def subscribe(self, event_name: str, handler):
        """Subscribe to an event by name."""
        return self._dispatcher.subscribe(event_name, handler)
    
    def publish(self, event_name: str, data: dict = None):
        """Publish an event by name with data."""
        # Create a simple event object
        class SimpleEvent(EventBase):
            def __init__(self, event_type: str, data: dict = None):
                super().__init__()
                self.event_type = event_type
                self.data = data or {}
        
        event = SimpleEvent(event_name, data)
        return self._dispatcher.publish_sync(event)
    
    def unsubscribe(self, event_name: str, handler):
        """Unsubscribe from an event by name."""
        return self._dispatcher.unsubscribe(event_name, handler)

# Export key components for canonical imports
__all__ = [
    "EventDispatcher", 
    "EventBus",
    "EventBase",
    "EventHandler",
    "events",
    "models", 
    "repositories",
    "routers",
    "schemas", 
    "services",
    "utils"
]

# Backward compatibility for systems expecting the old import path
event_dispatcher = EventDispatcher

# Add EventHandler alias for backward compatibility
EventHandler = EventBase

# Global event bus instance
_event_bus_instance = None

def get_event_bus() -> EventBus:
    """Get or create the global event bus instance."""
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus()
    return _event_bus_instance
