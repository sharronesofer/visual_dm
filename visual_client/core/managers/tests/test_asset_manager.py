import pytest
from visual_client.core.managers.asset_manager import AssetManager

@pytest.fixture
def asset_manager():
    return AssetManager(asset_dir="/tmp/assets")

def test_register_and_get_asset_lod(asset_manager):
    asset_manager.register_asset_lod("tree", 0, {"mesh": "tree_high.obj"})
    asset_manager.register_asset_lod("tree", 1, {"mesh": "tree_med.obj"})
    asset_manager.register_asset_lod("tree", 2, {"mesh": "tree_low.obj"})
    assert asset_manager.get_asset_lod("tree", 0)["mesh"] == "tree_high.obj"
    assert asset_manager.get_asset_lod("tree", 1)["mesh"] == "tree_med.obj"
    assert asset_manager.get_asset_lod("tree", 2)["mesh"] == "tree_low.obj"

def test_lod_fallback(asset_manager):
    asset_manager.register_asset_lod("rock", 1, {"mesh": "rock_med.obj"})
    # Should return None for missing LOD
    assert asset_manager.get_asset_lod("rock", 0) is None
    assert asset_manager.get_asset_lod("rock", 1)["mesh"] == "rock_med.obj"

def test_asset_cache_eviction(asset_manager):
    # Simulate cache size limit
    for i in range(100):
        asset_manager.register_asset_lod(f"asset_{i}", 0, {"mesh": f"mesh_{i}.obj"})
    # Check that assets are still retrievable (no real cache eviction in this stub, but test for future logic)
    assert asset_manager.get_asset_lod("asset_99", 0)["mesh"] == "mesh_99.obj" 