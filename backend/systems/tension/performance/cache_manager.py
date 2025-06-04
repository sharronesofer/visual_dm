"""
Tension System Cache Manager

Provides intelligent caching for tension system data with:
- Multi-level caching (memory, Redis)
- TTL-based expiration
- Cache invalidation strategies
- Performance metrics
- Batch cache operations

Based on patterns from NPC and equipment system performance optimizations.
"""

import time
import json
import logging
from typing import Dict, Any, Optional, List, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached item with metadata"""
    data: Any
    created_at: datetime
    expires_at: datetime
    last_accessed: datetime
    access_count: int = 0
    size_bytes: int = 0
    cache_key: str = ""

    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.utcnow() > self.expires_at

    def is_stale(self, staleness_threshold: timedelta = timedelta(minutes=5)) -> bool:
        """Check if cache entry is stale but not expired"""
        return datetime.utcnow() > (self.created_at + staleness_threshold)

    def refresh_access(self) -> None:
        """Update access statistics"""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1


@dataclass 
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size_bytes: int = 0
    entry_count: int = 0
    hit_rate: float = 0.0
    
    def calculate_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total_requests = self.hits + self.misses
        if total_requests == 0:
            return 0.0
        self.hit_rate = self.hits / total_requests
        return self.hit_rate


class TensionCacheManager:
    """
    Advanced caching system for tension data with multiple strategies
    
    Features:
    - Memory-based caching with TTL
    - Redis caching for distributed systems
    - Intelligent cache invalidation
    - Performance monitoring
    - Batch operations
    - Cache warming strategies
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Cache storage layers
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._redis_client = None  # Initialize Redis if available
        
        # Cache configuration
        self.default_ttl = self.config.get('default_ttl_seconds', 300)  # 5 minutes
        self.max_memory_entries = self.config.get('max_memory_entries', 10000)
        self.max_memory_size_mb = self.config.get('max_memory_size_mb', 100)
        self.enable_redis = self.config.get('enable_redis', False)
        
        # Performance tracking
        self._stats = CacheStats()
        self._last_cleanup = datetime.utcnow()
        self._cleanup_interval = timedelta(minutes=10)
        
        # Cache strategies
        self.cache_strategies = {
            'tension_levels': {'ttl': 30, 'strategy': 'write_through'},     # 30 seconds
            'region_summaries': {'ttl': 120, 'strategy': 'write_behind'},   # 2 minutes 
            'conflict_triggers': {'ttl': 300, 'strategy': 'write_through'}, # 5 minutes
            'event_impacts': {'ttl': 3600, 'strategy': 'write_through'},    # 1 hour
            'dashboard_data': {'ttl': 60, 'strategy': 'write_behind'},      # 1 minute
            'metrics_summary': {'ttl': 180, 'strategy': 'write_behind'}     # 3 minutes
        }
        
        # Initialize Redis if enabled
        if self.enable_redis:
            self._init_redis()

    def _init_redis(self) -> None:
        """Initialize Redis connection if available"""
        try:
            import redis
            redis_host = self.config.get('redis_host', 'localhost')
            redis_port = self.config.get('redis_port', 6379)
            redis_db = self.config.get('redis_db', 0)
            
            self._redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True
            )
            
            # Test connection
            self._redis_client.ping()
            logger.info(f"Redis cache enabled: {redis_host}:{redis_port}")
            
        except Exception as e:
            logger.warning(f"Redis cache initialization failed: {e}")
            self._redis_client = None
            self.enable_redis = False

    def get(self, key: str, cache_type: str = 'default') -> Optional[Any]:
        """
        Get item from cache with automatic cleanup and performance tracking
        """
        # Cleanup expired entries periodically
        if datetime.utcnow() - self._last_cleanup > self._cleanup_interval:
            self._cleanup_expired()
        
        # Try memory cache first
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            
            if entry.is_expired():
                del self._memory_cache[key]
                self._stats.misses += 1
                return None
            
            entry.refresh_access()
            self._stats.hits += 1
            return entry.data
        
        # Try Redis cache if enabled
        if self.enable_redis and self._redis_client:
            try:
                redis_data = self._redis_client.get(f"tension:{key}")
                if redis_data:
                    data = json.loads(redis_data)
                    
                    # Store in memory cache for faster access
                    self._set_memory_cache(key, data, cache_type)
                    self._stats.hits += 1
                    return data
                    
            except Exception as e:
                logger.warning(f"Redis cache read failed for {key}: {e}")
        
        self._stats.misses += 1
        return None

    def set(self, key: str, value: Any, cache_type: str = 'default', ttl: Optional[int] = None) -> None:
        """
        Set item in cache with appropriate strategy
        """
        if ttl is None:
            strategy_config = self.cache_strategies.get(cache_type, {})
            ttl = strategy_config.get('ttl', self.default_ttl)
        
        # Set in memory cache
        self._set_memory_cache(key, value, cache_type, ttl)
        
        # Set in Redis cache if enabled
        if self.enable_redis and self._redis_client:
            try:
                redis_key = f"tension:{key}"
                redis_data = json.dumps(value, default=str)
                self._redis_client.setex(redis_key, ttl, redis_data)
                
            except Exception as e:
                logger.warning(f"Redis cache write failed for {key}: {e}")

    def _set_memory_cache(self, key: str, value: Any, cache_type: str, ttl: int) -> None:
        """Set item in memory cache with size management"""
        try:
            # Calculate data size
            data_size = len(json.dumps(value, default=str).encode('utf-8'))
            
            # Check memory limits
            if len(self._memory_cache) >= self.max_memory_entries:
                self._evict_lru_entries(1)
            
            # Create cache entry
            entry = CacheEntry(
                data=value,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(seconds=ttl),
                last_accessed=datetime.utcnow(),
                access_count=1,
                size_bytes=data_size,
                cache_key=key
            )
            
            self._memory_cache[key] = entry
            self._stats.size_bytes += data_size
            self._stats.entry_count += 1
            
        except Exception as e:
            logger.error(f"Memory cache set failed for {key}: {e}")

    def delete(self, key: str) -> bool:
        """Delete item from all cache layers"""
        deleted = False
        
        # Delete from memory cache
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            self._stats.size_bytes -= entry.size_bytes
            self._stats.entry_count -= 1
            del self._memory_cache[key]
            deleted = True
        
        # Delete from Redis cache
        if self.enable_redis and self._redis_client:
            try:
                redis_key = f"tension:{key}"
                redis_deleted = self._redis_client.delete(redis_key)
                deleted = deleted or bool(redis_deleted)
                
            except Exception as e:
                logger.warning(f"Redis cache delete failed for {key}: {e}")
        
        return deleted

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern"""
        invalidated = 0
        
        # Invalidate memory cache entries
        keys_to_delete = []
        for key in self._memory_cache:
            if self._matches_pattern(key, pattern):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            self.delete(key)
            invalidated += 1
        
        # Invalidate Redis cache entries
        if self.enable_redis and self._redis_client:
            try:
                redis_pattern = f"tension:{pattern}"
                redis_keys = self._redis_client.keys(redis_pattern)
                if redis_keys:
                    self._redis_client.delete(*redis_keys)
                    invalidated += len(redis_keys)
                    
            except Exception as e:
                logger.warning(f"Redis pattern invalidation failed for {pattern}: {e}")
        
        return invalidated

    def bulk_set(self, items: Dict[str, Any], cache_type: str = 'default', ttl: Optional[int] = None) -> None:
        """Set multiple items efficiently"""
        for key, value in items.items():
            self.set(key, value, cache_type, ttl)

    def bulk_get(self, keys: List[str], cache_type: str = 'default') -> Dict[str, Any]:
        """Get multiple items efficiently"""
        results = {}
        
        for key in keys:
            value = self.get(key, cache_type)
            if value is not None:
                results[key] = value
        
        return results

    def warm_cache(self, warm_data: Dict[str, Any], cache_type: str = 'default') -> None:
        """Pre-populate cache with frequently accessed data"""
        logger.info(f"Warming cache with {len(warm_data)} items")
        self.bulk_set(warm_data, cache_type)

    def _cleanup_expired(self) -> None:
        """Remove expired entries from memory cache"""
        current_time = datetime.utcnow()
        expired_keys = []
        
        for key, entry in self._memory_cache.items():
            if entry.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            entry = self._memory_cache[key]
            self._stats.size_bytes -= entry.size_bytes
            self._stats.entry_count -= 1
            self._stats.evictions += 1
            del self._memory_cache[key]
        
        self._last_cleanup = current_time
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def _evict_lru_entries(self, count: int) -> None:
        """Evict least recently used entries"""
        if not self._memory_cache:
            return
        
        # Sort by last accessed time
        entries_by_access = sorted(
            self._memory_cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        for i in range(min(count, len(entries_by_access))):
            key, entry = entries_by_access[i]
            self._stats.size_bytes -= entry.size_bytes
            self._stats.entry_count -= 1
            self._stats.evictions += 1
            del self._memory_cache[key]

    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern (simple wildcard support)"""
        if '*' not in pattern:
            return key == pattern
        
        import fnmatch
        return fnmatch.fnmatch(key, pattern)

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        self._stats.calculate_hit_rate()
        
        memory_usage_mb = self._stats.size_bytes / (1024 * 1024)
        
        return {
            'hits': self._stats.hits,
            'misses': self._stats.misses,
            'hit_rate': self._stats.hit_rate,
            'evictions': self._stats.evictions,
            'entry_count': self._stats.entry_count,
            'memory_usage_mb': round(memory_usage_mb, 2),
            'memory_limit_mb': self.max_memory_size_mb,
            'redis_enabled': self.enable_redis,
            'cache_strategies': self.cache_strategies,
            'uptime_seconds': (datetime.utcnow() - self._last_cleanup).total_seconds()
        }

    def clear_all(self) -> None:
        """Clear all cache data"""
        # Clear memory cache
        self._memory_cache.clear()
        self._stats = CacheStats()
        
        # Clear Redis cache
        if self.enable_redis and self._redis_client:
            try:
                redis_keys = self._redis_client.keys("tension:*")
                if redis_keys:
                    self._redis_client.delete(*redis_keys)
                    
            except Exception as e:
                logger.warning(f"Redis cache clear failed: {e}")
        
        logger.info("All tension cache data cleared")

    def health_check(self) -> Dict[str, Any]:
        """Perform cache health check"""
        health = {
            'memory_cache': 'healthy',
            'redis_cache': 'disabled',
            'issues': []
        }
        
        # Check memory usage
        memory_usage_mb = self._stats.size_bytes / (1024 * 1024)
        if memory_usage_mb > self.max_memory_size_mb * 0.9:
            health['issues'].append('Memory cache near limit')
            health['memory_cache'] = 'warning'
        
        # Check Redis connection
        if self.enable_redis and self._redis_client:
            try:
                self._redis_client.ping()
                health['redis_cache'] = 'healthy'
            except Exception as e:
                health['redis_cache'] = 'error'
                health['issues'].append(f'Redis connection failed: {e}')
        
        return health


def cached(cache_type: str = 'default', ttl: Optional[int] = None):
    """
    Decorator for caching function results
    
    Args:
        cache_type: Type of cache strategy to use
        ttl: Time to live in seconds (None for default)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_data = f"{func.__name__}:{hash(str(args))}:{hash(str(kwargs))}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            if hasattr(wrapper, '_cache_manager'):
                cached_result = wrapper._cache_manager.get(cache_key, cache_type)
                if cached_result is not None:
                    return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            if hasattr(wrapper, '_cache_manager'):
                wrapper._cache_manager.set(cache_key, result, cache_type, ttl)
            
            return result
        
        return wrapper
    return decorator 