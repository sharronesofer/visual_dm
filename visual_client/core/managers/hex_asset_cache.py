"""
Cache manager for hex grid assets.
"""

import os
import json
import time
from typing import Dict, Optional, Any, List, Tuple
import pygame
from dataclasses import dataclass
from ..error_handler import handle_component_error, ErrorSeverity

@dataclass
class CacheEntry:
    """Data class for cache entries."""
    surface: pygame.Surface
    timestamp: float
    metadata: Dict[str, Any]

class HexAssetCache:
    """Cache manager for hex grid assets."""
    
    def __init__(self, cache_dir: str, max_size_mb: int = 100):
        """
        Initialize the hex asset cache.
        
        Args:
            cache_dir: Directory to store cached assets
            max_size_mb: Maximum cache size in megabytes
        """
        self.cache_dir = cache_dir
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache: Dict[str, CacheEntry] = {}
        self._ensure_cache_dir()
        
    def _ensure_cache_dir(self) -> None:
        """Create the cache directory if it doesn't exist."""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
        except Exception as e:
            handle_component_error(
                e,
                "HexAssetCache",
                ErrorSeverity.HIGH,
                {"cache_dir": self.cache_dir}
            )
            
    def get(self, key: str) -> Optional[pygame.Surface]:
        """
        Get an asset from the cache.
        
        Args:
            key: Cache key for the asset
            
        Returns:
            The cached surface if found, None otherwise
        """
        try:
            if key in self.cache:
                entry = self.cache[key]
                entry.timestamp = time.time()
                return entry.surface
            return None
        except Exception as e:
            handle_component_error(
                e,
                "HexAssetCache.get",
                ErrorSeverity.MEDIUM,
                {"key": key}
            )
            return None
            
    def put(self, key: str, surface: pygame.Surface, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add an asset to the cache.
        
        Args:
            key: Cache key for the asset
            surface: Surface to cache
            metadata: Optional metadata to store with the asset
            
        Returns:
            True if the asset was cached successfully, False otherwise
        """
        try:
            # Check if we need to make space
            while self._get_cache_size() + self._get_surface_size(surface) > self.max_size_bytes:
                if not self._evict_oldest():
                    return False
                    
            self.cache[key] = CacheEntry(
                surface=surface,
                timestamp=time.time(),
                metadata=metadata or {}
            )
            return True
        except Exception as e:
            handle_component_error(
                e,
                "HexAssetCache.put",
                ErrorSeverity.MEDIUM,
                {"key": key, "metadata": metadata}
            )
            return False
            
    def remove(self, key: str) -> None:
        """
        Remove an asset from the cache.
        
        Args:
            key: Cache key to remove
        """
        try:
            if key in self.cache:
                del self.cache[key]
        except Exception as e:
            handle_component_error(
                e,
                "HexAssetCache.remove",
                ErrorSeverity.LOW,
                {"key": key}
            )
            
    def clear(self) -> None:
        """Clear all assets from the cache."""
        try:
            self.cache.clear()
        except Exception as e:
            handle_component_error(
                e,
                "HexAssetCache.clear",
                ErrorSeverity.MEDIUM
            )
            
    def _get_cache_size(self) -> int:
        """Get the current size of the cache in bytes."""
        try:
            return sum(self._get_surface_size(entry.surface) for entry in self.cache.values())
        except Exception as e:
            handle_component_error(
                e,
                "HexAssetCache._get_cache_size",
                ErrorSeverity.LOW
            )
            return 0
            
    def _get_surface_size(self, surface: pygame.Surface) -> int:
        """Get the size of a surface in bytes."""
        try:
            return surface.get_width() * surface.get_height() * surface.get_bytesize()
        except Exception as e:
            handle_component_error(
                e,
                "HexAssetCache._get_surface_size",
                ErrorSeverity.LOW,
                {"surface": str(surface)}
            )
            return 0
            
    def _evict_oldest(self) -> bool:
        """
        Remove the oldest entry from the cache.
        
        Returns:
            True if an entry was evicted, False if the cache is empty
        """
        try:
            if not self.cache:
                return False
                
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k].timestamp
            )
            del self.cache[oldest_key]
            return True
        except Exception as e:
            handle_component_error(
                e,
                "HexAssetCache._evict_oldest",
                ErrorSeverity.LOW
            )
            return False

    @property
    def current_memory(self) -> int:
        """Return the current cache size in bytes (for test compatibility)."""
        return self._get_cache_size() 

    @property
    def max_memory(self) -> int:
        """Return the maximum cache size in bytes (for test compatibility)."""
        return self.max_size_bytes 