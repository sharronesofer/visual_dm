import time
import threading
from collections import OrderedDict, Counter
from typing import Any, Dict, Optional, Callable, List

class DialogueCache:
    """
    Caching layer for dialogue responses with TTL, LRU eviction, analytics, and pre-warming support.
    Thread-safe for concurrent access.
    """
    def __init__(self, max_size: int = 1000, ttl: int = 600):
        """
        :param max_size: Maximum number of items in cache (LRU eviction)
        :param ttl: Time-to-live for cache entries in seconds
        """
        self.max_size = max_size
        self.ttl = ttl
        self._lock = threading.RLock()
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._timestamps: Dict[str, float] = {}
        self._hits = 0
        self._misses = 0
        self._access_counter = Counter()

    def _evict_expired(self):
        now = time.time()
        keys_to_delete = [k for k, t in self._timestamps.items() if now - t > self.ttl]
        for k in keys_to_delete:
            self._cache.pop(k, None)
            self._timestamps.pop(k, None)
            self._access_counter.pop(k, None)

    def _evict_lru(self):
        while len(self._cache) > self.max_size:
            k, _ = self._cache.popitem(last=False)
            self._timestamps.pop(k, None)
            self._access_counter.pop(k, None)

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            self._evict_expired()
            if key in self._cache:
                self._cache.move_to_end(key)
                self._access_counter[key] += 1
                self._hits += 1
                return self._cache[key]
            else:
                self._misses += 1
                return None

    def set(self, key: str, value: Any):
        with self._lock:
            self._evict_expired()
            self._cache[key] = value
            self._timestamps[key] = time.time()
            self._cache.move_to_end(key)
            self._evict_lru()

    def invalidate(self, key: str):
        with self._lock:
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
            self._access_counter.pop(key, None)

    def invalidate_pattern(self, pattern: str):
        with self._lock:
            keys = [k for k in self._cache if pattern in k]
            for k in keys:
                self.invalidate(k)

    def clear(self):
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            self._access_counter.clear()
            self._hits = 0
            self._misses = 0

    def prewarm(self, items: Dict[str, Any]):
        """Pre-populate the cache with a dictionary of key-value pairs."""
        with self._lock:
            for k, v in items.items():
                self.set(k, v)

    def prewarm_from_file(self, filepath: str, loader: Optional[Callable[[str], Dict[str, Any]]] = None):
        """Pre-populate the cache from a file using a loader function."""
        if loader is None:
            import json
            def loader(path):
                with open(path, 'r') as f:
                    return json.load(f)
        items = loader(filepath)
        self.prewarm(items)

    def analytics(self) -> Dict[str, Any]:
        with self._lock:
            total = self._hits + self._misses
            hit_ratio = self._hits / total if total > 0 else 0.0
            most_common = self._access_counter.most_common(10)
            return {
                'hits': self._hits,
                'misses': self._misses,
                'hit_ratio': hit_ratio,
                'most_frequently_requested': most_common,
                'current_size': len(self._cache),
                'max_size': self.max_size,
                'ttl': self.ttl
            }

    def keys(self) -> List[str]:
        with self._lock:
            return list(self._cache.keys())

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)

# Example usage:
# cache = DialogueCache(max_size=500, ttl=300)
# cache.set('prompt:user:hello', 'Hi there!')
# response = cache.get('prompt:user:hello')
# print(cache.analytics()) 