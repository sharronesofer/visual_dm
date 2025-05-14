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
        self.animation_data: Dict[str, Dict[str, Any]] = {}
        self._setup_hex_directories()
        
    def _setup_hex_directories(self) -> None:
        """Set up required hex asset directories."""
        try:
            hex_directories = [
                "terrain/base",
                "terrain/features",
                "terrain/overlay",
                "terrain/variations",
                "terrain/seasonal",
                "terrain/test_overlays",
                "terrain/test_all",
                "terrain/characters",
                "terrain/equipment",
                "terrain/animations"
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
                self._maintain_cache_size()
                
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
            # Try to load fallback image
            fallback_path = self.asset_dir / "terrain" / "base" / "fallback.png"
            if fallback_path.exists():
                return pygame.image.load(str(fallback_path))
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
            if surface.get_alpha():
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
        if category:
            # Clear only assets in the specified category
            for path in list(self.cache.keys()):
                if path in self.hex_metadata and self.hex_metadata[path].get("category") == category:
                    self.cache.pop(path)
                    self.memory_usage.pop(path, None)
                    self.hex_metadata.pop(path, None)
        else:
            # Clear all hex assets
            for path in list(self.hex_metadata.keys()):
                self.cache.pop(path, None)
                
            self.memory_usage.clear()
            self.hex_metadata.clear()
    
    def process_hex_loading_queue(self) -> None:
        """Process hex-specific items in the loading queue."""
        try:
            for path, info in list(self.loading_queue.items()):
                if info["type"] == "hex_image":
                    # Load the image
                    full_path = info["path"]
                    surface = pygame.image.load(full_path)
                    
                    if info.get("optimize", False):
                        surface = self._optimize_hex_image(surface)
                        
                    # Store the loaded surface
                    if info.get("cache", True):
                        self.cache[path] = surface
                        
                    # Store metadata if provided
                    if info.get("metadata"):
                        self.hex_metadata[path] = {
                            "category": info["category"],
                            "dimensions": surface.get_size(),
                            "memory": surface.get_bytesize() * surface.get_size()[0] * surface.get_size()[1],
                            **info["metadata"]
                        }
                        self.memory_usage[path] = self.hex_metadata[path]["memory"]
                        
                    # Remove from queue
                    self.loading_queue.pop(path, None)
                    
            # Let the parent class handle other types
            super().process_loading_queue()
            
        except Exception as e:
            handle_component_error(
                "HexAssetManager",
                "process_hex_loading_queue",
                e,
                ErrorSeverity.ERROR
            )
    
    def load_terrain(self, terrain_type: str) -> Optional[pygame.Surface]:
        """Load a terrain asset.
        
        Args:
            terrain_type: Type of terrain to load
            
        Returns:
            Loaded terrain surface or None if failed
        """
        try:
            # Try to find in base directory first
            path = f"{terrain_type}.png"
            return self.load_hex_image(path, "base")
        except Exception as e:
            handle_component_error(
                "HexAssetManager",
                "load_terrain",
                e,
                ErrorSeverity.ERROR,
                {"terrain_type": terrain_type}
            )
            return None
    
    def load_hex_animation(
        self,
        animation_name: str,
        category: str = "animations",
        frame_width: Optional[int] = None,
        frame_height: Optional[int] = None
    ) -> Optional[List[pygame.Surface]]:
        """Load a hex-based animation.
        
        Args:
            animation_name: Name of the animation
            category: Animation category
            frame_width: Width of each frame (if loading from sprite sheet)
            frame_height: Height of each frame (if loading from sprite sheet)
            
        Returns:
            List of animation frame surfaces or None if failed
        """
        try:
            # Check if we already have animation data
            if animation_name in self.animation_data:
                return self.animation_data[animation_name]["frames"]
                
            # Try to load from sprite sheet first if dimensions provided
            if frame_width and frame_height:
                sheet_path = f"{category}/{animation_name}_sheet.png"
                frames = self.load_sprite_sheet(
                    sheet_path,
                    frame_width,
                    frame_height,
                    lazy=False,
                    optimize=True
                )
                if frames:
                    self.animation_data[animation_name] = {
                        "frames": frames,
                        "durations": [100] * len(frames),  # Default 100ms per frame
                        "loop": True
                    }
                    return frames
                    
            # If no sprite sheet or loading failed, try individual frames
            frame_paths = []
            frame_num = 1
            
            while True:
                frame_path = f"{category}/{animation_name}_{frame_num:02d}.png"
                full_path = self.asset_dir / "terrain" / frame_path
                
                if not full_path.exists():
                    break
                    
                frame_paths.append(frame_path)
                frame_num += 1
                
            if not frame_paths:
                return None
                
            frames = []
            for frame_path in frame_paths:
                frame = self.load_hex_image(frame_path, category)
                if frame:
                    frames.append(frame)
                    
            if frames:
                self.animation_data[animation_name] = {
                    "frames": frames,
                    "durations": [100] * len(frames),  # Default 100ms per frame
                    "loop": True
                }
                
            return frames
            
        except Exception as e:
            handle_component_error(
                "HexAssetManager",
                "load_hex_animation",
                e,
                ErrorSeverity.ERROR,
                {"animation_name": animation_name, "category": category}
            )
            return None
    
    def apply_hex_tint(
        self,
        surface: pygame.Surface,
        tint_color: Tuple[int, int, int],
        alpha: int = 128
    ) -> pygame.Surface:
        """Apply a hex-specific tint to a surface.
        
        Args:
            surface: Surface to tint
            tint_color: RGB tuple (0-255) for tint color
            alpha: Alpha value (0-255) for tint opacity
            
        Returns:
            Tinted surface
        """
        # Delegate to parent class method
        return self.apply_tint_to_surface(surface, tint_color, alpha)
    
    def load_hex_terrain_set(self, terrain_type: str) -> Optional[List[pygame.Surface]]:
        """Load all variants of a hex terrain type.
        
        Args:
            terrain_type: Type of terrain (e.g., 'grass', 'water')
            
        Returns:
            List of terrain variant surfaces or None if loading failed
        """
        return self.load_terrain_set(terrain_type)
    
    def load_hex_feature_set(self, feature_type: str) -> Optional[List[pygame.Surface]]:
        """Load all variants of a hex feature type.
        
        Args:
            feature_type: Type of feature (e.g., 'tree', 'rock')
            
        Returns:
            List of feature variant surfaces or None if loading failed
        """
        try:
            frames = []
            for i in range(1, 6):  # Try up to 5 variations
                path = f"{feature_type}_{i:02d}.png"
                frame = self.load_hex_image(path, "features")
                if frame:
                    frames.append(frame)
                    
            return frames if frames else None
            
        except Exception as e:
            handle_component_error(
                "HexAssetManager",
                "load_hex_feature_set",
                e,
                ErrorSeverity.ERROR,
                {"feature_type": feature_type}
            )
            return None
    
    def load_hex_seasonal_variations(self, base_asset: str) -> Optional[Dict[str, pygame.Surface]]:
        """Load seasonal variations of a hex asset.
        
        Args:
            base_asset: Base asset name
            
        Returns:
            Dictionary of season to surface mappings or None if loading failed
        """
        try:
            seasons = {
                "summer": "summer",
                "autumn": "autumn", 
                "winter": "winter",
                "spring": "spring",
                "rain": "rain",
                "snow": "snow",
                "fog": "fog"
            }
            
            variations = {}
            
            for season_key, season_name in seasons.items():
                path = f"{season_name}_{base_asset}"
                surface = self.load_hex_image(path, "seasonal")
                if surface:
                    variations[season_key] = surface
                    
            return variations if variations else None
            
        except Exception as e:
            handle_component_error(
                "HexAssetManager",
                "load_hex_seasonal_variations",
                e,
                ErrorSeverity.ERROR,
                {"base_asset": base_asset}
            )
            return None
    
    def load_hex_asset_index(self, index_path: str) -> Optional[Dict[str, Any]]:
        """Load and validate a hex asset index file.
        
        Args:
            index_path: Path to the index file
            
        Returns:
            Parsed index data or None if loading failed
        """
        try:
            schema_path = "hex_asset_index.schema.json"
            return self.load_json(index_path, validate_schema=True, schema_path=schema_path)
        except Exception as e:
            handle_component_error(
                "HexAssetManager",
                "load_hex_asset_index",
                e,
                ErrorSeverity.ERROR,
                {"index_path": index_path}
            )
            return None 