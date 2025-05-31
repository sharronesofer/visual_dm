"""
Debugging middleware for the event system.

This middleware provides detailed debugging information about events
and can be used to trace event flow, measure performance, and test
event handling in development environments.
"""
import logging
import time
from typing import Any, Callable, Dict, List, Optional
import os

from backend.infrastructure.events.core.event_base import EventBase

logger = logging.getLogger('events.debug')

# Global flag to enable/disable debug middleware
DEBUG_ENABLED = os.environ.get('EVENT_DEBUG', 'false').lower() in ('true', '1', 'yes')

# Track event statistics for debugging
_event_stats = {
    'counts': {},      # Count of events by type
    'timings': {},     # Processing time by type
    'handlers': {},    # Number of handlers by type
    'recent': []       # Recent events for inspection
}

# Configure max events to keep in recent list
MAX_RECENT_EVENTS = int(os.environ.get('EVENT_DEBUG_MAX_RECENT', '100'))

async def debug_middleware(event: EventBase, next_middleware: Callable[[EventBase], Any]) -> Any:
    """
    Middleware that captures debug information about events.
    
    Args:
        event: The event being dispatched
        next_middleware: The next middleware in the chain
        
    Returns:
        The result from the next middleware
    """
    if not DEBUG_ENABLED:
        return await next_middleware(event)
    
    # Update event counts
    event_type = event.event_type
    _event_stats['counts'][event_type] = _event_stats['counts'].get(event_type, 0) + 1
    
    # Add to recent events
    _event_stats['recent'].append({
        'type': event_type,
        'timestamp': event.timestamp,
        'event': event
    })
    
    # Trim recent events list if needed
    if len(_event_stats['recent']) > MAX_RECENT_EVENTS:
        _event_stats['recent'] = _event_stats['recent'][-MAX_RECENT_EVENTS:]
    
    # Time the event processing
    start_time = time.time()
    
    # Process the event
    result = await next_middleware(event)
    
    # Calculate processing time
    elapsed_ms = (time.time() - start_time) * 1000
    if event_type not in _event_stats['timings']:
        _event_stats['timings'][event_type] = []
    _event_stats['timings'][event_type].append(elapsed_ms)
    
    # Log detailed info if very slow
    if elapsed_ms > 100:  # More than 100ms is slow
        logger.warning(f"Slow event processing: {event_type} took {elapsed_ms:.2f}ms")
    
    return result

def get_event_stats() -> Dict:
    """
    Get current event statistics for debugging.
    
    Returns:
        Dict containing event statistics
    """
    stats = _event_stats.copy()
    
    # Calculate average processing times
    avg_timings = {}
    for event_type, timings in stats['timings'].items():
        if timings:
            avg_timings[event_type] = sum(timings) / len(timings)
    
    stats['avg_timings_ms'] = avg_timings
    return stats

def clear_event_stats() -> None:
    """Clear all event statistics."""
    global _event_stats
    _event_stats = {
        'counts': {},
        'timings': {},
        'handlers': {},
        'recent': []
    }

def get_recent_events() -> List[Dict]:
    """
    Get recent events for debugging.
    
    Returns:
        List of recent event data
    """
    return _event_stats['recent'] 