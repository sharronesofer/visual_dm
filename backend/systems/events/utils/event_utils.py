"""
Event management utilities.

This module provides helper classes and functions for working with
the event system, including registration helpers, event generation,
and convenience methods.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
import time

from ..core.event_base import EventBase
from ..core.event_dispatcher import EventDispatcher

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=EventBase)

class EventManager:
    """
    Helper utility for working with the event system.
    
    This class provides convenience methods for registering event
    handlers, publishing events, and managing subscriptions.
    
    Example:
        # Create an event manager
        event_manager = EventManager()
        
        # Register handlers
        event_manager.subscribe(MemoryEvent, handle_memory_event)
        
        # Publish events
        event_manager.publish(MemoryEvent(event_type="memory:created", ...))
    """
    
    def __init__(self):
        """Initialize with the global event dispatcher."""
        self.dispatcher = EventDispatcher.get_instance()
        self._subscriptions = {}  # Keep track of subscriptions for cleanup
    
    def subscribe(self, 
                 event_type: Type[T], 
                 handler: Callable[[T], Any],
                 priority: int = 0) -> None:
        """
        Register a handler for a specific event type.
        
        Args:
            event_type: The event class to subscribe to
            handler: Callback function to handle the event
            priority: Execution priority (higher executes first)
        """
        self.dispatcher.subscribe(event_type, handler, priority)
        
        # Track this subscription for cleanup
        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = []
        self._subscriptions[event_type].append(handler)
        
        logger.debug(f"Registered handler for {event_type.__name__}")
    
    def unsubscribe(self, 
                   event_type: Type[EventBase], 
                   handler: Callable) -> bool:
        """
        Remove a handler subscription.
        
        Args:
            event_type: The event class to unsubscribe from
            handler: The handler to remove
            
        Returns:
            True if successfully unsubscribed, False otherwise
        """
        result = self.dispatcher.unsubscribe(event_type, handler)
        
        # Remove from our tracking
        if result and event_type in self._subscriptions:
            if handler in self._subscriptions[event_type]:
                self._subscriptions[event_type].remove(handler)
                
                # Clean up empty lists
                if not self._subscriptions[event_type]:
                    del self._subscriptions[event_type]
        
        return result
    
    def publish(self, event: EventBase) -> List[Any]:
        """
        Publish an event to all subscribers.
        
        This is a synchronous method that will block until all handlers
        have processed the event.
        
        Args:
            event: The event to publish
            
        Returns:
            List of results from all handlers
        """
        return self.dispatcher.publish_sync(event)
    
    async def publish_async(self, event: EventBase) -> List[Any]:
        """
        Publish an event to all subscribers asynchronously.
        
        Args:
            event: The event to publish
            
        Returns:
            List of results from all handlers
        """
        return await self.dispatcher.publish(event)
    
    def cleanup(self) -> None:
        """
        Unsubscribe all handlers registered through this manager.
        
        Call this method when you're done with the EventManager to avoid
        memory leaks from dangling event handlers.
        """
        for event_type, handlers in self._subscriptions.items():
            for handler in handlers:
                self.dispatcher.unsubscribe(event_type, handler)
        
        self._subscriptions.clear()
        logger.debug("Cleaned up all event subscriptions")
        
    def __del__(self):
        """Automatically cleanup when destroyed."""
        try:
            self.cleanup()
        except:
            # Ignore errors during destruction
            pass 