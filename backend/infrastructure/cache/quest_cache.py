"""
Quest System Caching Layer
Provides intelligent caching for quest data to improve performance.
Supports Redis with in-memory fallback.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache only")


class QuestCache:
    """Intelligent caching for quest system data"""
    
    def __init__(self, redis_url: str = None, default_ttl: int = 300):
        """
        Initialize cache with Redis and in-memory fallback
        
        Args:
            redis_url: Redis connection URL (optional)
            default_ttl: Default cache TTL in seconds (5 minutes)
        """
        self.default_ttl = default_ttl
        self.redis_client = None
        self.memory_cache = {}
        self.memory_cache_ttl = {}
        
        # Initialize Redis if available
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                logger.info("Connected to Redis cache")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}, using memory cache")
                self.redis_client = None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and parameters"""
        # Create deterministic key from arguments
        key_data = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_data += f":{':'.join(f'{k}={v}' for k, v in sorted_kwargs)}"
        
        # Hash long keys to keep them manageable
        if len(key_data) > 100:
            key_hash = hashlib.md5(key_data.encode()).hexdigest()[:8]
            key_data = f"{prefix}:hash:{key_hash}"
        
        return key_data
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (Redis first, then memory)"""
        try:
            # Try Redis first
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            
            # Fallback to memory cache
            if key in self.memory_cache:
                # Check if expired
                if key in self.memory_cache_ttl:
                    if datetime.now() > self.memory_cache_ttl[key]:
                        del self.memory_cache[key]
                        del self.memory_cache_ttl[key]
                        return None
                return self.memory_cache[key]
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache (both Redis and memory)"""
        if ttl is None:
            ttl = self.default_ttl
        
        try:
            serialized_value = json.dumps(value, default=str)
            
            # Store in Redis
            if self.redis_client:
                self.redis_client.setex(key, ttl, serialized_value)
            
            # Store in memory as backup
            self.memory_cache[key] = value
            self.memory_cache_ttl[key] = datetime.now() + timedelta(seconds=ttl)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            
            if key in self.memory_cache:
                del self.memory_cache[key]
            if key in self.memory_cache_ttl:
                del self.memory_cache_ttl[key]
            
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        deleted = 0
        try:
            # Redis pattern deletion
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    deleted += self.redis_client.delete(*keys)
            
            # Memory cache pattern deletion
            memory_keys = [k for k in self.memory_cache.keys() if self._match_pattern(k, pattern)]
            for key in memory_keys:
                del self.memory_cache[key]
                if key in self.memory_cache_ttl:
                    del self.memory_cache_ttl[key]
                deleted += 1
            
        except Exception as e:
            logger.error(f"Cache pattern delete error for pattern {pattern}: {e}")
        
        return deleted
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Simple pattern matching for memory cache"""
        if '*' not in pattern:
            return key == pattern
        
        # Convert Redis-style pattern to simple matching
        import re
        regex_pattern = pattern.replace('*', '.*')
        return bool(re.match(f"^{regex_pattern}$", key))
    
    def clear_all(self) -> bool:
        """Clear all cache data"""
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            
            self.memory_cache.clear()
            self.memory_cache_ttl.clear()
            
            return True
            
        except Exception as e:
            logger.error(f"Cache clear all error: {e}")
            return False


# Global cache instance
_quest_cache = None

def get_quest_cache() -> QuestCache:
    """Get the global quest cache instance"""
    global _quest_cache
    if _quest_cache is None:
        _quest_cache = QuestCache()
    return _quest_cache

def configure_quest_cache(redis_url: str = None, default_ttl: int = 300):
    """Configure the global quest cache"""
    global _quest_cache
    _quest_cache = QuestCache(redis_url, default_ttl)


# Caching decorators for common quest operations
def cache_quest_data(ttl: int = 300, key_prefix: str = "quest"):
    """Decorator to cache quest data method results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_quest_cache()
            
            # Generate cache key
            cache_key = cache._generate_key(key_prefix, func.__name__, *args[1:], **kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, ttl)
                logger.debug(f"Cached result for {cache_key}")
            
            return result
        return wrapper
    return decorator


def cache_quest_list(ttl: int = 120, key_prefix: str = "quest_list"):
    """Decorator specifically for quest list queries"""
    return cache_quest_data(ttl, key_prefix)


def cache_quest_stats(ttl: int = 600, key_prefix: str = "quest_stats"):
    """Decorator for quest statistics (longer TTL)"""
    return cache_quest_data(ttl, key_prefix)


def invalidate_quest_cache(quest_id: str = None, player_id: str = None, npc_id: str = None):
    """Invalidate quest-related cache entries"""
    cache = get_quest_cache()
    
    patterns_to_clear = []
    
    if quest_id:
        patterns_to_clear.extend([
            f"quest:*:{quest_id}*",
            f"quest_list:*:{quest_id}*",
            f"quest_steps:*:{quest_id}*"
        ])
    
    if player_id:
        patterns_to_clear.extend([
            f"quest:*:{player_id}*",
            f"quest_list:*:{player_id}*",
            f"player_quests:*:{player_id}*"
        ])
    
    if npc_id:
        patterns_to_clear.extend([
            f"quest:*:{npc_id}*",
            f"quest_list:*:{npc_id}*",
            f"npc_quests:*:{npc_id}*"
        ])
    
    # Always clear general stats that might be affected
    patterns_to_clear.extend([
        "quest_stats:*",
        "quest_count:*",
        "available_quests:*"
    ])
    
    for pattern in patterns_to_clear:
        try:
            deleted = cache.delete_pattern(pattern)
            if deleted > 0:
                logger.debug(f"Invalidated {deleted} cache entries matching {pattern}")
        except Exception as e:
            logger.error(f"Error invalidating cache pattern {pattern}: {e}")


class QuestCacheManager:
    """High-level cache management for quest operations"""
    
    def __init__(self, cache: QuestCache = None):
        self.cache = cache or get_quest_cache()
    
    def get_available_quests(self, player_level: int = None, location_id: str = None, 
                           theme: str = None, difficulty: str = None) -> Optional[List[Dict]]:
        """Get cached available quests with filters"""
        key = self.cache._generate_key(
            "available_quests", 
            player_level=player_level,
            location_id=location_id,
            theme=theme,
            difficulty=difficulty
        )
        return self.cache.get(key)
    
    def cache_available_quests(self, quests: List[Dict], player_level: int = None, 
                             location_id: str = None, theme: str = None, 
                             difficulty: str = None, ttl: int = 120):
        """Cache available quests with filters"""
        key = self.cache._generate_key(
            "available_quests", 
            player_level=player_level,
            location_id=location_id,
            theme=theme,
            difficulty=difficulty
        )
        self.cache.set(key, quests, ttl)
    
    def get_player_quests(self, player_id: str, status: str = None) -> Optional[List[Dict]]:
        """Get cached player quests"""
        key = self.cache._generate_key("player_quests", player_id, status=status)
        return self.cache.get(key)
    
    def cache_player_quests(self, player_id: str, quests: List[Dict], 
                          status: str = None, ttl: int = 180):
        """Cache player quests"""
        key = self.cache._generate_key("player_quests", player_id, status=status)
        self.cache.set(key, quests, ttl)
    
    def get_npc_quests(self, npc_id: str) -> Optional[List[Dict]]:
        """Get cached NPC quests"""
        key = self.cache._generate_key("npc_quests", npc_id)
        return self.cache.get(key)
    
    def cache_npc_quests(self, npc_id: str, quests: List[Dict], ttl: int = 300):
        """Cache NPC quests"""
        key = self.cache._generate_key("npc_quests", npc_id)
        self.cache.set(key, quests, ttl)
    
    def get_quest_templates(self, theme: str = None, difficulty: str = None) -> Optional[List[Dict]]:
        """Get cached quest templates"""
        key = self.cache._generate_key("quest_templates", theme=theme, difficulty=difficulty)
        return self.cache.get(key)
    
    def cache_quest_templates(self, templates: List[Dict], theme: str = None, 
                            difficulty: str = None, ttl: int = 3600):
        """Cache quest templates (long TTL since they change rarely)"""
        key = self.cache._generate_key("quest_templates", theme=theme, difficulty=difficulty)
        self.cache.set(key, templates, ttl)
    
    def get_quest_statistics(self) -> Optional[Dict]:
        """Get cached quest statistics"""
        return self.cache.get("quest_statistics:global")
    
    def cache_quest_statistics(self, stats: Dict, ttl: int = 600):
        """Cache quest statistics"""
        self.cache.set("quest_statistics:global", stats, ttl)
    
    def invalidate_player_cache(self, player_id: str):
        """Invalidate all cache entries for a specific player"""
        invalidate_quest_cache(player_id=player_id)
    
    def invalidate_quest_cache(self, quest_id: str):
        """Invalidate all cache entries for a specific quest"""
        invalidate_quest_cache(quest_id=quest_id)
    
    def invalidate_location_cache(self, location_id: str):
        """Invalidate cache entries for a specific location"""
        self.cache.delete_pattern(f"*:*:{location_id}*")
        self.cache.delete_pattern(f"available_quests:*")


# Usage example functions
def example_cached_quest_service():
    """Example of how to integrate caching with quest services"""
    
    class CachedQuestService:
        def __init__(self):
            self.cache_manager = QuestCacheManager()
        
        @cache_quest_data(ttl=300, key_prefix="quest_detail")
        def get_quest_by_id(self, quest_id: str):
            # This would call the actual database/service
            # Result is automatically cached
            pass
        
        @cache_quest_list(ttl=120, key_prefix="available_quests")
        def get_available_quests(self, player_level: int, location_id: str):
            # This would call the actual database/service
            # Result is automatically cached
            pass
        
        def update_quest(self, quest_id: str, updates: Dict):
            # Update the quest
            result = self._update_quest_in_db(quest_id, updates)
            
            # Invalidate relevant cache entries
            invalidate_quest_cache(quest_id=quest_id)
            
            return result
        
        def _update_quest_in_db(self, quest_id: str, updates: Dict):
            # Actual database update logic
            pass


# Configuration constants
CACHE_CONFIG = {
    'DEFAULT_TTL': 300,      # 5 minutes
    'QUEST_DETAIL_TTL': 300, # 5 minutes
    'QUEST_LIST_TTL': 120,   # 2 minutes
    'QUEST_STATS_TTL': 600,  # 10 minutes
    'QUEST_TEMPLATES_TTL': 3600,  # 1 hour
    'PLAYER_QUESTS_TTL': 180,     # 3 minutes
    'NPC_QUESTS_TTL': 300,        # 5 minutes
} 