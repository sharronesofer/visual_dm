"""Redis caching utilities for the application."""

import os
import json
import pickle
from typing import Any, Dict, List, Optional, TypeVar, Generic, Type, Union
import logging
from redis import Redis
from redis.exceptions import RedisError

T = TypeVar('T')  # Generic type for entities

# Configure Redis connection from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_SSL = os.getenv("REDIS_SSL", "False").lower() in ("true", "1", "t")

# Default TTL in seconds (30 minutes)
DEFAULT_TTL = 1800

logger = logging.getLogger(__name__)

class CacheManager:
    """Redis cache manager for handling caching operations."""
    
    _instance = None
    _redis_client = None
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern to ensure only one cache manager instance."""
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
            try:
                cls._redis_client = Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=REDIS_DB,
                    password=REDIS_PASSWORD,
                    ssl=REDIS_SSL,
                    socket_timeout=5,
                    decode_responses=False  # We'll handle decoding ourselves
                )
                # Test connection
                cls._redis_client.ping()
                logger.info("Successfully connected to Redis")
            except RedisError as e:
                logger.error(f"Failed to connect to Redis: {e}")
                cls._redis_client = None
        return cls._instance
    
    @property
    def is_available(self) -> bool:
        """Check if Redis is available."""
        if self._redis_client is None:
            return False
        try:
            return self._redis_client.ping()
        except RedisError:
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found and Redis is available, None otherwise
        """
        if not self.is_available:
            return None
        
        try:
            data = self._redis_client.get(key)
            if data:
                return pickle.loads(data)
            return None
        except (RedisError, pickle.PickleError) as e:
            logger.error(f"Error retrieving from cache: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = DEFAULT_TTL) -> bool:
        """Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if value was cached successfully, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            data = pickle.dumps(value)
            return self._redis_client.setex(key, ttl, data)
        except (RedisError, pickle.PickleError) as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if value was deleted successfully, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            return bool(self._redis_client.delete(key))
        except RedisError as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    def flush_all(self) -> bool:
        """Flush all cache data.
        
        Returns:
            True if cache was flushed successfully, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            return self._redis_client.flushdb()
        except RedisError as e:
            logger.error(f"Error flushing cache: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        if not self.is_available:
            return False
        
        try:
            return bool(self._redis_client.exists(key))
        except RedisError as e:
            logger.error(f"Error checking key existence: {e}")
            return False


# Initialize the cache manager
cache_manager = CacheManager() 