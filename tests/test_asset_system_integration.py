"""
Integration tests for the hex asset management system.
Tests the interaction between all components and end-to-end functionality.
"""

import pytest
import pygame
import numpy as np
from pathlib import Path
from PIL import Image
import json
import time

from visual_client.core.managers.hex_asset_manager import HexAssetManager
from visual_client.core.managers.hex_asset_metadata import HexAssetMetadataManager
from visual_client.core.managers.hex_asset_cache import HexAssetCache
from visual_client.core.managers.hex_sprite_sheet import HexSpriteSheet
from visual_client.core.managers.hex_asset_renderer import HexAssetRenderer
from visual_client.core.tools.hex_asset_preview_ui import HexAssetPreviewUI

@pytest.fixture
def test_environment(tmp_path):
    """Set up a complete test environment with all components."""
    # Create test asset directory structure
    assets_dir = tmp_path / "assets"
    terrain_dir = assets_dir / "terrain"
    
    # Create test directories and assets
    categories = ["base", "features", "overlay", "effects"]
    for category in categories:
        category_dir = terrain_dir / category
        category_dir.mkdir(parents=True)
        
        # Create test images with different characteristics
        for i in range(3):
            # Create variations in color and transparency
            color = (i * 50, 255 - i * 50, i * 30, 200)
            img = Image.new("RGBA", (64, 64), color)
            img.save(category_dir / f"test_{category}_{i}.png")
    
    # Initialize all components
    pygame.init()
    asset_manager = HexAssetManager(str(assets_dir))
    metadata_manager = HexAssetMetadataManager()
    cache = HexAssetCache(str(assets_dir / "cache"), max_size_mb=10)
    sprite_sheet = HexSpriteSheet()
    renderer = HexAssetRenderer(asset_manager, sprite_sheet, cache)
    preview_ui = HexAssetPreviewUI(asset_manager, metadata_manager, cache)
    
    return {
        "assets_dir": assets_dir,
        "asset_manager": asset_manager,
        "metadata_manager": metadata_manager,
        "cache": cache,
        "sprite_sheet": sprite_sheet,
        "renderer": renderer,
        "preview_ui": preview_ui
    }

def test_end_to_end_asset_pipeline(test_environment):
    """Test the complete asset pipeline from loading to rendering."""
    env = test_environment
    
    # 1. Load and cache assets
    base_assets = list((env["assets_dir"] / "terrain" / "base").glob("*.png"))
    assert len(base_assets) > 0
    
    for asset in base_assets:
        # Load asset
        surface = env["asset_manager"].load_hex_image(
            asset.name,
            "base",
            metadata={"type": "terrain"},
            lazy=False
        )
        assert surface is not None
        
        # Verify metadata
        metadata = env["asset_manager"].get_hex_metadata(asset.name)
        assert metadata is not None
        assert metadata["category"] == "base"
        
        # Check cache
        cached = env["cache"].get(f"base_{asset.name}")
        assert cached is not None

def test_memory_management_under_load(test_environment):
    """Test memory management with heavy asset loading."""
    env = test_environment
    
    # Track initial memory
    initial_memory = env["cache"].current_memory
    
    # Load multiple assets to trigger cache cleanup
    for category in ["base", "features", "overlay", "effects"]:
        category_dir = env["assets_dir"] / "terrain" / category
        assets = list(category_dir.glob("*.png"))
        
        for asset in assets:
            env["asset_manager"].load_hex_image(
                asset.name,
                category,
                lazy=False
            )
    
    # Verify cache cleanup occurred
    assert env["cache"].current_memory <= env["cache"].max_memory
    assert env["cache"].current_memory > initial_memory

def test_sprite_sheet_optimization(test_environment):
    """Test sprite sheet generation and optimization."""
    env = test_environment
    
    # Generate sprite sheets for each category
    for category in ["base", "features", "overlay", "effects"]:
        sheet_path = env["asset_manager"].generate_sprite_sheet(category)
        assert sheet_path is not None
        
        # Verify sheet dimensions
        sheet = Image.open(sheet_path)
        width, height = sheet.size
        assert width <= env["sprite_sheet"].sheet_size[0]
        assert height <= env["sprite_sheet"].sheet_size[1]
        
        # Check sprite extraction
        sprite_size = env["sprite_sheet"].sprite_size
        num_sprites = (width // sprite_size[0]) * (height // sprite_size[1])
        assert num_sprites > 0

def test_renderer_performance(test_environment):
    """Test rendering performance with multiple layers."""
    env = test_environment
    
    # Create test surface
    surface = pygame.Surface((800, 600))
    
    # Prepare test data
    hex_coords = [(q, r) for q in range(5) for r in range(5)]
    terrain_types = ["test_base_0", "test_base_1", "test_base_2"]
    features = ["test_features_0", "test_features_1"]
    overlays = ["test_overlay_0"]
    effects = ["test_effects_0"]
    
    # Measure rendering time
    start_time = time.time()
    
    for coord in hex_coords:
        env["renderer"].render_hex_tile(
            surface,
            coord,
            terrain_types[coord[0] % len(terrain_types)],
            features=[features[coord[1] % len(features)]],
            overlays=[overlays[0]],
            effects=[effects[0]]
        )
    
    render_time = time.time() - start_time
    
    # Performance should be reasonable (adjust threshold as needed)
    assert render_time < 1.0  # Should render 25 tiles in under 1 second

def test_metadata_search_and_filtering(test_environment):
    """Test metadata management and search functionality."""
    env = test_environment
    
    # Add test metadata
    test_metadata = [
        {"id": "test_base_0", "category": "base", "tags": ["grass", "basic"]},
        {"id": "test_base_1", "category": "base", "tags": ["water", "animated"]},
        {"id": "test_features_0", "category": "features", "tags": ["tree", "tall"]},
    ]
    
    for meta in test_metadata:
        env["metadata_manager"].add_metadata(meta["id"], meta)
    
    # Test search functionality
    water_assets = env["metadata_manager"].search({"tags": ["water"]})
    assert len(water_assets) == 1
    assert water_assets[0]["id"] == "test_base_1"
    
    base_assets = env["metadata_manager"].search({"category": "base"})
    assert len(base_assets) == 2

def test_ui_interaction(test_environment):
    """Test UI component interaction with the asset system."""
    env = test_environment
    
    # Initialize UI
    screen = pygame.Surface((1024, 768))
    manager = pygame_gui.UIManager((1024, 768))
    
    # Test category navigation
    categories = env["preview_ui"].get_categories()
    assert "base" in categories
    assert "features" in categories
    
    # Test asset loading in UI
    selected_asset = env["preview_ui"].select_asset("test_base_0")
    assert selected_asset is not None
    
    # Test preview rendering
    preview_surface = env["preview_ui"].render_preview(selected_asset)
    assert preview_surface is not None

def test_error_handling_and_recovery(test_environment):
    """Test system behavior with invalid assets and error conditions."""
    env = test_environment
    
    # Test loading non-existent asset
    result = env["asset_manager"].load_hex_image(
        "nonexistent.png",
        "base",
        lazy=False
    )
    assert result is None
    
    # Test invalid sprite sheet generation
    result = env["asset_manager"].generate_sprite_sheet("nonexistent")
    assert result is None
    
    # Test cache recovery after errors
    initial_memory = env["cache"].current_memory
    env["cache"].put("test", pygame.Surface((64, 64)))
    assert env["cache"].current_memory > initial_memory
    
    # Clear cache and verify recovery
    env["cache"].clear()
    assert env["cache"].current_memory == 0 