"""
Canonical EventDispatcher: Central event bus for all narrative and mechanical events in Visual DM.

This module implements the publish-subscribe pattern for loose coupling between all subsystems.
It provides both synchronous and asynchronous interfaces for maximum flexibility.

See docs/Development_Bible.md for architecture details.
"""
from typing import Any, Callable, Dict, List, Type, Optional, Union, TypeVar
import asyncio
import inspect
import logging
import time
from collections import defaultdict

from .base import EventBase, T
from .event_types import EventType

logger = logging.getLogger(__name__)

class EventMiddleware:
    """Base class for event middleware components."""
    
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
    
    def __str__(self) -> str:
        return self.__class__.__name__


class LoggingMiddleware(EventMiddleware):
    """Middleware that logs all events dispatched."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    async def pre_dispatch(self, event: EventBase) -> EventBase:
        """Log event before dispatch."""
        self.logger.debug(f"Dispatching event: {event}")
        return event
    
    async def post_dispatch(self, event: EventBase, success: bool) -> None:
        """Log result after dispatch."""
        if not success:
            self.logger.warning(f"Failed to dispatch event: {event}")


class AsyncEventHandler:
    """Wrapper for event handlers with metadata."""
    
    def __init__(self, 
                 handler: Callable, 
                 once: bool = False, 
                 priority: int = 0):
        """
        Initialize a new event handler.
        
        Args:
            handler: The handler function
            once: If True, remove after first execution
            priority: Handler priority (higher = executed earlier)
        """
        self.handler = handler
        self.once = once
        self.priority = priority
    
    def __eq__(self, other):
        if isinstance(other, AsyncEventHandler):
            return self.handler == other.handler
        return False
    
    async def __call__(self, event: EventBase) -> None:
        """Call the handler with the event."""
        await self.handler(event)


class EventDispatcher:
    """
    Central event dispatcher using a publish-subscribe model.
    
    This is a singleton class that handles event registration,
    publication, and subscription throughout the application.
    Use EventDispatcher.get_instance() to access the canonical dispatcher.
    
    Example:
        # Subscribe to an event
        dispatcher = EventDispatcher.get_instance()
        dispatcher.subscribe(UserLoggedInEvent, handle_user_login)
        
        # Publish an event
        event = UserLoggedInEvent(event_type="user.login", user_id="123")
        await dispatcher.publish(event)
    """
    _instance = None
    _lock = asyncio.Lock()
    
    @classmethod
    async def get_instance_async(cls):
        """Get the canonical singleton instance of the event dispatcher (async version)."""
        async with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance
        
    @classmethod
    def get_instance(cls):
        """Get the canonical singleton instance of the event dispatcher."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the event dispatcher (use get_instance() instead)."""
        if EventDispatcher._instance is not None:
            # Return the existing instance if already initialized
            return
            
        self._subscribers = {}
        self._middlewares = []
        EventDispatcher._instance = self
        logger.info("EventDispatcher initialized")
    
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
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
            
        self._subscribers[event_type].append({
            'handler': handler, 
            'priority': priority
        })
        
        # Sort by priority (descending)
        self._subscribers[event_type].sort(
            key=lambda x: x['priority'], reverse=True
        )
        
        logger.debug(f"Handler {handler.__name__} subscribed to {event_type.__name__}")
    
    def unsubscribe(self, 
                   event_type: Type[EventBase], 
                   handler: Callable) -> bool:
        """
        Remove a handler subscription.
        
        Args:
            event_type: The event class to unsubscribe from
            handler: The handler to remove
            
        Returns:
            bool: True if successfully unsubscribed, False otherwise
        """
        if event_type in self._subscribers:
            for idx, subscriber in enumerate(self._subscribers[event_type]):
                if subscriber['handler'] == handler:
                    self._subscribers[event_type].pop(idx)
                    logger.debug(f"Handler {handler.__name__} unsubscribed from {event_type.__name__}")
                    return True
        return False
        
    def add_middleware(self, middleware: Callable[[EventBase, Callable], Any]) -> None:
        """
        Add middleware to process events before dispatching.
        
        Middleware should be a callable with the signature:
            async def middleware(event, next_middleware)
        
        Args:
            middleware: Function taking (event, next) parameters
        """
        self._middlewares.append(middleware)
        logger.debug(f"Middleware {middleware.__name__} added to dispatcher")
    
    async def publish(self, event: EventBase) -> List[Any]:
        """
        Publish an event to all subscribers asynchronously.
        
        Args:
            event: The event to publish
            
        Returns:
            List of results from all handlers
        """
        event_type = type(event)
        results = []
        
        # Apply middlewares chain
        async def process_event(event, middleware_index=0):
            if middleware_index < len(self._middlewares):
                result = await self._middlewares[middleware_index](
                    event, 
                    lambda evt: process_event(evt, middleware_index + 1)
                )
                # If middleware returns None, it means event was filtered out
                if result is None:
                    return []
                return result
            else:
                # Find handlers for this exact event type
                exact_handlers = self._subscribers.get(event_type, [])
                
                # Also find handlers for any parent classes
                parent_handlers = []
                for registered_type, handlers in self._subscribers.items():
                    # Check if event is instance of this registered type, but not the exact type
                    if registered_type != event_type and isinstance(event, registered_type):
                        parent_handlers.extend(handlers)
                
                # Sort combined handlers by priority
                all_handlers = exact_handlers + parent_handlers
                all_handlers.sort(key=lambda x: x['priority'], reverse=True)
                
                for subscriber in all_handlers:
                    handler = subscriber['handler']
                    try:
                        if inspect.iscoroutinefunction(handler):
                            result = await handler(event)
                        else:
                            result = handler(event)
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Error in event handler {handler.__name__}: {e}")
                        # Error logging is handled by error_handling_middleware
                return results
                
        logger.debug(f"Publishing event of type {event_type.__name__}")
        return await process_event(event)
        
    def publish_sync(self, event: EventBase) -> List[Any]:
        """
        Synchronous version of publish for non-async contexts.
        
        Args:
            event: The event to publish
            
        Returns:
            List of results from all handlers
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If there's no event loop in this thread, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        try:
            return loop.run_until_complete(self.publish(event))
        except Exception as e:
            logger.error(f"Error in publish_sync: {e}")
            # Return empty results on error
            return [] 