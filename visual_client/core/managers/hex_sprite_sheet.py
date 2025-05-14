"""
Sprite sheet generator for hex-based assets.
"""

import pygame
import math
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from PIL import Image
import numpy as np
from ..error_handler import handle_component_error, ErrorSeverity

class HexSpriteSheet:
    """Manages sprite sheets for hex-based assets."""
    
    def __init__(
        self,
        sheet_size: Tuple[int, int] = (2048, 2048),
        sprite_size: Tuple[int, int] = (64, 64)
    ):
        """Initialize the sprite sheet generator.
        
        Args:
            sheet_size: Maximum dimensions for sprite sheets
            sprite_size: Size of individual sprites
        """
        self.sheet_size = sheet_size
        self.sprite_size = sprite_size
        self.sprites_per_row = sheet_size[0] // sprite_size[0]
        self.sprites_per_col = sheet_size[1] // sprite_size[1]
        self.max_sprites = self.sprites_per_row * self.sprites_per_col
        
    def generate_sheet(
        self,
        sprites: List[pygame.Surface],
        output_path: Path,
        category: str
    ) -> Dict[str, Tuple[int, int]]:
        """Generate a sprite sheet from individual sprites.
        
        Args:
            sprites: List of sprite surfaces to combine
            output_path: Where to save the sprite sheet
            category: Category name for the sprites
            
        Returns:
            Dictionary mapping sprite indices to their positions
        """
        try:
            # Calculate required sheets
            num_sheets = math.ceil(len(sprites) / self.max_sprites)
            sprite_positions = {}
            
            for sheet_idx in range(num_sheets):
                # Create sheet surface
                sheet = pygame.Surface(self.sheet_size, pygame.SRCALPHA)
                start_idx = sheet_idx * self.max_sprites
                end_idx = min(start_idx + self.max_sprites, len(sprites))
                
                # Place sprites on sheet
                for i, sprite in enumerate(sprites[start_idx:end_idx], start=start_idx):
                    row = (i % self.max_sprites) // self.sprites_per_row
                    col = (i % self.max_sprites) % self.sprites_per_row
                    x = col * self.sprite_size[0]
                    y = row * self.sprite_size[1]
                    
                    sheet.blit(sprite, (x, y))
                    sprite_positions[i] = (x, y)
                
                # Save sheet
                sheet_path = output_path / f"{category}_sheet_{sheet_idx}.png"
                pygame.image.save(sheet, str(sheet_path))
                
            return sprite_positions
            
        except Exception as e:
            handle_component_error(
                e,
                "Failed to generate sprite sheet",
                ErrorSeverity.ERROR,
                component="HexSpriteSheet"
            )
            return {}
            
    def load_sprites_from_directory(
        self,
        directory: Path,
        pattern: str = "*.png"
    ) -> List[pygame.Surface]:
        """Load all sprites from a directory.
        
        Args:
            directory: Directory containing sprite images
            pattern: File pattern to match
            
        Returns:
            List of loaded sprite surfaces
        """
        try:
            sprites = []
            for sprite_path in sorted(directory.glob(pattern)):
                sprite = pygame.image.load(str(sprite_path))
                if sprite.get_size() != self.sprite_size:
                    sprite = pygame.transform.scale(sprite, self.sprite_size)
                sprites.append(sprite)
            return sprites
            
        except Exception as e:
            handle_component_error(
                e,
                "Failed to load sprites from directory",
                ErrorSeverity.ERROR,
                component="HexSpriteSheet"
            )
            return []
            
    def extract_sprite(
        self,
        sheet: pygame.Surface,
        position: Tuple[int, int]
    ) -> Optional[pygame.Surface]:
        """Extract a single sprite from a sheet.
        
        Args:
            sheet: The sprite sheet surface
            position: Position of the sprite (x, y)
            
        Returns:
            The extracted sprite surface
        """
        try:
            sprite = pygame.Surface(self.sprite_size, pygame.SRCALPHA)
            sprite.blit(sheet, (0, 0), (*position, *self.sprite_size))
            return sprite
            
        except Exception as e:
            handle_component_error(
                e,
                "Failed to extract sprite from sheet",
                ErrorSeverity.ERROR,
                component="HexSpriteSheet"
            )
            return None 