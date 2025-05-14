from functools import wraps
from typing import Optional, Union, Callable
from datetime import datetime
import time

from flask import request, current_app, g
import redis

from .response import APIResponse

class RateLimiter:
    """Rate limiting implementation using Redis."""
    
    def __init__(self, redis_url: str):
        """Initialize rate limiter with Redis connection."""
        self.redis = redis.from_url(redis_url)
        
    def _get_rate_limit_key(self, key_prefix: str) -> str:
        """Generate a unique key for rate limiting."""
        identifier = request.headers.get('X-API-Key') or request.remote_addr
        return f"rate_limit:{key_prefix}:{identifier}"
        
    def is_rate_limited(self, key_prefix: str, 
                       max_requests: int, 
                       period: int) -> tuple[bool, dict]:
        """Check if the request should be rate limited."""
        key = self._get_rate_limit_key(key_prefix)
        current_time = int(time.time())
        window_start = current_time - period
        
        # Clean up old requests
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Get current request count
        request_count = self.redis.zcard(key)
        
        # Add current request timestamp
        self.redis.zadd(key, {str(current_time): current_time})
        self.redis.expire(key, period)
        
        # Calculate rate limit headers
        reset_time = current_time + period
        remaining = max(0, max_requests - request_count - 1)
        
        headers = {
            'X-RateLimit-Limit': str(max_requests),
            'X-RateLimit-Remaining': str(remaining),
            'X-RateLimit-Reset': str(reset_time)
        }
        
        return request_count >= max_requests, headers

def rate_limit(requests_per_period: int, 
               period: int = 3600, 
               key_prefix: Optional[str] = None) -> Callable:
    """Rate limiting decorator for API endpoints."""
    
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not hasattr(current_app, 'rate_limiter'):
                current_app.rate_limiter = RateLimiter(
                    current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
                )
                
            prefix = key_prefix or f.__name__
            is_limited, headers = current_app.rate_limiter.is_rate_limited(
                prefix, requests_per_period, period
            )
            
            if is_limited:
                response = APIResponse.error(
                    message="Rate limit exceeded",
                    status_code=429,
                    error_code="RATE_LIMIT_EXCEEDED",
                    details={
                        "retry_after": headers['X-RateLimit-Reset']
                    }
                ).to_dict()
                return response, 429, headers
                
            response = f(*args, **kwargs)
            
            if isinstance(response, tuple):
                body, status_code, *rest = response
                headers.update(rest[0] if rest else {})
                return body, status_code, headers
            
            return response, 200, headers
            
        return wrapped
    return decorator 