"""
Error handling middleware for the event system.

This module provides middleware for error handling during event processing,
implementing the error handling mechanisms described in the Development Bible.
"""
import logging
import traceback
from typing import Any, Callable, Dict, Optional

from .event_dispatcher import EventBase
from .canonical_events import SystemEvent, SystemEventType

logger = logging.getLogger(__name__)

async def error_handling_middleware(event: EventBase, next_middleware: Callable):
    """
    Middleware to catch and handle errors during event processing.
    
    This middleware wraps the event processing chain in a try-except block
    to catch and handle any exceptions that occur during event handling.
    It logs the error, publishes a system error event, and allows the
    event processing to continue for other handlers.
    
    Args:
        event: The event being dispatched
        next_middleware: Function to call the next middleware
        
    Returns:
        Results from subsequent middlewares and handlers, or empty list on error
    """
    try:
        # Try to process the event normally
        return await next_middleware(event)
    except Exception as e:
        # Log the error
        error_message = f"Error processing event {type(event).__name__}: {str(e)}"
        stack_trace = traceback.format_exc()
        logger.error(f"{error_message}\n{stack_trace}")
        
        # Create error details
        error_details = {
            "error": str(e),
            "error_type": type(e).__name__,
            "event_type": type(event).__name__,
            "event_data": event.dict(),
            "stack_trace": stack_trace.split('\n'),
        }
        
        try:
            # Attempt to publish an error event
            # Import here to avoid circular imports
            from .event_factory import get_event_factory
            
            # Get the event factory
            event_factory = get_event_factory()
            
            # Create and publish an error event (don't wait for it)
            # Using create_and_publish_sync to avoid asyncio issues
            event_factory.system_event_sync(
                event_type=SystemEventType.ERROR,
                component="event_system",
                details=error_details
            )
        except Exception as publish_error:
            # If we can't publish the error event, just log it
            logger.error(f"Failed to publish error event: {str(publish_error)}")
        
        # Return empty results
        return []

def capture_and_report_error(func):
    """
    Decorator to capture and report errors from event handlers.
    
    This decorator wraps an event handler function in a try-except block,
    logging and reporting any errors that occur but allowing the event
    processing to continue.
    
    Args:
        func: The event handler function to wrap
        
    Returns:
        Wrapped function
    """
    async def wrapper(event, *args, **kwargs):
        try:
            return await func(event, *args, **kwargs)
        except Exception as e:
            # Log the error
            error_message = f"Error in event handler {func.__name__}: {str(e)}"
            stack_trace = traceback.format_exc()
            logger.error(f"{error_message}\n{stack_trace}")
            
            # Create error details
            error_details = {
                "error": str(e),
                "error_type": type(e).__name__,
                "handler": func.__name__,
                "event_type": type(event).__name__,
                "event_data": event.dict(),
                "stack_trace": stack_trace.split('\n'),
            }
            
            try:
                # Attempt to publish an error event
                from .event_factory import get_event_factory
                
                # Get the event factory
                event_factory = get_event_factory()
                
                # Create and publish an error event (don't wait for it)
                event_factory.system_event_sync(
                    event_type=SystemEventType.ERROR,
                    component=f"event_handler.{func.__name__}",
                    details=error_details
                )
            except Exception as publish_error:
                # If we can't publish the error event, just log it
                logger.error(f"Failed to publish error event: {str(publish_error)}")
                
            # Return None to indicate error
            return None
    
    # For synchronous functions
    def sync_wrapper(event, *args, **kwargs):
        try:
            return func(event, *args, **kwargs)
        except Exception as e:
            # Log the error
            error_message = f"Error in event handler {func.__name__}: {str(e)}"
            stack_trace = traceback.format_exc()
            logger.error(f"{error_message}\n{stack_trace}")
            
            # Create error details
            error_details = {
                "error": str(e),
                "error_type": type(e).__name__,
                "handler": func.__name__,
                "event_type": type(event).__name__,
                "event_data": event.dict(),
                "stack_trace": stack_trace.split('\n'),
            }
            
            try:
                # Attempt to publish an error event
                from .event_factory import get_event_factory
                
                # Get the event factory
                event_factory = get_event_factory()
                
                # Create and publish an error event
                event_factory.system_event_sync(
                    event_type=SystemEventType.ERROR,
                    component=f"event_handler.{func.__name__}",
                    details=error_details
                )
            except Exception as publish_error:
                # If we can't publish the error event, just log it
                logger.error(f"Failed to publish error event: {str(publish_error)}")
                
            # Return None to indicate error
            return None
    
    # Check if the function is a coroutine function
    import inspect
    if inspect.iscoroutinefunction(func):
        return wrapper
    else:
        return sync_wrapper 
