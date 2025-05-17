import pytest
from unittest.mock import MagicMock
from visual_client.core.scene.streaming import ChunkStreamingManager

@pytest.fixture
def chunk_streaming_manager():
    partition_tree = MagicMock()
    return ChunkStreamingManager(partition_tree, max_workers=2, cache_size=8)

def test_chunk_load_and_event(chunk_streaming_manager):
    # Register a mock event listener
    events = []
    def listener(event):
        events.append(event)
    chunk_streaming_manager.event_system.register_listener(listener)
    # Simulate chunk load request
    chunk_key = (0, 0)
    chunk_streaming_manager.request_chunk_load(chunk_key)
    # Simulate worker processing (direct call for test)
    chunk_streaming_manager._load_chunk(chunk_key)
    assert any("chunk_loaded" in str(e) or "CHUNK_LOADED" in str(e) for e in events)

def test_chunk_cache_eviction(chunk_streaming_manager):
    # Fill cache and trigger eviction
    for i in range(10):
        chunk_streaming_manager.cache.put((i, i), f"chunk_{i}")
    # Oldest chunk should be evicted if cache size exceeded
    assert chunk_streaming_manager.cache.get((0, 0)) is None
    assert chunk_streaming_manager.cache.get((9, 9)) == "chunk_9" 