"""
Test suite for the RobustSceneManager implementation.

This module contains comprehensive unit and integration tests for the 
RobustSceneManager's error handling capabilities.
"""

import os
import pytest
import time
import pygame
import shutil
from unittest.mock import MagicMock, patch
import sys
import threading
import psutil

# Import the modules to test
from visual_client.core.managers.robust_scene_manager import RobustSceneManager
from visual_client.core.managers.scene_error_handler import SceneErrorHandler, SceneErrorType
from visual_client.core.managers.error_handler import ErrorSeverity
from visual_client.core.managers.scene_loader_manager import SceneLoaderManager
from visual_client.core.managers.loading_manager import LoadingManager

# Initialize Pygame
pygame.init()

# Setup paths
PLACEHOLDER_DIR = os.path.join('visual_client', 'assets', 'placeholders')
TEST_ASSETS_DIR = os.path.join('visual_client', 'core', 'managers', 'tests', 'test_assets')

# Create test directories
os.makedirs(PLACEHOLDER_DIR, exist_ok=True)
os.makedirs(TEST_ASSETS_DIR, exist_ok=True)

# --- FIXED IMPORTS FOR PYTEST COMPATIBILITY ---
# Use absolute imports and ensure test discovery works in CI/CD and local runs
# (No changes needed if running from project root, but add sys.path adjustment for flexibility)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

class MockSceneManager:
    """Mock base scene manager for testing."""
    
    def __init__(self, *args, **kwargs):
        self.current_scene = "test_scene"
        self.scenes = {
            "loading": {"name": "loading"},
            "test_scene": {"name": "test_scene"},
            "error_scene": {"name": "error_scene"},
            "valid_scene": {"name": "valid_scene"},
        }
        self.is_transitioning = False
        self.load_called = False
        self.load_args = None
        self.update_called = False
        self.asset_map = {}
        
    def load_scene(self, scene_name, *args, **kwargs):
        """Mock scene loading."""
        self.load_called = True
        self.load_args = (scene_name, args, kwargs)
        
        # Simulate errors for certain scenes
        if scene_name == "error_scene":
            raise ValueError("Simulated scene load error")
            
        self.current_scene = scene_name
        return True
        
    def update(self, *args, **kwargs):
        """Mock update method."""
        self.update_called = True
        
        # Simulate errors for certain scenes
        if self.current_scene == "error_scene" and not kwargs.get('suppress_error', False):
            raise ValueError("Simulated update error")

# Create test fixture
@pytest.fixture
def manager():
    """Create a test instance of RobustSceneManager."""
    # Patch the BaseSceneManager import in robust_scene_manager
    with patch('visual_client.core.managers.robust_scene_manager.BaseSceneManager', MockSceneManager):
        manager = RobustSceneManager(
            default_scene="loading",
            max_retries=2,
            transition_timeout=100  # Short timeout for testing
        )
        yield manager

@pytest.fixture
def create_test_assets():
    """Create test assets for testing asset validation."""
    # Create a test texture
    surface = pygame.Surface((64, 64))
    surface.fill((255, 0, 0))  # Red
    pygame.image.save(surface, os.path.join(TEST_ASSETS_DIR, 'test_texture.png'))
    
    # Create a test placeholder
    surface = pygame.Surface((64, 64))
    surface.fill((255, 0, 255))  # Magenta
    pygame.image.save(surface, os.path.join(PLACEHOLDER_DIR, 'missing_texture.png'))
    
    # Cleanup after tests
    yield
    
    # Remove test assets
    try:
        shutil.rmtree(TEST_ASSETS_DIR)
    except:
        pass

# TEST CASES

# 1. Failed Scene Loads
def test_load_scene_error_handling(manager):
    """Test error handling for failed scene loads."""
    # Try to load a scene that will generate an error
    result = manager.load_scene("error_scene")
    
    # Should return False after max retries
    assert result is False
    
    # Should have fallen back to default scene
    assert manager.current_scene == "loading"
    
    # Should have tracked load attempts
    assert "error_scene" in manager.error_handler.load_attempts
    assert manager.error_handler.load_attempts["error_scene"] == 0  # Reset after max retries
    
    # Should have tracked transition
    assert len(manager.error_handler.transition_history) == 1
    assert manager.error_handler.transition_history[0]["status"] == "failed"

def test_scene_load_retry(manager):
    """Test retry mechanism for scene loading."""
    # Create a counter for attempts
    attempt_count = [0]
    def mock_load_scene(scene_name, *args, **kwargs):
        attempt_count[0] += 1
        if attempt_count[0] == 1:
            raise ValueError("First attempt error")
        return True
    # Monkey patch the load_scene method
    with patch.object(manager, 'load_scene', side_effect=mock_load_scene):
        # Try to load the scene
        result = manager.load_scene_safe("test_retry_scene")
        # Should succeed on second attempt
        assert result is True
        assert attempt_count[0] == 2
        # Should have tracked load attempts
        assert "test_retry_scene" in manager.error_handler.load_attempts
        assert manager.error_handler.load_attempts["test_retry_scene"] == 2

# 2. Missing Assets
def test_missing_asset_handling(manager, create_test_assets):
    """Test handling of missing assets."""
    # Register some assets
    manager.register_scene_asset_dependencies("test_assets_scene", [
        os.path.join(TEST_ASSETS_DIR, 'test_texture.png'),
        os.path.join(TEST_ASSETS_DIR, 'missing_texture.png')  # This one doesn't exist
    ])
    
    # Validate assets
    missing = manager.validate_scene_assets("test_assets_scene")
    
    # Should find one missing asset
    assert len(missing) == 1
    assert missing[0][0] == os.path.join(TEST_ASSETS_DIR, 'missing_texture.png')
    assert missing[0][1] == 'texture'
    
    # Get placeholder for the missing asset
    placeholder = manager.handle_missing_asset(
        os.path.join(TEST_ASSETS_DIR, 'missing_texture.png'),
        'texture'
    )
    
    # Should return a valid placeholder path
    assert placeholder == os.path.join(PLACEHOLDER_DIR, 'missing_texture.png')
    assert os.path.exists(placeholder)
    
    # Should track the missing asset
    report = manager.error_handler.get_missing_assets_report()
    assert "unknown" in report  # Current scene for tests is "unknown"
    assert os.path.join(TEST_ASSETS_DIR, 'missing_texture.png') in report["unknown"]

# 3. Interrupted Transitions
def test_transition_timeout(manager):
    """Test handling of transition timeouts."""
    # Start a transition
    manager.current_transition_id = manager.error_handler.start_transition(
        from_scene="test_scene",
        to_scene="valid_scene"
    )
    
    # Mock that we've updated the transition to loading stage
    manager.error_handler.update_transition(
        manager.current_transition_id,
        "loading_scene"
    )
    
    # Force timeout by manipulating the start time
    for transition in manager.error_handler.transition_history:
        if transition["id"] == manager.current_transition_id:
            transition["start_time"] = time.time() - 1  # Set to 1 second ago (timeout is 100ms)
    
    # Run an update which should trigger timeout handling
    manager.update()
    
    # Transition should be marked as timeout
    for transition in manager.error_handler.transition_history:
        if transition["id"] == manager.current_transition_id:
            assert transition["status"] == "timeout"
    
    # Current_transition_id should be reset
    assert manager.current_transition_id is None
    
    # Current scene should be set to the destination scene (force completed)
    assert manager.current_scene == "valid_scene"

def test_transition_rollback(manager):
    """Test rollback of an interrupted transition."""
    # Start a transition
    manager.current_transition_id = manager.error_handler.start_transition(
        from_scene="test_scene",
        to_scene="error_scene"  # Will cause an error
    )
    
    # Force timeout but DON'T update to loading stage
    # This should trigger a rollback instead of force-complete
    for transition in manager.error_handler.transition_history:
        if transition["id"] == manager.current_transition_id:
            transition["start_time"] = time.time() - 1  # Set to 1 second ago
    
    # Run an update which should trigger timeout handling
    manager.update(suppress_error=True)  # Suppress the error scene update error
    
    # Transition should be marked as timeout
    for transition in manager.error_handler.transition_history:
        if transition["id"] == manager.current_transition_id:
            assert transition["status"] == "timeout"
    
    # Current_transition_id should be reset
    assert manager.current_transition_id is None
    
    # Current scene should be set back to the original scene (rolled back)
    assert manager.current_scene == "test_scene"

# Integration Tests
def test_error_reporting(manager, create_test_assets):
    """Test the error reporting functionality."""
    # Generate some errors and missing assets
    manager.register_scene_asset_dependencies("test_scene", [
        os.path.join(TEST_ASSETS_DIR, 'nonexistent1.png'),
        os.path.join(TEST_ASSETS_DIR, 'nonexistent2.wav')
    ])
    
    # Validate assets to record missing ones
    manager.validate_scene_assets("test_scene")
    
    # Try to load an error scene (will fail)
    manager.load_scene("error_scene")
    
    # Start a transition and timeout
    manager.current_transition_id = manager.error_handler.start_transition(
        from_scene="test_scene",
        to_scene="valid_scene"
    )
    
    # Force timeout
    for transition in manager.error_handler.transition_history:
        if transition["id"] == manager.current_transition_id:
            transition["start_time"] = time.time() - 1
    
    # Run update to handle timeout
    manager.update()
    
    # Get error state
    error_state = manager.get_error_state()
    
    # Should have missing assets
    assert "missing_assets" in error_state
    assert "test_scene" in error_state["missing_assets"]
    assert len(error_state["missing_assets"]["test_scene"]) == 2
    
    # Should have transition history
    assert "transition_history" in error_state
    assert len(error_state["transition_history"]) >= 2  # At least 2 transitions
    
    # Should have load attempts
    assert "load_attempts" in error_state
    assert "error_scene" in error_state["load_attempts"]
    
    # Should have dependencies
    assert "scene_asset_dependencies" in error_state
    assert "test_scene" in error_state["scene_asset_dependencies"]
    assert len(error_state["scene_asset_dependencies"]["test_scene"]) == 2

def test_scene_manager_integration(manager):
    """Test overall integration of error handling components."""
    # 1. Successfully load a valid scene
    result = manager.load_scene("valid_scene")
    assert result is True
    assert manager.current_scene == "valid_scene"
    
    # 2. Try to load an error scene, which should fall back to default
    result = manager.load_scene("error_scene")
    assert result is False
    assert manager.current_scene == "loading"
    
    # 3. Reset error tracking
    manager.reset_error_tracking()
    assert len(manager.error_handler.load_attempts) == 0
    assert manager.current_transition_id is None
    
    # 4. Test asset substitution
    manager.substitute_asset("original.png", "placeholder.png")
    assert "original.png" in manager.asset_map
    assert manager.asset_map["original.png"] == "placeholder.png"

def test_scene_loader_manager_integration(manager):
    """Test integration of SceneLoaderManager with RobustSceneManager and LoadingManager."""
    # Register 'valid_scene' before loading
    manager.register_scene('valid_scene', {'name': 'valid_scene'})
    loading_manager = LoadingManager()
    loader_manager = SceneLoaderManager(manager, loading_manager)
    manager.set_scene_loader_manager(loader_manager)
    # Track callback result
    callback_result = {"called": False, "success": None}
    def cb(success, error=None):
        callback_result["called"] = True
        callback_result["success"] = success
    # Queue a scene load
    loader_manager.queue_scene_load("valid_scene", priority=1, callback=cb)
    # Wait for async load to complete
    timeout = time.time() + 2.0
    while not callback_result["called"] and time.time() < timeout:
        time.sleep(0.05)
    assert callback_result["called"]
    assert callback_result["success"] is True
    # Check progress reached 100
    assert loader_manager.progress["valid_scene"] == 100.0

def test_scene_loader_manager_error_handling(manager):
    """Test error handling in SceneLoaderManager for invalid scene."""
    loading_manager = LoadingManager()
    loader_manager = SceneLoaderManager(manager, loading_manager)
    manager.set_scene_loader_manager(loader_manager)
    callback_result = {"called": False, "success": None, "error": None}
    def cb(success, error=None):
        callback_result["called"] = True
        callback_result["success"] = success
        callback_result["error"] = error
    # Queue a scene load for an invalid scene
    loader_manager.queue_scene_load("nonexistent_scene", priority=1, callback=cb)
    # Wait for async load to complete
    timeout = time.time() + 2.0
    while not callback_result["called"] and time.time() < timeout:
        time.sleep(0.05)
    assert callback_result["called"]
    assert callback_result["success"] is False
    assert callback_result["error"] is not None
    # Check progress reached 100
    assert loader_manager.progress["nonexistent_scene"] == 100.0

def test_scene_loader_manager_stress(manager):
    """Stress test SceneLoaderManager with many scenes and rapid loads."""
    # Register all scenes before loading
    for i in range(10):
        manager.register_scene(f'scene_{i}', {'name': f'scene_{i}'})
    loading_manager = LoadingManager()
    loader_manager = SceneLoaderManager(manager, loading_manager)
    manager.set_scene_loader_manager(loader_manager)
    cb = {"count": 0, "success": True}
    def callback(success, error=None):
        cb["count"] += 1
        cb["success"] = cb["success"] and success
    # Queue many scenes
    for i in range(10):
        loader_manager.queue_scene_load(f'scene_{i}', callback=callback)
    # Also queue a non-existent scene
    loader_manager.queue_scene_load('nonexistent_scene', callback=callback)
    # Wait for all to finish
    loader_manager.wait_for_all()
    assert cb["count"] == 11
    assert cb["success"] is True

# --- ADDITIONAL STRESS TESTS FOR RESOURCE CONSTRAINTS AND QUEUE OVERFLOW ---
def test_scene_loader_manager_resource_constraints(manager):
    """Simulate low memory and high CPU load during scene loading."""
    loading_manager = LoadingManager()
    loader_manager = SceneLoaderManager(manager, loading_manager)
    manager.set_scene_loader_manager(loader_manager)
    scene_id = "resource_constraint_scene"
    callback_result = {"called": False, "success": None, "error": None}
    def cb(success, error=None):
        callback_result["called"] = True
        callback_result["success"] = success
        callback_result["error"] = error
    # Simulate high CPU load in a background thread
    def cpu_stress():
        end = time.time() + 1.5
        while time.time() < end:
            _ = sum(i*i for i in range(10000))
    stress_thread = threading.Thread(target=cpu_stress)
    stress_thread.start()
    # Simulate low memory by allocating a large list (if possible)
    try:
        big_list = [0] * (10**7)
    except MemoryError:
        big_list = None
    loader_manager.queue_scene_load(scene_id, priority=1, callback=cb)
    timeout = time.time() + 3.0
    while not callback_result["called"] and time.time() < timeout:
        time.sleep(0.05)
    stress_thread.join()
    del big_list
    assert callback_result["called"]
    # Progress should reach 100
    assert loader_manager.progress[scene_id] == 100.0
    # Log resource usage
    process = psutil.Process(os.getpid())
    print(f"Memory usage: {process.memory_info().rss / 1024**2:.2f} MB")
    print(f"CPU percent: {process.cpu_percent(interval=0.1)}%")

def test_scene_loader_manager_queue_overflow(manager):
    """Test queue overflow and rapid scene switching."""
    loading_manager = LoadingManager()
    loader_manager = SceneLoaderManager(manager, loading_manager)
    manager.set_scene_loader_manager(loader_manager)
    max_queue = 50
    callback_results = {f"scene_{i}": {"called": False, "success": None, "error": None} for i in range(max_queue)}
    for i in range(max_queue):
        def make_cb(sid):
            return lambda success, error=None: (
                callback_results[sid].update({"called": True, "success": success, "error": error})
            )
        loader_manager.queue_scene_load(f"scene_{i}", priority=1, callback=make_cb(f"scene_{i}"))
    timeout = time.time() + 10.0
    while not all(cb["called"] for cb in callback_results.values()) and time.time() < timeout:
        time.sleep(0.05)
    for sid, cb in callback_results.items():
        assert cb["called"], f"Callback not called for {sid}"
        assert loader_manager.progress[sid] == 100.0

# Run tests if file is executed directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 