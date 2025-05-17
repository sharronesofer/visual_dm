from typing import Dict, List, Any, Optional, Set, Callable
from collections import defaultdict
import asyncio
import logging

logger = logging.getLogger('events')

class EventEmitter:
    """
    EventEmitter provides a simple event bus implementation for Python.
    
    It supports both synchronous and asynchronous event handlers, 
    allowing for pub/sub pattern in Python code.
    """
    
    def __init__(self):
        """Initialize the EventEmitter with empty handler collections."""
        self._event_handlers: Dict[str, Set[Callable]] = defaultdict(set)
        self._async_event_handlers: Dict[str, Set[Callable]] = defaultdict(set)
    
    def on(self, event: str, handler: Callable) -> None:
        """
        Register an event handler for the specified event.
        
        Args:
            event: The event name to listen for
            handler: The function to call when the event is emitted
        """
        if asyncio.iscoroutinefunction(handler):
            self._async_event_handlers[event].add(handler)
        else:
            self._event_handlers[event].add(handler)
        
        logger.debug(f"Registered handler for event '{event}'")
    
    def off(self, event: str, handler: Callable) -> None:
        """
        Remove an event handler for the specified event.
        
        Args:
            event: The event name
            handler: The handler function to remove
        """
        if asyncio.iscoroutinefunction(handler):
            if event in self._async_event_handlers:
                self._async_event_handlers[event].discard(handler)
        else:
            if event in self._event_handlers:
                self._event_handlers[event].discard(handler)
        
        logger.debug(f"Removed handler for event '{event}'")
    
    def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        """
        Emit an event, triggering all registered handlers.
        
        This method calls all synchronous handlers immediately and schedules 
        asynchronous handlers to run in the event loop.
        
        Args:
            event: The event name to emit
            *args: Arguments to pass to the event handlers
            **kwargs: Keyword arguments to pass to the event handlers
        """
        # Call synchronous handlers
        for handler in self._event_handlers.get(event, set()):
            try:
                handler(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in event handler for '{event}': {str(e)}", exc_info=True)
        
        # Schedule async handlers
        if self._async_event_handlers.get(event):
            for handler in self._async_event_handlers[event]:
                asyncio.create_task(self._call_async_handler(handler, event, *args, **kwargs))
    
    async def _call_async_handler(self, handler: Callable, event: str, *args: Any, **kwargs: Any) -> None:
        """
        Helper method to call an async handler and handle exceptions.
        
        Args:
            handler: The async handler function to call
            event: The event name (for error reporting)
            *args: Arguments to pass to the handler
            **kwargs: Keyword arguments to pass to the handler
        """
        try:
            await handler(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in async event handler for '{event}': {str(e)}", exc_info=True)
    
    async def emit_async(self, event: str, *args: Any, **kwargs: Any) -> None:
        """
        Emit an event and wait for all async handlers to complete.
        
        This is useful when you want to ensure all handlers have finished 
        processing before continuing.
        
        Args:
            event: The event name to emit
            *args: Arguments to pass to the event handlers
            **kwargs: Keyword arguments to pass to the event handlers
        """
        # Call synchronous handlers
        for handler in self._event_handlers.get(event, set()):
            try:
                handler(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in event handler for '{event}': {str(e)}", exc_info=True)
        
        # Call async handlers and wait for them to complete
        tasks = []
        for handler in self._async_event_handlers.get(event, set()):
            tasks.append(self._call_async_handler(handler, event, *args, **kwargs))
        
        if tasks:
            await asyncio.gather(*tasks)
    
    def listeners(self, event: str) -> int:
        """
        Get the number of listeners for an event.
        
        Args:
            event: The event name
            
        Returns:
            The total number of listeners (sync + async)
        """
        sync_count = len(self._event_handlers.get(event, set()))
        async_count = len(self._async_event_handlers.get(event, set()))
        return sync_count + async_count
    
    def clear(self) -> None:
        """Remove all event handlers."""
        self._event_handlers.clear()
        self._async_event_handlers.clear()
        logger.debug("Cleared all event handlers") 