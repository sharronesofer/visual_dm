"""
Flask integration for the centralized logging system.

This module provides integration with Flask applications, including
request logging middleware and application setup utilities.
"""

import time
import uuid
import json
import logging
from typing import Optional, Dict, Any, Union
from functools import wraps

from flask import request, g, Flask, Response
from werkzeug.exceptions import HTTPException

from app.core.logging.config import LogFormat, logging_config
from app.core.logging.handlers import get_logger, log_with_context

class FlaskRequestLogger:
    """
    Flask middleware for logging requests and responses.
    """
    
    def __init__(self, app: Optional[Flask] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the request logger.
        
        Args:
            app: Flask application instance
            config: Optional configuration overrides
        """
        self.config = config or {}
        
        # Merge with default config
        self.exclude_paths = self.config.get('exclude_paths', ['/health', '/metrics', '/favicon.ico'])
        self.include_request_body = self.config.get('include_request_body', False)
        self.include_response_body = self.config.get('include_response_body', False)
        self.include_headers = self.config.get('include_headers', True)
        self.request_body_methods = self.config.get('request_body_methods', ['POST', 'PUT', 'PATCH'])
        self.max_body_size = self.config.get('max_body_size', 10000)  # 10KB
        
        # Get logger
        self.logger = get_logger('flask.request')
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """
        Initialize the request logger with a Flask application.
        
        Args:
            app: Flask application instance
        """
        # Register before/after request handlers
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)
        
    def should_log_request(self) -> bool:
        """
        Determine if this request should be logged.
        
        Returns:
            True if the request should be logged, False otherwise
        """
        # Skip excluded paths
        if request.path in self.exclude_paths:
            return False
            
        # Skip OPTIONS requests
        if request.method == 'OPTIONS':
            return False
            
        return True
    
    def before_request(self) -> None:
        """Log request details before processing."""
        # Store start time for duration calculation
        g.start_time = time.time()
        
        # Generate or use existing request ID
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        
        # Skip logging for excluded paths
        if not self.should_log_request():
            return
        
        # Build request context
        log_context = {
            'request_id': g.request_id,
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.args)
        }
        
        # Add remote address if available
        if request.remote_addr:
            log_context['ip_address'] = request.remote_addr
            
        # Add user ID if available in session
        user_id = None
        if hasattr(g, 'user') and hasattr(g.user, 'id'):
            user_id = g.user.id
        elif 'user_id' in g:
            user_id = g.user_id
        
        if user_id:
            log_context['user_id'] = user_id
        
        # Add headers if enabled
        if self.include_headers:
            log_context['headers'] = {k: v for k, v in request.headers.items()}
        
        # Add request body for appropriate methods if enabled
        if (self.include_request_body and 
            request.method in self.request_body_methods and 
            request.content_length and 
            request.content_length < self.max_body_size):
            
            if request.is_json:
                try:
                    log_context['body'] = request.get_json()
                except Exception as e:
                    log_context['body_error'] = str(e)
            elif request.form:
                log_context['form'] = dict(request.form)
        
        # Log the request
        log_with_context(
            logging.INFO,
            f"Request started: {request.method} {request.path}",
            self.logger,
            **log_context
        )
        
    def after_request(self, response: Response) -> Response:
        """
        Log response details after processing.
        
        Args:
            response: Flask response object
            
        Returns:
            Unmodified response object
        """
        # Calculate request duration
        duration = time.time() - g.get('start_time', time.time())
        
        # Add request ID to response headers
        response.headers['X-Request-ID'] = g.get('request_id', str(uuid.uuid4()))
        
        # Skip logging for excluded paths
        if not self.should_log_request():
            return response
        
        # Build response context
        log_context = {
            'request_id': g.get('request_id', 'unknown'),
            'status_code': response.status_code,
            'duration': duration,
            'response_size': response.content_length or 0
        }
        
        # Add response headers if enabled
        if self.include_headers:
            log_context['headers'] = {k: v for k, v in response.headers.items()}
        
        # Add response body if enabled and JSON
        if (self.include_response_body and 
            response.content_type and 
            'application/json' in response.content_type and
            response.content_length and 
            response.content_length < self.max_body_size):
            
            try:
                if hasattr(response, 'json'):
                    log_context['body'] = response.json
                elif hasattr(response, 'get_json'):
                    log_context['body'] = response.get_json()
                # For regular response, try to decode and parse JSON
                elif hasattr(response, 'get_data'):
                    data = response.get_data(as_text=True)
                    try:
                        log_context['body'] = json.loads(data)
                    except json.JSONDecodeError:
                        # Not valid JSON or empty
                        pass
            except Exception as e:
                log_context['body_error'] = str(e)
                
        # Log the response
        log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
        
        log_with_context(
            log_level,
            f"Request completed: {request.method} {request.path} - {response.status_code} ({duration:.4f}s)",
            self.logger,
            **log_context
        )
        
        return response
        
    def teardown_request(self, exception: Optional[Exception]) -> None:
        """
        Log any errors that occurred during request processing.
        
        Args:
            exception: Exception that occurred (if any)
        """
        if not exception or not self.should_log_request():
            return
            
        # Skip logging for HTTPExceptions that were already logged in after_request
        if isinstance(exception, HTTPException):
            return
            
        # Calculate request duration
        duration = time.time() - g.get('start_time', time.time())
        
        # Build error context
        error_context = {
            'request_id': g.get('request_id', 'unknown'),
            'method': request.method,
            'path': request.path,
            'duration': duration,
            'error_type': type(exception).__name__,
            'error_message': str(exception)
        }
        
        # Log the error
        log_with_context(
            logging.ERROR,
            f"Request failed: {request.method} {request.path} - {type(exception).__name__}: {str(exception)}",
            self.logger,
            **error_context
        )

def configure_flask_logging(
    app: Flask, 
    request_logger_config: Optional[Dict[str, Any]] = None
) -> Flask:
    """
    Configure logging for a Flask application.
    
    Args:
        app: Flask application
        request_logger_config: Optional configuration for request logger
        
    Returns:
        The configured Flask application
    """
    # Configure the Flask logger
    app.logger = get_logger('flask.app')
    
    # Determine environment based on Flask configuration
    is_production = not app.config.get('DEBUG', False)
    
    # Set appropriate log format based on environment
    if is_production:
        format_type = LogFormat.JSON
    else:
        format_type = LogFormat.PRETTY
        
    # Update global logging configuration
    from app.core.logging.config import update_configuration
    update_configuration(format=format_type.value)
    
    # Initialize request logger
    FlaskRequestLogger(app, config=request_logger_config)
    
    # Return the configured app
    return app

def log_flask_view(function=None, *, level=logging.INFO):
    """
    Decorator to log Flask view function calls.
    
    Args:
        function: View function to decorate
        level: Logging level
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            logger = get_logger(f"flask.view.{func.__module__}")
            
            log_context = {
                'view': func.__name__,
                'request_id': g.get('request_id', 'unknown'),
                'endpoint': request.endpoint,
                'method': request.method,
                'path': request.path
            }
            
            # Log view function entry
            log_with_context(
                level,
                f"Executing view: {func.__name__}",
                logger,
                **log_context
            )
            
            # Call the view function
            return func(*args, **kwargs)
            
        return wrapped
        
    return decorator if function is None else decorator(function) 