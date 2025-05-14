"""
Asset management system with lazy loading and caching.
"""

import os
import pygame
import json
import re
from typing import Dict, Optional, Any, Tuple
from pathlib import Path
from .error_handler import handle_component_error, ErrorSeverity

class AssetManager:
    """Manages loading, caching, and optimization of game assets."""
    
    def __init__(self, asset_dir: str = "assets"):
        """Initialize the asset manager.
        
        Args:
            asset_dir: Directory containing game assets
        """
        self.asset_dir = Path(asset_dir)
        self.cache: Dict[str, Any] = {}
        self.loading_queue: Dict[str, Dict[str, Any]] = {}
        self.asset_metadata: Dict[str, Dict[str, Any]] = {}
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
                "cache"
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
                
            return surface
            
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "load_image",
                e,
                ErrorSeverity.ERROR,
                {"path": path}
            )
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
            if surface.get_bitsize() != 32:
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
            
    def process_loading_queue(self) -> None:
        """Process the loading queue to load assets in the background."""
        try:
            for path, info in list(self.loading_queue.items()):
                if info["type"] == "image":
                    surface = pygame.image.load(info["path"])
                    if info["optimize"]:
                        surface = self._optimize_image(surface)
                    if info["cache"]:
                        self.cache[path] = surface
                elif info["type"] == "sound":
                    sound = pygame.mixer.Sound(info["path"])
                    if info["cache"]:
                        self.cache[path] = sound
                elif info["type"] == "font":
                    font = pygame.font.Font(info["path"], info["size"])
                    if info["cache"]:
                        self.cache[path] = font
                        
                del self.loading_queue[path]
                
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "process_loading_queue",
                e,
                ErrorSeverity.ERROR
            )
            
    def clear_cache(self) -> None:
        """Clear the asset cache."""
        try:
            self.cache.clear()
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "clear_cache",
                e,
                ErrorSeverity.ERROR
            )
            
    def get_cache_size(self) -> int:
        """Get the current size of the asset cache in bytes."""
        try:
            return sum(
                sys.getsizeof(obj)
                for obj in self.cache.values()
            )
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "get_cache_size",
                e,
                ErrorSeverity.ERROR
            )
            return 0
            
    def preload_assets(self, manifest_path: str) -> None:
        """Preload assets based on a manifest file.
        
        Args:
            manifest_path: Path to the asset manifest file
        """
        try:
            with open(self.asset_dir / "data" / manifest_path, "r") as f:
                manifest = json.load(f)
                
            for asset_type, assets in manifest.items():
                for asset in assets:
                    if asset_type == "images":
                        self.load_image(asset["path"], lazy=False)
                    elif asset_type == "sounds":
                        self.load_sound(asset["path"], lazy=False)
                    elif asset_type == "fonts":
                        self.load_font(asset["path"], asset["size"], lazy=False)
                        
        except Exception as e:
            handle_component_error(
                "AssetManager",
                "preload_assets",
                e,
                ErrorSeverity.ERROR,
                {"manifest_path": manifest_path}
            )

    def discover_assets(self) -> Dict[str, list]:
        """
        Recursively scan the asset directory and return a dict of asset types to file paths.
        Asset types: characters, equipment, regions (with subtypes as keys)
        """
        asset_map = {"characters": [], "equipment": [], "regions": []}
        for root, dirs, files in os.walk(self.asset_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.asset_dir)
                if rel_path.startswith("characters/"):
                    asset_map["characters"].append(rel_path)
                elif rel_path.startswith("equipment/"):
                    asset_map["equipment"].append(rel_path)
                elif rel_path.startswith("regions/"):
                    asset_map["regions"].append(rel_path)
        return asset_map

    def validate_assets(self) -> Dict[str, list]:
        """
        Validate all discovered assets against naming conventions and file requirements.
        Returns a dict of errors by asset type.
        """
        errors = {"characters": [], "equipment": [], "regions": []}
        asset_map = self.discover_assets()
        # Regex patterns from ASSET_STRUCTURE.md
        patterns = {
            "characters": re.compile(r"^characters/(idle|walk|attack|death|special|head|torso|arms|legs|accessories)/character_([a-z_]+)_\d{3}\.png$"),
            "equipment": re.compile(r"^equipment/(weapons|armor|consumables)/(weapon|armor|consumable)_([a-z_]+)_\d{3}\.png$"),
            "regions": re.compile(r"^regions/(terrain|buildings|decorations|background)/(terrain|building|decoration|background)_([a-z_]+)_(\d{3}|[a-z_]+)\.png$"),
        }
        for asset_type, files in asset_map.items():
            for f in files:
                if not patterns[asset_type].match(f):
                    errors[asset_type].append(f"Invalid name or location: {f}")
                elif not f.lower().endswith('.png'):
                    errors[asset_type].append(f"Invalid format (not PNG): {f}")
        return errors

    def generate_manifest(self, output_path: str) -> None:
        """
        Generate a JSON manifest of all valid assets for efficient loading.
        Args:
            output_path: Path to write the manifest JSON file
        """
        asset_map = self.discover_assets()
        errors = self.validate_assets()
        manifest = {k: [f for f in v if f not in errors[k]] for k, v in asset_map.items()}
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2) 