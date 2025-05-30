"""
Analytics middleware for the EventDispatcher.

This middleware captures events for the analytics system, implementing the integration
described in the Development Bible.
"""
import logging
from typing import Any, Callable, Dict, Optional
import time

from backend.core.events.event_dispatcher import EventBase

logger = logging.getLogger(__name__)

class AnalyticsEvent(EventBase):
    """Analytics event with additional metadata."""
    category: str
    user_id: Optional[str] = None
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

async def analytics_middleware(event: EventBase, next_middleware: Callable):
    """
    Middleware to capture events for analytics.
    
    This middleware captures all events passing through the dispatcher and
    forwards them to the analytics service. It does not modify the events
    or interrupt the middleware chain.
    
    Args:
        event: The event being dispatched
        next_middleware: Function to call the next middleware
        
    Returns:
        Results from subsequent middlewares and handlers
    """
    try:
        # Import here to avoid circular imports
        from backend.app.core.analytics.analytics_service import AnalyticsService
        
        # Get the analytics service (lazy loaded)
        analytics_service = AnalyticsService.get_instance()
        
        # Prepare metadata from event
        metadata = {}
        for key, value in event.dict().items():
            if key not in ['event_type', 'timestamp']:
                metadata[key] = value
                
        # Track the event (don't wait for it)
        event_category = event.__class__.__name__
        event_action = event.event_type
        
        # For some events, we want to extract entity information
        entity_id = getattr(event, 'entity_id', None)
        entity_type = getattr(event, 'entity_type', None)
        
        # Queue the event tracking (don't block the event flow)
        analytics_service.queue_track_event(
            category=event_category,
            action=event_action,
            entity_id=entity_id,
            metadata=metadata
        )
    except Exception as e:
        logger.error(f"Error in analytics middleware: {e}")
        # Never block events due to analytics errors
    
    # Continue the middleware chain
    return await next_middleware(event)


async def filtering_middleware(event: EventBase, next_middleware: Callable):
    """
    Middleware to filter events based on configurable rules.
    
    This middleware can block or modify events based on rules, such as:
    - Rate limiting for specific event types
    - Filtering out debug or test events in production
    - Transforming event data for compatibility
    
    Args:
        event: The event being dispatched
        next_middleware: Function to call the next middleware
        
    Returns:
        Results from subsequent middlewares and handlers or None if filtered
    """
    # Import configuration (can be moved to middleware initialization)
    from backend.app.config import get_settings
    settings = get_settings()
    
    # Skip certain event types in production if configured
    if (settings.environment == "production" and 
        hasattr(settings, "filtered_event_types") and
        event.__class__.__name__ in settings.filtered_event_types):
        logger.debug(f"Filtered event in production: {event.event_type}")
        return None
    
    # Apply rate limiting for high-volume events
    if hasattr(settings, "rate_limited_events"):
        event_key = f"{event.__class__.__name__}:{event.event_type}"
        if event_key in settings.rate_limited_events:
            # Get rate limit settings
            rate_limit = settings.rate_limited_events[event_key]
            last_time_key = f"last_time_{event_key}"
            
            # Check if we should rate limit
            now = time.time()
            if (hasattr(filtering_middleware, last_time_key) and
                now - getattr(filtering_middleware, last_time_key) < rate_limit):
                logger.debug(f"Rate limited event: {event_key}")
                return None
                
            # Update last time
            setattr(filtering_middleware, last_time_key, now)
    
    # Continue the middleware chain
    return await next_middleware(event) 
