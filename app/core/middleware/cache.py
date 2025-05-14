"""
Caching middleware using Redis.
"""

import json
import hashlib
from typing import Any, Dict, Optional
import redis
from flask import request

class APICache:
    """API response caching implementation using Redis."""
    
    def __init__(self, redis_url: str):
        """Initialize the cache with Redis connection."""
        self.redis = redis.from_url(redis_url)
        
    def _generate_cache_key(
        self,
        endpoint_type: str,
        path: str,
        query_params: Dict[str, Any],
        *args,
        **kwargs
    ) -> str:
        """
        Generate a unique cache key based on the request.
        
        Args:
            endpoint_type: Type of endpoint (list, detail, etc.)
            path: Request path
            query_params: Query parameters
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            A unique cache key string
        """
        # Create a dictionary of all parameters that affect the response
        key_parts = {
            'endpoint_type': endpoint_type,
            'path': path,
            'query_params': dict(query_params),
            'args': args,
            'kwargs': kwargs
        }
        
        # Convert to JSON string and hash
        key_string = json.dumps(key_parts, sort_keys=True)
        return f"api_cache:{hashlib.sha256(key_string.encode()).hexdigest()}"
        
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found, None otherwise
        """
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None
        
    def set(
        self,
        key: str,
        value: Dict[str, Any],
        timeout: int
    ) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            timeout: Cache timeout in seconds
        """
        self.redis.setex(
            key,
            timeout,
            json.dumps(value)
        )
        
    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
        """
        self.redis.delete(key)
        
    def clear_pattern(self, pattern: str) -> None:
        """
        Clear all cache keys matching a pattern.
        
        Args:
            pattern: Redis key pattern to match
        """
        cursor = 0
        while True:
            cursor, keys = self.redis.scan(cursor, match=pattern)
            if keys:
                self.redis.delete(*keys)
            if cursor == 0:
                break 