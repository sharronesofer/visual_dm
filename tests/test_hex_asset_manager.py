"""
Tests for the hex asset management system.
"""

import os
import pytest
import pygame
import shutil
from pathlib import Path
from PIL import Image
import numpy as np
from visual_client.core.managers.hex_asset_manager import HexAssetManager

# Test fixtures
@pytest.fixture
def test_assets_dir(tmp_path):
    """Create a temporary assets directory with test files."""
    assets_dir = tmp_path / "assets"
    terrain_dir = assets_dir / "terrain"
    
    # Create test directories
    for category in ["base", "features", "overlay", "variations"]:
        category_dir = terrain_dir / category
        category_dir.mkdir(parents=True)
        
        # Create test images
        for i in range(3):
            img = Image.new("RGBA", (64, 64), (255, 0, 0, 255))
            img.save(category_dir / f"test_{i}.png")
            
    return assets_dir

@pytest.fixture
def hex_manager(test_assets_dir):
    """Create a HexAssetManager instance with test assets."""
    pygame.init()
    manager = HexAssetManager(str(test_assets_dir))
    yield manager
    pygame.quit()

# Tests
def test_init(hex_manager, test_assets_dir):
    """Test manager initialization."""
    assert hex_manager.asset_dir == Path(test_assets_dir)
    assert isinstance(hex_manager.hex_metadata, dict)
    assert isinstance(hex_manager.sprite_sheets, dict)
    assert isinstance(hex_manager.memory_usage, dict)
    
    # Check directory structure
    for category in ["base", "features", "overlay", "variations"]:
        assert (test_assets_dir / "terrain" / category).exists()

def test_load_hex_image(hex_manager):
    """Test loading hex images."""
    # Test immediate loading
    surface = hex_manager.load_hex_image(
        "test_0.png",
        "base",
        lazy=False
    )
    assert isinstance(surface, pygame.Surface)
    assert surface.get_size() == (64, 64)
    
    # Test lazy loading
    surface = hex_manager.load_hex_image(
        "test_1.png",
        "base",
        lazy=True
    )
    assert surface is None
    assert "test_1.png" in hex_manager.loading_queue
    
    # Test metadata
    metadata = {"type": "grass", "variant": "normal"}
    surface = hex_manager.load_hex_image(
        "test_2.png",
        "base",
        metadata=metadata,
        lazy=False
    )
    stored_metadata = hex_manager.get_hex_metadata("test_2.png")
    assert stored_metadata["type"] == "grass"
    assert stored_metadata["variant"] == "normal"
    assert "dimensions" in stored_metadata
    assert "memory" in stored_metadata

def test_generate_sprite_sheet(hex_manager, test_assets_dir):
    """Test sprite sheet generation."""
    output_path = hex_manager.generate_sprite_sheet("base")
    assert output_path is not None
    assert Path(output_path).exists()
    
    # Load and verify sheet
    sheet = Image.open(output_path)
    assert sheet.size == (192, 64)  # 3 64x64 images in a row
    
    # Check if sheet is stored in manager
    assert "base_sheet" in hex_manager.sprite_sheets

def test_memory_usage(hex_manager):
    """Test memory usage tracking."""
    # Load some assets
    for i in range(3):
        hex_manager.load_hex_image(
            f"test_{i}.png",
            "base",
            lazy=False
        )
        
    # Check total memory usage
    total_usage = hex_manager.get_memory_usage()
    assert total_usage > 0
    
    # Check category memory usage
    base_usage = hex_manager.get_memory_usage("base")
    assert base_usage > 0
    assert base_usage == total_usage  # Since we only loaded base assets

def test_clear_hex_cache(hex_manager):
    """Test cache clearing."""
    # Load some assets
    for i in range(3):
        hex_manager.load_hex_image(
            f"test_{i}.png",
            "base",
            lazy=False
        )
        
    # Clear specific category
    hex_manager.clear_hex_cache("base")
    assert not any(
        meta.get("category") == "base"
        for meta in hex_manager.hex_metadata.values()
    )
    
    # Load more assets
    for i in range(2):
        hex_manager.load_hex_image(
            f"test_{i}.png",
            "features",
            lazy=False
        )
        
    # Clear all
    hex_manager.clear_hex_cache()
    assert len(hex_manager.hex_metadata) == 0
    assert len(hex_manager.sprite_sheets) == 0
    assert len(hex_manager.memory_usage) == 0
    assert len(hex_manager.cache) == 0

def test_process_hex_loading_queue(hex_manager):
    """Test processing the loading queue."""
    # Add some assets to queue
    for i in range(3):
        hex_manager.load_hex_image(
            f"test_{i}.png",
            "base",
            metadata={"index": i},
            lazy=True
        )
        
    # Process queue
    hex_manager.process_hex_loading_queue()
    
    # Verify assets were loaded
    assert len(hex_manager.loading_queue) == 0
    assert len(hex_manager.hex_metadata) == 3
    
    # Check metadata
    for i in range(3):
        metadata = hex_manager.get_hex_metadata(f"test_{i}.png")
        assert metadata["index"] == i
        assert "dimensions" in metadata
        assert "memory" in metadata

def test_error_handling(hex_manager):
    """Test error handling for invalid operations."""
    # Try to load non-existent image
    surface = hex_manager.load_hex_image(
        "nonexistent.png",
        "base",
        lazy=False
    )
    assert surface is None
    
    # Try to generate sheet for empty category
    output_path = hex_manager.generate_sprite_sheet("nonexistent")
    assert output_path is None
    
    # Try to get metadata for non-existent asset
    metadata = hex_manager.get_hex_metadata("nonexistent.png")
    assert metadata is None 