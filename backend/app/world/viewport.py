"""Viewport management module."""

from typing import Tuple, Dict
import numpy as np

class ViewportManager:
    """Manages viewport state and coordinate transformations."""
    
    def __init__(
        self,
        width: float,
        height: float,
        min_zoom: float = 0.1,
        max_zoom: float = 10.0,
        initial_zoom: float = 1.0
    ):
        """Initialize viewport manager.
        
        Args:
            width: Viewport width in pixels
            height: Viewport height in pixels
            min_zoom: Minimum allowed zoom level
            max_zoom: Maximum allowed zoom level
            initial_zoom: Initial zoom level
        """
        self.width = width
        self.height = height
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        
        # Initialize viewport state
        self.center = np.array([0.0, 0.0])  # Center in world coordinates
        self.zoom = initial_zoom  # Scale factor
        
        # Calculate initial bounds
        self._update_bounds()
        
    def _update_bounds(self) -> None:
        """Update viewport bounds based on current state."""
        half_width = (self.width / 2) / self.zoom
        half_height = (self.height / 2) / self.zoom
        
        self.bounds = (
            self.center[0] - half_width,   # minx
            self.center[1] - half_height,  # miny
            self.center[0] + half_width,   # maxx
            self.center[1] + half_height   # maxy
        )
        
    def get_state(self) -> Dict:
        """Get current viewport state.
        
        Returns:
            Dict containing viewport state
        """
        return {
            "center": self.center.tolist(),
            "zoom": self.zoom,
            "bounds": self.bounds,
            "width": self.width,
            "height": self.height
        }
        
    def set_size(self, width: float, height: float) -> None:
        """Set viewport size.
        
        Args:
            width: New width in pixels
            height: New height in pixels
        """
        self.width = width
        self.height = height
        self._update_bounds()
        
    def pan_by(self, dx: float, dy: float) -> None:
        """Pan viewport by screen space delta.
        
        Args:
            dx: Change in x position in screen pixels
            dy: Change in y position in screen pixels
        """
        # Convert screen delta to world delta
        world_dx = dx / self.zoom
        world_dy = dy / self.zoom
        
        self.center += np.array([-world_dx, -world_dy])
        self._update_bounds()
        
    def pan_to(self, x: float, y: float) -> None:
        """Pan viewport to world space position.
        
        Args:
            x: Target x position in world coordinates
            y: Target y position in world coordinates
        """
        self.center = np.array([x, y])
        self._update_bounds()
        
    def zoom_to(self, zoom: float, focus_point: Tuple[float, float] = None) -> None:
        """Set zoom level with optional focus point.
        
        Args:
            zoom: Target zoom level
            focus_point: Optional (x, y) point in screen coordinates to maintain position
        """
        old_zoom = self.zoom
        self.zoom = np.clip(zoom, self.min_zoom, self.max_zoom)
        
        if focus_point is not None:
            # Convert focus point to world space
            focus_world = self.screen_to_world(focus_point)
            
            # Calculate how focus point would move and compensate
            scale_change = old_zoom / self.zoom
            focus_delta = np.array([
                focus_world[0] - self.center[0],
                focus_world[1] - self.center[1]
            ])
            self.center += focus_delta * (1 - scale_change)
            
        self._update_bounds()
        
    def zoom_by(self, factor: float, focus_point: Tuple[float, float] = None) -> None:
        """Adjust zoom level by factor with optional focus point.
        
        Args:
            factor: Zoom adjustment factor (>1 zooms in, <1 zooms out)
            focus_point: Optional (x, y) point in screen coordinates to maintain position
        """
        self.zoom_to(self.zoom * factor, focus_point)
        
    def screen_to_world(self, point: Tuple[float, float]) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates.
        
        Args:
            point: (x, y) in screen coordinates
            
        Returns:
            (x, y) in world coordinates
        """
        return (
            self.center[0] + (point[0] - self.width/2) / self.zoom,
            self.center[1] + (point[1] - self.height/2) / self.zoom
        )
        
    def world_to_screen(self, point: Tuple[float, float]) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates.
        
        Args:
            point: (x, y) in world coordinates
            
        Returns:
            (x, y) in screen coordinates
        """
        return (
            (point[0] - self.center[0]) * self.zoom + self.width/2,
            (point[1] - self.center[1]) * self.zoom + self.height/2
        ) 