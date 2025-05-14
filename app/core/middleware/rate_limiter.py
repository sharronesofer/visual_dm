"""
Rate limiting middleware using Redis for storage.
"""

import time
from typing import Any, Callable, Optional, Tuple, Union
from functools import wraps
from flask import request, current_app
from redis import Redis
from ..utils.api_response import create_rate_limit_error

class RateLimiter:
    """Rate limiting implementation using Redis."""

    def __init__(
        self,
        redis_client: Redis,
        key_prefix: str = "rate_limit",
        default_limit: int = 100,
        default_window: int = 3600  # 1 hour in seconds
    ) -> None:
        """
        Initialize rate limiter.

        Args:
            redis_client: Redis client instance
            key_prefix: Prefix for Redis keys
            default_limit: Default number of requests allowed per window
            default_window: Default time window in seconds
        """
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.default_limit = default_limit
        self.default_window = default_window

    def _get_rate_limit_key(self, identifier: str) -> str:
        """Generate Redis key for rate limiting."""
        return f"{self.key_prefix}:{identifier}"

    def _get_client_identifier(self) -> str:
        """Get unique identifier for the client."""
        # Try to get user ID from authenticated request
        if hasattr(request, 'user_data'):
            return str(request.user_data.get('id', ''))
        
        # Fall back to IP address
        return request.remote_addr or 'unknown'

    def check_rate_limit(
        self,
        identifier: Optional[str] = None,
        limit: Optional[int] = None,
        window: Optional[int] = None
    ) -> Tuple[bool, dict]:
        """
        Check if request is within rate limits.

        Args:
            identifier: Unique identifier for the client
            limit: Maximum number of requests allowed
            window: Time window in seconds

        Returns:
            Tuple of (is_allowed, limit_info)
        """
        identifier = identifier or self._get_client_identifier()
        limit = limit or self.default_limit
        window = window or self.default_window
        
        key = self._get_rate_limit_key(identifier)
        current_time = int(time.time())
        
        # Clean up old requests
        self.redis.zremrangebyscore(key, 0, current_time - window)
        
        # Count recent requests
        recent_requests = self.redis.zcard(key)
        
        # Get reset time
        if recent_requests == 0:
            reset_time = current_time + window
        else:
            oldest_request = float(self.redis.zrange(key, 0, 0, withscores=True)[0][1])
            reset_time = int(oldest_request + window)
        
        # Calculate remaining requests
        remaining = max(0, limit - recent_requests)
        
        limit_info = {
            "limit": limit,
            "remaining": remaining,
            "reset": reset_time,
            "window": window
        }
        
        if recent_requests >= limit:
            return False, limit_info
        
        # Record this request
        self.redis.zadd(key, {str(current_time): current_time})
        self.redis.expire(key, window)
        
        return True, limit_info

    def get_headers(self, limit_info: dict) -> dict:
        """Generate rate limit headers."""
        return {
            "X-RateLimit-Limit": str(limit_info["limit"]),
            "X-RateLimit-Remaining": str(limit_info["remaining"]),
            "X-RateLimit-Reset": str(limit_info["reset"]),
            "X-RateLimit-Window": str(limit_info["window"])
        }

def rate_limit(
    limit: Optional[int] = None,
    window: Optional[int] = None,
    key_func: Optional[Callable[[], str]] = None
) -> Callable:
    """
    Decorator for rate limiting routes.

    Args:
        limit: Maximum number of requests allowed
        window: Time window in seconds
        key_func: Function to generate rate limit key

    Returns:
        Decorated function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            limiter: RateLimiter = current_app.rate_limiter
            
            # Get identifier
            if key_func:
                identifier = key_func()
            else:
                identifier = limiter._get_client_identifier()
            
            # Check rate limit
            is_allowed, limit_info = limiter.check_rate_limit(
                identifier=identifier,
                limit=limit,
                window=window
            )
            
            # Add rate limit headers
            headers = limiter.get_headers(limit_info)
            
            if not is_allowed:
                response = create_rate_limit_error()
                response_tuple = response.to_response()
                response_tuple[0].headers.extend(headers)
                return response_tuple
            
            # Call the route function
            response = f(*args, **kwargs)
            
            # Add headers to the response
            if isinstance(response, tuple):
                response[0].headers.extend(headers)
            else:
                response.headers.extend(headers)
            
            return response
        
        return decorated_function
    
    return decorator 