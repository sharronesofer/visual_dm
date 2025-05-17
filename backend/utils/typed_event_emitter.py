import asyncio
import json
import logging
from typing import Any, Callable, Dict, Set
from datetime import datetime

# Configure logger
logger = logging.getLogger('event_bus')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [EVENT_BUS] %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

EventHandler = Callable[[Any], None]
AsyncEventHandler = Callable[[Any], asyncio.coroutine]

class EventBus:
    """An event bus implementation for Python backends, supporting both sync and async handlers."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'EventBus':
        """Get the singleton instance of EventBus"""
        if cls._instance is None:
            cls._instance = EventBus()
        return cls._instance
    
    def __init__(self):
        """Initialize a new EventBus"""
        self.listeners: Dict[str, Set[EventHandler]] = {}
        self.async_listeners: Dict[str, Set[AsyncEventHandler]] = {}
    
    def emit(self, event_type: str, payload: Any) -> None:
        """Emit an event synchronously to all registered handlers"""
        logger.info(f"Emitting event: {event_type} with payload: {json.dumps(payload, default=str)}")
        
        handlers = self.listeners.get(event_type, set())
        for handler in handlers:
            try:
                handler(payload)
            except Exception as e:
                logger.error(f"Error in handler for event {event_type}: {e}")
    
    async def emit_async(self, event_type: str, payload: Any) -> None:
        """Emit an event asynchronously to all registered handlers"""
        logger.info(f"Emitting async event: {event_type} with payload: {json.dumps(payload, default=str)}")
        
        # Process synchronous handlers in a non-blocking way
        sync_handlers = self.listeners.get(event_type, set())
        for handler in sync_handlers:
            try:
                asyncio.create_task(asyncio.to_thread(handler, payload))
            except Exception as e:
                logger.error(f"Error in sync handler for async event {event_type}: {e}")
        
        # Process async handlers
        async_handlers = self.async_listeners.get(event_type, set())
        for handler in async_handlers:
            try:
                asyncio.create_task(handler(payload))
            except Exception as e:
                logger.error(f"Error in async handler for event {event_type}: {e}")
    
    def on(self, event_type: str, handler: EventHandler) -> None:
        """Register a synchronous event handler"""
        logger.info(f"Registering handler for event: {event_type}")
        if event_type not in self.listeners:
            self.listeners[event_type] = set()
        self.listeners[event_type].add(handler)
    
    def on_async(self, event_type: str, handler: AsyncEventHandler) -> None:
        """Register an asynchronous event handler"""
        logger.info(f"Registering async handler for event: {event_type}")
        if event_type not in self.async_listeners:
            self.async_listeners[event_type] = set()
        self.async_listeners[event_type].add(handler)
    
    def off(self, event_type: str, handler: EventHandler) -> None:
        """Unregister a synchronous event handler"""
        logger.info(f"Unregistering handler for event: {event_type}")
        if event_type in self.listeners and handler in self.listeners[event_type]:
            self.listeners[event_type].remove(handler)
    
    def off_async(self, event_type: str, handler: AsyncEventHandler) -> None:
        """Unregister an asynchronous event handler"""
        logger.info(f"Unregistering async handler for event: {event_type}")
        if event_type in self.async_listeners and handler in self.async_listeners[event_type]:
            self.async_listeners[event_type].remove(handler)

# Singleton instance for app-wide use
event_bus = EventBus.get_instance() 