"""
HTTP caching utilities.
Provides tools for implementing HTTP cache headers and conditional request handling.
"""

from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
import hashlib
import json
from flask import request, Response, make_response
from functools import wraps
import time
import gzip
import brotli
from werkzeug.http import http_date, parse_date

class HTTPCache:
    """Handles HTTP caching headers and conditional requests."""
    
    def __init__(self, app=None):
        """Initialize the HTTP cache handler."""
        self.app = app
        self.default_max_age = 300  # 5 minutes
        self.compression_min_size = 1024  # 1KB
        self.compression_types = {'gzip', 'br'}  # Supported compression algorithms
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask application."""
        self.app = app
        self.default_max_age = app.config.get('HTTP_CACHE_MAX_AGE', 300)
        self.compression_min_size = app.config.get('HTTP_CACHE_COMPRESSION_MIN_SIZE', 1024)
        self.compression_types = set(app.config.get('HTTP_CACHE_COMPRESSION_TYPES', ['gzip', 'br']))
    
    def generate_etag(self, data: Any) -> str:
        """Generate an ETag for the given data."""
        if isinstance(data, (dict, list)):
            data = json.dumps(data, sort_keys=True)
        elif not isinstance(data, str):
            data = str(data)
        
        return hashlib.sha1(data.encode('utf-8')).hexdigest()
    
    def should_compress(self, data: Any, accept_encoding: str) -> Optional[str]:
        """Determine if response should be compressed and which algorithm to use."""
        if not isinstance(data, (str, bytes)):
            data = json.dumps(data)
        
        data_size = len(data.encode('utf-8') if isinstance(data, str) else data)
        if data_size < self.compression_min_size:
            return None
        
        # Check client's accepted encoding
        accepted = set(e.strip() for e in accept_encoding.split(','))
        
        # Prefer Brotli over gzip if supported
        if 'br' in accepted and 'br' in self.compression_types:
            return 'br'
        elif 'gzip' in accepted and 'gzip' in self.compression_types:
            return 'gzip'
        
        return None
    
    def compress_data(self, data: Union[str, bytes], algorithm: str) -> bytes:
        """Compress data using the specified algorithm."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if algorithm == 'br':
            return brotli.compress(data)
        elif algorithm == 'gzip':
            return gzip.compress(data)
        
        return data
    
    def add_cache_headers(self, response: Response, etag: str, max_age: int = None,
                         last_modified: datetime = None, vary: Optional[list] = None) -> Response:
        """Add cache headers to response."""
        if max_age is None:
            max_age = self.default_max_age
        
        # Add ETag
        response.headers['ETag'] = f'"{etag}"'
        
        # Add Cache-Control
        cache_control = f'public, max-age={max_age}'
        if max_age == 0:
            cache_control = 'no-cache'
        response.headers['Cache-Control'] = cache_control
        
        # Add Last-Modified if provided
        if last_modified:
            response.headers['Last-Modified'] = http_date(last_modified.timestamp())
        
        # Add Vary header if needed
        if vary:
            response.headers['Vary'] = ', '.join(vary)
        
        return response
    
    def is_fresh(self, etag: str, last_modified: Optional[datetime] = None) -> bool:
        """Check if the client's cached copy is still fresh."""
        if_none_match = request.headers.get('If-None-Match')
        if if_none_match:
            return f'"{etag}"' == if_none_match
        
        if_modified_since = request.headers.get('If-Modified-Since')
        if if_modified_since and last_modified:
            try:
                ims_date = parse_date(if_modified_since)
                return last_modified.timestamp() <= ims_date.timestamp()
            except (TypeError, ValueError):
                pass
        
        return False

def cache_control(max_age: int = None, vary: Optional[list] = None):
    """Decorator to add HTTP cache headers to responses."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Get the response
            response = f(*args, **kwargs)
            
            # Only cache 200 OK responses
            if not isinstance(response, Response) or response.status_code != 200:
                return response
            
            http_cache = current_app.extensions.get('http_cache')
            if not http_cache:
                return response
            
            # Generate ETag from response data
            data = response.get_json() if response.is_json else response.get_data()
            etag = http_cache.generate_etag(data)
            
            # Check if client's cache is still valid
            if http_cache.is_fresh(etag):
                return '', 304
            
            # Add cache headers
            response = http_cache.add_cache_headers(
                response,
                etag=etag,
                max_age=max_age,
                vary=vary
            )
            
            # Handle compression if appropriate
            accept_encoding = request.headers.get('Accept-Encoding', '')
            compression = http_cache.should_compress(data, accept_encoding)
            
            if compression:
                compressed_data = http_cache.compress_data(data, compression)
                response.data = compressed_data
                response.headers['Content-Encoding'] = compression
                response.headers['Content-Length'] = len(compressed_data)
            
            return response
        return wrapped
    return decorator 

def etag(f):
    """Stub decorator for ETag support (actual logic handled by cache_control)."""
    return f

def last_modified(f):
    """Stub decorator for Last-Modified support (actual logic handled by cache_control)."""
    return f 