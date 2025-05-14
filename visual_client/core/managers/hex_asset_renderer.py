"""
Renderer for hex-based assets that integrates with the hex mapping system.
Uses standardized coordinate system for consistent rendering across the application.
"""

import pygame
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import numpy as np
from .hex_asset_manager import HexAssetManager
from .hex_asset_cache import HexAssetCache
from .hex_sprite_sheet import HexSpriteSheet
from ..error_handler import handle_component_error, ErrorSeverity
from ..utils.coordinates import GlobalCoord, LocalCoord
from ..utils import coordinate_utils as cu

class HexAssetRenderer:
    """Renders hex-based assets with proper scaling, layering, and transitions."""
    
    def __init__(
        self,
        asset_manager: HexAssetManager,
        sprite_sheet: HexSpriteSheet,
        cache: HexAssetCache,
        hex_size: int = 64
    ):
        """Initialize the hex asset renderer.
        
        Args:
            asset_manager: Manager for hex assets
            sprite_sheet: Sprite sheet generator/manager
            cache: Asset cache system
            hex_size: Base size of hex tiles in pixels
        """
        self.asset_manager = asset_manager
        self.sprite_sheet = sprite_sheet
        self.cache = cache
        self.hex_size = hex_size
        self.layer_order = {
            "base": 0,
            "terrain": 1,
            "feature": 2,
            "overlay": 3,
            "effect": 4,
            "ui": 5
        }
        
    def calculate_hex_position(
        self,
        hex_coord: Tuple[int, int],
        scale: float = 1.0
    ) -> LocalCoord:
        """Calculate local position for a hex coordinate (relative to floating origin)."""
        q, r = hex_coord
        x = self.hex_size * (3/2 * q) * scale
        y = self.hex_size * (np.sqrt(3)/2 * q + np.sqrt(3) * r) * scale
        global_pos = GlobalCoord(x, y)
        # Convert to local coordinates for floating origin
        local_pos = cu.global_to_local(global_pos)
        assert isinstance(local_pos, LocalCoord), "Hex position must be a LocalCoord"
        return local_pos
        
    def render_hex_tile(
        self,
        surface: pygame.Surface,
        hex_coord: Tuple[int, int],
        terrain_type: str,
        features: List[str] = None,
        overlays: List[str] = None,
        effects: List[str] = None,
        scale: float = 1.0
    ) -> None:
        """Render a complete hex tile with all its components using local coordinates."""
        try:
            # Calculate position using LocalCoord (floating origin aware)
            pos_coord = self.calculate_hex_position(hex_coord, scale)
            assert isinstance(pos_coord, LocalCoord), "Hex tile position must be a LocalCoord"
            pos = (int(pos_coord.x), int(pos_coord.y))
            scaled_size = int(self.hex_size * scale)
            
            # Render base terrain
            base_sprite = self.cache.get(f"terrain_{terrain_type}")
            if base_sprite is None:
                base_sprite = self.asset_manager.load_terrain(terrain_type)
                self.cache.put(f"terrain_{terrain_type}", base_sprite)
            
            if scale != 1.0:
                base_sprite = pygame.transform.scale(
                    base_sprite,
                    (scaled_size, scaled_size)
                )
            
            surface.blit(base_sprite, pos)
            
            # Render features
            if features:
                for feature in features:
                    feature_sprite = self.cache.get(f"feature_{feature}")
                    if feature_sprite is None:
                        feature_sprite = self.asset_manager.load_feature(feature)
                        self.cache.put(f"feature_{feature}", feature_sprite)
                    
                    if scale != 1.0:
                        feature_sprite = pygame.transform.scale(
                            feature_sprite,
                            (scaled_size, scaled_size)
                        )
                    
                    surface.blit(feature_sprite, pos)
            
            # Render overlays
            if overlays:
                for overlay in overlays:
                    overlay_sprite = self.cache.get(f"overlay_{overlay}")
                    if overlay_sprite is None:
                        overlay_sprite = self.asset_manager.load_overlay(overlay)
                        self.cache.put(f"overlay_{overlay}", overlay_sprite)
                    
                    if scale != 1.0:
                        overlay_sprite = pygame.transform.scale(
                            overlay_sprite,
                            (scaled_size, scaled_size)
                        )
                    
                    surface.blit(overlay_sprite, pos)
            
            # Render effects
            if effects:
                for effect in effects:
                    effect_sprite = self.cache.get(f"effect_{effect}")
                    if effect_sprite is None:
                        effect_sprite = self.asset_manager.load_effect(effect)
                        self.cache.put(f"effect_{effect}", effect_sprite)
                    
                    if scale != 1.0:
                        effect_sprite = pygame.transform.scale(
                            effect_sprite,
                            (scaled_size, scaled_size)
                        )
                    
                    surface.blit(effect_sprite, pos)
                    
        except Exception as e:
            handle_component_error(
                e,
                "HexAssetRenderer",
                ErrorSeverity.HIGH
            )
            
    def render_region(
        self,
        surface: pygame.Surface,
        region_data: Dict[Tuple[int, int], Dict[str, Any]],
        view_rect: pygame.Rect,
        scale: float = 1.0
    ) -> None:
        """Render a region of the hex map using local coordinates."""
        try:
            rect_bounds = (
                view_rect.left,
                view_rect.top,
                view_rect.right,
                view_rect.bottom
            )
            for hex_coord, tile_data in region_data.items():
                pos_coord = self.calculate_hex_position(hex_coord, scale)
                hex_bottom_right = LocalCoord(
                    pos_coord.x + self.hex_size * scale,
                    pos_coord.y + self.hex_size * scale
                )
                if not (cu.is_within_bounds(pos_coord, rect_bounds) or 
                        cu.is_within_bounds(hex_bottom_right, rect_bounds)):
                    continue
                
                self.render_hex_tile(
                    surface,
                    hex_coord,
                    tile_data.get("terrain", "grass"),
                    tile_data.get("features", []),
                    tile_data.get("overlays", []),
                    tile_data.get("effects", []),
                    scale
                )
                
        except Exception as e:
            handle_component_error(
                e,
                "Failed to render region",
                ErrorSeverity.ERROR,
                component="HexAssetRenderer"
            )
            
    def render_transition(
        self,
        surface: pygame.Surface,
        start_region: Dict[Tuple[int, int], Dict[str, Any]],
        end_region: Dict[Tuple[int, int], Dict[str, Any]],
        progress: float,
        view_rect: pygame.Rect,
        scale: float = 1.0
    ) -> None:
        """Render a smooth transition between two regions.
        
        Args:
            surface: Target surface to render on
            start_region: Initial region data
            end_region: Target region data
            progress: Transition progress (0.0 to 1.0)
            view_rect: Visible region in pixel coordinates
            scale: Zoom scale factor
        """
        try:
            # Create transition surface
            transition_surface = pygame.Surface(
                surface.get_size(),
                pygame.SRCALPHA
            )
            
            # Render both regions
            self.render_region(surface, start_region, view_rect, scale)
            self.render_region(transition_surface, end_region, view_rect, scale)
            
            # Apply transition alpha
            transition_surface.set_alpha(int(255 * progress))
            surface.blit(transition_surface, (0, 0))
            
        except Exception as e:
            handle_component_error(
                e,
                "Failed to render transition",
                ErrorSeverity.ERROR,
                component="HexAssetRenderer"
            ) 