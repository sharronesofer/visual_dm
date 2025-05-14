"""Tests for renderer system."""

import pytest
from PIL import Image
import numpy as np
from io import BytesIO

from ..region import Region, RegionProperties, RegionManager
from ..viewport import ViewportManager
from ..renderer import RegionRenderer

@pytest.fixture
def viewport():
    """Create a viewport for testing."""
    return ViewportManager(800, 600)

@pytest.fixture
def renderer(viewport):
    """Create a renderer for testing."""
    return RegionRenderer(viewport)

@pytest.fixture
def test_region():
    """Create a test region."""
    props = RegionProperties(
        name="Test Region",
        description="A test region",
        color=(255, 0, 0),
        border_color=(0, 0, 0),
        z_index=1
    )
    
    boundary = [(0, 0), (100, 0), (100, 100), (0, 100)]
    return Region("test-region", boundary, props)

def test_renderer_initialization(renderer):
    """Test renderer initialization."""
    assert renderer.viewport is not None
    assert renderer.background_color == (255, 255, 255)

def test_create_image(renderer):
    """Test image creation."""
    image = renderer._create_image()
    
    assert isinstance(image, Image.Image)
    assert image.mode == "RGBA"
    assert image.size == (800, 600)
    
    # Check background color
    background = Image.new("RGBA", (800, 600), renderer.background_color)
    assert list(image.getdata()) == list(background.getdata())

def test_transform_points(renderer):
    """Test point transformation."""
    world_points = [(0, 0), (100, 0), (100, 100), (0, 100)]
    screen_points = renderer._transform_points(world_points)
    
    # With default viewport (centered at origin, zoom=1),
    # world point (0,0) should map to screen point (400,300)
    assert np.allclose(screen_points[0], (400, 300))
    
    # Test after viewport transformation
    renderer.viewport.pan_by(50, 50)
    renderer.viewport.zoom_to(2.0)
    
    transformed_points = renderer._transform_points(world_points)
    assert len(transformed_points) == len(world_points)
    assert all(isinstance(p, tuple) and len(p) == 2 for p in transformed_points)

def test_draw_region(renderer, test_region):
    """Test region drawing."""
    image = renderer._create_image()
    draw = Image.new("RGBA", image.size, (0, 0, 0, 0)).draw
    
    # Draw region
    renderer._draw_region(draw, test_region)
    
    # Test with different alpha values
    renderer._draw_region(draw, test_region, alpha=128)
    
    # Test with selection/hover
    test_region.properties.is_selected = True
    renderer._draw_region(draw, test_region)
    
    test_region.properties.is_selected = False
    test_region.properties.is_hovered = True
    renderer._draw_region(draw, test_region)

def test_render_regions(renderer, test_region):
    """Test rendering multiple regions."""
    # Create another test region
    props2 = RegionProperties(
        name="Test Region 2",
        description="Another test region",
        color=(0, 255, 0),
        border_color=(0, 0, 0),
        z_index=2
    )
    region2 = Region(
        "test-region-2",
        [(200, 200), (300, 200), (300, 300), (200, 300)],
        props2
    )
    
    # Render regions
    image_data = renderer.render_regions([test_region, region2])
    
    # Verify output
    assert isinstance(image_data, bytes)
    image = Image.open(BytesIO(image_data))
    assert image.mode == "RGBA"
    assert image.size == (800, 600)
    
    # Test different format
    jpeg_data = renderer.render_regions([test_region, region2], format='JPEG')
    jpeg_image = Image.open(BytesIO(jpeg_data))
    assert jpeg_image.format == 'JPEG'

def test_render_region_labels(renderer, test_region):
    """Test rendering region labels."""
    # Create another test region
    props2 = RegionProperties(
        name="Test Region 2",
        description="Another test region",
        color=(0, 255, 0),
        border_color=(0, 0, 0),
        z_index=2
    )
    region2 = Region(
        "test-region-2",
        [(200, 200), (300, 200), (300, 300), (200, 300)],
        props2
    )
    
    # Render labels
    label_data = renderer.render_region_labels([test_region, region2])
    
    # Verify output
    assert isinstance(label_data, bytes)
    image = Image.open(BytesIO(label_data))
    assert image.mode == "RGBA"
    assert image.size == (800, 600)
    
    # Test with different font size
    label_data = renderer.render_region_labels(
        [test_region, region2],
        font_size=24
    )
    
    # Test different format
    jpeg_data = renderer.render_region_labels(
        [test_region, region2],
        format='JPEG'
    )
    jpeg_image = Image.open(BytesIO(jpeg_data))
    assert jpeg_image.format == 'JPEG'

def test_render_with_zoom(renderer, test_region):
    """Test rendering with different zoom levels."""
    # Test zoomed in
    renderer.viewport.zoom_to(2.0)
    image_data = renderer.render_regions([test_region])
    image = Image.open(BytesIO(image_data))
    assert image.size == (800, 600)
    
    # Test zoomed out
    renderer.viewport.zoom_to(0.5)
    image_data = renderer.render_regions([test_region])
    image = Image.open(BytesIO(image_data))
    assert image.size == (800, 600)

def test_render_with_pan(renderer, test_region):
    """Test rendering with different viewport positions."""
    # Test panned view
    renderer.viewport.pan_by(200, 150)
    image_data = renderer.render_regions([test_region])
    image = Image.open(BytesIO(image_data))
    assert image.size == (800, 600)
    
    # Test with region partially out of view
    renderer.viewport.pan_to(1000, 1000)
    image_data = renderer.render_regions([test_region])
    image = Image.open(BytesIO(image_data))
    assert image.size == (800, 600) 