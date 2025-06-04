"""
Cached World State Repository

Repository wrapper that adds Redis caching to any world state repository
while maintaining the same interface. Infrastructure layer component.
"""

import logging
from typing import Any, Dict, Optional, List

from backend.infrastructure.cache.redis_cache import RedisCache

logger = logging.getLogger(__name__)


class CachedWorldStateRepository:
    """Repository wrapper that adds Redis caching to any world state repository"""
    
    def __init__(self, base_repository, cache: RedisCache):
        self.base_repository = base_repository
        self.cache = cache
    
    async def get_state(self, state_type: str) -> Dict[str, Any]:
        """Get state with caching"""
        # Try cache first
        cache_key = f"state:{state_type}"
        cached_data = await self.cache.get(cache_key)
        
        if cached_data is not None:
            logger.debug(f"Cache hit for {state_type}")
            return cached_data
        
        # Cache miss - get from base repository
        logger.debug(f"Cache miss for {state_type}, fetching from repository")
        data = await self.base_repository.get_state(state_type)
        
        # Cache the result
        await self.cache.set(cache_key, data)
        
        return data
    
    async def update_state(self, state_type: str, state_data: Dict[str, Any]) -> bool:
        """Update state and invalidate cache"""
        # Update in base repository
        result = await self.base_repository.update_state(state_type, state_data)
        
        if result:
            # Invalidate related cache entries
            await self.cache.invalidate_state_cache(state_type)
            logger.debug(f"Invalidated cache for {state_type}")
        
        return result
    
    async def create_snapshot(self, snapshot_id: str, metadata: Dict[str, Any]) -> bool:
        """Create snapshot and invalidate snapshots cache"""
        result = await self.base_repository.create_snapshot(snapshot_id, metadata)
        
        if result:
            await self.cache.delete("snapshots")
            await self.cache.delete("metrics")
        
        return result
    
    async def get_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Get snapshot with caching"""
        cache_key = f"snapshot:{snapshot_id}"
        cached_data = await self.cache.get(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        data = await self.base_repository.get_snapshot(snapshot_id)
        if data:
            await self.cache.set(cache_key, data)
        
        return data
    
    async def list_snapshots(self) -> List[Dict[str, Any]]:
        """List snapshots with caching"""
        cache_key = "snapshots"
        cached_data = await self.cache.get(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        data = await self.base_repository.list_snapshots()
        await self.cache.set(cache_key, data)
        
        return data
    
    async def generate_regional_summary(self, region_key: str, context: str = "") -> str:
        """Generate regional summary with caching"""
        cache_key = f"summary:{region_key}:{hash(context)}"
        cached_summary = await self.cache.get(cache_key)
        
        if cached_summary is not None:
            return cached_summary
        
        summary = await self.base_repository.generate_regional_summary(region_key, context)
        
        # Cache summaries for shorter time (10 minutes)
        await self.cache.set(cache_key, summary, ttl=600)
        
        return summary
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics including cache stats"""
        # Get base metrics
        base_metrics = await self.base_repository.get_performance_metrics()
        
        # Add cache metrics
        cache_metrics = self.cache.get_metrics()
        
        return {**base_metrics, **cache_metrics}
    
    # Delegate other methods to base repository
    async def close(self):
        """Close connections"""
        await self.cache.close()
        if hasattr(self.base_repository, 'close'):
            await self.base_repository.close()
    
    def __getattr__(self, name):
        """Delegate unknown methods to base repository"""
        return getattr(self.base_repository, name) 