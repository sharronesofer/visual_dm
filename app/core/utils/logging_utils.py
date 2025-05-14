"""
Logging utilities for the application.
Provides logging configuration and performance monitoring.
"""

import logging
import logging.handlers
import sys
import time
from functools import wraps
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from app.core.utils.config_utils import config
import os
from logging.handlers import RotatingFileHandler

# Configure root logger
logging.basicConfig(
    level=config.logging.level,
    format=config.logging.format,
    filename=config.logging.file_path if config.logging.file_path else None
)

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add file handler if log file is configured
if config.logging.file_path:
    file_handler = logging.FileHandler(
        config.logging.file_path,
        maxBytes=config.logging.max_bytes,
        backupCount=config.logging.backup_count
    )
    file_handler.setFormatter(logging.Formatter(config.logging.format))
    logger.addHandler(file_handler)

# Add console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(console_handler)

def log_info(message: str, extra: Optional[Dict[str, Any]] = None) -> None:
    """Log an info message with optional extra data."""
    logger.info(message, extra=extra or {})

def log_warning(message: str, extra: Optional[Dict[str, Any]] = None) -> None:
    """Log a warning message with optional extra data."""
    logger.warning(message, extra=extra or {})

def log_error(message: str, extra: Optional[Dict[str, Any]] = None) -> None:
    """Log an error message with optional extra data."""
    logger.error(message, extra=extra or {})

def log_exception(
    message: str,
    exc_info: Optional[Exception] = None,
    extra: Optional[Dict[str, Any]] = None
) -> None:
    """Log an exception with optional extra data."""
    logger.exception(message, exc_info=exc_info, extra=extra or {})

def log_request(
    method: str,
    path: str,
    status_code: int,
    duration: float,
    user_id: Optional[str] = None
) -> None:
    """Log an HTTP request with timing information."""
    extra = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration": duration,
        "user_id": user_id
    }
    logger.info(
        f"{method} {path} - {status_code} ({duration:.2f}s)",
        extra=extra
    )

def log_database_operation(
    operation: str,
    collection: str,
    document_id: Optional[str] = None,
    duration: Optional[float] = None
) -> None:
    """Log a database operation with timing information."""
    extra = {
        "operation": operation,
        "collection": collection,
        "document_id": document_id,
        "duration": duration
    }
    logger.info(
        f"DB {operation} on {collection}" + 
        (f" ({document_id})" if document_id else "") +
        (f" - {duration:.2f}s" if duration else ""),
        extra=extra
    )

def log_security_event(
    event_type: str,
    user_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """Log a security-related event."""
    extra = {
        "event_type": event_type,
        "user_id": user_id,
        "details": details or {}
    }
    logger.warning(
        f"Security event: {event_type}" +
        (f" (user: {user_id})" if user_id else ""),
        extra=extra
    )

def log_performance(func: Callable) -> Callable:
    """Decorator to log function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.2f}s: {str(e)}")
            raise
    return wrapper

def setup_logging(app):
    """Set up logging for the application.
    
    Args:
        app: Flask application instance
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Set up file handler
    file_handler = RotatingFileHandler(
        'logs/visual_dm.log',
        maxBytes=10240,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    console_handler.setLevel(logging.INFO)
    
    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    app.logger.info('Visual DM startup')

__all__ = ['logger', 'log_performance', 'setup_logging'] 