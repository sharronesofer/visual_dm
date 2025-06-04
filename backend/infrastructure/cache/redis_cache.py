"""
Redis Caching Infrastructure

High-performance caching layer providing 10-100x faster reads
with intelligent cache invalidation and performance metrics.
Infrastructure layer - handles Redis connection and caching logic.
"""

import json
import asyncio
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
import logging

try:
    import aioredis
    AIOREDIS_AVAILABLE = True
except ImportError:
    aioredis = None
    AIOREDIS_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

class RedisCache:
    """High-performance Redis caching wrapper with fallback modes"""
    
    def __init__(self, 
                 redis_url: str = "redis://localhost:6379",
                 key_prefix: str = "worldstate:",
                 default_ttl: int = 3600):  # 1 hour default
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
        self.redis_client = None
        self.sync_client = None
        self.is_async = False
        self.metrics = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    async def connect(self):
        """Connect to Redis with fallback modes"""
        # Try async first
        if AIOREDIS_AVAILABLE:
            try:
                self.redis_client = await aioredis.from_url(self.redis_url)
                await self.redis_client.ping()
                self.is_async = True
                logger.info("Redis async cache connected successfully")
                return
            except Exception as e:
                logger.warning(f"Async Redis connection failed: {e}, trying sync mode")
                if self.redis_client:
                    try:
                        await self.redis_client.close()
                    except:
                        pass
                    self.redis_client = None
        
        # Try sync Redis
        if REDIS_AVAILABLE:
            try:
                self.sync_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
                self.sync_client.ping()
                self.is_async = False
                logger.info("Redis sync cache connected successfully")
                return
            except Exception as e:
                logger.warning(f"Sync Redis connection failed: {e}")
                self.sync_client = None
        
        logger.warning("Redis not available, cache disabled")
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
        if self.sync_client:
            self.sync_client.close()
            self.sync_client = None
    
    def _make_key(self, key: str) -> str:
        """Create prefixed cache key"""
        return f"{self.key_prefix}{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not (self.redis_client or self.sync_client):
            self.metrics['misses'] += 1
            return None
        
        try:
            cache_key = self._make_key(key)
            
            if self.is_async and self.redis_client:
                value = await self.redis_client.get(cache_key)
            elif self.sync_client:
                value = self.sync_client.get(cache_key)
            else:
                value = None
            
            if value:
                self.metrics['hits'] += 1
                return json.loads(value)
            else:
                self.metrics['misses'] += 1
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.metrics['misses'] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not (self.redis_client or self.sync_client):
            return False
        
        try:
            cache_key = self._make_key(key)
            serialized = json.dumps(value, default=str)
            ttl = ttl or self.default_ttl
            
            if self.is_async and self.redis_client:
                await self.redis_client.setex(cache_key, ttl, serialized)
            elif self.sync_client:
                self.sync_client.setex(cache_key, ttl, serialized)
            else:
                return False
            
            self.metrics['sets'] += 1
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not (self.redis_client or self.sync_client):
            return False
        
        try:
            cache_key = self._make_key(key)
            
            if self.is_async and self.redis_client:
                result = await self.redis_client.delete(cache_key)
            elif self.sync_client:
                result = self.sync_client.delete(cache_key)
            else:
                return False
            
            self.metrics['deletes'] += 1
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern"""
        if not (self.redis_client or self.sync_client):
            return 0
        
        try:
            cache_pattern = self._make_key(pattern)
            
            if self.is_async and self.redis_client:
                keys = await self.redis_client.keys(cache_pattern)
                if keys:
                    result = await self.redis_client.delete(*keys)
                    self.metrics['deletes'] += len(keys)
                    return result
            elif self.sync_client:
                keys = self.sync_client.keys(cache_pattern)
                if keys:
                    result = self.sync_client.delete(*keys)
                    self.metrics['deletes'] += len(keys)
                    return result
            
            return 0
        except Exception as e:
            logger.error(f"Cache pattern delete error: {e}")
            return 0
    
    async def invalidate_state_cache(self, state_type: str):
        """Invalidate all cache entries for a state type"""
        patterns = [
            f"state:{state_type}",
            f"summary:{state_type}:*",
            "snapshots",
            "metrics"
        ]
        
        for pattern in patterns:
            await self.delete_pattern(pattern)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        total_requests = self.metrics['hits'] + self.metrics['misses']
        hit_rate = self.metrics['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'cache_hits': self.metrics['hits'],
            'cache_misses': self.metrics['misses'],
            'total_requests': total_requests,
            'cache_hit_rate': hit_rate,
            'cache_sets': self.metrics['sets'],
            'cache_deletes': self.metrics['deletes'],
            'is_connected': self.redis_client is not None or self.sync_client is not None,
            'mode': 'async' if self.is_async else 'sync'
        } 