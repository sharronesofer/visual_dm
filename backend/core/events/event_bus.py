"""
Event Bus implementation for component communication.

This module provides an event-based communication system with support for:
- Type-safe event publishing and subscribing
- Async event handling
- Event filtering and prioritization
- Pydantic model support for structured events
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, Generic, List, Optional, Set, TypeVar, Union
from enum import Enum
from pydantic import BaseModel
from weakref import WeakMethod, ref

# Define a type variable for generic event types
T = TypeVar('T')

# Configure logging
logger = logging.getLogger(__name__)

class EventPriority(Enum):
    """Priority levels for event handlers."""
    HIGH = 0
    NORMAL = 1
    LOW = 2
    BACKGROUND = 3

class EventHandler(Generic[T]):
    """Event handler with priority and filtering support."""
    
    def __init__(
        self, 
        callback: Callable[[T], Any], 
        priority: EventPriority = EventPriority.NORMAL,
        filter_func: Optional[Callable[[T], bool]] = None
    ):
        """
        Initialize a new event handler.
        
        Args:
            callback: Function to call when event occurs
            priority: Handler priority (lower values = higher priority)
            filter_func: Optional function to filter events
        """
        # Store callback, handling methods specially to avoid memory leaks
        if hasattr(callback, '__self__') and not isinstance(callback.__self__, type):
            # For bound methods, store a weak reference
            self._weak_callback = WeakMethod(callback)
            self._callback = None
        else:
            # For static methods, functions, or lambdas, store directly
            self._callback = callback
            self._weak_callback = None
            
        self.priority = priority
        self.filter_func = filter_func
        
    def __eq__(self, other):
        """Compare two handlers for equality, used for unsubscribing."""
        if not isinstance(other, EventHandler):
            return False
            
        # Check if callbacks match
        if self._callback and other._callback:
            return self._callback == other._callback
            
        if self._weak_callback and other._weak_callback:
            return (self._weak_callback() == other._weak_callback() and 
                    self._weak_callback() is not None)
                    
        return False
        
    def __call__(self, event: T) -> bool:
        """
        Invoke the handler with the event.
        
        Args:
            event: The event to handle
            
        Returns:
            bool: True if callback was called, False otherwise
        """
        # Check filter first
        if self.filter_func and not self.filter_func(event):
            return False
            
        # Get the actual callback
        callback = self._callback
        if self._weak_callback:
            callback = self._weak_callback()
            if callback is None:
                # Reference has been garbage collected
                return False
                
        try:
            callback(event)
            return True
        except Exception as e:
            logger.error(f"Error in event handler: {e}", exc_info=True)
            return False

class EventBus:
    """
    Event bus for publisher-subscriber communication with type safety.
    
    Supports:
    - Type-safe event subscription and publishing
    - Prioritized event handling
    - Event filtering
    - Asynchronous events
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of EventBus."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize a new EventBus."""
        self._handlers: Dict[Any, List[EventHandler]] = {}
        self._async_handlers: Dict[Any, List[EventHandler]] = {}
        
    def subscribe(
        self, 
        event_type: Any, 
        handler: Callable[[T], Any],
        priority: EventPriority = EventPriority.NORMAL,
        filter_func: Optional[Callable[[T], bool]] = None
    ) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to (string or class)
            handler: Function to call when event occurs
            priority: Handler priority (lower values = higher priority)
            filter_func: Optional function to filter events
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
            
        event_handler = EventHandler(handler, priority, filter_func)
        self._handlers[event_type].append(event_handler)
        
        # Sort handlers by priority
        self._handlers[event_type].sort(key=lambda h: h.priority.value)
        
        logger.debug(f"Subscribed to {event_type} with priority {priority}")
        
    def subscribe_async(
        self, 
        event_type: Any, 
        handler: Callable[[T], Any],
        priority: EventPriority = EventPriority.NORMAL,
        filter_func: Optional[Callable[[T], bool]] = None
    ) -> None:
        """
        Subscribe to an event type with an async handler.
        
        Args:
            event_type: Type of event to subscribe to (string or class)
            handler: Async function to call when event occurs
            priority: Handler priority (lower values = higher priority)
            filter_func: Optional function to filter events
        """
        if event_type not in self._async_handlers:
            self._async_handlers[event_type] = []
            
        event_handler = EventHandler(handler, priority, filter_func)
        self._async_handlers[event_type].append(event_handler)
        
        # Sort handlers by priority
        self._async_handlers[event_type].sort(key=lambda h: h.priority.value)
        
        logger.debug(f"Subscribed async handler to {event_type} with priority {priority}")
        
    def unsubscribe(self, event_type: Any, handler: Callable[[T], Any]) -> bool:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler function to remove
            
        Returns:
            bool: True if handler was removed, False otherwise
        """
        if event_type not in self._handlers:
            return False
            
        # Create a test handler for comparison
        test_handler = EventHandler(handler)
        
        # Find and remove the handler
        original_count = len(self._handlers[event_type])
        self._handlers[event_type] = [
            h for h in self._handlers[event_type] if h != test_handler
        ]
        
        # Clean up empty lists
        if not self._handlers[event_type]:
            del self._handlers[event_type]
            
        # Return True if we removed something
        return len(self._handlers.get(event_type, [])) < original_count
        
    def unsubscribe_async(self, event_type: Any, handler: Callable[[T], Any]) -> bool:
        """
        Unsubscribe an async handler from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Async handler function to remove
            
        Returns:
            bool: True if handler was removed, False otherwise
        """
        if event_type not in self._async_handlers:
            return False
            
        # Create a test handler for comparison
        test_handler = EventHandler(handler)
        
        # Find and remove the handler
        original_count = len(self._async_handlers[event_type])
        self._async_handlers[event_type] = [
            h for h in self._async_handlers[event_type] if h != test_handler
        ]
        
        # Clean up empty lists
        if not self._async_handlers[event_type]:
            del self._async_handlers[event_type]
            
        # Return True if we removed something
        return len(self._async_handlers.get(event_type, [])) < original_count
    
    def emit(self, event_type: Any, event: T) -> None:
        """
        Emit an event to all subscribers.
        
        Args:
            event_type: Type of the event (string or class)
            event: The event data to emit
        """
        logger.debug(f"Emitting event: {event_type}")
        
        # Process synchronous handlers
        if event_type in self._handlers:
            # Make a copy to avoid issues if handlers are added/removed during iteration
            handlers = self._handlers[event_type].copy()
            
            for handler in handlers:
                handler(event)
                
        # Process asynchronous handlers in the background
        if event_type in self._async_handlers:
            asyncio.create_task(self._process_async_handlers(event_type, event))
    
    async def emit_async(self, event_type: Any, event: T) -> None:
        """
        Emit an event and wait for all async handlers to complete.
        
        Args:
            event_type: Type of the event (string or class)
            event: The event data to emit
        """
        logger.debug(f"Emitting async event: {event_type}")
        
        # Process synchronous handlers
        if event_type in self._handlers:
            handlers = self._handlers[event_type].copy()
            
            for handler in handlers:
                handler(event)
        
        # Process and await async handlers
        if event_type in self._async_handlers:
            await self._process_async_handlers(event_type, event)
    
    async def _process_async_handlers(self, event_type: Any, event: T) -> None:
        """
        Process all async handlers for an event.
        
        Args:
            event_type: Type of the event
            event: The event data
        """
        if event_type not in self._async_handlers:
            return
            
        handlers = self._async_handlers[event_type].copy()
        tasks = []
        
        for handler in handlers:
            callback = handler._callback
            if handler._weak_callback:
                callback = handler._weak_callback()
                if callback is None:
                    continue
            
            # Only process if filter passes
            if handler.filter_func and not handler.filter_func(event):
                continue
                
            try:
                # Create a task for each async handler
                task = asyncio.create_task(callback(event))
                tasks.append(task)
            except Exception as e:
                logger.error(f"Error creating task for async handler: {e}", exc_info=True)
        
        # Wait for all tasks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

# Create a singleton instance
event_bus = EventBus.get_instance() 