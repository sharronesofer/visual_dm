"""
Error handling middleware for the event system.

This middleware provides error catching and logging for the event system,
ensuring that errors don't propagate and crash the application.
"""
import logging
import traceback
from enum import Enum
from typing import Any, Callable, Dict, Optional

from backend.infrastructure.events.core.event_base import EventBase

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Enumeration of error severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


def handle_component_error(
    component_name: str,
    method_name: str,
    error: Exception,
    severity: ErrorSeverity,
    context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Handle component errors with appropriate logging and context.
    
    Args:
        component_name: Name of the component where error occurred
        method_name: Name of the method where error occurred
        error: The exception that was raised
        severity: Severity level of the error
        context: Additional context information
    """
    context = context or {}
    
    error_msg = f"{component_name}.{method_name}: {str(error)}"
    
    if severity == ErrorSeverity.DEBUG:
        logger.debug(error_msg, extra={"context": context})
    elif severity == ErrorSeverity.INFO:
        logger.info(error_msg, extra={"context": context})
    elif severity == ErrorSeverity.WARNING:
        logger.warning(error_msg, extra={"context": context})
    elif severity == ErrorSeverity.ERROR:
        logger.error(error_msg, extra={"context": context})
        logger.error(traceback.format_exc())
    elif severity == ErrorSeverity.CRITICAL:
        logger.critical(error_msg, extra={"context": context})
        logger.critical(traceback.format_exc())


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
        # from backend.infrastructure.events.services.monitoring import report_error
        # report_error('event_system', error_data)

    except:
        # Don't let error reporting cause more errors
        logger.error("Error reporting failed")
