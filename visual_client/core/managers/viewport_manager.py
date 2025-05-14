from typing import Tuple, Optional
from dataclasses import dataclass
from visual_client.ui.screens.game.region_map_screen import Viewport
import time
from visual_client.core.utils.coordinates import GlobalCoord, LocalCoord
from visual_client.core.utils import coordinate_utils as cu

class ViewportManager:
    """
    Manages the state and operations of the map viewport, including position, zoom, and visible bounds.
    Uses the standardized coordinate system to maintain precision in large-scale environments.
    """
    def __init__(self, x: float = 0, y: float = 0, width: int = 800, height: int = 600, scale: float = 1.0):
        self.viewport = Viewport(x, y, width, height, scale)
        # Animation state
        self._animating = False
        self._animation_start_time = 0.0
        self._animation_duration = 0.0
        self._animation_from = (x, y, scale)
        self._animation_to = (x, y, scale)
        self._animation_elapsed = 0.0

    def get_position(self) -> LocalCoord:
        """Return the position of the viewport as a LocalCoord (floating origin aware)."""
        # Convert global position to local using coordinate utilities
        pos = GlobalCoord(self.viewport.x, self.viewport.y)
        local = cu.global_to_local(pos)
        assert isinstance(local, LocalCoord), "Viewport position must be a LocalCoord"
        return local

    def set_position(self, position: LocalCoord) -> None:
        """Set the position of the viewport using a LocalCoord and mark as dirty."""
        assert isinstance(position, LocalCoord), "Position must be a LocalCoord"
        # Convert local position to global using coordinate utilities
        global_pos = cu.local_to_global(position)
        self.viewport.x = global_pos.x
        self.viewport.y = global_pos.y
        self.viewport.dirty = True

    def get_zoom(self) -> float:
        """Return the current zoom (scale) of the viewport."""
        return self.viewport.scale

    def set_zoom(self, scale: float) -> None:
        """Set the zoom (scale) of the viewport and mark as dirty."""
        self.viewport.scale = scale
        self.viewport.dirty = True

    def get_dimensions(self) -> Tuple[int, int]:
        """Return the (width, height) of the viewport."""
        return (self.viewport.width, self.viewport.height)

    def set_dimensions(self, width: int, height: int) -> None:
        """Set the (width, height) of the viewport and mark as dirty."""
        self.viewport.width = width
        self.viewport.height = height
        self.viewport.dirty = True

    def get_visible_rect(self) -> Tuple[float, float, float, float]:
        """Return the visible rectangle (x, y, width, height) in world coordinates."""
        return (
            self.viewport.x,
            self.viewport.y,
            self.viewport.width / self.viewport.scale,
            self.viewport.height / self.viewport.scale
        )

    def mark_dirty(self) -> None:
        """Mark the viewport as needing redraw."""
        self.viewport.dirty = True

    def clear_dirty(self) -> None:
        """Clear the dirty flag after redraw."""
        self.viewport.dirty = False

    def screen_to_world(self, screen_x: float, screen_y: float) -> LocalCoord:
        """
        Convert screen (pixel) coordinates to local (map) coordinates (floating origin aware).
        Args:
            screen_x: X coordinate on the screen (pixels)
            screen_y: Y coordinate on the screen (pixels)
        Returns:
            LocalCoord: Corresponding local coordinates
        """
        screen_coord = (screen_x, screen_y)
        view_pos = (self.viewport.x, self.viewport.y)
        view_size = (self.viewport.width / self.viewport.scale, self.viewport.height / self.viewport.scale)
        screen_size = (self.viewport.width, self.viewport.height)
        # Use the utility function to convert, returning local
        return cu.screen_to_world(
            screen_coord,
            view_pos,
            view_size,
            screen_size,
            return_global=False
        )

    def world_to_screen(self, world_coord: LocalCoord) -> Tuple[float, float]:
        """
        Convert local (map) coordinates to screen (pixel) coordinates (floating origin aware).
        Args:
            world_coord: LocalCoord in local space
        Returns:
            (screen_x, screen_y): Corresponding screen coordinates (pixels)
        """
        view_pos = (self.viewport.x, self.viewport.y)
        view_size = (self.viewport.width / self.viewport.scale, self.viewport.height / self.viewport.scale)
        screen_size = (self.viewport.width, self.viewport.height)
        # Use the utility function to convert
        return cu.world_to_screen(
            world_coord,
            view_pos,
            view_size,
            screen_size,
            use_local=True
        )

    def set_constraints(self, map_width: int, map_height: int, min_zoom: float = 0.1, max_zoom: float = 10.0) -> None:
        """
        Set the allowed world boundaries and zoom limits for the viewport.
        Args:
            map_width: Width of the map in world units
            map_height: Height of the map in world units
            min_zoom: Minimum allowed zoom (default 0.1)
            max_zoom: Maximum allowed zoom (default 10.0)
        """
        self._map_width = map_width
        self._map_height = map_height
        self._min_zoom = min_zoom
        self._max_zoom = max_zoom

    def _apply_constraints(self) -> None:
        """
        Clamp the viewport position and zoom to the allowed boundaries.
        """
        # Clamp zoom
        if hasattr(self, '_min_zoom') and hasattr(self, '_max_zoom'):
            self.viewport.scale = max(self._min_zoom, min(self._max_zoom, self.viewport.scale))
        # Clamp position
        if hasattr(self, '_map_width') and hasattr(self, '_map_height'):
            visible_width = self.viewport.width / self.viewport.scale
            visible_height = self.viewport.height / self.viewport.scale
            max_x = max(0, self._map_width - visible_width)
            max_y = max(0, self._map_height - visible_height)
            self.viewport.x = max(0, min(self.viewport.x, max_x))
            self.viewport.y = max(0, min(self.viewport.y, max_y))

    def pan_by(self, dx: float, dy: float) -> None:
        """
        Pan (move) the viewport by a delta in world coordinates.
        Args:
            dx: Change in x (world units)
            dy: Change in y (world units)
        """
        current_pos = GlobalCoord(self.viewport.x, self.viewport.y)
        delta_vec = (dx, dy)
        
        # Use vector addition from coordinate utilities
        new_pos_tuple = cu.vec_add(cu.global_to_tuple(current_pos), delta_vec + (0.0,))
        
        # Update position
        self.viewport.x = new_pos_tuple[0]
        self.viewport.y = new_pos_tuple[1]
        
        self._apply_constraints()
        self.viewport.dirty = True

    def zoom_by(self, factor: float, center_x: float = None, center_y: float = None) -> None:
        """
        Zoom the viewport in or out by a factor, optionally around a specific point.
        Args:
            factor: Zoom multiplier (e.g., 1.1 for zoom in, 0.9 for zoom out)
            center_x: X coordinate in screen space to zoom around (optional)
            center_y: Y coordinate in screen space to zoom around (optional)
        """
        old_scale = self.viewport.scale
        new_scale = old_scale * factor
        if hasattr(self, '_min_zoom') and hasattr(self, '_max_zoom'):
            new_scale = max(self._min_zoom, min(self._max_zoom, new_scale))
        if center_x is not None and center_y is not None:
            # Convert screen coordinate to world before zoom
            world_before = self.screen_to_world(center_x, center_y)
            
            # Apply zoom
            self.viewport.scale = new_scale
            
            # Convert same screen coordinate to world after zoom
            world_after = self.screen_to_world(center_x, center_y)
            
            # Adjust viewport position to keep the point under cursor
            self.viewport.x += world_before.x - world_after.x
            self.viewport.y += world_before.y - world_after.y
        else:
            self.viewport.scale = new_scale
            
        self._apply_constraints()
        self.viewport.dirty = True

    def animate_to(self, target_pos: GlobalCoord, target_scale: float, duration_ms: int) -> None:
        """
        Start a smooth animation to the target position and scale over the given duration (ms).
        Args:
            target_pos: Target position as GlobalCoord
            target_scale: Target zoom (scale)
            duration_ms: Animation duration in milliseconds
        """
        self._animating = True
        self._animation_start_time = time.time()
        self._animation_duration = duration_ms / 1000.0  # seconds
        self._animation_from = (self.viewport.x, self.viewport.y, self.viewport.scale)
        self._animation_to = (target_pos.x, target_pos.y, target_scale)
        self._animation_elapsed = 0.0

    def update_animation(self, dt_ms: int) -> None:
        """
        Update the animation state. Call this each frame with the elapsed time in ms.
        Args:
            dt_ms: Time since last update in milliseconds
        """
        if not self._animating:
            return
        self._animation_elapsed += dt_ms / 1000.0
        t = min(1.0, self._animation_elapsed / self._animation_duration)
        from_x, from_y, from_scale = self._animation_from
        to_x, to_y, to_scale = self._animation_to
        
        # Use vector lerp from coordinate utilities
        start_vec = (from_x, from_y)
        end_vec = (to_x, to_y)
        new_pos = cu.vec_lerp(start_vec, end_vec, t)
        
        # Linear interpolation for scale
        new_scale = from_scale + (to_scale - from_scale) * t
        
        self.viewport.x = new_pos[0]
        self.viewport.y = new_pos[1]
        self.viewport.scale = new_scale
        self._apply_constraints()
        self.viewport.dirty = True
        if t >= 1.0:
            self._animating = False

    def is_animating(self) -> bool:
        """Return True if a transition animation is in progress."""
        return self._animating

    def fit_content(self, padding: float = 0.0, animate: bool = True, duration_ms: int = 300) -> None:
        """
        Adjust the viewport to fit the entire map content, with optional padding and animation.
        Args:
            padding: Extra space (in world units) to add around the map edges
            animate: Whether to animate the transition
            duration_ms: Animation duration in milliseconds
        """
        if not hasattr(self, '_map_width') or not hasattr(self, '_map_height'):
            return  # Constraints must be set first
        map_width = self._map_width + 2 * padding
        map_height = self._map_height + 2 * padding
        viewport_width = self.viewport.width
        viewport_height = self.viewport.height
        # Calculate optimal zoom to fit map
        zoom_x = viewport_width / map_width
        zoom_y = viewport_height / map_height
        target_zoom = min(zoom_x, zoom_y)
        # Clamp zoom to allowed range
        if hasattr(self, '_min_zoom') and hasattr(self, '_max_zoom'):
            target_zoom = max(self._min_zoom, min(self._max_zoom, target_zoom))
        # Center position
        target_x = (self._map_width - (viewport_width / target_zoom)) / 2
        target_y = (self._map_height - (viewport_height / target_zoom)) / 2
        
        # Create target position as GlobalCoord
        target_pos = GlobalCoord(target_x, target_y)
        
        if animate:
            self.animate_to(target_pos, target_zoom, duration_ms)
        else:
            self.viewport.x = target_pos.x
            self.viewport.y = target_pos.y
            self.viewport.scale = target_zoom
            self._apply_constraints()
            self.viewport.dirty = True 