import pytest
from unittest.mock import MagicMock
from visual_client.core.managers.scene_manager import SceneManager, AssetPriority, UnloadStrategy

@pytest.fixture
def scene_manager():
    asset_manager = MagicMock()
    return SceneManager(asset_manager=asset_manager, memory_budget_mb=1, streaming_enabled=False, auto_unload=False)

def test_register_and_activate_scene(scene_manager):
    scene_id = "test_scene"
    scene_data = {"asset_manifest": [{"id": "asset1", "type": "image", "size": 1024, "priority": AssetPriority.HIGH}]}
    scene_manager.register_scene(scene_id, scene_data)
    assert scene_id in scene_manager.scenes
    assert scene_id in scene_manager.scene_assets
    assert scene_manager.activate_scene(scene_id)
    assert scene_manager.get_active_scene() == scene_id

def test_memory_budget_and_asset_registration(scene_manager):
    scene_id = "scene2"
    scene_data = {"asset_manifest": [{"id": "asset2", "type": "image", "size": 2048, "priority": AssetPriority.MEDIUM}]}
    scene_manager.register_scene(scene_id, scene_data)
    usage = scene_manager.get_memory_usage_report()
    assert usage["asset_count"] >= 1
    assert usage["used_memory_mb"] > 0

def test_set_asset_priority(scene_manager):
    scene_id = "scene3"
    scene_data = {"asset_manifest": [{"id": "asset3", "type": "image", "size": 512, "priority": AssetPriority.LOW}]}
    scene_manager.register_scene(scene_id, scene_data)
    assert scene_manager.set_asset_priority("asset3", AssetPriority.CRITICAL, scene_id=scene_id)

def test_unload_scene_assets(scene_manager):
    scene_id = "scene4"
    scene_data = {"asset_manifest": [{"id": "asset4", "type": "image", "size": 256, "priority": AssetPriority.LOW}]}
    scene_manager.register_scene(scene_id, scene_data)
    scene_manager.unregister_scene(scene_id)
    assert scene_id not in scene_manager.scenes
    assert scene_id not in scene_manager.scene_assets

def test_set_unload_strategy(scene_manager):
    scene_manager.set_unload_strategy(UnloadStrategy.TIME_BASED)
    assert scene_manager.unload_strategy == UnloadStrategy.TIME_BASED 