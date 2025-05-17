import time
import threading
import pytest
from dialogue.cache import DialogueCache

def test_set_and_get():
    cache = DialogueCache(max_size=3, ttl=10)
    cache.set('a', 1)
    cache.set('b', 2)
    assert cache.get('a') == 1
    assert cache.get('b') == 2
    assert cache.get('c') is None

def test_lru_eviction():
    cache = DialogueCache(max_size=2, ttl=10)
    cache.set('a', 1)
    cache.set('b', 2)
    cache.set('c', 3)
    assert cache.get('a') is None  # 'a' should be evicted
    assert cache.get('b') == 2
    assert cache.get('c') == 3

def test_ttl_expiration():
    cache = DialogueCache(max_size=2, ttl=1)
    cache.set('a', 1)
    time.sleep(1.1)
    assert cache.get('a') is None  # expired

def test_manual_invalidation():
    cache = DialogueCache(max_size=2, ttl=10)
    cache.set('a', 1)
    cache.invalidate('a')
    assert cache.get('a') is None

def test_invalidate_pattern():
    cache = DialogueCache(max_size=5, ttl=10)
    cache.set('prompt:1', 'x')
    cache.set('prompt:2', 'y')
    cache.set('other:3', 'z')
    cache.invalidate_pattern('prompt:')
    assert cache.get('prompt:1') is None
    assert cache.get('prompt:2') is None
    assert cache.get('other:3') == 'z'

def test_analytics():
    cache = DialogueCache(max_size=2, ttl=10)
    cache.set('a', 1)
    cache.get('a')
    cache.get('b')
    stats = cache.analytics()
    assert stats['hits'] == 1
    assert stats['misses'] == 1
    assert stats['current_size'] == 1

def test_prewarm():
    cache = DialogueCache(max_size=5, ttl=10)
    items = {'a': 1, 'b': 2}
    cache.prewarm(items)
    assert cache.get('a') == 1
    assert cache.get('b') == 2

def test_thread_safety():
    cache = DialogueCache(max_size=100, ttl=10)
    def writer():
        for i in range(50):
            cache.set(f'k{i}', i)
    def reader():
        for i in range(50):
            cache.get(f'k{i}')
    threads = [threading.Thread(target=writer) for _ in range(2)] + [threading.Thread(target=reader) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # No exceptions should be raised, and cache should have at most 100 items
    assert len(cache) <= 100 