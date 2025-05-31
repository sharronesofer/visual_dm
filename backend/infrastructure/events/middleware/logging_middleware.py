"""
Logging middleware for event processing.

This middleware logs all events passing through the event dispatcher
for debugging and auditing purposes.
"""
import logging
from typing import Any, Callable, Dict
from datetime import datetime

from backend.infrastructure.events.core.event_base import EventBase

logger = logging.getLogger('events')

def logging_middleware(event: EventBase, next_middleware: Callable[[EventBase], Any]) -> Any:
    """
    Middleware that logs all events before processing them.
    
    Args:
        event: The event being dispatched
        next_middleware: The next middleware in the chain
        
    Returns:
        The result from the next middleware
    """
    logger.debug(f"Event dispatched: {event.event_type} - {event.json(exclude_none=True)}")
    return next_middleware(event) 