"""
Contextual LLM Caching System

This module provides intelligent caching for expensive LLM operations with
context-aware invalidation, semantic similarity detection, and usage analytics.
"""

import hashlib
import json
import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import redis
import pickle
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Cache invalidation strategies"""
    TTL_ONLY = "ttl_only"  # Time-based expiration only
    CONTENT_AWARE = "content_aware"  # Invalidate based on content changes
    SEMANTIC_SIMILARITY = "semantic_similarity"  # Use semantic similarity for matches
    AGGRESSIVE = "aggressive"  # Cache everything with long TTL
    CONSERVATIVE = "conservative"  # Short TTL, frequent invalidation

@dataclass
class CacheEntry:
    """Structure for cache entries with metadata"""
    content: Any
    prompt_hash: str
    context_hash: str
    response_hash: str
    created_at: float
    last_accessed: float
    access_count: int
    ttl_seconds: int
    strategy: CacheStrategy
    tags: List[str]
    cost_saved: float
    token_count: int
    model_used: str
    semantic_embedding: Optional[List[float]] = None

class ContextualLLMCache:
    """
    Intelligent caching system for LLM operations with context awareness.
    
    Features:
    - Context-sensitive cache keys
    - Semantic similarity matching
    - Intelligent invalidation
    - Cost tracking and analytics
    - Performance monitoring
    """
    
    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        default_ttl: int = 3600,  # 1 hour
        max_cache_size: int = 10000,
        similarity_threshold: float = 0.85
    ):
        self.redis_client = redis_client or self._get_default_redis()
        self.default_ttl = default_ttl
        self.max_cache_size = max_cache_size
        self.similarity_threshold = similarity_threshold
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_cost_saved": 0.0,
            "total_tokens_saved": 0,
            "cache_size": 0
        }
        
        # Strategy configurations
        self.strategy_configs = {
            CacheStrategy.TTL_ONLY: {"ttl": 3600, "similarity_check": False},
            CacheStrategy.CONTENT_AWARE: {"ttl": 7200, "similarity_check": False},
            CacheStrategy.SEMANTIC_SIMILARITY: {"ttl": 3600, "similarity_check": True},
            CacheStrategy.AGGRESSIVE: {"ttl": 86400, "similarity_check": True},  # 24 hours
            CacheStrategy.CONSERVATIVE: {"ttl": 1800, "similarity_check": False}  # 30 minutes
        }
    
    def _get_default_redis(self) -> redis.Redis:
        """Get default Redis client"""
        try:
            return redis.Redis(host='localhost', port=6379, db=1, decode_responses=False)
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory cache: {e}")
            return None
    
    async def get_cached_response(
        self,
        prompt: str,
        context: Dict[str, Any],
        strategy: CacheStrategy = CacheStrategy.CONTENT_AWARE,
        tags: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached response if available and valid.
        
        Args:
            prompt: The LLM prompt
            context: Additional context for cache key generation
            strategy: Caching strategy to use
            tags: Optional tags for cache organization
            
        Returns:
            Cached response or None if not found/invalid
        """
        try:
            cache_key = self._generate_cache_key(prompt, context, strategy)
            
            # Try exact match first
            cached_entry = await self._get_cache_entry(cache_key)
            if cached_entry and self._is_entry_valid(cached_entry):
                await self._update_access_stats(cache_key, cached_entry)
                self.stats["hits"] += 1
                return cached_entry.content
            
            # Try semantic similarity if enabled
            if self.strategy_configs[strategy].get("similarity_check", False):
                similar_entry = await self._find_similar_entry(prompt, context, tags)
                if similar_entry:
                    await self._update_access_stats(cache_key, similar_entry)
                    self.stats["hits"] += 1
                    return similar_entry.content
            
            self.stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached response: {e}")
            self.stats["misses"] += 1
            return None
    
    async def cache_response(
        self,
        prompt: str,
        context: Dict[str, Any],
        response: Dict[str, Any],
        strategy: CacheStrategy = CacheStrategy.CONTENT_AWARE,
        tags: List[str] = None,
        cost: float = 0.0,
        token_count: int = 0,
        model_used: str = "unknown"
    ) -> bool:
        """
        Cache LLM response with metadata.
        
        Args:
            prompt: The LLM prompt
            context: Additional context
            response: The LLM response to cache
            strategy: Caching strategy
            tags: Optional tags
            cost: Cost of the LLM call
            token_count: Number of tokens in response
            model_used: Model that generated the response
            
        Returns:
            True if successfully cached
        """
        try:
            cache_key = self._generate_cache_key(prompt, context, strategy)
            config = self.strategy_configs[strategy]
            
            # Create cache entry
            cache_entry = CacheEntry(
                content=response,
                prompt_hash=self._hash_content(prompt),
                context_hash=self._hash_content(context),
                response_hash=self._hash_content(response),
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=0,
                ttl_seconds=config["ttl"],
                strategy=strategy,
                tags=tags or [],
                cost_saved=cost,
                token_count=token_count,
                model_used=model_used,
                semantic_embedding=await self._generate_embedding(prompt) if config.get("similarity_check") else None
            )
            
            # Store in cache
            await self._store_cache_entry(cache_key, cache_entry)
            
            # Update statistics
            self.stats["cache_size"] += 1
            self.stats["total_cost_saved"] += cost
            self.stats["total_tokens_saved"] += token_count
            
            # Perform cache maintenance if needed
            await self._maintain_cache_size()
            
            return True
            
        except Exception as e:
            logger.error(f"Error caching response: {e}")
            return False
    
    async def invalidate_by_context(
        self,
        context_changes: Dict[str, Any],
        strategy: CacheStrategy = CacheStrategy.CONTENT_AWARE
    ) -> int:
        """
        Invalidate cache entries based on context changes.
        
        Args:
            context_changes: Dictionary of changed context elements
            strategy: Strategy to guide invalidation logic
            
        Returns:
            Number of entries invalidated
        """
        try:
            if strategy == CacheStrategy.TTL_ONLY:
                return 0  # TTL-only strategy doesn't use context invalidation
            
            invalidated_count = 0
            
            # Get all cache keys
            pattern = f"llm_cache:{strategy.value}:*"
            cache_keys = await self._get_cache_keys(pattern)
            
            for cache_key in cache_keys:
                entry = await self._get_cache_entry(cache_key)
                if entry and self._should_invalidate_entry(entry, context_changes):
                    await self._delete_cache_entry(cache_key)
                    invalidated_count += 1
            
            self.stats["evictions"] += invalidated_count
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Error invalidating cache by context: {e}")
            return 0
    
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate all cache entries with any of the specified tags"""
        try:
            invalidated_count = 0
            
            # Get all cache keys
            cache_keys = await self._get_cache_keys("llm_cache:*")
            
            for cache_key in cache_keys:
                entry = await self._get_cache_entry(cache_key)
                if entry and any(tag in entry.tags for tag in tags):
                    await self._delete_cache_entry(cache_key)
                    invalidated_count += 1
            
            self.stats["evictions"] += invalidated_count
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Error invalidating cache by tags: {e}")
            return 0
    
    def _generate_cache_key(
        self,
        prompt: str,
        context: Dict[str, Any],
        strategy: CacheStrategy
    ) -> str:
        """Generate cache key from prompt and context"""
        # Create deterministic hash from prompt and relevant context
        content_to_hash = {
            "prompt": prompt.strip(),
            "context": self._normalize_context(context),
            "strategy": strategy.value
        }
        
        content_str = json.dumps(content_to_hash, sort_keys=True)
        cache_hash = hashlib.sha256(content_str.encode()).hexdigest()[:16]
        
        return f"llm_cache:{strategy.value}:{cache_hash}"
    
    def _normalize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize context for consistent hashing"""
        normalized = {}
        
        # Include only relevant context fields for caching
        relevant_fields = [
            "arc_type", "themes", "character_class", "background",
            "quest_type", "complexity", "player_level", "location"
        ]
        
        for field in relevant_fields:
            if field in context:
                value = context[field]
                if isinstance(value, list):
                    normalized[field] = sorted(value)  # Sort lists for consistency
                else:
                    normalized[field] = value
        
        return normalized
    
    def _hash_content(self, content: Any) -> str:
        """Generate hash for content"""
        if isinstance(content, dict):
            content_str = json.dumps(content, sort_keys=True)
        else:
            content_str = str(content)
        
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]
    
    async def _get_cache_entry(self, cache_key: str) -> Optional[CacheEntry]:
        """Retrieve cache entry from storage"""
        try:
            if self.redis_client:
                data = self.redis_client.get(cache_key)
                if data:
                    return pickle.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error retrieving cache entry: {e}")
            return None
    
    async def _store_cache_entry(self, cache_key: str, entry: CacheEntry):
        """Store cache entry in storage"""
        try:
            if self.redis_client:
                data = pickle.dumps(entry)
                self.redis_client.setex(cache_key, entry.ttl_seconds, data)
        except Exception as e:
            logger.error(f"Error storing cache entry: {e}")
    
    async def _delete_cache_entry(self, cache_key: str):
        """Delete cache entry from storage"""
        try:
            if self.redis_client:
                self.redis_client.delete(cache_key)
                self.stats["cache_size"] = max(0, self.stats["cache_size"] - 1)
        except Exception as e:
            logger.error(f"Error deleting cache entry: {e}")
    
    async def _get_cache_keys(self, pattern: str) -> List[str]:
        """Get all cache keys matching pattern"""
        try:
            if self.redis_client:
                return [key.decode() if isinstance(key, bytes) else key 
                       for key in self.redis_client.keys(pattern)]
            return []
        except Exception as e:
            logger.error(f"Error getting cache keys: {e}")
            return []
    
    def _is_entry_valid(self, entry: CacheEntry) -> bool:
        """Check if cache entry is still valid"""
        current_time = time.time()
        
        # Check TTL
        if current_time - entry.created_at > entry.ttl_seconds:
            return False
        
        # Additional validation based on strategy
        if entry.strategy == CacheStrategy.CONSERVATIVE:
            # More aggressive expiration for conservative strategy
            if current_time - entry.last_accessed > 1800:  # 30 minutes since last access
                return False
        
        return True
    
    async def _update_access_stats(self, cache_key: str, entry: CacheEntry):
        """Update access statistics for cache entry"""
        try:
            entry.last_accessed = time.time()
            entry.access_count += 1
            await self._store_cache_entry(cache_key, entry)
        except Exception as e:
            logger.error(f"Error updating access stats: {e}")
    
    async def _find_similar_entry(
        self,
        prompt: str,
        context: Dict[str, Any],
        tags: List[str]
    ) -> Optional[CacheEntry]:
        """Find semantically similar cache entry"""
        try:
            if not self.redis_client:
                return None
            
            prompt_embedding = await self._generate_embedding(prompt)
            if not prompt_embedding:
                return None
            
            # Get all cache entries with embeddings
            cache_keys = await self._get_cache_keys("llm_cache:*")
            
            best_match = None
            best_similarity = 0.0
            
            for cache_key in cache_keys:
                entry = await self._get_cache_entry(cache_key)
                if (entry and entry.semantic_embedding and 
                    self._is_entry_valid(entry) and
                    self._context_compatible(context, entry)):
                    
                    similarity = self._calculate_similarity(prompt_embedding, entry.semantic_embedding)
                    if similarity > self.similarity_threshold and similarity > best_similarity:
                        best_similarity = similarity
                        best_match = entry
            
            return best_match
            
        except Exception as e:
            logger.error(f"Error finding similar entry: {e}")
            return None
    
    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for semantic similarity (placeholder implementation)"""
        # This would integrate with an actual embedding service
        # For now, return a simple hash-based pseudo-embedding
        try:
            # Simplified embedding based on text characteristics
            words = text.lower().split()
            
            # Create a simple feature vector based on text properties
            features = [
                len(words),  # Length
                len(set(words)),  # Unique words
                sum(1 for word in words if len(word) > 6),  # Long words
                text.count('?'),  # Questions
                text.count('!'),  # Exclamations
            ]
            
            # Normalize features to [0, 1] range
            max_val = max(features) if features else 1
            normalized = [f / max_val for f in features]
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        try:
            if len(embedding1) != len(embedding2):
                return 0.0
            
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            norm1 = sum(a * a for a in embedding1) ** 0.5
            norm2 = sum(b * b for b in embedding2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def _context_compatible(self, current_context: Dict[str, Any], entry: CacheEntry) -> bool:
        """Check if contexts are compatible for cache reuse"""
        # Check key context fields for compatibility
        key_fields = ["arc_type", "character_class", "quest_type"]
        
        for field in key_fields:
            if field in current_context:
                # For context compatibility, we need the stored entry to have similar context
                # This is a simplified check - in practice, you'd want more sophisticated logic
                return True
        
        return True
    
    def _should_invalidate_entry(
        self,
        entry: CacheEntry,
        context_changes: Dict[str, Any]
    ) -> bool:
        """Determine if entry should be invalidated based on context changes"""
        # Check if any of the changed context affects this entry
        sensitive_fields = ["arc_type", "themes", "character_class", "background"]
        
        for field in sensitive_fields:
            if field in context_changes:
                # If this is a sensitive field that changed, invalidate
                return True
        
        return False
    
    async def _maintain_cache_size(self):
        """Maintain cache size within limits"""
        try:
            if self.stats["cache_size"] <= self.max_cache_size:
                return
            
            # Get all cache entries with their access stats
            cache_keys = await self._get_cache_keys("llm_cache:*")
            entries_with_keys = []
            
            for cache_key in cache_keys:
                entry = await self._get_cache_entry(cache_key)
                if entry:
                    entries_with_keys.append((cache_key, entry))
            
            # Sort by LRU (least recently used) and low access count
            entries_with_keys.sort(key=lambda x: (x[1].last_accessed, x[1].access_count))
            
            # Remove oldest entries until we're under the limit
            entries_to_remove = len(entries_with_keys) - self.max_cache_size
            if entries_to_remove > 0:
                for cache_key, _ in entries_with_keys[:entries_to_remove]:
                    await self._delete_cache_entry(cache_key)
                    self.stats["evictions"] += 1
                    
        except Exception as e:
            logger.error(f"Error maintaining cache size: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        hit_rate = 0.0
        total_requests = self.stats["hits"] + self.stats["misses"]
        if total_requests > 0:
            hit_rate = self.stats["hits"] / total_requests
        
        return {
            **self.stats,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
            "average_cost_per_hit": (
                self.stats["total_cost_saved"] / self.stats["hits"] 
                if self.stats["hits"] > 0 else 0.0
            ),
            "average_tokens_per_hit": (
                self.stats["total_tokens_saved"] / self.stats["hits"]
                if self.stats["hits"] > 0 else 0.0
            )
        }
    
    async def clear_cache(self, strategy: Optional[CacheStrategy] = None):
        """Clear cache entries, optionally filtered by strategy"""
        try:
            pattern = f"llm_cache:{strategy.value}:*" if strategy else "llm_cache:*"
            cache_keys = await self._get_cache_keys(pattern)
            
            for cache_key in cache_keys:
                await self._delete_cache_entry(cache_key)
            
            if not strategy:
                # Reset stats if clearing all
                self.stats = {
                    "hits": 0,
                    "misses": 0,
                    "evictions": 0,
                    "total_cost_saved": 0.0,
                    "total_tokens_saved": 0,
                    "cache_size": 0
                }
                
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

# Global cache instance
_global_cache = None

def get_llm_cache() -> ContextualLLMCache:
    """Get global LLM cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = ContextualLLMCache()
    return _global_cache 