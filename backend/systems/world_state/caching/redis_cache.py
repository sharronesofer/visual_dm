"""
Redis Caching Layer for World State System

Provides high-performance caching for frequently accessed world state data
while maintaining data consistency with the underlying repository.

Benefits:
- Sub-millisecond access to frequently accessed state
- Reduces database load for read-heavy operations
- Intelligent cache invalidation on state changes
- Optional for development, essential for production scale

Usage:
    # Without cache (direct repository access)
    service = WorldStateService(repository)
    
    # With cache (Redis acceleration)
    cache = RedisWorldStateCache("redis://localhost:6379")
    cached_repo = CachedWorldStateRepository(repository, cache)
    service = WorldStateService(cached_repo)
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json
import logging
import redis.asyncio as aioredis
import hashlib

from backend.systems.world_state.manager import WorldStateRepository
from backend.systems.world_state.world_types import WorldState, StateCategory

logger = logging.getLogger(__name__)


class RedisWorldStateCache:
    """Redis-based caching for world state data"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", default_ttl: int = 300):
        self.redis_url = redis_url
        self.default_ttl = default_ttl  # 5 minutes default
        self._redis: Optional[aioredis.Redis] = None
    
    async def initialize(self) -> bool:
        """Initialize Redis connection"""
        try:
            self._redis = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )
            
            # Test connection
            await self._redis.ping()
            logger.info("Redis cache initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if not self._redis:
                return None
                
            value = await self._redis.get(key)
            if value:
                return json.loads(value)
            return None
            
        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        try:
            if not self._redis:
                return False
            
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, default=str)
            await self._redis.setex(key, ttl, serialized)
            return True
            
        except Exception as e:
            logger.warning(f"Cache set failed for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if not self._redis:
                return False
                
            await self._redis.delete(key)
            return True
            
        except Exception as e:
            logger.warning(f"Cache delete failed for key {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            if not self._redis:
                return 0
            
            keys = await self._redis.keys(pattern)
            if keys:
                return await self._redis.delete(*keys)
            return 0
            
        except Exception as e:
            logger.warning(f"Cache pattern delete failed for {pattern}: {e}")
            return 0
    
    async def clear_all(self) -> bool:
        """Clear entire cache (use with caution!)"""
        try:
            if not self._redis:
                return False
                
            await self._redis.flushdb()
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def _make_key(self, *parts) -> str:
        """Create consistent cache key from parts"""
        return ":".join(str(part) for part in ["worldstate"] + list(parts))


class CachedWorldStateRepository(WorldStateRepository):
    """Repository wrapper that adds Redis caching to any repository"""
    
    def __init__(self, base_repository: WorldStateRepository, cache: RedisWorldStateCache):
        self.base_repo = base_repository
        self.cache = cache
        
        # Cache TTL configurations for different data types
        self.cache_ttls = {
            'world_state': 60,        # Current world state: 1 minute
            'region_state': 120,      # Region data: 2 minutes  
            'state_variable': 180,    # Individual variables: 3 minutes
            'historical_data': 600,   # Historical queries: 10 minutes
            'system_status': 30,      # System status: 30 seconds
        }
    
    # ===== CACHED WORLD STATE OPERATIONS =====
    
    async def load_world_state(self) -> Optional[WorldState]:
        """Load world state with caching"""
        cache_key = self.cache._make_key("current_state")
        
        # Try cache first
        cached_state = await self.cache.get(cache_key)
        if cached_state:
            logger.debug("World state cache hit")
            return WorldState(**cached_state)
        
        # Cache miss - load from repository
        logger.debug("World state cache miss - loading from repository")
        world_state = await self.base_repo.load_world_state()
        
        if world_state:
            # Cache the result
            state_dict = {
                'current_time': world_state.current_time.isoformat() if world_state.current_time else None,
                'game_day': world_state.game_day,
                'season': world_state.season,
                'year': world_state.year,
                'global_state': world_state.global_state,
                'regions': world_state.regions,
                'active_effects': world_state.active_effects
            }
            await self.cache.set(cache_key, state_dict, self.cache_ttls['world_state'])
        
        return world_state
    
    async def save_world_state(self, world_state: WorldState) -> bool:
        """Save world state and invalidate cache"""
        # Save to repository first
        success = await self.base_repo.save_world_state(world_state)
        
        if success:
            # Invalidate related caches
            await self.cache.delete_pattern("worldstate:current_state*")
            await self.cache.delete_pattern("worldstate:region:*")
            await self.cache.delete_pattern("worldstate:system_status*")
            logger.debug("Invalidated world state caches after save")
        
        return success
    
    # ===== CACHED STATE VARIABLE ACCESS =====
    
    async def get_cached_state_variable(
        self,
        key: str,
        region_id: Optional[str] = None,
        default: Any = None
    ) -> Any:
        """Get state variable with intelligent caching"""
        # Create cache key based on variable path
        cache_parts = ["state_var", key]
        if region_id:
            cache_parts.append(f"region:{region_id}")
        cache_key = self.cache._make_key(*cache_parts)
        
        # Try cache first
        cached_value = await self.cache.get(cache_key)
        if cached_value is not None:
            logger.debug(f"State variable cache hit: {key}")
            return cached_value
        
        # Cache miss - would need to load from world state
        logger.debug(f"State variable cache miss: {key}")
        world_state = await self.load_world_state()
        
        if not world_state:
            return default
        
        # Extract value from world state (simplified logic)
        value = default  # In real implementation, would parse key path
        
        # Cache the result
        if value is not None:
            await self.cache.set(cache_key, value, self.cache_ttls['state_variable'])
        
        return value
    
    # ===== CACHED REGION OPERATIONS =====
    
    async def get_cached_region_state(self, region_id: str) -> Optional[Dict[str, Any]]:
        """Get complete region state with caching"""
        cache_key = self.cache._make_key("region", region_id)
        
        # Try cache first
        cached_region = await self.cache.get(cache_key)
        if cached_region:
            logger.debug(f"Region cache hit: {region_id}")
            return cached_region
        
        # Cache miss - load from world state
        logger.debug(f"Region cache miss: {region_id}")
        world_state = await self.load_world_state()
        
        if world_state and region_id in world_state.regions:
            region_data = world_state.regions[region_id]
            await self.cache.set(cache_key, region_data, self.cache_ttls['region_state'])
            return region_data
        
        return None
    
    async def invalidate_region_cache(self, region_id: str):
        """Invalidate all caches related to a region"""
        await self.cache.delete_pattern(f"worldstate:region:{region_id}*")
        await self.cache.delete_pattern(f"worldstate:state_var:*:region:{region_id}*")
        logger.debug(f"Invalidated region caches for {region_id}")
    
    # ===== CACHED HISTORICAL QUERIES =====
    
    async def get_cached_historical_query(
        self,
        query_hash: str,
        query_func,
        *args,
        **kwargs
    ) -> Any:
        """Generic cached historical query wrapper"""
        cache_key = self.cache._make_key("historical", query_hash)
        
        # Try cache first
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            logger.debug(f"Historical query cache hit: {query_hash[:8]}...")
            return cached_result
        
        # Cache miss - execute query
        logger.debug(f"Historical query cache miss: {query_hash[:8]}...")
        result = await query_func(*args, **kwargs)
        
        if result:
            await self.cache.set(cache_key, result, self.cache_ttls['historical_data'])
        
        return result
    
    # ===== CACHE PERFORMANCE METRICS =====
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        try:
            if not self.cache._redis:
                return {"error": "Redis not connected"}
            
            info = await self.cache._redis.info()
            
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                ),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0
    
    # ===== PASS-THROUGH METHODS =====
    # All other repository methods pass through to base repository
    # while selectively invalidating caches on mutations
    
    async def record_state_change(self, change) -> bool:
        """Record state change and invalidate relevant caches"""
        success = await self.base_repo.record_state_change(change)
        
        if success:
            # Intelligent cache invalidation based on change
            if change.region_id:
                await self.invalidate_region_cache(change.region_id)
            
            # Invalidate state variable caches for the changed key
            await self.cache.delete_pattern(f"worldstate:state_var:{change.key_path}*")
            
            # Invalidate current state cache
            await self.cache.delete("worldstate:current_state")
        
        return success


# ===== CACHE FACTORY AND UTILITIES =====

async def create_cached_repository(
    base_repository: WorldStateRepository,
    redis_url: str = "redis://localhost:6379",
    enable_cache: bool = True
) -> WorldStateRepository:
    """Factory to create cached or non-cached repository based on configuration"""
    if not enable_cache:
        logger.info("Cache disabled - using base repository directly")
        return base_repository
    
    try:
        cache = RedisWorldStateCache(redis_url)
        if await cache.initialize():
            logger.info("Created cached repository with Redis")
            return CachedWorldStateRepository(base_repository, cache)
        else:
            logger.warning("Cache initialization failed - falling back to base repository")
            return base_repository
            
    except Exception as e:
        logger.error(f"Failed to create cached repository: {e}")
        return base_repository


# ===== CACHE WARMING UTILITIES =====

async def warm_cache_for_region(cached_repo: CachedWorldStateRepository, region_id: str):
    """Pre-populate cache with commonly accessed region data"""
    try:
        # Load region state to cache it
        await cached_repo.get_cached_region_state(region_id)
        
        # Pre-cache common state variables for this region
        common_vars = [
            "population", "resources.food", "resources.gold", 
            "controlling_faction", "stability"
        ]
        
        for var in common_vars:
            await cached_repo.get_cached_state_variable(var, region_id)
        
        logger.info(f"Warmed cache for region {region_id}")
        
    except Exception as e:
        logger.error(f"Failed to warm cache for region {region_id}: {e}")


async def warm_cache_startup(cached_repo: CachedWorldStateRepository):
    """Warm cache with essential data on system startup"""
    try:
        # Load current world state
        await cached_repo.load_world_state()
        
        # Pre-load common system data
        # This would be customized based on your game's access patterns
        
        logger.info("Cache warming completed")
        
    except Exception as e:
        logger.error(f"Failed to warm cache on startup: {e}") 