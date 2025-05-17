"""
Caching utilities for performance optimization.
Provides Redis-based caching for database query results.
"""

from typing import Any, Optional, Union, Dict
from datetime import timedelta
import json
import redis
from functools import wraps
from flask import current_app, request
import hashlib
from redis import Redis

class RedisCache:
    """
    Redis cache implementation
    """
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    def set(self, key: str, value: Any, expire: int = None) -> None:
        """Set a value in cache with optional expiration"""
        serialized = json.dumps(value)
        if expire:
            self.redis.setex(key, expire, serialized)
        else:
            self.redis.set(key, serialized)

    def delete(self, key: str) -> None:
        """Delete a value from cache"""
        self.redis.delete(key)

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache"""
        return self.redis.exists(key)

    def clear(self) -> None:
        """Clear all cache entries"""
        self.redis.flushdb()

    def get_stats(self) -> Dict[str, Any]:
        """Return cache statistics such as total keys and memory usage."""
        info = self.redis.info() if hasattr(self.redis, 'info') else {}
        stats = {
            'total_keys': self.redis.dbsize() if hasattr(self.redis, 'dbsize') else None,
            'used_memory': info.get('used_memory_human') if info else None,
            'hits': info.get('keyspace_hits') if info else None,
            'misses': info.get('keyspace_misses') if info else None,
            'evicted_keys': info.get('evicted_keys') if info else None,
            'expired_keys': info.get('expired_keys') if info else None,
        }
        return stats

    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix, args, and kwargs."""
        key_base = f"{prefix}:{json.dumps(args, sort_keys=True, default=str)}:{json.dumps(kwargs, sort_keys=True, default=str)}"
        return hashlib.sha256(key_base.encode('utf-8')).hexdigest()

def cached(timeout: Optional[Union[int, timedelta]] = None, key_prefix: str = ""):
    """Decorator for caching view function results."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get cache instance
            cache = current_app.extensions.get('redis_cache')
            if not cache:
                return f(*args, **kwargs)
            
            # Generate cache key
            cache_key = cache.generate_key(
                f"{key_prefix}:{f.__name__}",
                request.args.to_dict(),
                *args,
                **kwargs
            )
            
            # Try to get from cache
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            
            # If not in cache, call function and cache result
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout)
            return rv
            
        return decorated_function
    return decorator

def init_cache(app) -> RedisCache:
    """
    Initialize Redis cache with app configuration
    """
    redis_client = Redis.from_url(app.config['REDIS_URL'])
    return RedisCache(redis_client)

class Cache:
    def __init__(self):
        self._store = {}
    def get(self, key):
        return self._store.get(key)
    def set(self, key, value):
        self._store[key] = value
    def clear(self):
        self._store.clear() 