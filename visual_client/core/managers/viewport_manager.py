from typing import Tuple
from dataclasses import dataclass
from visual_client.ui.screens.game.region_map_screen import Viewport
import time

class ViewportManager:
    """
    Manages the state and operations of the map viewport, including position, zoom, and visible bounds.
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

    def get_position(self) -> Tuple[float, float]:
        """Return the (x, y) position of the viewport."""
        return (self.viewport.x, self.viewport.y)

    def set_position(self, x: float, y: float) -> None:
        """Set the (x, y) position of the viewport and mark as dirty."""
        self.viewport.x = x
        self.viewport.y = y
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

    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """
        Convert screen (pixel) coordinates to world (map) coordinates.
        Args:
            screen_x: X coordinate on the screen (pixels)
            screen_y: Y coordinate on the screen (pixels)
        Returns:
            (world_x, world_y): Corresponding world coordinates
        """
        world_x = self.viewport.x + (screen_x / self.viewport.scale)
        world_y = self.viewport.y + (screen_y / self.viewport.scale)
        return (world_x, world_y)

    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """
        Convert world (map) coordinates to screen (pixel) coordinates.
        Args:
            world_x: X coordinate in world space
            world_y: Y coordinate in world space
        Returns:
            (screen_x, screen_y): Corresponding screen coordinates (pixels)
        """
        screen_x = (world_x - self.viewport.x) * self.viewport.scale
        screen_y = (world_y - self.viewport.y) * self.viewport.scale
        return (screen_x, screen_y)

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
        self.viewport.x += dx
        self.viewport.y += dy
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
            world_before = self.screen_to_world(center_x, center_y)
            self.viewport.scale = new_scale
            world_after = self.screen_to_world(center_x, center_y)
            self.viewport.x += world_before[0] - world_after[0]
            self.viewport.y += world_before[1] - world_after[1]
        else:
            self.viewport.scale = new_scale
        self._apply_constraints()
        self.viewport.dirty = True

    def animate_to(self, target_x: float, target_y: float, target_scale: float, duration_ms: int) -> None:
        """
        Start a smooth animation to the target position and scale over the given duration (ms).
        Args:
            target_x: Target x position (world units)
            target_y: Target y position (world units)
            target_scale: Target zoom (scale)
            duration_ms: Animation duration in milliseconds
        """
        self._animating = True
        self._animation_start_time = time.time()
        self._animation_duration = duration_ms / 1000.0  # seconds
        self._animation_from = (self.viewport.x, self.viewport.y, self.viewport.scale)
        self._animation_to = (target_x, target_y, target_scale)
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
        # Linear interpolation
        new_x = from_x + (to_x - from_x) * t
        new_y = from_y + (to_y - from_y) * t
        new_scale = from_scale + (to_scale - from_scale) * t
        self.viewport.x = new_x
        self.viewport.y = new_y
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
        if animate:
            self.animate_to(target_x, target_y, target_zoom, duration_ms)
        else:
            self.viewport.x = target_x
            self.viewport.y = target_y
            self.viewport.scale = target_zoom
            self._apply_constraints()
            self.viewport.dirty = True 