"""
Debugging middleware for the event system.

This middleware provides runtime debugging capabilities for events,
including filtering, inspection, and detailed performance metrics.
It's intended for development and debugging environments.
"""
import logging
import time
import inspect
import asyncio
from typing import Any, Callable, Dict, List, Optional, Set, Type

from backend.infrastructure.events.core.event_base import EventBase

logger = logging.getLogger(__name__)

# Default debugging configuration
DEFAULT_CONFIG = {
    'enabled': False,  # Disabled by default
    'verbose': False,  # Detailed output
    'log_handler_timing': False,  # Log timing for each handler
    'include_types': [],  # Event types to include (empty = all)
    'exclude_types': [],  # Event types to exclude
    'break_on_types': [],  # Event types to break on (stop execution)
    'max_event_depth': 10,  # Maximum depth for nested events
}

# Global state for the middleware
_config = DEFAULT_CONFIG.copy()
_event_nesting = 0  # Track event nesting depth
_handlers_timing = {}  # Track handler timing statistics

async def debug_middleware(event: EventBase, next_middleware: Callable) -> Any:
    """
    Middleware for debugging the event system.
    
    This middleware provides detailed logging, filtering, and timing
    for events passing through the event system. It's particularly
    useful for debugging complex event chains and performance issues.
    
    Args:
        event: The event being dispatched
        next_middleware: Function to call the next middleware
        
    Returns:
        Results from subsequent middlewares and handlers
    """
    global _event_nesting
    
    # Skip if disabled
    if not _config['enabled']:
        return await next_middleware(event)
    
    # Skip based on inclusion/exclusion rules
    event_class = type(event).__name__
    if _config['include_types'] and event_class not in _config['include_types']:
        return await next_middleware(event)
    if event_class in _config['exclude_types']:
        return await next_middleware(event)
    
    # Track nesting depth to prevent infinite recursion
    _event_nesting += 1
    indent = '  ' * _event_nesting
    
    # Skip if we've exceeded maximum nesting depth
    if _event_nesting > _config['max_event_depth']:
        logger.warning(f"{indent}⚠️ Max event nesting depth exceeded: {event_class}")
        _event_nesting -= 1
        return await next_middleware(event)
    
    try:
        # Log event details
        if _config['verbose']:
            data_str = str(event.dict()) if hasattr(event, 'dict') else str(event)
            logger.debug(f"{indent}📊 Event: {event_class} - {event.event_type}\n{indent}Data: {data_str}")
        else:
            logger.debug(f"{indent}📊 Event: {event_class} - {event.event_type}")
        
        # Break on specified event types
        if event_class in _config['break_on_types']:
            logger.warning(f"{indent}🛑 BREAK on event: {event_class}")
            # This is where we'd add interactive debugging if implemented
            # For now, just a pause and warning
            await asyncio.sleep(0.5)  
            
        # Process event and track timing
        start_time = time.time()
        result = await next_middleware(event)
        total_time = time.time() - start_time
        
        # Log timing information
        if total_time > 0.1:  # Only log slow events
            logger.warning(f"{indent}⏱️ SLOW Event: {event_class} - {total_time:.3f}s")
        elif _config['verbose']:
            logger.debug(f"{indent}⏱️ Event time: {event_class} - {total_time:.3f}s")
            
        return result
    finally:
        # Always decrement nesting level to prevent leaks
        _event_nesting -= 1

def configure_debug(config: Dict[str, Any]) -> None:
    """
    Configure the debugging middleware.
    
    Args:
        config: Configuration options to update
    """
    global _config
    _config.update(config)
    
    if _config['enabled']:
        if _config['verbose']:
            logger.setLevel(logging.DEBUG)
        logger.info(f"Debug middleware enabled: {_config}")
    else:
        logger.info("Debug middleware disabled")

def get_handler_timing_stats() -> Dict[str, Dict[str, float]]:
    """
    Get timing statistics for event handlers.
    
    Returns:
        Dictionary mapping handler names to timing statistics
    """
    return _handlers_timing

def reset_timing_stats() -> None:
    """
    Reset all timing statistics.
    """
    global _handlers_timing
    _handlers_timing = {} 