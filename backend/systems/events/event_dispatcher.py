"""
Canonical EventDispatcher: Central event bus for all narrative and mechanical events in Visual DM.

This module implements the publish-subscribe pattern for loose coupling between all subsystems.
It provides both synchronous and asynchronous interfaces for maximum flexibility.

See docs/Development_Bible.md for architecture details.
"""

import asyncio
import inspect
import logging
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Type, Union, Set, TypeVar
from functools import wraps
from collections import defaultdict

from .base import EventBase, T

logger = logging.getLogger(__name__)

class EventMiddleware:
    """
    Base class for middleware that can intercept and modify events.
    
    Middleware can process events before they are dispatched (pre_dispatch),
    and/or after they are dispatched (post_dispatch). This allows for
    cross-cutting concerns like logging, analytics, and error handling.
    """
    
    async def process_async(self, event: Any) -> Any:
        """
        Process an event asynchronously.
        
        Args:
            event: The event to process
            
        Returns:
            The processed event (which may be modified)
        """
        return event
    
    def process_sync(self, event: Any) -> Any:
        """
        Process an event synchronously.
        
        Args:
            event: The event to process
            
        Returns:
            The processed event (which may be modified)
        """
        return event
        
    async def pre_dispatch(self, event: EventBase) -> Optional[EventBase]:
        """
        Process an event before dispatch.
        
        Args:
            event: The event being dispatched
            
        Returns:
            The processed event or None to cancel dispatch
        """
        return event
    
    async def post_dispatch(self, event: EventBase, success: bool) -> None:
        """
        Process after an event is dispatched.
        
        Args:
            event: The event that was dispatched
            success: Whether dispatch was successful
        """
        pass


class LoggingMiddleware(EventMiddleware):
    """Middleware that logs all events passing through the dispatcher."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize logging middleware.
        
        Args:
            logger: Logger to use, or creates one if None
        """
        self.logger = logger or logging.getLogger("event_dispatcher")
    
    async def process_async(self, event: Any) -> Any:
        """Log event asynchronously and pass it through."""
        self.logger.debug(f"Event dispatched: {event.__class__.__name__} - {event.event_type}")
        return event
    
    def process_sync(self, event: Any) -> Any:
        """Log event synchronously and pass it through."""
        self.logger.debug(f"Event dispatched: {event.__class__.__name__} - {event.event_type}")
        return event
        
    async def pre_dispatch(self, event: EventBase) -> EventBase:
        """Log event before dispatch."""
        self.logger.debug(f"Dispatching event: {event}")
        return event
    
    async def post_dispatch(self, event: EventBase, success: bool) -> None:
        """Log result after dispatch."""
        if not success:
            self.logger.warning(f"Failed to dispatch event: {event}")


class AnalyticsMiddleware(EventMiddleware):
    """Middleware that tracks events for analytics purposes."""
    
    def __init__(self, analytics_service=None):
        """
        Initialize analytics middleware.
        
        Args:
            analytics_service: Optional analytics service to use
        """
        self.analytics_service = analytics_service
    
    async def process_async(self, event: Any) -> Any:
        """Record event for analytics and pass it through."""
        if hasattr(event, "to_dict"):
            event_data = event.to_dict()
        else:
            event_data = {
                "event_type": getattr(event, "event_type", event.__class__.__name__),
                "timestamp": getattr(event, "timestamp", datetime.utcnow().isoformat())
            }
            for attr in dir(event):
                if not attr.startswith("_") and not callable(getattr(event, attr)):
                    event_data[attr] = getattr(event, attr)
        
        # If we have an analytics service, use it
        if self.analytics_service:
            await self.analytics_service.log_event_async(event_data)
        return event
    
    def process_sync(self, event: Any) -> Any:
        """Record event for analytics and pass it through."""
        if hasattr(event, "to_dict"):
            event_data = event.to_dict()
        else:
            event_data = {
                "event_type": getattr(event, "event_type", event.__class__.__name__),
                "timestamp": getattr(event, "timestamp", datetime.utcnow().isoformat())
            }
            for attr in dir(event):
                if not attr.startswith("_") and not callable(getattr(event, attr)):
                    event_data[attr] = getattr(event, attr)
        
        # If we have an analytics service, use it
        if self.analytics_service:
            self.analytics_service.log_event(event_data)
        return event


class EventDispatcher:
    """
    Singleton event dispatcher implementing the publish-subscribe pattern.
    Supports middleware, synchronous and asynchronous dispatch, prioritized
    handlers, and typed events.
    
    This is a singleton class that handles event registration,
    publication, and subscription throughout the application.
    Use EventDispatcher.get_instance() to access the canonical dispatcher.
    """
    
    _instance = None
    
    # Priority defaults
    DEFAULT_PRIORITY = 0
    HIGH_PRIORITY = 100
    MEDIUM_PRIORITY = 50
    LOW_PRIORITY = -50
    VERY_LOW_PRIORITY = -100
    
    @classmethod
    def get_instance(cls) -> 'EventDispatcher':
        """Get the singleton instance of the event dispatcher."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    @classmethod
    async def get_instance_async(cls) -> 'EventDispatcher':
        """Get the singleton instance of the event dispatcher (async version)."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the event dispatcher. Use get_instance() instead."""
        # Ensure only one instance exists
        if EventDispatcher._instance is not None:
            # Return instead of raising an exception to support non-async initialization
            return
        
        # Dictionary of event_type -> list of {handler, priority} dictionaries
        self._subscribers: Dict[Type, List[Dict[str, Any]]] = {}
        self._async_subscribers: Dict[Type, List[Dict[str, Any]]] = {}
        
        # Middleware chains
        self._middleware: List[EventMiddleware] = []
        self._async_middleware: List[EventMiddleware] = []
        
        # Event type priorities
        self._event_type_priorities: Dict[Type, int] = {}
        
        # Add default middleware
        self.add_middleware(LoggingMiddleware())
        
        # Thread safety
        self._lock = asyncio.Lock()
        
        # Set instance
        EventDispatcher._instance = self
        logger.info("EventDispatcher initialized")
    
    def add_middleware(self, middleware: EventMiddleware) -> None:
        """
        Add middleware to process events before dispatch.
        
        Args:
            middleware: Middleware to add
        """
        self._middleware.append(middleware)
        self._async_middleware.append(middleware)
        logger.debug(f"Middleware {middleware.__class__.__name__} added to dispatcher")
    
    def subscribe(self, 
                  event_type: Type, 
                  handler: Callable, 
                  priority: int = DEFAULT_PRIORITY) -> None:
        """
        Subscribe to events of a specific type with a synchronous handler.
        
        Args:
            event_type: Type of events to subscribe to
            handler: Function to call when events occur
            priority: Handler execution priority (higher = earlier)
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        # Check if handler already registered
        for subscriber in self._subscribers[event_type]:
            if subscriber["handler"] == handler:
                # Update priority if already registered
                subscriber["priority"] = priority
                # Resort the list
                self._subscribers[event_type].sort(key=lambda s: s["priority"], reverse=True)
                return
        
        # Add new handler with priority
        self._subscribers[event_type].append({
            "handler": handler,
            "priority": priority
        })
        
        # Sort by priority (highest first)
        self._subscribers[event_type].sort(key=lambda s: s["priority"], reverse=True)
        logger.debug(f"Handler {handler.__name__} subscribed to {event_type.__name__}")
    
    def subscribe_async(self, 
                       event_type: Type, 
                       handler: Callable,
                       priority: int = DEFAULT_PRIORITY) -> None:
        """
        Subscribe to events of a specific type with an asynchronous handler.
        
        Args:
            event_type: Type of events to subscribe to
            handler: Async function to call when events occur
            priority: Handler execution priority (higher = earlier)
        """
        if not inspect.iscoroutinefunction(handler):
            raise ValueError("Handler must be an async function")
        
        if event_type not in self._async_subscribers:
            self._async_subscribers[event_type] = []
        
        # Check if handler already registered
        for subscriber in self._async_subscribers[event_type]:
            if subscriber["handler"] == handler:
                # Update priority if already registered
                subscriber["priority"] = priority
                # Resort the list
                self._async_subscribers[event_type].sort(key=lambda s: s["priority"], reverse=True)
                return
        
        # Add new handler with priority
        self._async_subscribers[event_type].append({
            "handler": handler,
            "priority": priority
        })
        
        # Sort by priority (highest first)
        self._async_subscribers[event_type].sort(key=lambda s: s["priority"], reverse=True)
    
    def unsubscribe(self, event_type: Type, handler: Callable) -> bool:
        """
        Unsubscribe a handler from events of a specific type.
        
        Args:
            event_type: Type of events to unsubscribe from
            handler: Handler to remove
            
        Returns:
            bool: True if successfully unsubscribed, False otherwise
        """
        removed = False
        
        # Remove from sync subscribers
        if event_type in self._subscribers:
            original_length = len(self._subscribers[event_type])
            self._subscribers[event_type] = [
                s for s in self._subscribers[event_type] 
                if s["handler"] != handler
            ]
            if len(self._subscribers[event_type]) < original_length:
                removed = True
                
        # Also remove from async subscribers
        if event_type in self._async_subscribers:
            original_length = len(self._async_subscribers[event_type])
            self._async_subscribers[event_type] = [
                s for s in self._async_subscribers[event_type] 
                if s["handler"] != handler
            ]
            if len(self._async_subscribers[event_type]) < original_length:
                removed = True
                
        if removed:
            logger.debug(f"Handler {handler.__name__} unsubscribed from {event_type.__name__}")
            
        return removed
    
    def set_event_type_priority(self, event_type: Type, priority: int) -> None:
        """
        Set priority for a specific event type.
        
        This affects the order in which events are processed when multiple
        events are dispatched together using publish_prioritized.
        
        Args:
            event_type: The event type to prioritize
            priority: Priority value (higher = processed earlier)
        """
        self._event_type_priorities[event_type] = priority
    
    def get_event_type_priority(self, event_type: Type) -> int:
        """
        Get priority for a specific event type.
        
        Args:
            event_type: The event type to get priority for
            
        Returns:
            Priority value (default is 0 if not explicitly set)
        """
        return self._event_type_priorities.get(event_type, 0)
    
    def publish_sync(self, event: Any) -> List[Any]:
        """
        Publish an event to all subscribers synchronously.
        
        This method processes the event through middleware and then
        dispatches it to all subscribers of its type.
        
        Args:
            event: The event to publish
            
        Returns:
            List of results from all handlers
        """
        results = []
        event_type = type(event)
        
        # Apply middleware chain
        for middleware in self._middleware:
            event = middleware.process_sync(event)
            if event is None:
                # Middleware filtered out the event
                return []
        
        # Find handlers for this exact event type
        handlers = self._subscribers.get(event_type, [])
        
        # Also find handlers for any parent classes (for polymorphis)
        for registered_type, registered_handlers in self._subscribers.items():
            if registered_type != event_type and isinstance(event, registered_type):
                handlers.extend(registered_handlers)
        
        # Sort by priority
        handlers.sort(key=lambda h: h["priority"], reverse=True)
        
        # Call handlers
        for handler_info in handlers:
            try:
                result = handler_info["handler"](event)
                results.append(result)
            except Exception as e:
                logger.exception(f"Error in event handler {handler_info['handler'].__name__}: {e}")
        
        return results
    
    async def publish_async(self, event: Any) -> List[Any]:
        """
        Publish an event to all subscribers asynchronously.
        
        This method processes the event through middleware and then
        dispatches it to all async and sync subscribers of its type.
        Sync subscribers are run in a thread pool.
        
        Args:
            event: The event to publish
            
        Returns:
            List of results from all handlers
        """
        results = []
        event_type = type(event)
        success = True
        
        # Apply middleware chain (pre-dispatch)
        for middleware in self._async_middleware:
            try:
                event = await middleware.pre_dispatch(event)
                if event is None:
                    # Middleware filtered out the event
                    return []
            except Exception as e:
                logger.exception(f"Error in middleware pre_dispatch: {e}")
        
        try:
            # Find async handlers for this exact event type
            async_handlers = self._async_subscribers.get(event_type, [])
            
            # Also find async handlers for any parent classes
            for registered_type, registered_handlers in self._async_subscribers.items():
                if registered_type != event_type and isinstance(event, registered_type):
                    async_handlers.extend(registered_handlers)
            
            # Find sync handlers for this exact event type
            sync_handlers = self._subscribers.get(event_type, [])
            
            # Also find sync handlers for any parent classes
            for registered_type, registered_handlers in self._subscribers.items():
                if registered_type != event_type and isinstance(event, registered_type):
                    sync_handlers.extend(registered_handlers)
            
            # Combine and sort by priority
            all_handlers = async_handlers + sync_handlers
            all_handlers.sort(key=lambda h: h["priority"], reverse=True)
            
            # Call handlers
            for handler_info in all_handlers:
                handler = handler_info["handler"]
                try:
                    if inspect.iscoroutinefunction(handler):
                        result = await handler(event)
                    else:
                        # Run sync handler in a thread pool
                        result = await self._safe_sync_call_as_async(handler, event)
                    results.append(result)
                except Exception as e:
                    logger.exception(f"Error in event handler {handler.__name__}: {e}")
                    success = False
        except Exception as e:
            logger.exception(f"Error publishing event: {e}")
            success = False
        
        # Apply middleware chain (post-dispatch)
        for middleware in self._async_middleware:
            try:
                await middleware.post_dispatch(event, success)
            except Exception as e:
                logger.exception(f"Error in middleware post_dispatch: {e}")
        
        return results
    
    async def publish_prioritized(self, events: List[Any]) -> List[Any]:
        """
        Publish multiple events in priority order.
        
        Events are sorted by their type priority, then dispatched in sequence.
        This is useful for batch processing events with different priorities.
        
        Args:
            events: List of events to publish
            
        Returns:
            List of results, one per event
        """
        # Sort events by type priority
        events.sort(key=lambda e: self.get_event_type_priority(type(e)), reverse=True)
        
        # Publish events in sequence
        results = []
        for event in events:
            result = await self.publish_async(event)
            results.append(result)
        
        return results
    
    def publish_prioritized_sync(self, events: List[Any]) -> List[Any]:
        """
        Publish multiple events in priority order synchronously.
        
        Events are sorted by their type priority, then dispatched in sequence.
        This is useful for batch processing events with different priorities.
        
        Args:
            events: List of events to publish
            
        Returns:
            List of results, one per event
        """
        # Sort events by type priority
        events.sort(key=lambda e: self.get_event_type_priority(type(e)), reverse=True)
        
        # Publish events in sequence
        results = []
        for event in events:
            result = self.publish_sync(event)
            results.append(result)
        
        return results
    
    async def _safe_async_call(self, handler: Callable, event: Any) -> Any:
        """Safely call an async handler with exception handling."""
        try:
            return await handler(event)
        except Exception as e:
            logger.exception(f"Error in async event handler {handler.__name__}: {e}")
            return None
    
    async def _safe_sync_call_as_async(self, handler: Callable, event: Any) -> Any:
        """Safely call a sync handler from async context."""
        try:
            return handler(event)
        except Exception as e:
            logger.exception(f"Error in sync event handler {handler.__name__}: {e}")
            return None
    
    def get_all_subscribers(self) -> Dict[str, int]:
        """
        Get a summary of all registered subscribers.
        
        Returns:
            Dictionary mapping event type names to subscriber counts
        """
        result = {}
        
        # Count sync subscribers
        for event_type, handlers in self._subscribers.items():
            type_name = event_type.__name__
            if type_name not in result:
                result[type_name] = 0
            result[type_name] += len(handlers)
        
        # Count async subscribers
        for event_type, handlers in self._async_subscribers.items():
            type_name = event_type.__name__
            if type_name not in result:
                result[type_name] = 0
            result[type_name] += len(handlers)
        
        return result


# For backward compatibility
def get_dispatcher() -> EventDispatcher:
    """Convenience function to get the singleton dispatcher instance."""
    return EventDispatcher.get_instance() 