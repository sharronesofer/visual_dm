"""Tests for viewport management system."""

import pytest
import numpy as np
from ..viewport import ViewportManager

def test_viewport_initialization():
    """Test viewport initialization."""
    viewport = ViewportManager(800, 600, min_zoom=0.5, max_zoom=2.0, initial_zoom=1.0)
    
    assert viewport.width == 800
    assert viewport.height == 600
    assert viewport.min_zoom == 0.5
    assert viewport.max_zoom == 2.0
    assert viewport.zoom == 1.0
    assert np.array_equal(viewport.center, np.array([0.0, 0.0]))
    assert viewport.bounds == (-400.0, -300.0, 400.0, 300.0)

def test_viewport_set_size():
    """Test viewport size update."""
    viewport = ViewportManager(800, 600)
    viewport.set_size(1024, 768)
    
    assert viewport.width == 1024
    assert viewport.height == 768
    assert viewport.bounds == (-512.0, -384.0, 512.0, 384.0)

def test_viewport_pan():
    """Test viewport panning."""
    viewport = ViewportManager(800, 600)
    
    # Test pan_by
    viewport.pan_by(100, 50)  # Pan right and down
    assert np.allclose(viewport.center, np.array([-100.0, -50.0]))
    
    # Test pan_to
    viewport.pan_to(200, -200)
    assert np.allclose(viewport.center, np.array([200.0, -200.0]))
    
    # Verify bounds update after panning
    expected_bounds = (
        200.0 - 400.0,  # minx
        -200.0 - 300.0,  # miny
        200.0 + 400.0,  # maxx
        -200.0 + 300.0   # maxy
    )
    assert np.allclose(viewport.bounds, expected_bounds)

def test_viewport_zoom():
    """Test viewport zooming."""
    viewport = ViewportManager(800, 600, min_zoom=0.5, max_zoom=2.0)
    
    # Test zoom_to without focus point
    viewport.zoom_to(1.5)
    assert viewport.zoom == 1.5
    assert np.allclose(viewport.bounds, (-266.67, -200.0, 266.67, 200.0), rtol=1e-2)
    
    # Test zoom_to with focus point
    viewport.zoom_to(0.75, (400, 300))  # Zoom out focusing on bottom-right corner
    assert viewport.zoom == 0.75
    assert not np.array_equal(viewport.center, np.array([0.0, 0.0]))  # Center should shift
    
    # Test zoom_by
    viewport = ViewportManager(800, 600, min_zoom=0.5, max_zoom=2.0)
    viewport.zoom_by(2.0)  # Double zoom
    assert viewport.zoom == 2.0
    
    # Test zoom limits
    viewport.zoom_by(2.0)  # Try to exceed max zoom
    assert viewport.zoom == 2.0  # Should stay at max
    
    viewport.zoom_by(0.1)  # Try to go below min zoom
    assert viewport.zoom == 0.5  # Should stay at min

def test_viewport_coordinate_conversion():
    """Test coordinate conversion between screen and world space."""
    viewport = ViewportManager(800, 600)
    
    # Test screen to world
    screen_point = (400, 300)  # Center of screen
    world_point = viewport.screen_to_world(screen_point)
    assert np.allclose(world_point, (0.0, 0.0))  # Should map to world origin
    
    screen_point = (0, 0)  # Top-left corner
    world_point = viewport.screen_to_world(screen_point)
    assert np.allclose(world_point, (-400.0, -300.0))
    
    # Test world to screen
    world_point = (0.0, 0.0)  # World origin
    screen_point = viewport.world_to_screen(world_point)
    assert np.allclose(screen_point, (400.0, 300.0))  # Should map to screen center
    
    world_point = (-400.0, -300.0)
    screen_point = viewport.world_to_screen(world_point)
    assert np.allclose(screen_point, (0.0, 0.0))
    
    # Test round trip conversion
    original_screen_point = (123, 456)
    world_point = viewport.screen_to_world(original_screen_point)
    final_screen_point = viewport.world_to_screen(world_point)
    assert np.allclose(original_screen_point, final_screen_point)

def test_viewport_state():
    """Test viewport state management."""
    viewport = ViewportManager(800, 600)
    
    # Get initial state
    state = viewport.get_state()
    assert state["width"] == 800
    assert state["height"] == 600
    assert state["zoom"] == 1.0
    assert np.array_equal(state["center"], [0.0, 0.0])
    assert state["bounds"] == (-400.0, -300.0, 400.0, 300.0)
    
    # Modify viewport and check state update
    viewport.pan_by(100, 50)
    viewport.zoom_to(1.5)
    
    state = viewport.get_state()
    assert state["zoom"] == 1.5
    assert not np.array_equal(state["center"], [0.0, 0.0])
    assert state["bounds"] != (-400.0, -300.0, 400.0, 300.0) 