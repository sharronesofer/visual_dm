"""
Asset management system with lazy loading and caching.
"""

import os
import pygame
import json
import re
from typing import Dict, Optional, Any, Tuple, List
from pathlib import Path
import numpy as np
from .error_handler import handle_component_error, ErrorSeverity

class AssetManager:
    """Manages loading, caching, and optimization of game assets, with LOD support."""
    
    def __init__(self, asset_dir: str = "assets"):
        """Initialize the asset manager.
        
        Args:
            asset_dir: Directory containing game assets
        """
        self.asset_dir = Path(asset_dir)
        self.cache: Dict[str, Any] = {}
        self.loading_queue: Dict[str, Dict[str, Any]] = {}
        self.asset_metadata: Dict[str, Dict[str, Any]] = {}
        self.sprite_sheets: Dict[str, Dict[str, Any]] = {}
        self.cache_size_limit = 100  # Default cache size limit
        self.asset_lod_metadata: Dict[str, Dict[int, Dict[str, Any]]] = {}  # asset_id -> {lod_level: metadata}
        self._setup_directories()
        
    def _setup_directories(self) -> None:
        """Set up required asset directories."""
        try:
            # Create main asset directories
            directories = [
                "images",
                "sounds",
                "fonts",
                "data",
                "cache",
                "sprite_sheets"
            ]
            
            for directory in directories:
                path = self.asset_dir / directory
                path.mkdir(parents=True, exist_ok=True)
                
            # Create cache directory
            cache_dir = self.asset_dir / "cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "_setup_directories",
                e,
                ErrorSeverity.ERROR
            )
            
    def load_image(
        self,
        path: str,
        lazy: bool = True,
        optimize: bool = True,
        cache: bool = True
    ) -> Optional[pygame.Surface]:
        """Load an image with optional lazy loading and optimization.
        
        Args:
            path: Path to the image file
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
                
            full_path = self.asset_dir / "images" / path
            
            if lazy:
                # Add to loading queue
                self.loading_queue[path] = {
                    "type": "image",
                    "path": str(full_path),
                    "optimize": optimize,
                    "cache": cache
                }
                return None
                
            # Load immediately
            surface = pygame.image.load(str(full_path))
            
            if optimize:
                surface = self._optimize_image(surface)
                
            if cache:
                self.cache[path] = surface
                self._maintain_cache_size()
                
            return surface
            
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "load_image",
                e,
                ErrorSeverity.ERROR,
                {"path": path}
            )
            # Try to load fallback image
            try:
                fallback_path = self.asset_dir / "images" / "fallback.png"
                if fallback_path.exists():
                    return pygame.image.load(str(fallback_path))
            except:
                pass
            return None
            
    def _optimize_image(self, surface: pygame.Surface) -> pygame.Surface:
        """Optimize an image surface for better performance.
        
        Args:
            surface: Image surface to optimize
            
        Returns:
            Optimized image surface
        """
        try:
            # Convert to optimal format
            if surface.get_alpha():
                surface = surface.convert_alpha()
            else:
                surface = surface.convert()
                
            # Apply any additional optimizations here
            return surface
            
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "_optimize_image",
                e,
                ErrorSeverity.ERROR
            )
            return surface
            
    def load_sound(
        self,
        path: str,
        lazy: bool = True,
        cache: bool = True
    ) -> Optional[pygame.mixer.Sound]:
        """Load a sound file with optional lazy loading.
        
        Args:
            path: Path to the sound file
            lazy: Whether to use lazy loading
            cache: Whether to cache the loaded sound
            
        Returns:
            Loaded sound object or None if loading failed
        """
        try:
            # Check cache first
            if cache and path in self.cache:
                return self.cache[path]
                
            full_path = self.asset_dir / "sounds" / path
            
            if lazy:
                # Add to loading queue
                self.loading_queue[path] = {
                    "type": "sound",
                    "path": str(full_path),
                    "cache": cache
                }
                return None
                
            # Load immediately
            sound = pygame.mixer.Sound(str(full_path))
            
            if cache:
                self.cache[path] = sound
                self._maintain_cache_size()
                
            return sound
            
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "load_sound",
                e,
                ErrorSeverity.ERROR,
                {"path": path}
            )
            return None
            
    def load_font(
        self,
        path: str,
        size: int,
        lazy: bool = True,
        cache: bool = True
    ) -> Optional[pygame.font.Font]:
        """Load a font file with optional lazy loading.
        
        Args:
            path: Path to the font file
            size: Font size
            lazy: Whether to use lazy loading
            cache: Whether to cache the loaded font
            
        Returns:
            Loaded font object or None if loading failed
        """
        try:
            cache_key = f"{path}:{size}"
            
            # Check cache first
            if cache and cache_key in self.cache:
                return self.cache[cache_key]
                
            full_path = self.asset_dir / "fonts" / path
            
            if lazy:
                # Add to loading queue
                self.loading_queue[cache_key] = {
                    "type": "font",
                    "path": str(full_path),
                    "size": size,
                    "cache": cache
                }
                return None
                
            # Load immediately
            font = pygame.font.Font(str(full_path), size)
            
            if cache:
                self.cache[cache_key] = font
                self._maintain_cache_size()
                
            return font
            
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "load_font",
                e,
                ErrorSeverity.ERROR,
                {"path": path, "size": size}
            )
            return None
            
    def load_json(
        self,
        path: str,
        validate_schema: bool = False,
        schema_path: Optional[str] = None,
        lazy: bool = True,
        cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Load and parse a JSON file with optional schema validation.
        
        Args:
            path: Path to the JSON file
            validate_schema: Whether to validate against a schema
            schema_path: Path to the JSON schema file (required if validate_schema is True)
            lazy: Whether to use lazy loading
            cache: Whether to cache the loaded data
            
        Returns:
            Parsed JSON data or None if loading failed
        """
        try:
            # Check cache first
            if cache and path in self.cache:
                return self.cache[path]
                
            full_path = self.asset_dir / "data" / path
            
            if lazy:
                # Add to loading queue
                self.loading_queue[path] = {
                    "type": "json",
                    "path": str(full_path),
                    "validate_schema": validate_schema,
                    "schema_path": schema_path,
                    "cache": cache
                }
                return None
                
            # Load immediately
            with open(full_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            # Validate against schema if requested
            if validate_schema and schema_path:
                schema_full_path = self.asset_dir / "data" / schema_path
                with open(schema_full_path, 'r', encoding='utf-8') as schema_file:
                    schema = json.load(schema_file)
                
                # Basic validation - in a real implementation, use a proper JSON schema validator
                if not self._validate_json_schema(data, schema):
                    handle_component_error(
                        "AssetManager",
                        "load_json",
                        ValueError("JSON validation failed"),
                        ErrorSeverity.ERROR,
                        {"path": path}
                    )
                    return None
                    
            if cache:
                self.cache[path] = data
                self._maintain_cache_size()
                
            return data
            
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "load_json",
                e,
                ErrorSeverity.ERROR,
                {"path": path}
            )
            return None
            
    def _validate_json_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Basic JSON schema validation.
        
        Note: This is a placeholder. In a real implementation, use a library like jsonschema.
        
        Args:
            data: JSON data to validate
            schema: JSON schema to validate against
            
        Returns:
            True if valid, False otherwise
        """
        # This is a very basic implementation
        # In a real system, use the jsonschema library or similar
        try:
            # Check required fields
            if "required" in schema:
                for field in schema["required"]:
                    if field not in data:
                        return False
                        
            # Check property types (basic)
            if "properties" in schema and isinstance(schema["properties"], dict):
                for prop, prop_schema in schema["properties"].items():
                    if prop in data:
                        if "type" in prop_schema:
                            if prop_schema["type"] == "string" and not isinstance(data[prop], str):
                                return False
                            elif prop_schema["type"] == "number" and not isinstance(data[prop], (int, float)):
                                return False
                            elif prop_schema["type"] == "integer" and not isinstance(data[prop], int):
                                return False
                            elif prop_schema["type"] == "array" and not isinstance(data[prop], list):
                                return False
                            elif prop_schema["type"] == "object" and not isinstance(data[prop], dict):
                                return False
                                
            return True
            
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "_validate_json_schema",
                e,
                ErrorSeverity.ERROR
            )
            return False
            
    def process_loading_queue(self) -> None:
        """Process the loading queue to load assets in the background."""
        try:
            for path, info in list(self.loading_queue.items()):
                if info["type"] == "image":
                    surface = pygame.image.load(info["path"])
                    if info.get("optimize", False):
                        surface = self._optimize_image(surface)
                    if info.get("cache", True):
                        self.cache[path] = surface
                        
                elif info["type"] == "sound":
                    sound = pygame.mixer.Sound(info["path"])
                    if info.get("cache", True):
                        self.cache[path] = sound
                        
                elif info["type"] == "font":
                    font = pygame.font.Font(info["path"], info["size"])
                    if info.get("cache", True):
                        self.cache[path] = font
                        
                elif info["type"] == "sprite_sheet":
                    sheet_surface = pygame.image.load(info["path"])
                    
                    # Calculate rows and columns if not provided
                    cols = info.get("cols") or sheet_surface.get_width() // info["frame_width"]
                    rows = info.get("rows") or sheet_surface.get_height() // info["frame_height"]
                    
                    frames = []
                    
                    # Extract individual frames
                    for row in range(rows):
                        for col in range(cols):
                            frame_rect = pygame.Rect(
                                col * info["frame_width"],
                                row * info["frame_height"],
                                info["frame_width"],
                                info["frame_height"]
                            )
                            
                            frame = pygame.Surface((info["frame_width"], info["frame_height"]), pygame.SRCALPHA)
                            frame.blit(sheet_surface, (0, 0), frame_rect)
                            
                            if info.get("optimize", False):
                                frame = self._optimize_image(frame)
                                
                            frames.append(frame)
                            
                    if info.get("cache", True):
                        self.sprite_sheets[path] = {
                            "sheet": sheet_surface,
                            "frames": frames,
                            "frame_width": info["frame_width"],
                            "frame_height": info["frame_height"],
                            "rows": rows,
                            "cols": cols
                        }
                        
                elif info["type"] == "json":
                    with open(info["path"], 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        
                    if info.get("validate_schema", False) and info.get("schema_path"):
                        schema_path = self.asset_dir / "data" / info["schema_path"]
                        with open(schema_path, 'r', encoding='utf-8') as schema_file:
                            schema = json.load(schema_file)
                            
                        if not self._validate_json_schema(data, schema):
                            continue
                            
                    if info.get("cache", True):
                        self.cache[path] = data
                        
                # Remove processed item from queue
                self.loading_queue.pop(path, None)
                
            # Maintain cache size after processing
            self._maintain_cache_size()
                
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "process_loading_queue",
                e,
                ErrorSeverity.ERROR
            )
            
    def clear_cache(self) -> None:
        """Clear all cached assets."""
        self.cache.clear()
        self.sprite_sheets.clear()
        
    def get_cache_size(self) -> int:
        """Get the current size of the cache.
        
        Returns:
            Number of items in the cache
        """
        return len(self.cache) + len(self.sprite_sheets)
            
    def preload_assets(self, manifest_path: str) -> None:
        """Preload assets based on a manifest file.
        
        Args:
            manifest_path: Path to the manifest JSON file
        """
        try:
            manifest_data = self.load_json(manifest_path, lazy=False)
            
            if not manifest_data:
                return
                
            # Process each asset type in the manifest
            if "images" in manifest_data:
                for img_path in manifest_data["images"]:
                    self.load_image(img_path, lazy=True)
                    
            if "sprite_sheets" in manifest_data:
                for sheet in manifest_data["sprite_sheets"]:
                    self.load_sprite_sheet(
                        sheet["path"],
                        sheet["frame_width"],
                        sheet["frame_height"],
                        sheet.get("rows"),
                        sheet.get("cols"),
                        lazy=True
                    )
                    
            if "sounds" in manifest_data:
                for sound_path in manifest_data["sounds"]:
                    self.load_sound(sound_path, lazy=True)
                    
            if "fonts" in manifest_data:
                for font in manifest_data["fonts"]:
                    self.load_font(font["path"], font["size"], lazy=True)
                    
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "preload_assets",
                e,
                ErrorSeverity.ERROR,
                {"manifest_path": manifest_path}
            )
            
    def discover_assets(self) -> Dict[str, list]:
        """Discover all assets in the asset directory.
        
        Returns:
            Dictionary of asset types and their paths
        """
        asset_map = {
            "images": [],
            "sounds": [],
            "fonts": [],
            "data": []
        }
        
        try:
            for asset_type in asset_map.keys():
                asset_dir = self.asset_dir / asset_type
                if asset_dir.exists():
                    for file_path in asset_dir.glob("**/*.*"):
                        if file_path.is_file():
                            rel_path = str(file_path.relative_to(asset_dir))
                            asset_map[asset_type].append(rel_path)
                            
            return asset_map
            
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "discover_assets",
                e,
                ErrorSeverity.ERROR
            )
            return asset_map
            
    def validate_assets(self) -> Dict[str, list]:
        """Validate all assets in the asset directory.
        
        Returns:
            Dictionary of asset types and invalid assets
        """
        invalid_assets = {
            "images": [],
            "sounds": [],
            "fonts": [],
            "data": []
        }
        
        try:
            assets = self.discover_assets()
            
            # Check each image
            for img_path in assets["images"]:
                try:
                    full_path = self.asset_dir / "images" / img_path
                    pygame.image.load(str(full_path))
                except:
                    invalid_assets["images"].append(img_path)
                    
            # Check each sound
            for sound_path in assets["sounds"]:
                try:
                    full_path = self.asset_dir / "sounds" / sound_path
                    pygame.mixer.Sound(str(full_path))
                except:
                    invalid_assets["sounds"].append(sound_path)
                    
            # Check each font
            for font_path in assets["fonts"]:
                try:
                    full_path = self.asset_dir / "fonts" / font_path
                    pygame.font.Font(str(full_path), 12)  # Test with size 12
                except:
                    invalid_assets["fonts"].append(font_path)
                    
            # Check each data file (JSON)
            for data_path in assets["data"]:
                if data_path.lower().endswith('.json'):
                    try:
                        full_path = self.asset_dir / "data" / data_path
                        with open(full_path, 'r', encoding='utf-8') as f:
                            json.load(f)
                    except:
                        invalid_assets["data"].append(data_path)
                        
            return invalid_assets
            
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "validate_assets",
                e,
                ErrorSeverity.ERROR
            )
            return invalid_assets
            
    def generate_manifest(self, output_path: str) -> None:
        """Generate an asset manifest file.
        
        Args:
            output_path: Path where the manifest will be saved
        """
        try:
            assets = self.discover_assets()
            
            manifest = {
                "version": "1.0.0",
                "generated": True,
                "date": pygame.time.get_ticks(),
                **assets
            }
            
            full_path = self.asset_dir / "data" / output_path
            
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
                
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "generate_manifest",
                e,
                ErrorSeverity.ERROR,
                {"output_path": output_path}
            )
            
    def load_terrain_set(self, terrain_type: str, lazy: bool = True) -> Optional[List[pygame.Surface]]:
        """Load all variations for a terrain type.
        
        Args:
            terrain_type: Type of terrain (e.g., 'grass', 'water')
            lazy: Whether to use lazy loading
            
        Returns:
            List of terrain surfaces or None if loading failed
        """
        try:
            pattern = "{base}_{frame:02d}.png"
            frames = self.load_animation_frames(
                terrain_type,
                6,  # Typical number of terrain variations
                pattern,
                lazy
            )
            return frames
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "load_terrain_set",
                e,
                ErrorSeverity.ERROR,
                {"terrain_type": terrain_type}
            )
            return None
            
    def load_feature_variations(self, feature_type: str, lazy: bool = True) -> Optional[List[pygame.Surface]]:
        """Load all variations for a feature type.
        
        Args:
            feature_type: Type of feature (e.g., 'tree', 'rock')
            lazy: Whether to use lazy loading
            
        Returns:
            List of feature surfaces or None if loading failed
        """
        try:
            pattern = "{base}_{frame:02d}.png"
            frames = self.load_animation_frames(
                feature_type,
                5,  # Typical number of feature variations
                pattern,
                lazy
            )
            return frames
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "load_feature_variations",
                e,
                ErrorSeverity.ERROR,
                {"feature_type": feature_type}
            )
            return None
            
    def load_seasonal_variations(self, asset_name: str, lazy: bool = True) -> Optional[Dict[str, pygame.Surface]]:
        """Load all seasonal variations for a base asset.
        
        Args:
            asset_name: Base asset name
            lazy: Whether to use lazy loading
            
        Returns:
            Dictionary of season to surface mappings or None if loading failed
        """
        try:
            seasons = ['summer', 'autumn', 'winter', 'spring']
            weather = ['rain', 'snow', 'fog']
            
            variations = {}
            
            for season in seasons:
                path = f"variations/{season}_{asset_name}"
                surface = self.load_image(path, lazy)
                if surface:
                    variations[season] = surface
                    
            for condition in weather:
                path = f"variations/{condition}_{asset_name}"
                surface = self.load_image(path, lazy)
                if surface:
                    variations[condition] = surface
                    
            return variations if variations else None
            
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "load_seasonal_variations",
                e,
                ErrorSeverity.ERROR,
                {"asset_name": asset_name}
            )
            return None

    def load_sprite_sheet(
        self,
        path: str,
        frame_width: int,
        frame_height: int,
        rows: Optional[int] = None,
        cols: Optional[int] = None,
        lazy: bool = True,
        optimize: bool = True,
        cache: bool = True
    ) -> Optional[List[pygame.Surface]]:
        """Load a sprite sheet and split it into individual frames.
        
        Args:
            path: Path to the sprite sheet image
            frame_width: Width of each frame in pixels
            frame_height: Height of each frame in pixels
            rows: Optional number of rows in the sheet (auto-calculated if None)
            cols: Optional number of columns in the sheet (auto-calculated if None)
            lazy: Whether to use lazy loading
            optimize: Whether to optimize the frames
            cache: Whether to cache the loaded frames
            
        Returns:
            List of frame surfaces or None if loading failed
        """
        try:
            cache_key = f"{path}:{frame_width}x{frame_height}"
            
            # Check cache first
            if cache and cache_key in self.sprite_sheets:
                return self.sprite_sheets[cache_key]["frames"]
                
            full_path = self.asset_dir / "sprite_sheets" / path
            if not full_path.exists():
                full_path = self.asset_dir / "images" / path
                
            if lazy:
                # Add to loading queue
                self.loading_queue[cache_key] = {
                    "type": "sprite_sheet",
                    "path": str(full_path),
                    "frame_width": frame_width,
                    "frame_height": frame_height,
                    "rows": rows,
                    "cols": cols,
                    "optimize": optimize,
                    "cache": cache
                }
                return None
                
            # Load immediately
            sheet_surface = pygame.image.load(str(full_path))
            
            # Calculate rows and columns if not provided
            if cols is None:
                cols = sheet_surface.get_width() // frame_width
            if rows is None:
                rows = sheet_surface.get_height() // frame_height
                
            frames = []
            
            # Extract individual frames
            for row in range(rows):
                for col in range(cols):
                    # Create rectangle for frame position
                    frame_rect = pygame.Rect(
                        col * frame_width,
                        row * frame_height,
                        frame_width,
                        frame_height
                    )
                    
                    # Create new surface for the frame
                    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    frame.blit(sheet_surface, (0, 0), frame_rect)
                    
                    if optimize:
                        frame = self._optimize_image(frame)
                        
                    frames.append(frame)
                    
            if cache:
                self.sprite_sheets[cache_key] = {
                    "sheet": sheet_surface,
                    "frames": frames,
                    "frame_width": frame_width,
                    "frame_height": frame_height,
                    "rows": rows,
                    "cols": cols
                }
                self._maintain_cache_size()
                
            return frames
            
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "load_sprite_sheet",
                e,
                ErrorSeverity.ERROR,
                {"path": path, "frame_width": frame_width, "frame_height": frame_height}
            )
            return None

    def apply_tint_to_surface(
        self,
        surface: pygame.Surface,
        tint_color: Tuple[int, int, int],
        alpha: int = 255
    ) -> pygame.Surface:
        """Apply a color tint to a surface.
        
        Args:
            surface: Surface to tint
            tint_color: RGB tuple (0-255) for tint color
            alpha: Alpha value (0-255) for tint opacity
            
        Returns:
            Tinted surface
        """
        try:
            # Create a copy to avoid modifying the original
            tinted_surface = surface.copy()
            
            # Create a surface with the tint color
            tint_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            tint_surface.fill((tint_color[0], tint_color[1], tint_color[2], alpha))
            
            # Blit the tint surface onto the copy with blending
            tinted_surface.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            return tinted_surface
            
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "apply_tint_to_surface",
                e,
                ErrorSeverity.ERROR
            )
            return surface

    def load_animation_frames(
        self,
        base_path: str,
        frame_count: int,
        frame_pattern: str = "{base}_{frame:02d}.png",
        lazy: bool = True,
        optimize: bool = True,
        cache: bool = True
    ) -> Optional[List[pygame.Surface]]:
        """Load a sequence of animation frames using a pattern.
        
        Args:
            base_path: Base path/name for the animation frames
            frame_count: Number of frames to load
            frame_pattern: Pattern for frame filenames with {base} and {frame} placeholders
            lazy: Whether to use lazy loading
            optimize: Whether to optimize the frames
            cache: Whether to cache the loaded frames
            
        Returns:
            List of frame surfaces or None if loading failed
        """
        try:
            base_name = Path(base_path).stem
            frames = []
            
            for i in range(frame_count):
                frame_path = frame_pattern.format(base=base_name, frame=i+1)
                frame = self.load_image(frame_path, lazy, optimize, cache)
                
                if frame:
                    frames.append(frame)
                    
            return frames if frames else None
            
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "load_animation_frames",
                e,
                ErrorSeverity.ERROR,
                {"base_path": base_path, "frame_count": frame_count}
            )
            return None

    def _maintain_cache_size(self) -> None:
        """Enforce the cache size limit using LRU eviction."""
        while len(self.cache) > self.cache_size_limit:
            # Remove the first (oldest) item
            if self.cache:
                oldest_key = next(iter(self.cache))
                self.cache.pop(oldest_key)
                
        # Also manage sprite sheet cache
        while len(self.sprite_sheets) > self.cache_size_limit // 2:  # Use half the limit for sprite sheets
            if self.sprite_sheets:
                oldest_key = next(iter(self.sprite_sheets))
                self.sprite_sheets.pop(oldest_key)
    
    def set_cache_size_limit(self, limit: int) -> None:
        """Set the maximum number of items to keep in cache.
        
        Args:
            limit: Maximum cache size
        """
        self.cache_size_limit = max(1, limit)  # Ensure at least 1
        self._maintain_cache_size() 

    def register_asset_lod(self, asset_id: str, lod_level: int, metadata: Dict[str, Any]) -> None:
        """Register asset metadata for a specific LOD level."""
        if asset_id not in self.asset_lod_metadata:
            self.asset_lod_metadata[asset_id] = {}
        self.asset_lod_metadata[asset_id][lod_level] = metadata

    def get_asset_lod(self, asset_id: str, lod_level: int) -> Optional[Dict[str, Any]]:
        """Return the metadata for a given asset and LOD level, or None if not found."""
        return self.asset_lod_metadata.get(asset_id, {}).get(lod_level)

    def load_image_lod(
        self,
        asset_id: str,
        lod_level: int = 0,
        lazy: bool = True,
        optimize: bool = True,
        cache: bool = True
    ) -> Optional[pygame.Surface]:
        """Load an image for a specific LOD level."""
        metadata = self.get_asset_lod(asset_id, lod_level)
        if not metadata:
            # Fallback to base asset
            return self.load_image(asset_id, lazy=lazy, optimize=optimize, cache=cache)
        path = metadata.get("path", asset_id)
        return self.load_image(path, lazy=lazy, optimize=optimize, cache=cache)

    def select_lod_level(self, distance: float, thresholds: Tuple[float, float] = (200.0, 600.0)) -> int:
        """Select LOD level based on distance. thresholds=(high/med, med/low)"""
        if distance < thresholds[0]:
            return 0  # High
        elif distance < thresholds[1]:
            return 1  # Medium
        else:
            return 2  # Low

    # Example usage in a rendering system:
    # distance = ...
    # lod = asset_manager.select_lod_level(distance)
    # surface = asset_manager.load_image_lod("tree_oak", lod) 