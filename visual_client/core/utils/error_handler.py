"""
Error handling and user feedback system for UI components.
"""

import logging
from typing import Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum, auto

# Configure logging
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Severity levels for errors."""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

@dataclass
class ErrorContext:
    """Context information for errors."""
    component: str
    operation: str
    severity: ErrorSeverity
    message: str
    details: Optional[dict] = None

class ErrorHandler:
    """Centralized error handling and user feedback system."""
    
    def __init__(self):
        """Initialize error handler."""
        self._error_callbacks: list[Callable[[ErrorContext], None]] = []
        self._last_error: Optional[ErrorContext] = None
        
    def register_callback(self, callback: Callable[[ErrorContext], None]) -> None:
        """Register an error callback function."""
        self._error_callbacks.append(callback)
        
    def unregister_callback(self, callback: Callable[[ErrorContext], None]) -> None:
        """Unregister an error callback function."""
        if callback in self._error_callbacks:
            self._error_callbacks.remove(callback)
            
    def handle_error(self, context: ErrorContext) -> None:
        """Handle an error and notify callbacks."""
        try:
            # Log the error
            log_message = f"{context.component}: {context.operation} - {context.message}"
            if context.details:
                log_message += f" (Details: {context.details})"
                
            if context.severity == ErrorSeverity.INFO:
                logger.info(log_message)
            elif context.severity == ErrorSeverity.WARNING:
                logger.warning(log_message)
            elif context.severity == ErrorSeverity.ERROR:
                logger.error(log_message)
            else:
                logger.critical(log_message)
                
            # Store the error
            self._last_error = context
            
            # Notify callbacks
            for callback in self._error_callbacks:
                try:
                    callback(context)
                except Exception as e:
                    logger.error(f"Error in error callback: {e}")
                    
        except Exception as e:
            logger.critical(f"Error in error handler: {e}")
            
    def get_last_error(self) -> Optional[ErrorContext]:
        """Get the last error that occurred."""
        return self._last_error
        
    def clear_last_error(self) -> None:
        """Clear the last error."""
        self._last_error = None
        
    def create_context(
        self,
        component: str,
        operation: str,
        severity: ErrorSeverity,
        message: str,
        details: Optional[dict] = None
    ) -> ErrorContext:
        """Create an error context."""
        return ErrorContext(
            component=component,
            operation=operation,
            severity=severity,
            message=message,
            details=details
        )

# Global error handler instance
error_handler = ErrorHandler()

def handle_component_error(
    component: str,
    operation: str,
    error: Exception,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    details: Optional[dict] = None
) -> None:
    """Handle a component error with the global error handler."""
    context = error_handler.create_context(
        component=component,
        operation=operation,
        severity=severity,
        message=str(error),
        details=details
    )
    error_handler.handle_error(context)

def get_user_friendly_message(context: ErrorContext) -> str:
    """Get a user-friendly error message."""
    if context.severity == ErrorSeverity.INFO:
        return f"Info: {context.message}"
    elif context.severity == ErrorSeverity.WARNING:
        return f"Warning: {context.message}"
    elif context.severity == ErrorSeverity.ERROR:
        return f"Error: {context.message}"
    else:
        return f"Critical Error: {context.message}" 