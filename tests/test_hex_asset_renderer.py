"""
Tests for the hex asset renderer.
"""

import pytest
import pygame
import numpy as np
from pathlib import Path
from PIL import Image
from visual_client.core.managers.hex_asset_renderer import HexAssetRenderer
from visual_client.core.managers.hex_asset_manager import HexAssetManager
from visual_client.core.managers.hex_asset_cache import HexAssetCache
from visual_client.core.managers.hex_sprite_sheet import HexSpriteSheet

@pytest.fixture
def test_assets(tmp_path):
    """Create test assets."""
    assets_dir = tmp_path / "assets"
    terrain_dir = assets_dir / "terrain"
    
    # Create test directories
    for category in ["base", "features", "overlay", "effects"]:
        category_dir = terrain_dir / category
        category_dir.mkdir(parents=True)
        
        # Create test images
        for i in range(3):
            color = (i * 50, 255 - i * 50, i * 30, 255)
            img = Image.new("RGBA", (64, 64), color)
            img.save(category_dir / f"test_{category}_{i}.png")
    
    return assets_dir

@pytest.fixture
def renderer(test_assets):
    """Create a test renderer instance."""
    pygame.init()
    asset_manager = HexAssetManager(str(test_assets))
    sprite_sheet = HexSpriteSheet()
    cache = HexAssetCache("/tmp/hex_cache", max_size_mb=1)
    return HexAssetRenderer(asset_manager, sprite_sheet, cache)

def test_calculate_hex_position(renderer):
    """Test hex coordinate to pixel position calculation."""
    # Test origin
    assert renderer.calculate_hex_position((0, 0)) == (0, 0)
    
    # Test positive coordinates
    pos = renderer.calculate_hex_position((1, 1))
    assert isinstance(pos[0], int)
    assert isinstance(pos[1], int)
    assert pos[0] > 0
    assert pos[1] > 0
    
    # Test with scaling
    pos_scaled = renderer.calculate_hex_position((1, 1), scale=2.0)
    assert pos_scaled[0] == pos[0] * 2
    assert pos_scaled[1] == pos[1] * 2

def test_render_hex_tile(renderer):
    """Test rendering a single hex tile."""
    surface = pygame.Surface((128, 128), pygame.SRCALPHA)
    
    # Test basic terrain rendering
    renderer.render_hex_tile(
        surface,
        (0, 0),
        "test_base_0"
    )
    
    # Test with features
    renderer.render_hex_tile(
        surface,
        (0, 0),
        "test_base_0",
        features=["test_features_0"]
    )
    
    # Test with overlays
    renderer.render_hex_tile(
        surface,
        (0, 0),
        "test_base_0",
        overlays=["test_overlay_0"]
    )
    
    # Test with effects
    renderer.render_hex_tile(
        surface,
        (0, 0),
        "test_base_0",
        effects=["test_effects_0"]
    )
    
    # Test with scaling
    renderer.render_hex_tile(
        surface,
        (0, 0),
        "test_base_0",
        scale=0.5
    )

def test_render_region(renderer):
    """Test rendering a region of hex tiles."""
    surface = pygame.Surface((256, 256), pygame.SRCALPHA)
    view_rect = pygame.Rect(0, 0, 256, 256)
    
    # Create test region data
    region_data = {
        (0, 0): {
            "terrain": "test_base_0",
            "features": ["test_features_0"],
            "overlays": ["test_overlay_0"],
            "effects": ["test_effects_0"]
        },
        (1, 0): {
            "terrain": "test_base_1"
        },
        (0, 1): {
            "terrain": "test_base_2",
            "features": ["test_features_1"]
        }
    }
    
    # Test basic region rendering
    renderer.render_region(surface, region_data, view_rect)
    
    # Test with scaling
    renderer.render_region(surface, region_data, view_rect, scale=0.5)
    
    # Test view culling
    small_view = pygame.Rect(0, 0, 32, 32)
    renderer.render_region(surface, region_data, small_view)

def test_render_transition(renderer):
    """Test rendering transitions between regions."""
    surface = pygame.Surface((256, 256), pygame.SRCALPHA)
    view_rect = pygame.Rect(0, 0, 256, 256)
    
    # Create test region data
    start_region = {
        (0, 0): {"terrain": "test_base_0"},
        (1, 0): {"terrain": "test_base_1"}
    }
    
    end_region = {
        (0, 0): {"terrain": "test_base_1"},
        (1, 0): {"terrain": "test_base_2"}
    }
    
    # Test transition at different progress points
    for progress in [0.0, 0.5, 1.0]:
        renderer.render_transition(
            surface,
            start_region,
            end_region,
            progress,
            view_rect
        )
        
    # Test with scaling
    renderer.render_transition(
        surface,
        start_region,
        end_region,
        0.5,
        view_rect,
        scale=0.5
    ) 