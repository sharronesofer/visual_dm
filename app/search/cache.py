"""Cache implementation for search results."""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import hashlib
import json
from datetime import datetime, timedelta

from .models import EntityType
from .pagination import PaginationParams, PaginatedResponse

@dataclass
class CacheKey:
    """Key for caching search results.
    
    Attributes:
        query: Search query string
        entity_type: Type of entity being searched
        filters: Applied filters
        pagination: Pagination parameters
        sort_fields: Sort field configuration
    """
    query: str
    entity_type: Optional[EntityType] = None
    filters: Optional[Dict[str, Any]] = None
    pagination: Optional[PaginationParams] = None
    sort_fields: Optional[List[Dict[str, str]]] = None

    def __hash__(self) -> int:
        """Generate a stable hash for the cache key."""
        key_dict = {
            "query": self.query,
            "entity_type": self.entity_type.value if self.entity_type else None,
            "filters": json.dumps(self.filters, sort_keys=True) if self.filters else None,
            "pagination": {
                "limit": self.pagination.limit if self.pagination else None,
                # Only include cursor/page if present
                **({"cursor": self.pagination.cursor} if hasattr(self.pagination, "cursor") and self.pagination.cursor else {}),
                **({"page": self.pagination.page} if hasattr(self.pagination, "page") else {})
            } if self.pagination else None,
            "sort_fields": json.dumps(self.sort_fields, sort_keys=True) if self.sort_fields else None
        }
        key_str = json.dumps(key_dict, sort_keys=True)
        return int(hashlib.sha1(key_str.encode()).hexdigest(), 16)

class CacheEntry:
    """Entry in the search cache.
    
    Attributes:
        result: Cached search result
        timestamp: When the entry was cached
        ttl: Time-to-live in seconds
    """
    def __init__(self, result: PaginatedResponse, ttl: int = 300):
        self.result = result
        self.timestamp = datetime.now()
        self.ttl = ttl

    @property
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl)

class SearchCache:
    """Cache for search results.
    
    Implements a simple in-memory LRU cache with TTL support.
    """
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """Initialize the cache.
        
        Args:
            max_size: Maximum number of entries to store
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[int, CacheEntry] = {}
        self._access_order: List[int] = []

    def get(self, key: CacheKey) -> Optional[PaginatedResponse]:
        """Get a cached result if available and not expired.
        
        Args:
            key: Cache key to look up
            
        Returns:
            Cached paginated response or None if not found/expired
        """
        key_hash = hash(key)
        entry = self._cache.get(key_hash)
        
        if entry is None or entry.is_expired:
            # Remove expired entry if it exists
            if entry is not None:
                self._remove_entry(key_hash)
            return None
            
        # Update access order
        self._access_order.remove(key_hash)
        self._access_order.append(key_hash)
        
        return entry.result

    def set(self, key: CacheKey, result: PaginatedResponse, ttl: Optional[int] = None) -> None:
        """Cache a search result.
        
        Args:
            key: Cache key to store under
            result: Search result to cache
            ttl: Optional custom time-to-live in seconds
        """
        key_hash = hash(key)
        
        # Remove existing entry if present
        self._remove_entry(key_hash)
        
        # Add new entry
        self._cache[key_hash] = CacheEntry(result, ttl or self.default_ttl)
        self._access_order.append(key_hash)
        
        # Enforce max size
        while len(self._cache) > self.max_size:
            self._remove_oldest()

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
        self._access_order.clear()

    def _remove_entry(self, key_hash: int) -> None:
        """Remove a cache entry and its access record."""
        if key_hash in self._cache:
            del self._cache[key_hash]
        if key_hash in self._access_order:
            self._access_order.remove(key_hash)

    def _remove_oldest(self) -> None:
        """Remove the least recently accessed cache entry."""
        if self._access_order:
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key] 