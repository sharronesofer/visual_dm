"""
Caching system for the dialogue module.

This module provides caching functionality for dialogue responses,
context, and information extraction to improve performance.
"""

from typing import Optional, Dict, Any


class DialogueCache:
    """
    Cache for dialogue data to improve performance and reduce redundant processing.
    """
    def __init__(self):
        self.response_cache = {}
        self.context_cache = {}
        self.extraction_cache = {}
    
    def get_cached_response(self, key: str) -> Optional[str]:
        """Get a cached response if available."""
        return self.response_cache.get(key)
    
    def cache_response(self, key: str, response: str):
        """Cache a response for future use."""
        self.response_cache[key] = response
    
    def get_cached_context(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached context if available."""
        return self.context_cache.get(key)
    
    def cache_context(self, key: str, context: Dict[str, Any]):
        """Cache context for future use."""
        self.context_cache[key] = context
    
    def get_cached_extraction(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached information extraction if available."""
        return self.extraction_cache.get(key)
    
    def cache_extraction(self, key: str, extraction: Dict[str, Any]):
        """Cache information extraction for future use."""
        self.extraction_cache[key] = extraction
    
    def clear(self):
        """Clear all caches."""
        self.response_cache.clear()
        self.context_cache.clear()
        self.extraction_cache.clear() 