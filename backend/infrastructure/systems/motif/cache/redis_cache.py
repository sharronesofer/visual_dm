"""
Redis caching layer for motif system performance optimization.

Provides intelligent caching with TTL, invalidation, and warming strategies.
"""

import json
import logging
import asyncio
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import redis.asyncio as redis
from functools import wraps
import hashlib

from backend.infrastructure.systems.motif.models import Motif, MotifFilter

logger = logging.getLogger(__name__)


class MotifCache:
    """Redis cache manager for motif system."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        default_ttl: int = 3600,  # 1 hour
        key_prefix: str = "motif:"
    ):
        """
        Initialize cache manager.
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds
            key_prefix: Prefix for all cache keys
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self.redis_client: Optional[redis.Redis] = None
        
        # TTL configurations for different data types
        self.ttl_config = {
            "motif": 1800,          # 30 minutes - motifs change frequently
            "motif_list": 600,      # 10 minutes - lists change often
            "statistics": 300,      # 5 minutes - stats need frequent updates
            "conflicts": 900,       # 15 minutes - conflicts change moderately
            "context": 1200,        # 20 minutes - context is expensive to compute
            "canonical": 86400,     # 24 hours - canonical motifs are stable
        }
    
    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                retry_on_timeout=True,
                health_check_interval=30
            )
            await self.redis_client.ping()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis cache")
    
    def _build_key(self, key_type: str, identifier: str) -> str:
        """Build cache key with prefix."""
        return f"{self.key_prefix}{key_type}:{identifier}"
    
    def _hash_filter(self, filter_params: Optional[MotifFilter]) -> str:
        """Create hash of filter parameters for cache key."""
        if not filter_params:
            return "all"
        
        # Create a deterministic string from filter parameters
        filter_dict = filter_params.dict(exclude_none=True)
        filter_str = json.dumps(filter_dict, sort_keys=True)
        return hashlib.md5(filter_str.encode()).hexdigest()[:8]
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        key_type: str = "default"
    ) -> bool:
        """Set value in cache with TTL."""
        if not self.redis_client:
            return False
        
        try:
            # Use type-specific TTL or default
            if ttl is None:
                ttl = self.ttl_config.get(key_type, self.default_ttl)
            
            serialized = json.dumps(value, default=str)
            await self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    async def invalidate_motif_caches(self, motif_id: Optional[str] = None) -> None:
        """Invalidate motif-related caches."""
        try:
            patterns_to_clear = [
                f"{self.key_prefix}motif_list:*",
                f"{self.key_prefix}statistics:*",
                f"{self.key_prefix}conflicts:*",
                f"{self.key_prefix}context:*"
            ]
            
            if motif_id:
                patterns_to_clear.append(f"{self.key_prefix}motif:{motif_id}")
            
            for pattern in patterns_to_clear:
                await self.delete_pattern(pattern)
                
            logger.debug(f"Invalidated cache patterns: {patterns_to_clear}")
        except Exception as e:
            logger.warning(f"Cache invalidation error: {e}")
    
    # Specific cache methods for different data types
    
    async def get_motif(self, motif_id: str) -> Optional[Dict]:
        """Get cached motif."""
        key = self._build_key("motif", motif_id)
        return await self.get(key)
    
    async def set_motif(self, motif_id: str, motif_data: Dict) -> bool:
        """Cache motif data."""
        key = self._build_key("motif", motif_id)
        return await self.set(key, motif_data, key_type="motif")
    
    async def get_motif_list(
        self,
        filter_params: Optional[MotifFilter] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Optional[List[Dict]]:
        """Get cached motif list."""
        filter_hash = self._hash_filter(filter_params)
        key = self._build_key("motif_list", f"{filter_hash}:{limit}:{offset}")
        return await self.get(key)
    
    async def set_motif_list(
        self,
        motifs: List[Dict],
        filter_params: Optional[MotifFilter] = None,
        limit: int = 50,
        offset: int = 0
    ) -> bool:
        """Cache motif list."""
        filter_hash = self._hash_filter(filter_params)
        key = self._build_key("motif_list", f"{filter_hash}:{limit}:{offset}")
        return await self.set(key, motifs, key_type="motif_list")
    
    async def get_statistics(self) -> Optional[Dict]:
        """Get cached system statistics."""
        key = self._build_key("statistics", "system")
        return await self.get(key)
    
    async def set_statistics(self, stats: Dict) -> bool:
        """Cache system statistics."""
        key = self._build_key("statistics", "system")
        return await self.set(key, stats, key_type="statistics")
    
    async def get_conflicts(self) -> Optional[List[Dict]]:
        """Get cached conflicts."""
        key = self._build_key("conflicts", "active")
        return await self.get(key)
    
    async def set_conflicts(self, conflicts: List[Dict]) -> bool:
        """Cache active conflicts."""
        key = self._build_key("conflicts", "active")
        return await self.set(key, conflicts, key_type="conflicts")
    
    async def get_context(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None,
        context_size: str = "medium"
    ) -> Optional[Dict]:
        """Get cached narrative context."""
        if x is not None and y is not None:
            location_key = f"{x}:{y}"
        else:
            location_key = "global"
        
        key = self._build_key("context", f"{location_key}:{context_size}")
        return await self.get(key)
    
    async def set_context(
        self,
        context: Dict,
        x: Optional[float] = None,
        y: Optional[float] = None,
        context_size: str = "medium"
    ) -> bool:
        """Cache narrative context."""
        if x is not None and y is not None:
            location_key = f"{x}:{y}"
        else:
            location_key = "global"
        
        key = self._build_key("context", f"{location_key}:{context_size}")
        return await self.set(key, context, key_type="context")
    
    async def warm_cache(self, service) -> None:
        """Warm cache with frequently accessed data."""
        try:
            logger.info("Starting cache warming...")
            
            # Warm system statistics
            stats = await service.get_motif_statistics()
            await self.set_statistics(stats)
            
            # Warm global context
            global_context = await service.get_enhanced_narrative_context("medium")
            await self.set_context(global_context, context_size="medium")
            
            # Warm active conflicts
            conflicts = await service.get_active_conflicts()
            await self.set_conflicts(conflicts)
            
            # Warm frequently accessed motif lists
            common_filters = [
                None,  # All motifs
                MotifFilter(active_only=True),  # Active motifs
                MotifFilter(scope="GLOBAL"),  # Global motifs
                MotifFilter(is_canonical=True),  # Canonical motifs
            ]
            
            for filter_params in common_filters:
                motifs = await service.list_motifs(filter_params, limit=50, offset=0)
                motif_dicts = [motif.dict() if hasattr(motif, 'dict') else motif for motif in motifs]
                await self.set_motif_list(motif_dicts, filter_params, 50, 0)
            
            logger.info("Cache warming completed")
            
        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        if not self.redis_client:
            return {"error": "Redis not connected"}
        
        try:
            info = await self.redis_client.info()
            
            # Get our keys count
            our_keys = await self.redis_client.keys(f"{self.key_prefix}*")
            
            return {
                "connected": True,
                "total_keys": len(our_keys),
                "memory_usage": info.get("used_memory_human", "N/A"),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": round(
                    info.get("keyspace_hits", 0) / 
                    max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100, 2
                ),
                "connected_clients": info.get("connected_clients", 0),
                "uptime_seconds": info.get("uptime_in_seconds", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e), "connected": False}


def cached(
    cache_key_func,
    ttl: Optional[int] = None,
    key_type: str = "default",
    invalidate_on_error: bool = False
):
    """
    Decorator for caching function results.
    
    Args:
        cache_key_func: Function to generate cache key
        ttl: Time to live in seconds
        key_type: Type of cache for TTL configuration
        invalidate_on_error: Whether to invalidate cache on errors
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Skip caching if no cache instance
            if not hasattr(self, 'cache') or not self.cache:
                return await func(self, *args, **kwargs)
            
            # Generate cache key
            cache_key = cache_key_func(*args, **kwargs)
            
            # Try to get from cache first
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            try:
                result = await func(self, *args, **kwargs)
                
                # Cache successful result
                if result is not None:
                    await self.cache.set(cache_key, result, ttl=ttl, key_type=key_type)
                
                return result
                
            except Exception as e:
                # Optionally invalidate cache on errors
                if invalidate_on_error:
                    await self.cache.delete(cache_key)
                raise e
        
        return wrapper
    return decorator


# Cache key generators
def motif_key(motif_id: str) -> str:
    """Generate cache key for motif."""
    return f"motif:{motif_id}"


def motif_list_key(filter_params=None, limit=50, offset=0) -> str:
    """Generate cache key for motif list."""
    if filter_params:
        filter_hash = hashlib.md5(
            json.dumps(filter_params.dict(exclude_none=True), sort_keys=True).encode()
        ).hexdigest()[:8]
    else:
        filter_hash = "all"
    return f"motif_list:{filter_hash}:{limit}:{offset}"


def context_key(x=None, y=None, context_size="medium") -> str:
    """Generate cache key for narrative context."""
    if x is not None and y is not None:
        location = f"{x}:{y}"
    else:
        location = "global"
    return f"context:{location}:{context_size}" 