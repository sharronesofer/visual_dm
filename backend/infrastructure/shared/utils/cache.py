"""
Cache utilities for shared infrastructure.

This module provides caching functionality for business logic systems.
"""

from typing import Any, Optional, Dict
import time
from functools import wraps

class SimpleCache:
    """Simple in-memory cache implementation."""
    
    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self._cache:
            entry = self._cache[key]
            if time.time() < entry['expires']:
                return entry['value']
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        ttl = ttl or self._default_ttl
        self._cache[key] = {
            'value': value,
            'expires': time.time() + ttl
        }
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

class RedisCache:
    """Redis-compatible cache implementation (fallback to in-memory for now)."""
    
    def __init__(self, default_ttl: int = 300, redis_config: Optional[Dict[str, Any]] = None):
        # For now, use in-memory cache as fallback
        # TODO: Implement actual Redis connection when redis-py is available
        self._cache = SimpleCache(default_ttl)
        self._default_ttl = default_ttl
        self._redis_config = redis_config or {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        return self._cache.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in Redis cache."""
        self._cache.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete value from Redis cache."""
        return self._cache.delete(key)
    
    def clear(self) -> None:
        """Clear all Redis cache entries."""
        self._cache.clear()
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return self._cache.get(key) is not None
    
    def keys(self, pattern: str = "*") -> list:
        """Get all keys matching pattern (simplified implementation)."""
        # Simplified - just return all keys for now
        return list(self._cache._cache.keys())

# Global cache instance
cache = SimpleCache()

def cached(ttl: int = 300):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator

__all__ = ['SimpleCache', 'RedisCache', 'cache', 'cached'] 