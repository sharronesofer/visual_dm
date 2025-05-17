import time
from typing import Dict, List, Optional, TypedDict, Union, Callable
import json
import logging
from .types import DialogueMetadata

logger = logging.getLogger(__name__)

class CacheEntry(TypedDict):
    """A single cache entry with response and metadata."""
    key: str
    response: str
    metadata: DialogueMetadata
    timestamp: int

class CacheAnalytics(TypedDict):
    """Analytics data for cache performance."""
    hits: int
    misses: int
    mostFrequent: Dict[str, int]

class ResponseCacheConfig(TypedDict, total=False):
    """Configuration for the response cache."""
    maxSize: Optional[int]
    expiryMs: Optional[int]
    redisUrl: Optional[str]  # For Redis implementation

class ResponseCacheManager:
    """
    ResponseCacheManager caches dialogue responses to reduce API usage and improve response times.
    Provides analytics and pre-warming capabilities.
    """
    
    def __init__(self, config: Optional[ResponseCacheConfig] = None):
        """
        Initialize the cache manager with configuration.
        
        Args:
            config: Optional configuration for cache behavior
        """
        if config is None:
            config = {}
            
        self.config = {
            'maxSize': config.get('maxSize', 1000),
            'expiryMs': config.get('expiryMs', 5 * 60 * 1000),  # 5 minutes
        }
        
        # In-memory cache implementation
        self.cache: Dict[str, CacheEntry] = {}
        self.analytics: CacheAnalytics = {'hits': 0, 'misses': 0, 'mostFrequent': {}}
    
    @staticmethod
    def make_key(prompt: str, context: List[str]) -> str:
        """
        Generates a cache key from prompt and context.
        
        Args:
            prompt: The prompt string
            context: List of context strings
            
        Returns:
            A string key for cache lookups
        """
        # Simple hash combining prompt and context
        return f"{prompt}::{','.join(context)}"
    
    def get(self, prompt: str, context: List[str]) -> Optional[str]:
        """
        Retrieves a cached response if valid, or None if not found/expired.
        
        Args:
            prompt: The prompt string
            context: List of context strings
            
        Returns:
            The cached response string or None
        """
        key = self.make_key(prompt, context)
        entry = self.cache.get(key)
        
        if entry and (time.time() * 1000) - entry['timestamp'] < self.config['expiryMs']:
            # Valid cache hit
            self.analytics['hits'] += 1
            self.analytics['mostFrequent'][key] = self.analytics['mostFrequent'].get(key, 0) + 1
            return entry['response']
        else:
            # Cache miss or expired
            if entry:
                # Remove expired entry
                del self.cache[key]
            
            self.analytics['misses'] += 1
            return None
    
    def set(self, prompt: str, context: List[str], response: str, metadata: DialogueMetadata):
        """
        Stores a response in the cache.
        
        Args:
            prompt: The prompt string
            context: List of context strings
            response: The response to cache
            metadata: Metadata about the response
        """
        key = self.make_key(prompt, context)
        
        # Enforce max size limit (FIFO)
        if len(self.cache) >= self.config['maxSize']:
            # Remove oldest entry (first in dictionary)
            if self.cache:
                oldest_key = next(iter(self.cache.keys()))
                del self.cache[oldest_key]
        
        # Store entry
        self.cache[key] = {
            'key': key,
            'response': response,
            'metadata': metadata,
            'timestamp': int(time.time() * 1000)
        }
    
    def clear(self):
        """Clears the cache and resets analytics."""
        self.cache.clear()
        self.analytics = {'hits': 0, 'misses': 0, 'mostFrequent': {}}
    
    def invalidate(self, predicate: Callable[[CacheEntry], bool]):
        """
        Invalidates cache entries based on a predicate function.
        
        Args:
            predicate: Function that returns True for entries to invalidate
        """
        keys_to_remove = []
        for key, entry in self.cache.items():
            if predicate(entry):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.cache[key]
    
    def get_analytics(self) -> CacheAnalytics:
        """
        Returns analytics data.
        
        Returns:
            Copy of the current analytics data
        """
        return dict(self.analytics)
    
    def get_keys(self) -> List[str]:
        """
        Returns all cache keys (for inspection/testing).
        
        Returns:
            List of all cache keys
        """
        return list(self.cache.keys())
    
    def prewarm(self, entries: List[Dict[str, Union[str, List[str], DialogueMetadata]]]):
        """
        Pre-warms the cache with anticipated dialogue paths.
        
        Args:
            entries: List of entries to add to the cache
        """
        for entry in entries:
            # Type assertions
            prompt = entry['prompt']
            context = entry['context']
            response = entry['response']
            metadata = entry['metadata']
            
            if not isinstance(prompt, str) or not isinstance(response, str):
                continue
                
            # Handle context type variations
            if isinstance(context, list):
                context_list = context
            else:
                context_list = []
                
            self.set(prompt, context_list, response, metadata) 