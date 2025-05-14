import pytest
from .viewport_manager import ViewportManager

def test_initial_state():
    vm = ViewportManager()
    state = vm.get_state()
    assert state['x'] == 0
    assert state['y'] == 0
    assert state['width'] == 1024
    assert state['height'] == 768
    assert state['zoom'] == 1.0

def test_custom_initial_state():
    vm = ViewportManager(x=10, y=20, width=800, height=600, zoom=2.5)
    state = vm.get_state()
    assert state == {'x': 10, 'y': 20, 'width': 800, 'height': 600, 'zoom': 2.5}

def test_set_state_partial():
    vm = ViewportManager()
    vm.set_state(x=100, zoom=1.5)
    state = vm.get_state()
    assert state['x'] == 100
    assert state['zoom'] == 1.5
    assert state['y'] == 0
    assert state['width'] == 1024
    assert state['height'] == 768

def test_set_state_all():
    vm = ViewportManager()
    vm.set_state(x=5, y=6, width=200, height=300, zoom=0.75)
    state = vm.get_state()
    assert state == {'x': 5, 'y': 6, 'width': 200, 'height': 300, 'zoom': 0.75}

def test_set_state_invalid():
    vm = ViewportManager()
    # Should not raise, but should ignore None
    vm.set_state(x=None, y=None, width=None, height=None, zoom=None)
    state = vm.get_state()
    assert state == {'x': 0, 'y': 0, 'width': 1024, 'height': 768, 'zoom': 1.0}

def test_world_to_screen_and_back():
    vm = ViewportManager(x=10, y=20, width=800, height=600, zoom=2.0)
    wx, wy = 15, 25
    sx, sy = vm.world_to_screen(wx, wy)
    # Should be (5*2, 5*2) = (10, 10)
    assert sx == 10
    assert sy == 10
    # Now convert back
    wx2, wy2 = vm.screen_to_world(sx, sy)
    assert wx2 == pytest.approx(wx)
    assert wy2 == pytest.approx(wy)

def test_world_to_screen_origin():
    vm = ViewportManager(x=0, y=0, zoom=1.0)
    assert vm.world_to_screen(0, 0) == (0, 0)
    assert vm.screen_to_world(0, 0) == (0, 0)

def test_world_to_screen_zoom():
    vm = ViewportManager(x=0, y=0, zoom=0.5)
    assert vm.world_to_screen(4, 6) == (2, 3)
    assert vm.screen_to_world(2, 3) == (4, 6)

def test_screen_to_world_offset():
    vm = ViewportManager(x=100, y=200, zoom=1.0)
    assert vm.screen_to_world(0, 0) == (100, 200)
    assert vm.world_to_screen(100, 200) == (0, 0)

def test_pan():
    vm = ViewportManager(x=10, y=20)
    vm.pan(5, -3)
    state = vm.get_state()
    assert state['x'] == 15
    assert state['y'] == 17
    vm.pan(-10, 10)
    state = vm.get_state()
    assert state['x'] == 5
    assert state['y'] == 27

def test_zoom_at_center():
    vm = ViewportManager(x=0, y=0, width=100, height=100, zoom=1.0)
    # Zoom in by 2x at center (should keep center at same world position)
    center_world = (vm.x + vm.width/2/vm.zoom, vm.y + vm.height/2/vm.zoom)
    vm.zoom_at(2.0)
    assert vm.zoom == 2.0
    # Center should remain at same world position
    new_center_world = (vm.x + vm.width/2/vm.zoom, vm.y + vm.height/2/vm.zoom)
    assert new_center_world[0] == pytest.approx(center_world[0])
    assert new_center_world[1] == pytest.approx(center_world[1])

def test_zoom_at_point():
    vm = ViewportManager(x=0, y=0, width=100, height=100, zoom=1.0)
    # Zoom in at (10, 10) in world coordinates
    vm.zoom_at(2.0, center_x=10, center_y=10)
    assert vm.zoom == 2.0
    # (10, 10) should map to same screen position as before
    sx1, sy1 = 10 - vm.x, 10 - vm.y  # before zoom, at zoom=1
    # After zoom, screen position:
    sx2, sy2 = vm.world_to_screen(10, 10)
    assert sx2 == pytest.approx(sx1 * 2)
    assert sy2 == pytest.approx(sy1 * 2)

def test_zoom_invalid():
    vm = ViewportManager(zoom=1.0)
    vm.zoom_at(0)  # Should not change zoom
    assert vm.zoom == 1.0
    vm.zoom_at(-2)  # Should not allow negative zoom
    assert vm.zoom == 1.0

def test_pan_and_zoom_combined():
    vm = ViewportManager(x=5, y=5, width=100, height=100, zoom=1.0)
    vm.pan(10, 10)
    assert vm.get_state()['x'] == 15
    assert vm.get_state()['y'] == 15
    vm.zoom_at(2.0)
    assert vm.zoom == 2.0
    # After pan and zoom, check world_to_screen and screen_to_world are consistent
    wx, wy = 20, 20
    sx, sy = vm.world_to_screen(wx, wy)
    wx2, wy2 = vm.screen_to_world(sx, sy)
    assert wx2 == pytest.approx(wx)
    assert wy2 == pytest.approx(wy)

def test_fit_content_basic():
    vm = ViewportManager(width=100, height=100)
    vm.fit_content(map_width=50, map_height=50)
    state = vm.get_state()
    # Should be zoomed so all of 50x50 fits in 100x100 (zoom=2)
    assert state['zoom'] == 2.0
    # Should be centered
    assert state['x'] == 0.0
    assert state['y'] == 0.0

def test_fit_content_with_padding():
    vm = ViewportManager(width=100, height=100)
    vm.fit_content(map_width=50, map_height=50, padding=10)
    state = vm.get_state()
    # Now fitting 70x70 into 100x100 (zoom ~1.428)
    assert state['zoom'] == pytest.approx(100/70)
    # Centered
    assert state['x'] == pytest.approx((50 - 100/state['zoom'])/2)
    assert state['y'] == pytest.approx((50 - 100/state['zoom'])/2)

def test_fit_content_viewport_larger_than_map():
    vm = ViewportManager(width=200, height=200)
    vm.fit_content(map_width=50, map_height=50)
    state = vm.get_state()
    # Should zoom out so map fits, but not negative/zero zoom
    assert state['zoom'] == 1.0 or state['zoom'] > 0
    # Centered
    assert state['x'] == pytest.approx((50 - 200/state['zoom'])/2)
    assert state['y'] == pytest.approx((50 - 200/state['zoom'])/2)

def test_fit_content_extreme_aspect_ratio():
    vm = ViewportManager(width=200, height=50)
    vm.fit_content(map_width=50, map_height=200)
    state = vm.get_state()
    # Should fit the taller dimension
    assert state['zoom'] == pytest.approx(50/200)
    # Centered
    assert state['x'] == pytest.approx((50 - 200/state['zoom'])/2)
    assert state['y'] == pytest.approx((200 - 50/state['zoom'])/2) 