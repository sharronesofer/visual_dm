"""
Rate limiting middleware using Redis.
"""

import time
from typing import Tuple, Dict
import redis
from flask import request

class RateLimiter:
    """Rate limiting implementation using Redis."""
    
    def __init__(self, redis_url: str):
        """Initialize the rate limiter with Redis connection."""
        self.redis = redis.from_url(redis_url)
        
    def _get_client_identifier(self) -> str:
        """Get a unique identifier for the client."""
        # Use X-Forwarded-For header if behind a proxy, fallback to remote address
        return request.headers.get('X-Forwarded-For', request.remote_addr)
        
    def _generate_key(self, endpoint_type: str) -> str:
        """Generate a Redis key for rate limiting."""
        client_id = self._get_client_identifier()
        return f"rate_limit:{endpoint_type}:{client_id}"
        
    def is_rate_limited(
        self,
        endpoint_type: str,
        max_requests: int,
        period: int
    ) -> Tuple[bool, Dict[str, str]]:
        """
        Check if the request should be rate limited.
        
        Args:
            endpoint_type: Type of endpoint being accessed
            max_requests: Maximum number of requests allowed in the period
            period: Time period in seconds
            
        Returns:
            Tuple of (is_limited, headers)
            is_limited: True if request should be rate limited
            headers: Rate limit headers to include in response
        """
        key = self._generate_key(endpoint_type)
        current_time = int(time.time())
        
        # Create a pipeline for atomic operations
        pipe = self.redis.pipeline()
        
        # Remove old requests outside the current period
        pipe.zremrangebyscore(key, 0, current_time - period)
        
        # Count requests in the current period
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(current_time): current_time})
        
        # Set expiration on the key
        pipe.expire(key, period)
        
        # Execute pipeline
        _, request_count, _, _ = pipe.execute()
        
        # Calculate rate limit headers
        headers = {
            'X-RateLimit-Limit': str(max_requests),
            'X-RateLimit-Remaining': str(max(0, max_requests - request_count)),
            'X-RateLimit-Reset': str(current_time + period)
        }
        
        # Check if rate limit exceeded
        is_limited = request_count >= max_requests
        
        if is_limited:
            headers['Retry-After'] = str(period)
            
        return is_limited, headers 