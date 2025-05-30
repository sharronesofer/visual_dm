"""
Error handling middleware for the event system.

This middleware catches and logs errors during event processing,
preventing exceptions from stopping the event propagation chain.
"""
import logging
import traceback
from typing import Any, Callable

from ..core.event_base import EventBase

logger = logging.getLogger('events.errors')

async def error_handling_middleware(event: EventBase, next_middleware: Callable[[EventBase], Any]) -> Any:
    """
    Middleware that catches and logs errors during event processing.
    
    Args:
        event: The event being dispatched
        next_middleware: The next middleware in the chain
        
    Returns:
        The result from the next middleware or None if an error occurred
    """
    try:
        return await next_middleware(event)
    except Exception as e:
        logger.error(f"Error processing event {event.event_type}: {str(e)}")
        logger.debug(f"Exception details: {traceback.format_exc()}")
        
        # Optionally emit a system error event here
        
        # Return None instead of re-raising to prevent blocking the event chain
        return None 