"""Logging utilities for the Visual DM application."""

import logging
import functools
from datetime import datetime
from typing import Any, Callable, Dict, Optional

# Configure the base logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('visual_dm')

def log_action(action_type: str, details: Dict[str, Any], user_id: Optional[str] = None) -> None:
    """
    Log an action performed in the application.
    
    Args:
        action_type: The type of action being performed
        details: Dictionary containing details about the action
        user_id: Optional ID of the user performing the action
    """
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'action_type': action_type,
        'details': details,
        'user_id': user_id
    }
    logger.info(f"Action logged: {log_data}")

def log_error(error: Exception, context: Dict[str, Any]) -> None:
    """
    Log an error that occurred in the application.
    
    Args:
        error: The exception that occurred
        context: Dictionary containing context about when the error occurred
    """
    error_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context
    }
    logger.error(f"Error occurred: {error_data}")

def log_usage(feature: str, usage_data: Dict[str, Any]) -> None:
    """
    Log usage of a specific feature.
    
    Args:
        feature: The name of the feature being used
        usage_data: Dictionary containing data about the feature usage
    """
    usage_info = {
        'timestamp': datetime.utcnow().isoformat(),
        'feature': feature,
        'usage_data': usage_data
    }
    logger.info(f"Feature usage logged: {usage_info}")

def with_logging(action_type: str) -> Callable:
    """
    Decorator to automatically log function calls.
    
    Args:
        action_type: The type of action to log
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                result = func(*args, **kwargs)
                log_action(
                    action_type=action_type,
                    details={
                        'function': func.__name__,
                        'args': str(args),
                        'kwargs': str(kwargs),
                        'status': 'success'
                    }
                )
                return result
            except Exception as e:
                log_error(
                    error=e,
                    context={
                        'function': func.__name__,
                        'args': str(args),
                        'kwargs': str(kwargs)
                    }
                )
                raise
        return wrapper
    return decorator

def setup_logging(app=None):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
    )
    if app:
        app.logger.handlers = logging.getLogger().handlers
        app.logger.setLevel(logging.INFO) 