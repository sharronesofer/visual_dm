"""
Logging middleware for the event system.

This middleware provides simple logging for all events passing through
the event system, with configurable verbosity levels.
"""
import logging
from typing import Any, Callable, Dict, Optional

from ..base import EventBase

logger = logging.getLogger(__name__)

# Default logging configuration
DEFAULT_CONFIG = {
    'enabled': True,  # Enabled by default
    'level': 'DEBUG',  # Logging level
    'include_data': False,  # Include event data in logs
}

# Global state for the middleware
_config = DEFAULT_CONFIG.copy()


async def logging_middleware(event: EventBase, next_middleware: Callable) -> Any:
    """
    Middleware to log all events passing through the dispatcher.
    
    This simple middleware logs information about each event,
    optionally including the event data itself.
    
    Args:
        event: The event being dispatched
        next_middleware: Function to call the next middleware
        
    Returns:
        Results from subsequent middlewares and handlers
    """
    if not _config['enabled']:
        return await next_middleware(event)
    
    event_type = type(event).__name__
    log_msg = f"Event dispatched: {event_type} - {event.event_type}"
    
    if _config['include_data']:
        try:
            data_str = str(event.dict()) if hasattr(event, 'dict') else str(event)
            log_msg += f" - Data: {data_str}"
        except:
            log_msg += " (data could not be serialized)"
    
    # Log at the configured level
    log_level = getattr(logging, _config['level'])
    logger.log(log_level, log_msg)
    
    return await next_middleware(event)


def configure_logging(config: Dict[str, Any]) -> None:
    """
    Configure the logging middleware.
    
    Args:
        config: Configuration options to update
    """
    global _config
    _config.update(config)
    logger.debug(f"Logging middleware configured: {_config}") 