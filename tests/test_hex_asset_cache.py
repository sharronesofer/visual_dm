"""
Tests for the hex asset caching system.
"""

import pytest
import pygame
import time
from visual_client.core.managers.hex_asset_cache import HexAssetCache, CacheEntry

@pytest.fixture
def cache():
    """Create a test cache instance."""
    return HexAssetCache("/tmp/hex_cache", max_size_mb=1)  # Small cache for testing

@pytest.fixture
def test_surface():
    """Create a test surface."""
    return pygame.Surface((64, 64))

def test_cache_initialization(cache):
    """Test cache initialization."""
    assert cache.max_memory == 1 * 1024 * 1024  # 1MB
    assert cache.current_memory == 0
    assert cache.cleanup_threshold == 0.9
    assert cache.cleanup_target == 0.7
    assert len(cache._cache) == 0

def test_put_and_get(cache, test_surface):
    """Test adding and retrieving assets from cache."""
    # Add asset
    success = cache.put("test_asset", test_surface)
    assert success
    
    # Get asset
    surface = cache.get("test_asset")
    assert surface is not None
    assert surface.get_size() == (64, 64)
    
    # Check memory usage
    memory_size = 64 * 64 * test_surface.get_bytesize()
    assert cache.current_memory == memory_size

def test_remove(cache, test_surface):
    """Test removing assets from cache."""
    # Add and remove asset
    cache.put("test_asset", test_surface)
    success = cache.remove("test_asset")
    assert success
    
    # Verify removal
    assert cache.get("test_asset") is None
    assert cache.current_memory == 0

def test_clear(cache, test_surface):
    """Test clearing the cache."""
    # Add multiple assets
    cache.put("asset1", test_surface)
    cache.put("asset2", test_surface)
    
    # Clear cache
    cache.clear()
    assert len(cache._cache) == 0
    assert cache.current_memory == 0

def test_memory_cleanup(cache, test_surface):
    """Test automatic memory cleanup."""
    # Create a surface that will trigger cleanup
    large_surface = pygame.Surface((256, 256), pygame.SRCALPHA)
    memory_size = 256 * 256 * large_surface.get_bytesize()
    
    # Add assets until cleanup is triggered
    assets_added = 0
    while cache.current_memory < cache.max_memory * cache.cleanup_threshold:
        cache.put(f"asset_{assets_added}", large_surface)
        assets_added += 1
    
    # Verify cleanup occurred
    assert cache.current_memory <= cache.max_memory * cache.cleanup_target

def test_reference_counting(cache, test_surface):
    """Test reference counting for cached assets."""
    # Add asset and get multiple references
    cache.put("test_asset", test_surface)
    ref1 = cache.get("test_asset")
    ref2 = cache.get("test_asset")
    
    # Check reference count
    assert cache._cache["test_asset"].reference_count == 3
    
    # Remove references
    cache.remove("test_asset")
    assert cache._cache["test_asset"].reference_count == 2
    cache.remove("test_asset")
    assert cache._cache["test_asset"].reference_count == 1
    cache.remove("test_asset")
    assert "test_asset" not in cache._cache

def test_preload(cache, test_surface):
    """Test asset preloading."""
    def mock_loader(asset_id):
        return test_surface
    
    # Preload multiple assets
    asset_ids = ["asset1", "asset2", "asset3"]
    success_count = cache.preload(asset_ids, mock_loader)
    
    assert success_count == 3
    assert all(cache.get(aid) is not None for aid in asset_ids)

def test_memory_usage_reporting(cache, test_surface):
    """Test memory usage reporting."""
    # Add an asset
    cache.put("test_asset", test_surface)
    memory_size = 64 * 64 * test_surface.get_bytesize()
    
    # Check usage
    bytes_used, percentage = cache.get_memory_usage()
    assert bytes_used == memory_size
    assert 0 <= percentage <= 1.0

def test_cache_overflow_handling(cache, test_surface):
    """Test handling of assets that exceed cache size."""
    # Create a surface larger than cache size
    huge_surface = pygame.Surface((1024, 1024), pygame.SRCALPHA)
    
    # Attempt to cache
    success = cache.put("huge_asset", huge_surface)
    assert not success  # Should fail as it exceeds max memory

def test_last_access_tracking(cache, test_surface):
    """Test tracking of last access time."""
    # Add asset
    cache.put("test_asset", test_surface)
    initial_time = cache._cache["test_asset"].last_access
    
    # Wait briefly
    time.sleep(0.1)
    
    # Access asset
    cache.get("test_asset")
    new_time = cache._cache["test_asset"].last_access
    
    assert new_time > initial_time 

def test_configure_cleanup(cache):
    """Test cleanup configuration."""
    # Test valid configuration
    cache.configure_cleanup(0.8, 0.6)
    assert cache.cleanup_threshold == 0.8
    assert cache.cleanup_target == 0.6
    
    # Test invalid configuration
    cache.configure_cleanup(0.5, 0.6)  # target > threshold
    assert cache.cleanup_threshold != 0.5  # Should not change
    
    cache.configure_cleanup(1.2, 0.8)  # threshold > 1
    assert cache.cleanup_threshold != 1.2  # Should not change

def test_cache_stats(cache, test_surface):
    """Test cache statistics tracking."""
    # Initial stats
    stats = cache.get_stats()
    assert stats["totalAssets"] == 0
    assert stats["hitRate"] == 0
    assert stats["missRate"] == 0
    
    # Add and access asset
    cache.put("test_asset", test_surface)
    cache.get("test_asset")  # Hit
    cache.get("nonexistent")  # Miss
    
    stats = cache.get_stats()
    assert stats["totalAssets"] == 1
    assert stats["hitRate"] == 0.5  # 1 hit out of 2 requests
    assert stats["missRate"] == 0.5  # 1 miss out of 2 requests
    assert stats["cleanupCount"] == 0

def test_cache_validation(cache, test_surface):
    """Test cache validation and repair."""
    # Add valid asset
    cache.put("valid_asset", test_surface)
    
    # Manually corrupt cache
    cache._cache["invalid_asset"] = "not a surface"  # type: ignore
    cache.current_memory = 9999  # Wrong memory count
    
    # Validate should fix issues
    assert cache.validate()
    
    # Check fixes
    assert "invalid_asset" not in cache._cache
    assert cache.current_memory == test_surface.get_size()[0] * test_surface.get_size()[1] * test_surface.get_bytesize()

def test_cache_warmup(cache, test_surface):
    """Test cache warmup functionality."""
    # Add assets
    cache.put("asset1", test_surface)
    cache.put("asset2", test_surface)
    
    # Warm up assets
    initial_time = time.time()
    time.sleep(0.1)  # Ensure time difference
    
    cache.warmup(["asset1"], priority="high")
    
    # Check priority and access time
    assert cache._cache["asset1"].priority == "high"
    assert cache._cache["asset1"].last_access > initial_time
    assert cache._cache["asset2"].priority == "low"  # Default priority

def test_priority_based_cleanup(cache, test_surface):
    """Test cleanup respects priority levels."""
    # Fill cache with low priority assets
    for i in range(10):
        cache.put(f"low_priority_{i}", test_surface)
    
    # Add high priority asset
    high_priority = pygame.Surface((32, 32))
    cache.put("high_priority", high_priority)
    cache.warmup(["high_priority"], priority="high")
    
    # Force cleanup
    cache.cleanup_threshold = 0.1  # Trigger cleanup
    cache._cleanup()
    
    # High priority asset should remain
    assert "high_priority" in cache._cache
    assert len(cache._cache) < 11  # Some low priority assets should be removed

def test_cleanup_counter(cache, test_surface):
    """Test cleanup operation counting."""
    # Fill cache to trigger cleanup
    initial_stats = cache.get_stats()
    
    for i in range(20):
        cache.put(f"asset_{i}", test_surface)
    
    final_stats = cache.get_stats()
    assert final_stats["cleanupCount"] > initial_stats["cleanupCount"]

def test_memory_limit_enforcement(cache, test_surface):
    """Test memory limit is properly enforced."""
    # Calculate how many surfaces we can store
    surface_size = test_surface.get_size()[0] * test_surface.get_size()[1] * test_surface.get_bytesize()
    max_surfaces = cache.max_memory // surface_size
    
    # Try to store more than the limit
    for i in range(max_surfaces + 5):
        cache.put(f"asset_{i}", test_surface)
    
    # Check memory limit
    assert cache.current_memory <= cache.max_memory
    stats = cache.get_stats()
    assert stats["memoryUsed"] <= stats["memoryLimit"] 