"""
Error handling middleware for the event system.

This middleware provides error catching and logging for the event system,
ensuring that errors don't propagate and crash the application.
"""
import logging
import traceback
from typing import Any, Callable, Dict, Optional

from ..base import EventBase

logger = logging.getLogger(__name__)


async def error_handling_middleware(event: EventBase, next_middleware: Callable) -> Any:
    """
    Middleware to catch and log errors during event processing.
    
    This middleware ensures that errors during event handling don't
    crash the application, and logs detailed error information for debugging.
    
    Args:
        event: The event being dispatched
        next_middleware: Function to call the next middleware
        
    Returns:
        Results from subsequent middlewares and handlers, or None on error
    """
    try:
        return await next_middleware(event)
    except Exception as e:
        # Log the error with traceback
        logger.error(f"Error processing event {event.event_type}: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Optionally, could report to an error monitoring service
        # _report_error(event, e)
        
        # Return None to indicate error
        return None


# Optional: Error reporting function
def _report_error(event: EventBase, error: Exception) -> None:
    """
    Report an error to a monitoring service.
    
    Args:
        event: The event that caused the error
        error: The exception that was raised
    """
    try:
        event_data = event.dict() if hasattr(event, 'dict') else str(event)
        error_data = {
            'event_type': event.event_type,
            'event_data': event_data,
            'error': str(error),
            'traceback': traceback.format_exc()
        }
        
        # TODO: Implement error reporting
        # from services.monitoring import report_error
        # report_error('event_system', error_data)
        pass
    except:
        # Don't let error reporting cause more errors
        logger.error("Error reporting failed")
        pass 