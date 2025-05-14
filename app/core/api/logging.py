import time
import uuid
from typing import Optional, Dict, Any
from functools import wraps
import logging
import json
import traceback

from flask import request, g, current_app
from werkzeug.exceptions import HTTPException

class RequestLogger:
    """Request logging middleware."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
            
    def init_app(self, app):
        """Initialize the logger with a Flask application."""
        # Set up request logging
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_request(self.teardown_request)
        
        # Create logger if it doesn't exist
        if not app.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
            ))
            app.logger.addHandler(handler)
            app.logger.setLevel(logging.INFO)
            
    def before_request(self):
        """Log request details before processing."""
        g.start_time = time.time()
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        
        # Log request details
        log_data = {
            'request_id': g.request_id,
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.args),
            'headers': dict(request.headers),
            'source_ip': request.remote_addr
        }
        
        # Include request body for appropriate methods
        if request.is_json and request.method in ['POST', 'PUT', 'PATCH']:
            try:
                log_data['body'] = request.get_json()
            except Exception as e:
                log_data['body_error'] = str(e)
                
        current_app.logger.info(f"Request started: {json.dumps(log_data)}")
        
    def after_request(self, response):
        """Log response details after processing."""
        duration = time.time() - g.start_time
        
        # Log response details
        log_data = {
            'request_id': g.request_id,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'response_size': len(response.get_data()),
            'response_headers': dict(response.headers)
        }
        
        # Include response body for JSON responses
        if response.is_json:
            try:
                log_data['body'] = response.get_json()
            except Exception as e:
                log_data['body_error'] = str(e)
                
        current_app.logger.info(f"Request completed: {json.dumps(log_data)}")
        
        # Add request ID to response headers
        response.headers['X-Request-ID'] = g.request_id
        return response
        
    def teardown_request(self, exception):
        """Log any errors that occurred during request processing."""
        if exception:
            log_data = {
                'request_id': g.get('request_id', 'unknown'),
                'error_type': type(exception).__name__,
                'error_message': str(exception)
            }
            
            # Include traceback for non-HTTP exceptions
            if not isinstance(exception, HTTPException):
                log_data['traceback'] = traceback.format_exc()
                
            current_app.logger.error(f"Request failed: {json.dumps(log_data)}")

def log_function_call(func=None, *, include_args=True, include_result=True):
    """Decorator to log function calls with arguments and results."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            function_name = f.__name__
            log_data = {
                'function': function_name,
                'request_id': getattr(g, 'request_id', 'unknown')
            }
            
            # Log arguments if requested
            if include_args:
                log_data['args'] = str(args) if args else None
                log_data['kwargs'] = str(kwargs) if kwargs else None
                
            current_app.logger.debug(f"Function call started: {json.dumps(log_data)}")
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log successful completion
                log_data.update({
                    'duration_ms': round(duration * 1000, 2),
                    'status': 'success'
                })
                
                # Include result if requested
                if include_result:
                    log_data['result'] = str(result)
                    
                current_app.logger.debug(f"Function call completed: {json.dumps(log_data)}")
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Log error details
                log_data.update({
                    'duration_ms': round(duration * 1000, 2),
                    'status': 'error',
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'traceback': traceback.format_exc()
                })
                
                current_app.logger.error(f"Function call failed: {json.dumps(log_data)}")
                raise
                
        return wrapped
        
    return decorator if func is None else decorator(func)

def setup_logging(app, config: Optional[Dict[str, Any]] = None):
    """Set up application-wide logging configuration."""
    config = config or {}
    
    # Configure logging format
    logging.basicConfig(
        format=config.get('format', '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'),
        level=config.get('level', logging.INFO)
    )
    
    # Configure Flask logger
    app.logger.setLevel(config.get('level', logging.INFO))
    
    # Add file handler if specified
    log_file = config.get('file')
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            config.get('format', '[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
        ))
        app.logger.addHandler(file_handler)
        
    # Initialize request logger
    RequestLogger(app)
    
    return app.logger 