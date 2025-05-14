"""
Logging handlers and utilities.

This module provides standardized logging functions and utilities that ensure
consistent log format and metadata inclusion across the application.
"""

import time
import logging
import functools
import traceback
import inspect
from typing import Dict, Any, Optional, Callable, TypeVar, cast, Union
from datetime import datetime

from app.core.logging.config import configure_logger, logging_config

# Type variables for function decorator
F = TypeVar('F', bound=Callable[..., Any])
T = TypeVar('T')

# Create a registry of loggers to avoid duplicates
_loggers: Dict[str, logging.Logger] = {}

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (uses calling module name if None)
        
    Returns:
        Configured logger instance
    """
    if name is None:
        # Get the caller's module name
        frame = inspect.currentframe()
        if frame is not None:
            frame = frame.f_back
            if frame is not None:
                module = inspect.getmodule(frame)
                if module is not None:
                    name = module.__name__
    
    # Default to root logger name if we couldn't determine the module
    name = name or "root"
    
    # Return cached logger if it exists
    if name in _loggers:
        return _loggers[name]
    
    # Create and configure a new logger
    logger = logging.getLogger(name)
    configure_logger(logger)
    
    # Cache and return the logger
    _loggers[name] = logger
    return logger

def log_with_context(
    level: int, 
    message: str, 
    logger: Optional[logging.Logger] = None,
    **context
) -> None:
    """
    Log a message with additional context data.
    
    Args:
        level: Logging level
        message: Log message
        logger: Logger to use (gets default logger if None)
        **context: Additional context data for the log entry
    """
    logger = logger or get_logger()
    
    # Create a copy of the context to avoid modifying the original
    log_context = context.copy()
    
    # Add timestamp if not present
    if "timestamp" not in log_context:
        log_context["timestamp"] = datetime.utcnow().isoformat()
    
    # Create extra dict for logging
    extra = {"extra": log_context}
    
    # Log the message with context
    logger.log(level, message, extra=extra)

def log_request(
    method: str,
    path: str,
    status_code: int,
    duration: float,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Log an HTTP request with timing and context information.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path
        status_code: HTTP status code
        duration: Request duration in seconds
        user_id: Optional user ID
        request_id: Optional request ID for tracking
        ip_address: Optional client IP address
        logger: Logger to use (gets a request logger if None)
    """
    logger = logger or get_logger("request")
    
    log_with_context(
        logging.INFO,
        f"{method} {path} - {status_code} ({duration:.2f}s)",
        logger,
        method=method,
        path=path,
        status_code=status_code,
        duration=duration,
        user_id=user_id,
        request_id=request_id,
        ip_address=ip_address
    )

def log_performance(
    function: Optional[Callable] = None,
    *,
    logger_name: Optional[str] = None,
    level: int = logging.DEBUG,
    threshold_ms: Optional[float] = None
) -> Union[Callable[[F], F], F]:
    """
    Decorator to log function performance.
    
    Can be used as @log_performance or with parameters @log_performance(...)
    
    Args:
        function: Function to decorate
        logger_name: Name for the logger (defaults to function's module)
        level: Logging level for performance logs
        threshold_ms: Only log if execution time exceeds this threshold (in ms)
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get the appropriate logger
            logger = get_logger(logger_name or func.__module__)
            
            # Record start time
            start_time = time.time()
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Calculate duration
                duration = time.time() - start_time
                duration_ms = duration * 1000
                
                # Log if no threshold or duration exceeds threshold
                if threshold_ms is None or duration_ms >= threshold_ms:
                    log_with_context(
                        level,
                        f"{func.__name__} completed in {duration:.4f}s",
                        logger,
                        function=func.__name__,
                        duration_seconds=duration,
                        duration_ms=duration_ms,
                        status="success"
                    )
                    
                return result
            
            except Exception as e:
                # Calculate duration on error
                duration = time.time() - start_time
                duration_ms = duration * 1000
                
                # Always log errors regardless of threshold
                log_with_context(
                    logging.ERROR,
                    f"{func.__name__} failed after {duration:.4f}s: {str(e)}",
                    logger,
                    function=func.__name__,
                    duration_seconds=duration,
                    duration_ms=duration_ms,
                    status="error",
                    error_type=type(e).__name__,
                    error_message=str(e),
                    traceback=traceback.format_exc()
                )
                
                # Re-raise the exception
                raise
                
        return cast(F, wrapper)
    
    # Handle both @log_performance and @log_performance(...) usage
    if function is None:
        return decorator
    else:
        return decorator(function)

def log_error(
    error: Exception,
    message: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Log an error with additional context.
    
    Args:
        error: The exception that occurred
        message: Custom error message (defaults to exception message)
        context: Additional context data for the log entry
        logger: Logger to use (gets default logger if None)
    """
    logger = logger or get_logger()
    error_message = message or str(error)
    
    error_context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc()
    }
    
    # Merge with additional context if provided
    if context:
        error_context.update(context)
    
    log_with_context(
        logging.ERROR,
        error_message,
        logger,
        **error_context
    )

def log_security_event(
    event_type: str,
    message: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    success: bool = False,
    details: Optional[Dict[str, Any]] = None,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Log a security-related event.
    
    Args:
        event_type: Type of security event (login, logout, access_denied, etc.)
        message: Description of the security event
        user_id: Optional user ID involved in the event
        ip_address: Optional IP address involved in the event
        success: Whether the security operation succeeded
        details: Additional details about the security event
        logger: Logger to use (gets a security logger if None)
    """
    logger = logger or get_logger("security")
    
    log_level = logging.INFO if success else logging.WARNING
    
    # Build security context
    security_context = {
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": ip_address,
        "success": success
    }
    
    # Add additional details if provided
    if details:
        security_context.update(details)
    
    log_with_context(
        log_level,
        message,
        logger,
        **security_context
    )

def log_database_operation(
    operation: str,
    collection: str,
    query: Optional[Dict[str, Any]] = None,
    document_id: Optional[str] = None,
    duration: Optional[float] = None,
    affected_count: Optional[int] = None,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Log a database operation with timing and context information.
    
    Args:
        operation: Database operation (query, insert, update, delete)
        collection: Database collection or table name
        query: Optional query criteria
        document_id: Optional document/record ID
        duration: Operation duration in seconds
        affected_count: Number of records affected
        logger: Logger to use (gets a database logger if None)
    """
    logger = logger or get_logger("database")
    
    # Build message
    message_parts = [f"DB {operation} on {collection}"]
    if document_id:
        message_parts.append(f"(id: {document_id})")
    if duration is not None:
        message_parts.append(f"in {duration:.4f}s")
    if affected_count is not None:
        message_parts.append(f"affected: {affected_count}")
    
    message = " ".join(message_parts)
    
    # Build context
    db_context = {
        "operation": operation,
        "collection": collection,
        "document_id": document_id,
        "query": query,
        "duration": duration,
        "affected_count": affected_count
    }
    
    log_with_context(
        logging.INFO,
        message,
        logger,
        **db_context
    ) 