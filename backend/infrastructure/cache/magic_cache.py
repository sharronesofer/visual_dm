"""
Magic System Caching Layer

Provides Redis-based caching for frequently accessed magic system data:
- Spell definitions and configurations
- Character MP status
- Domain access permissions  
- Active concentration effects
- Metamagic and combination calculations

Implements intelligent cache invalidation and warming strategies.
"""

import json
import pickle
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import redis
import hashlib

@dataclass
class CacheConfig:
    """Cache configuration settings"""
    redis_url: str = "redis://localhost:6379/0"
    default_ttl: int = 3600  # 1 hour
    spell_ttl: int = 3600    # 1 hour (spells rarely change)
    character_mp_ttl: int = 300  # 5 minutes (MP changes frequently)
    domain_access_ttl: int = 1800  # 30 minutes (domain access changes rarely)
    concentration_ttl: int = 60   # 1 minute (concentration effects are dynamic)
    metamagic_calc_ttl: int = 900  # 15 minutes (calculations are expensive)
    enabled: bool = True

class MagicCache:
    """Redis-based cache for magic system data"""
    
    def __init__(self, config: CacheConfig = None):
        self.config = config or CacheConfig()
        self.redis_client = None
        
        if self.config.enabled:
            try:
                self.redis_client = redis.from_url(self.config.redis_url)
                # Test connection
                self.redis_client.ping()
            except Exception as e:
                print(f"Redis connection failed: {e}. Caching disabled.")
                self.config.enabled = False
    
    def _make_key(self, prefix: str, *args) -> str:
        """Create a cache key from prefix and arguments"""
        key_parts = [prefix] + [str(arg) for arg in args]
        return ":".join(key_parts)
    
    def _hash_data(self, data: Any) -> str:
        """Create a hash of data for cache keys"""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True)
        else:
            data_str = str(data)
        return hashlib.md5(data_str.encode()).hexdigest()[:8]
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.config.enabled or not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
        except Exception as e:
            print(f"Cache get error for key {key}: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        if not self.config.enabled or not self.redis_client:
            return False
        
        try:
            ttl = ttl or self.config.default_ttl
            pickled_value = pickle.dumps(value)
            return self.redis_client.setex(key, ttl, pickled_value)
        except Exception as e:
            print(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.config.enabled or not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Cache delete error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.config.enabled or not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    # === SPELL CACHING ===
    
    def get_spell(self, spell_id: str) -> Optional[Dict[str, Any]]:
        """Get spell data from cache"""
        key = self._make_key("spell", spell_id)
        return self.get(key)
    
    def set_spell(self, spell_id: str, spell_data: Dict[str, Any]) -> bool:
        """Cache spell data"""
        key = self._make_key("spell", spell_id)
        return self.set(key, spell_data, self.config.spell_ttl)
    
    def get_spells_by_domain(self, domain: str) -> Optional[List[Dict[str, Any]]]:
        """Get spells for domain from cache"""
        key = self._make_key("spells_domain", domain)
        return self.get(key)
    
    def set_spells_by_domain(self, domain: str, spells: List[Dict[str, Any]]) -> bool:
        """Cache spells for domain"""
        key = self._make_key("spells_domain", domain)
        return self.set(key, spells, self.config.spell_ttl)
    
    def invalidate_spell_cache(self, spell_id: str = None):
        """Invalidate spell-related cache entries"""
        if spell_id:
            self.delete(self._make_key("spell", spell_id))
        
        # Invalidate domain-based spell caches
        self.delete_pattern("spells_domain:*")
        self.delete_pattern("available_spells:*")
    
    # === CHARACTER MP CACHING ===
    
    def get_character_mp(self, character_id: int) -> Optional[Dict[str, Any]]:
        """Get character MP data from cache"""
        key = self._make_key("character_mp", character_id)
        return self.get(key)
    
    def set_character_mp(self, character_id: int, mp_data: Dict[str, Any]) -> bool:
        """Cache character MP data"""
        key = self._make_key("character_mp", character_id)
        return self.set(key, mp_data, self.config.character_mp_ttl)
    
    def invalidate_character_mp(self, character_id: int):
        """Invalidate character MP cache"""
        key = self._make_key("character_mp", character_id)
        self.delete(key)
    
    # === DOMAIN ACCESS CACHING ===
    
    def get_domain_access(self, character_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get character domain access from cache"""
        key = self._make_key("domain_access", character_id)
        return self.get(key)
    
    def set_domain_access(self, character_id: int, domains: List[Dict[str, Any]]) -> bool:
        """Cache character domain access"""
        key = self._make_key("domain_access", character_id)
        return self.set(key, domains, self.config.domain_access_ttl)
    
    def invalidate_domain_access(self, character_id: int):
        """Invalidate character domain access cache"""
        key = self._make_key("domain_access", character_id)
        self.delete(key)
    
    # === LEARNED SPELLS CACHING ===
    
    def get_learned_spells(self, character_id: int, domain: str = None) -> Optional[List[Dict[str, Any]]]:
        """Get character's learned spells from cache"""
        if domain:
            key = self._make_key("learned_spells", character_id, domain)
        else:
            key = self._make_key("learned_spells", character_id)
        return self.get(key)
    
    def set_learned_spells(self, character_id: int, spells: List[Dict[str, Any]], domain: str = None) -> bool:
        """Cache character's learned spells"""
        if domain:
            key = self._make_key("learned_spells", character_id, domain)
        else:
            key = self._make_key("learned_spells", character_id)
        return self.set(key, spells, self.config.spell_ttl)
    
    def invalidate_learned_spells(self, character_id: int):
        """Invalidate character's learned spells cache"""
        self.delete_pattern(f"learned_spells:{character_id}:*")
        self.delete(self._make_key("learned_spells", character_id))
    
    # === CONCENTRATION CACHING ===
    
    def get_concentration_effects(self, character_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get active concentration effects from cache"""
        key = self._make_key("concentration", character_id)
        return self.get(key)
    
    def set_concentration_effects(self, character_id: int, effects: List[Dict[str, Any]]) -> bool:
        """Cache active concentration effects"""
        key = self._make_key("concentration", character_id)
        return self.set(key, effects, self.config.concentration_ttl)
    
    def invalidate_concentration(self, character_id: int):
        """Invalidate concentration effects cache"""
        key = self._make_key("concentration", character_id)
        self.delete(key)
    
    # === METAMAGIC CALCULATIONS CACHING ===
    
    def get_metamagic_calculation(self, spell_properties: Dict[str, Any], metamagic_types: List[str]) -> Optional[Dict[str, Any]]:
        """Get cached metamagic calculation result"""
        calc_hash = self._hash_data({
            "spell": spell_properties,
            "metamagic": sorted(metamagic_types)
        })
        key = self._make_key("metamagic_calc", calc_hash)
        return self.get(key)
    
    def set_metamagic_calculation(self, spell_properties: Dict[str, Any], metamagic_types: List[str], result: Dict[str, Any]) -> bool:
        """Cache metamagic calculation result"""
        calc_hash = self._hash_data({
            "spell": spell_properties,
            "metamagic": sorted(metamagic_types)
        })
        key = self._make_key("metamagic_calc", calc_hash)
        return self.set(key, result, self.config.metamagic_calc_ttl)
    
    # === SPELL COMBINATION CACHING ===
    
    def get_combination_calculation(self, spell_names: List[str], combination_name: str) -> Optional[Dict[str, Any]]:
        """Get cached combination calculation result"""
        calc_hash = self._hash_data({
            "spells": sorted(spell_names),
            "combination": combination_name
        })
        key = self._make_key("combination_calc", calc_hash)
        return self.get(key)
    
    def set_combination_calculation(self, spell_names: List[str], combination_name: str, result: Dict[str, Any]) -> bool:
        """Cache combination calculation result"""
        calc_hash = self._hash_data({
            "spells": sorted(spell_names),
            "combination": combination_name
        })
        key = self._make_key("combination_calc", calc_hash)
        return self.set(key, result, self.config.metamagic_calc_ttl)
    
    # === CACHE WARMING ===
    
    def warm_spell_cache(self, spells: List[Dict[str, Any]]):
        """Warm the cache with common spell data"""
        for spell in spells:
            if "id" in spell:
                self.set_spell(spell["id"], spell)
    
    def warm_character_cache(self, character_id: int, mp_data: Dict[str, Any], 
                           domain_access: List[Dict[str, Any]], 
                           learned_spells: List[Dict[str, Any]]):
        """Warm cache with character data"""
        self.set_character_mp(character_id, mp_data)
        self.set_domain_access(character_id, domain_access)
        self.set_learned_spells(character_id, learned_spells)
    
    # === BATCH OPERATIONS ===
    
    def batch_get(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple keys in a single operation"""
        if not self.config.enabled or not self.redis_client:
            return {}
        
        try:
            pipe = self.redis_client.pipeline()
            for key in keys:
                pipe.get(key)
            
            results = pipe.execute()
            
            result_dict = {}
            for i, key in enumerate(keys):
                if results[i]:
                    try:
                        result_dict[key] = pickle.loads(results[i])
                    except Exception:
                        pass
            
            return result_dict
        except Exception as e:
            print(f"Batch get error: {e}")
            return {}
    
    def batch_set(self, key_value_ttl_tuples: List[tuple]) -> List[bool]:
        """Set multiple key-value pairs in a single operation"""
        if not self.config.enabled or not self.redis_client:
            return [False] * len(key_value_ttl_tuples)
        
        try:
            pipe = self.redis_client.pipeline()
            for item in key_value_ttl_tuples:
                if len(item) == 3:
                    key, value, ttl = item
                else:
                    key, value = item
                    ttl = self.config.default_ttl
                
                pickled_value = pickle.dumps(value)
                pipe.setex(key, ttl, pickled_value)
            
            results = pipe.execute()
            return results
        except Exception as e:
            print(f"Batch set error: {e}")
            return [False] * len(key_value_ttl_tuples)
    
    # === CACHE STATISTICS ===
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache usage statistics"""
        if not self.config.enabled or not self.redis_client:
            return {"enabled": False}
        
        try:
            info = self.redis_client.info()
            
            # Count keys by type
            spell_keys = len(self.redis_client.keys("spell:*"))
            character_keys = len(self.redis_client.keys("character_mp:*"))
            domain_keys = len(self.redis_client.keys("domain_access:*"))
            concentration_keys = len(self.redis_client.keys("concentration:*"))
            calc_keys = len(self.redis_client.keys("*_calc:*"))
            
            return {
                "enabled": True,
                "total_keys": info.get("db0", {}).get("keys", 0),
                "memory_used": info.get("used_memory_human"),
                "key_counts": {
                    "spells": spell_keys,
                    "characters": character_keys,
                    "domains": domain_keys,
                    "concentration": concentration_keys,
                    "calculations": calc_keys
                },
                "hit_rate": "N/A",  # Would need custom tracking
                "config": asdict(self.config)
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}

# Global cache instance
_magic_cache = None

def get_magic_cache() -> MagicCache:
    """Get the global magic cache instance"""
    global _magic_cache
    if _magic_cache is None:
        _magic_cache = MagicCache()
    return _magic_cache

def configure_magic_cache(config: CacheConfig):
    """Configure the global magic cache"""
    global _magic_cache
    _magic_cache = MagicCache(config)

# Cache decorators for easy use
def cached_spell(ttl: int = None):
    """Decorator to cache spell-related function results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache = get_magic_cache()
            if not cache.config.enabled:
                return func(*args, **kwargs)
            
            # Create cache key from function name and arguments
            key = f"func:{func.__name__}:{cache._hash_data((args, kwargs))}"
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, ttl or cache.config.spell_ttl)
            return result
        
        return wrapper
    return decorator 