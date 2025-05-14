from functools import wraps
from typing import Optional, Union, Callable, Any
import json
import hashlib
from datetime import datetime

from flask import request, current_app, Response
import redis

def generate_cache_key(prefix: str, args: tuple, kwargs: dict) -> str:
    """Generate a unique cache key based on the request."""
    # Include query parameters and request body in the key
    key_parts = [
        prefix,
        request.path,
        request.method,
        str(sorted(request.args.items())),
    ]
    
    # Include request body for POST/PUT requests
    if request.is_json and request.get_json():
        key_parts.append(json.dumps(request.get_json(), sort_keys=True))
        
    # Include function arguments
    if args:
        key_parts.append(str(args))
    if kwargs:
        key_parts.append(str(sorted(kwargs.items())))
        
    # Generate hash of the key parts
    key_string = ":".join(key_parts)
    return f"cache:{hashlib.sha256(key_string.encode()).hexdigest()}"

class CacheManager:
    """Redis-based cache manager for API responses."""
    
    def __init__(self, redis_url: str):
        """Initialize cache manager with Redis connection."""
        self.redis = redis.from_url(redis_url)
        
    def get(self, key: str) -> Optional[dict]:
        """Get cached response if it exists."""
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None
        
    def set(self, key: str, 
            value: dict, 
            timeout: int = 300,
            update_etag: bool = True) -> None:
        """Cache response with optional timeout."""
        if update_etag:
            value['etag'] = hashlib.sha256(
                json.dumps(value, sort_keys=True).encode()
            ).hexdigest()
            
        self.redis.setex(key, timeout, json.dumps(value))
        
    def delete(self, key_pattern: str) -> None:
        """Delete all keys matching the pattern."""
        for key in self.redis.scan_iter(key_pattern):
            self.redis.delete(key)
            
def cache(timeout: int = 300, 
          key_prefix: Optional[str] = None,
          unless: Optional[Callable] = None) -> Callable:
    """Cache decorator for API endpoints."""
    
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not hasattr(current_app, 'cache_manager'):
                current_app.cache_manager = CacheManager(
                    current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
                )
                
            # Skip caching if condition is met
            if unless and unless():
                return f(*args, **kwargs)
                
            # Generate cache key
            prefix = key_prefix or f.__name__
            cache_key = generate_cache_key(prefix, args, kwargs)
            
            # Check ETag
            if_none_match = request.headers.get('If-None-Match')
            cached_data = current_app.cache_manager.get(cache_key)
            
            if cached_data and if_none_match:
                if cached_data.get('etag') == if_none_match:
                    return '', 304, {'ETag': if_none_match}
                    
            # Return cached response if it exists
            if cached_data:
                return Response(
                    json.dumps(cached_data),
                    status=200,
                    mimetype='application/json',
                    headers={'ETag': cached_data.get('etag')}
                )
                
            # Get fresh response
            response = f(*args, **kwargs)
            
            if isinstance(response, tuple):
                response_data, status_code, *rest = response
                headers = rest[0] if rest else {}
            else:
                response_data = response
                status_code = 200
                headers = {}
                
            # Only cache successful responses
            if 200 <= status_code < 300:
                current_app.cache_manager.set(
                    cache_key,
                    response_data,
                    timeout=timeout
                )
                if isinstance(response_data, dict) and 'etag' in response_data:
                    headers['ETag'] = response_data['etag']
                    
            return response_data, status_code, headers
            
        return wrapped
    return decorator

def invalidate_cache(pattern: str) -> None:
    """Invalidate all cached responses matching the pattern."""
    if hasattr(current_app, 'cache_manager'):
        current_app.cache_manager.delete(f"cache:{pattern}*") 