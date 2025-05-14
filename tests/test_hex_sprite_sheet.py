"""
Tests for the hex sprite sheet generator.
"""

import pytest
import pygame
import numpy as np
from pathlib import Path
from PIL import Image
from visual_client.core.managers.hex_sprite_sheet import HexSpriteSheet

@pytest.fixture
def sprite_sheet():
    """Create a test sprite sheet instance."""
    return HexSpriteSheet(sheet_size=(256, 256), sprite_size=(64, 64))

@pytest.fixture
def test_sprites(tmp_path):
    """Create test sprite files."""
    sprite_dir = tmp_path / "test_sprites"
    sprite_dir.mkdir()
    
    sprites = []
    for i in range(4):
        # Create test sprite with unique color
        color = (i * 50, 255 - i * 50, i * 30, 255)
        img = Image.new("RGBA", (64, 64), color)
        path = sprite_dir / f"test_sprite_{i}.png"
        img.save(path)
        sprites.append(path)
    
    return sprite_dir, sprites

def test_init(sprite_sheet):
    """Test sprite sheet initialization."""
    assert sprite_sheet.sheet_size == (256, 256)
    assert sprite_sheet.sprite_size == (64, 64)
    assert sprite_sheet.sprites_per_row == 4
    assert sprite_sheet.sprites_per_col == 4
    assert sprite_sheet.max_sprites == 16

def test_load_sprites(sprite_sheet, test_sprites):
    """Test loading sprites from directory."""
    sprite_dir, _ = test_sprites
    sprites = sprite_sheet.load_sprites_from_directory(sprite_dir)
    
    assert len(sprites) == 4
    for sprite in sprites:
        assert isinstance(sprite, pygame.Surface)
        assert sprite.get_size() == (64, 64)

def test_generate_sheet(sprite_sheet, test_sprites, tmp_path):
    """Test generating sprite sheet."""
    sprite_dir, _ = test_sprites
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Load sprites and generate sheet
    sprites = sprite_sheet.load_sprites_from_directory(sprite_dir)
    positions = sprite_sheet.generate_sheet(sprites, output_dir, "test")
    
    # Verify output
    assert len(positions) == 4
    assert (output_dir / "test_sheet_0.png").exists()
    
    # Check sprite positions
    for i in range(4):
        x = (i % 4) * 64
        y = (i // 4) * 64
        assert positions[i] == (x, y)

def test_extract_sprite(sprite_sheet, test_sprites, tmp_path):
    """Test extracting sprite from sheet."""
    sprite_dir, _ = test_sprites
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Generate sheet
    sprites = sprite_sheet.load_sprites_from_directory(sprite_dir)
    positions = sprite_sheet.generate_sheet(sprites, output_dir, "test")
    sheet = pygame.image.load(str(output_dir / "test_sheet_0.png"))
    
    # Extract and verify each sprite
    for i, original in enumerate(sprites):
        position = positions[i]
        extracted = sprite_sheet.extract_sprite(sheet, position)
        
        assert extracted is not None
        assert extracted.get_size() == (64, 64)
        
        # Compare pixel data
        original_array = pygame.surfarray.array3d(original)
        extracted_array = pygame.surfarray.array3d(extracted)
        assert np.array_equal(original_array, extracted_array)

def test_error_handling(sprite_sheet):
    """Test error handling for invalid operations."""
    # Test loading from non-existent directory
    sprites = sprite_sheet.load_sprites_from_directory(Path("nonexistent"))
    assert sprites == []
    
    # Test generating sheet with no sprites
    positions = sprite_sheet.generate_sheet([], Path("output"), "test")
    assert positions == {} 