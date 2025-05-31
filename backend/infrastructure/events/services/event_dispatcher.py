"""
Canonical EventDispatcher: Central event bus for all narrative and mechanical events in Visual DM.
Implements the publish-subscribe pattern for loose coupling between all subsystems.
See docs/Development_Bible.md for architecture details.
"""
from typing import Any, Callable, Dict, List, Type, Optional, Union, TypeVar
import asyncio
import inspect
import logging
import time
from pydantic import BaseModel, Field, ConfigDict
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='EventBase')

class EventBase(BaseModel):
    """
    Base class for all event types in the system.
    
    All events must inherit from this class to ensure consistency and
    to provide common functionality.
    """
    event_type: str
    timestamp: float = Field(default_factory=time.time)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class EventDispatcher:
    """
    Central event dispatcher for the application.
    Implements the Singleton pattern to ensure a single event bus.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the EventDispatcher"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the event dispatcher"""
        if EventDispatcher._instance is not None:
            raise RuntimeError("EventDispatcher is a singleton. Use get_instance() instead.")
            
        EventDispatcher._instance = self
        self._subscribers: Dict[str, List[Callable]] = {}
        self._async_subscribers: Dict[str, List[Callable]] = {}
        
    def subscribe(self, event_type: str, callback: Callable):
        """
        Subscribe to a specific event type with a synchronous callback.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event is dispatched
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type} events")
        
    def unsubscribe(self, event_type: str, callback: Callable) -> bool:
        """
        Unsubscribe from a specific event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Function to unsubscribe
            
        Returns:
            True if unsubscribed successfully, False otherwise
        """
        if event_type not in self._subscribers:
            return False
            
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
            logger.debug(f"Unsubscribed from {event_type} events")
            return True
            
        return False
        
    def subscribe_async(self, event_type: str, callback: Callable):
        """
        Subscribe to a specific event type with an asynchronous callback.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Async function to call when event is dispatched
        """
        if event_type not in self._async_subscribers:
            self._async_subscribers[event_type] = []
            
        self._async_subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type} events (async)")
        
    def unsubscribe_async(self, event_type: str, callback: Callable) -> bool:
        """
        Unsubscribe an async function from a specific event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Async function to unsubscribe
            
        Returns:
            True if unsubscribed successfully, False otherwise
        """
        if event_type not in self._async_subscribers:
            return False
            
        if callback in self._async_subscribers[event_type]:
            self._async_subscribers[event_type].remove(callback)
            logger.debug(f"Unsubscribed from {event_type} events (async)")
            return True
            
        return False
        
    def publish_sync(self, event: EventBase):
        """
        Publish an event synchronously to all subscribers.
        
        Args:
            event: Event object to publish
        """
        event_type = event.event_type
        
        # Call all synchronous subscribers
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {str(e)}")
        
        # Schedule async subscribers to run in a separate task
        if event_type in self._async_subscribers and self._async_subscribers[event_type]:
            asyncio.create_task(self._publish_async(event))
    
    async def publish(self, event: EventBase):
        """
        Publish an event asynchronously to all subscribers.
        
        Args:
            event: Event object to publish
        """
        event_type = event.event_type
        
        # Call synchronous subscribers
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {str(e)}")
        
        # Call asynchronous subscribers
        await self._publish_async(event)
    
    async def _publish_async(self, event: EventBase):
        """
        Internal method to publish event to async subscribers.
        
        Args:
            event: Event object to publish
        """
        event_type = event.event_type
        
        if event_type not in self._async_subscribers:
            return
            
        # Create tasks for all async subscribers
        tasks = []
        for callback in self._async_subscribers[event_type]:
            try:
                task = asyncio.create_task(callback(event))
                tasks.append(task)
            except Exception as e:
                logger.error(f"Error in async event handler for {event_type}: {str(e)}")
                
        # Wait for all tasks to complete if there are any
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

def event_subscriber(event_type: str):
    """
    Decorator for event subscribers.
    
    Usage:
        @event_subscriber("character_created")
        def handle_character_created(event):
            # Process event
    
    Args:
        event_type: Type of event to subscribe to
        
    Returns:
        Decorator function
    """
    def decorator(func):
        EventDispatcher.get_instance().subscribe(event_type, func)
        return func
    return decorator
    
def async_event_subscriber(event_type: str):
    """
    Decorator for async event subscribers.
    
    Usage:
        @async_event_subscriber("character_created")
        async def handle_character_created(event):
            # Process event asynchronously
    
    Args:
        event_type: Type of event to subscribe to
        
    Returns:
        Decorator function
    """
    def decorator(func):
        EventDispatcher.get_instance().subscribe_async(event_type, func)
        return func
    return decorator

# Commonly used middleware
async def logging_middleware(event: EventBase, next_middleware: Callable):
    """
    Middleware to log all events passing through the dispatcher.
    
    Args:
        event: The event being dispatched
        next_middleware: Function to call the next middleware
        
    Returns:
        Results from subsequent middlewares and handlers
    """
    logger.info(f"Event dispatched: {event.event_type}")
    return await next_middleware(event)


async def error_handling_middleware(event: EventBase, next_middleware: Callable):
    """
    Middleware to catch and log errors during event processing.
    
    Args:
        event: The event being dispatched
        next_middleware: Function to call the next middleware
        
    Returns:
        Results from subsequent middlewares and handlers
    """
    try:
        return await next_middleware(event)
    except Exception as e:
        logger.error(f"Error processing event {event.event_type}: {str(e)}")
        # Optionally, could re-raise or transform the error
        raise 
