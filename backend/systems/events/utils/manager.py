"""
EventManager
-----------
Helper utility for easier interaction with the event system.

This provides a simpler facade over the EventDispatcher singleton
with convenience methods for common operations.
"""

from typing import Any, Callable, Dict, List, Type, Optional, Set, TypeVar
import asyncio

from ..base import EventBase
from ..dispatcher import EventDispatcher

T = TypeVar('T', bound=EventBase)

class EventManager:
    """
    A convenience wrapper for working with the event system.
    
    This class provides simplified methods for publishing and subscribing
    to events, with automatic cleanup when needed. It's useful for components
    that need temporary event handling without managing dispatcher directly.
    
    Example:
        # Create manager
        manager = EventManager()
        
        # Subscribe to events
        manager.subscribe(MemoryEvent, handle_memory_event)
        
        # Publish an event
        event = MemoryEvent(...)
        manager.publish(event)
        
        # Clean up when done
        manager.cleanup()
    """
    
    def __init__(self):
        """Initialize the event manager."""
        self.dispatcher = EventDispatcher.get_instance()
        self._subscriptions = set()
    
    def subscribe(self, 
                 event_type: Type[T], 
                 handler: Callable[[T], Any], 
                 priority: int = 0) -> None:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: The event class to subscribe to
            handler: Function to call when an event occurs
            priority: Handler priority (higher executes first)
        """
        self.dispatcher.subscribe(event_type, handler, priority)
        self._subscriptions.add((event_type, handler))
    
    def unsubscribe(self, event_type: Type[T], handler: Callable) -> bool:
        """
        Unsubscribe a handler from events.
        
        Args:
            event_type: Event type to unsubscribe from
            handler: Handler to remove
            
        Returns:
            bool: True if successfully unsubscribed, False otherwise
        """
        if (event_type, handler) in self._subscriptions:
            self._subscriptions.remove((event_type, handler))
        
        return self.dispatcher.unsubscribe(event_type, handler)
    
    async def publish(self, event: EventBase) -> List[Any]:
        """
        Publish an event asynchronously.
        
        Args:
            event: The event to publish
            
        Returns:
            List of results from event handlers
        """
        return await self.dispatcher.publish(event)
    
    def publish_sync(self, event: EventBase) -> List[Any]:
        """
        Publish an event synchronously.
        
        Args:
            event: The event to publish
            
        Returns:
            List of results from event handlers
        """
        return self.dispatcher.publish_sync(event)
    
    def cleanup(self) -> None:
        """
        Remove all subscriptions registered through this manager.
        
        This is useful when a component is being destroyed and
        needs to clean up its event subscriptions to prevent memory leaks.
        """
        for event_type, handler in self._subscriptions.copy():
            self.unsubscribe(event_type, handler)
        
        self._subscriptions.clear() 