from typing import Optional, Dict, Any
from flask import Flask

from .response import APIResponse
from .blueprint import BaseBlueprint
from .rate_limit import RateLimiter
from .cache import generate_cache_key
from .errors import register_error_handlers
from .logging import setup_logging, RequestLogger
from .metrics import MetricsCollector
from .validation import validate_request, validate_response
from .models import (
    PaginationParams,
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
    SearchParams,
    DateRangeParams,
    SortParams,
    FilterParams,
    BaseRequestModel,
    BaseResponseModel,
    SuccessResponse
)
from .auth_blueprint import APIKeyBlueprint

def init_api(app: Flask, config: Optional[Dict[str, Any]] = None) -> Flask:
    """Initialize API middleware and configuration."""
    config = config or {}
    
    # Set up logging
    setup_logging(app, config.get('logging', {}))
    
    # Initialize request logger
    RequestLogger(app)
    
    # Initialize metrics collector
    MetricsCollector(app)
    
    # Initialize rate limiter if Redis URL provided
    redis_url = config.get('redis_url')
    if redis_url:
        app.rate_limiter = RateLimiter(redis_url)
        
    # Register error handlers
    register_error_handlers(app)
    
    # Configure CORS if enabled
    if config.get('cors_enabled', True):
        from flask_cors import CORS
        CORS(app, **config.get('cors_options', {}))
        
    # Configure compression if enabled
    if config.get('compression_enabled', True):
        from flask_compress import Compress
        Compress(app)
        
    # Add request ID middleware
    @app.after_request
    def add_request_id(response):
        from flask import g
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        return response
        
    # Register API key management blueprint
    app.register_blueprint(APIKeyBlueprint())
    
    return app

__all__ = [
    'APIResponse',
    'BaseBlueprint',
    'RateLimiter',
    'generate_cache_key',
    'register_error_handlers',
    'setup_logging',
    'RequestLogger',
    'MetricsCollector',
    'validate_request',
    'validate_response',
    'PaginationParams',
    'ErrorDetail',
    'ErrorResponse',
    'PaginatedResponse',
    'SearchParams',
    'DateRangeParams',
    'SortParams',
    'FilterParams',
    'BaseRequestModel',
    'BaseResponseModel',
    'SuccessResponse',
    'init_api'
] 