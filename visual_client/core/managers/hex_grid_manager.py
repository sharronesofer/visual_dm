"""
Manager for hex grid operations and rendering.
"""

import math
from typing import Dict, List, Optional, Tuple, Any
import pygame
from ..error_handler import handle_component_error, ErrorSeverity
from .hex_asset_cache import HexAssetCache

class HexGridManager:
    """Manager for hex grid operations and rendering."""
    
    def __init__(self, hex_size: int = 32, cache_dir: str = "cache/hex"):
        """
        Initialize the hex grid manager.
        
        Args:
            hex_size: Size of hexagons in pixels
            cache_dir: Directory for caching hex assets
        """
        self.hex_size = hex_size
        self.cache = HexAssetCache(cache_dir)
        self.grid_offset = (0, 0)
        self.zoom_level = 1.0
        
    def set_grid_offset(self, offset: Tuple[int, int]) -> None:
        """
        Set the grid's offset from origin.
        
        Args:
            offset: (x, y) pixel offset
        """
        try:
            self.grid_offset = offset
        except Exception as e:
            handle_component_error(
                e,
                "HexGridManager.set_grid_offset",
                ErrorSeverity.LOW,
                {"offset": offset}
            )
            
    def set_zoom(self, level: float) -> None:
        """
        Set the zoom level.
        
        Args:
            level: Zoom level (1.0 = 100%)
        """
        try:
            self.zoom_level = max(0.1, min(level, 5.0))
        except Exception as e:
            handle_component_error(
                e,
                "HexGridManager.set_zoom",
                ErrorSeverity.LOW,
                {"level": level}
            )
            
    def pixel_to_hex(self, x: int, y: int) -> Tuple[int, int]:
        """
        Convert pixel coordinates to hex grid coordinates.
        
        Args:
            x: X pixel coordinate
            y: Y pixel coordinate
            
        Returns:
            (q, r) hex coordinates
        """
        try:
            # Adjust for offset and zoom
            x = (x - self.grid_offset[0]) / self.zoom_level
            y = (y - self.grid_offset[1]) / self.zoom_level
            
            # Convert to hex coordinates
            q = (2/3 * x) / self.hex_size
            r = (-1/3 * x + math.sqrt(3)/3 * y) / self.hex_size
            
            # Round to nearest hex
            return self._round_hex(q, r)
        except Exception as e:
            handle_component_error(
                e,
                "HexGridManager.pixel_to_hex",
                ErrorSeverity.LOW,
                {"x": x, "y": y}
            )
            return (0, 0)
            
    def hex_to_pixel(self, q: int, r: int) -> Tuple[int, int]:
        """
        Convert hex grid coordinates to pixel coordinates.
        
        Args:
            q: Q hex coordinate
            r: R hex coordinate
            
        Returns:
            (x, y) pixel coordinates
        """
        try:
            # Convert to pixel coordinates
            x = self.hex_size * (3/2 * q)
            y = self.hex_size * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
            
            # Adjust for offset and zoom
            x = x * self.zoom_level + self.grid_offset[0]
            y = y * self.zoom_level + self.grid_offset[1]
            
            return (int(x), int(y))
        except Exception as e:
            handle_component_error(
                e,
                "HexGridManager.hex_to_pixel",
                ErrorSeverity.LOW,
                {"q": q, "r": r}
            )
            return (0, 0)
            
    def get_hex_corners(self, q: int, r: int) -> List[Tuple[int, int]]:
        """
        Get the corner points of a hex.
        
        Args:
            q: Q hex coordinate
            r: R hex coordinate
            
        Returns:
            List of (x, y) corner coordinates
        """
        try:
            center = self.hex_to_pixel(q, r)
            corners = []
            
            for i in range(6):
                angle = 2 * math.pi / 6 * i
                x = center[0] + self.hex_size * self.zoom_level * math.cos(angle)
                y = center[1] + self.hex_size * self.zoom_level * math.sin(angle)
                corners.append((int(x), int(y)))
                
            return corners
        except Exception as e:
            handle_component_error(
                e,
                "HexGridManager.get_hex_corners",
                ErrorSeverity.LOW,
                {"q": q, "r": r}
            )
            return [(0, 0)] * 6
            
    def draw_hex(self, surface: pygame.Surface, q: int, r: int, color: Tuple[int, int, int], width: int = 0) -> None:
        """
        Draw a hex on the surface.
        
        Args:
            surface: Surface to draw on
            q: Q hex coordinate
            r: R hex coordinate
            color: RGB color tuple
            width: Line width (0 = filled)
        """
        try:
            corners = self.get_hex_corners(q, r)
            pygame.draw.polygon(surface, color, corners, width)
        except Exception as e:
            handle_component_error(
                e,
                "HexGridManager.draw_hex",
                ErrorSeverity.MEDIUM,
                {"q": q, "r": r, "color": color, "width": width}
            )
            
    def _round_hex(self, q: float, r: float) -> Tuple[int, int]:
        """
        Round floating point hex coordinates to nearest hex.
        
        Args:
            q: Q hex coordinate (float)
            r: R hex coordinate (float)
            
        Returns:
            (q, r) as integers
        """
        try:
            # Convert to cube coordinates
            x = q
            z = r
            y = -x - z
            
            # Round
            rx = round(x)
            ry = round(y)
            rz = round(z)
            
            # Convert back if needed
            x_diff = abs(rx - x)
            y_diff = abs(ry - y)
            z_diff = abs(rz - z)
            
            if x_diff > y_diff and x_diff > z_diff:
                rx = -ry - rz
            elif y_diff > z_diff:
                ry = -rx - rz
            else:
                rz = -rx - ry
                
            return (rx, rz)
        except Exception as e:
            handle_component_error(
                e,
                "HexGridManager._round_hex",
                ErrorSeverity.LOW,
                {"q": q, "r": r}
            )
            return (0, 0) 