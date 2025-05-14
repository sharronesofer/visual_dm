"""
Hex-based asset management system extending the base AssetManager.
"""

import os
import pygame
import json
from typing import Dict, Optional, Any, List, Tuple
from pathlib import Path
from PIL import Image
import numpy as np
from .asset_manager import AssetManager
from .error_handler import handle_component_error, ErrorSeverity

class HexAssetManager(AssetManager):
    """Manages hex-based game assets with specialized features."""
    
    def __init__(self, asset_dir: str = "assets"):
        """Initialize the hex asset manager.
        
        Args:
            asset_dir: Directory containing game assets
        """
        super().__init__(asset_dir)
        self.hex_metadata: Dict[str, Dict[str, Any]] = {}
        self.sprite_sheets: Dict[str, pygame.Surface] = {}
        self.memory_usage: Dict[str, int] = {}
        self._setup_hex_directories()
        
    def _setup_hex_directories(self) -> None:
        """Set up required hex asset directories."""
        try:
            hex_directories = [
                "terrain/base",
                "terrain/features",
                "terrain/overlay",
                "terrain/variations",
                "terrain/test_overlays",
                "terrain/test_all"
            ]
            
            for directory in hex_directories:
                path = self.asset_dir / directory
                path.mkdir(parents=True, exist_ok=True)
                
        except Exception as e:
            handle_component_error(
                "HexAssetManager",
                "_setup_hex_directories",
                e,
                ErrorSeverity.ERROR
            )
            
    def load_hex_image(
        self,
        path: str,
        category: str,
        metadata: Optional[Dict[str, Any]] = None,
        lazy: bool = True,
        optimize: bool = True,
        cache: bool = True
    ) -> Optional[pygame.Surface]:
        """Load a hex-based image with metadata tracking.
        
        Args:
            path: Path to the image file
            category: Asset category (base, feature, overlay, variation)
            metadata: Additional metadata for the asset
            lazy: Whether to use lazy loading
            optimize: Whether to optimize the image
            cache: Whether to cache the loaded image
            
        Returns:
            Loaded image surface or None if loading failed
        """
        try:
            # Check cache first
            if cache and path in self.cache:
                return self.cache[path]
                
            full_path = self.asset_dir / "terrain" / category / path
            
            if lazy:
                # Add to loading queue with metadata
                self.loading_queue[path] = {
                    "type": "hex_image",
                    "path": str(full_path),
                    "category": category,
                    "metadata": metadata,
                    "optimize": optimize,
                    "cache": cache
                }
                return None
                
            # Load immediately
            surface = pygame.image.load(str(full_path))
            
            if optimize:
                surface = self._optimize_hex_image(surface)
                
            if cache:
                self.cache[path] = surface
                
            # Store metadata
            if metadata:
                self.hex_metadata[path] = {
                    "category": category,
                    "dimensions": surface.get_size(),
                    "memory": surface.get_bytesize() * surface.get_size()[0] * surface.get_size()[1],
                    **metadata
                }
                self.memory_usage[path] = self.hex_metadata[path]["memory"]
                
            return surface
            
        except Exception as e:
            handle_component_error(
                "HexAssetManager",
                "load_hex_image",
                e,
                ErrorSeverity.ERROR,
                {"path": path, "category": category}
            )
            return None
            
    def _optimize_hex_image(self, surface: pygame.Surface) -> pygame.Surface:
        """Optimize a hex image surface for better performance.
        
        Args:
            surface: Image surface to optimize
            
        Returns:
            Optimized image surface
        """
        try:
            # Convert to optimal format for hex tiles
            if surface.get_bitsize() != 32:
                surface = surface.convert_alpha()
            else:
                surface = surface.convert()
                
            # Additional hex-specific optimizations can be added here
            return surface
            
        except Exception as e:
            handle_component_error(
                "HexAssetManager",
                "_optimize_hex_image",
                e,
                ErrorSeverity.ERROR
            )
            return surface
            
    def generate_sprite_sheet(
        self,
        category: str,
        pattern: str = "*.png",
        sheet_name: str = "sheet"
    ) -> Optional[str]:
        """Generate a sprite sheet from individual hex assets.
        
        Args:
            category: Asset category to create sheet from
            pattern: File pattern to match
            sheet_name: Name for the generated sheet
            
        Returns:
            Path to the generated sprite sheet or None if failed
        """
        try:
            source_dir = self.asset_dir / "terrain" / category
            images = list(source_dir.glob(pattern))
            
            if not images:
                return None
                
            # Calculate sheet dimensions
            num_images = len(images)
            sheet_width = min(8, num_images)  # Max 8 sprites per row
            sheet_height = (num_images + sheet_width - 1) // sheet_width
            
            # Get sprite dimensions from first image
            with Image.open(images[0]) as img:
                sprite_width, sprite_height = img.size
                
            # Create sheet surface
            sheet = pygame.Surface(
                (sheet_width * sprite_width, sheet_height * sprite_height),
                pygame.SRCALPHA
            )
            
            # Place sprites on sheet
            for i, image_path in enumerate(images):
                x = (i % sheet_width) * sprite_width
                y = (i // sheet_width) * sprite_height
                
                sprite = pygame.image.load(str(image_path))
                sheet.blit(sprite, (x, y))
                
            # Save sheet
            output_path = self.asset_dir / "terrain" / f"{sheet_name}_{category}.png"
            pygame.image.save(sheet, str(output_path))
            
            # Store sheet
            self.sprite_sheets[f"{category}_{sheet_name}"] = sheet
            
            return str(output_path)
            
        except Exception as e:
            handle_component_error(
                "HexAssetManager",
                "generate_sprite_sheet",
                e,
                ErrorSeverity.ERROR,
                {"category": category, "pattern": pattern}
            )
            return None
            
    def get_hex_metadata(self, path: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a hex asset.
        
        Args:
            path: Path to the asset
            
        Returns:
            Asset metadata or None if not found
        """
        return self.hex_metadata.get(path)
        
    def get_memory_usage(self, category: Optional[str] = None) -> int:
        """Get total memory usage of loaded hex assets.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            Total memory usage in bytes
        """
        if category:
            return sum(
                size for path, size in self.memory_usage.items()
                if self.hex_metadata.get(path, {}).get("category") == category
            )
        return sum(self.memory_usage.values())
        
    def clear_hex_cache(self, category: Optional[str] = None) -> None:
        """Clear hex asset cache.
        
        Args:
            category: Optional category to clear
        """
        try:
            if category:
                # Clear specific category
                paths_to_clear = [
                    path for path in self.cache.keys()
                    if self.hex_metadata.get(path, {}).get("category") == category
                ]
                for path in paths_to_clear:
                    del self.cache[path]
                    del self.hex_metadata[path]
                    del self.memory_usage[path]
            else:
                # Clear all hex assets
                self.hex_metadata.clear()
                self.sprite_sheets.clear()
                self.memory_usage.clear()
                self.cache.clear()
                
        except Exception as e:
            handle_component_error(
                "HexAssetManager",
                "clear_hex_cache",
                e,
                ErrorSeverity.ERROR,
                {"category": category}
            )
            
    def process_hex_loading_queue(self) -> None:
        """Process the hex asset loading queue."""
        try:
            for path, info in list(self.loading_queue.items()):
                if info["type"] == "hex_image":
                    surface = pygame.image.load(info["path"])
                    if info["optimize"]:
                        surface = self._optimize_hex_image(surface)
                    if info["cache"]:
                        self.cache[path] = surface
                        
                    # Store metadata
                    if info.get("metadata"):
                        self.hex_metadata[path] = {
                            "category": info["category"],
                            "dimensions": surface.get_size(),
                            "memory": surface.get_bytesize() * surface.get_size()[0] * surface.get_size()[1],
                            **info["metadata"]
                        }
                        self.memory_usage[path] = self.hex_metadata[path]["memory"]
                        
                    del self.loading_queue[path]
                    
        except Exception as e:
            handle_component_error(
                "HexAssetManager",
                "process_hex_loading_queue",
                e,
                ErrorSeverity.ERROR
            )
            
    def load_terrain(self, terrain_type: str) -> Optional[pygame.Surface]:
        """Load a terrain image from the base directory."""
        filename = f"terrain_{terrain_type}_00.png"
        return self.load_hex_image(filename, "base", metadata={"type": terrain_type}, lazy=False) 