class ViewportManager:
    """
    Manages the state of the viewport (camera) for the region map display system.
    Tracks position, size, and zoom level.
    """
    def __init__(self, x: float = 0, y: float = 0, width: int = 1024, height: int = 768, zoom: float = 1.0):
        self.x = x  # Top-left x in world coordinates
        self.y = y  # Top-left y in world coordinates
        self.width = width
        self.height = height
        self.zoom = zoom

    def get_state(self) -> dict:
        """Return the current viewport state as a dictionary."""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'zoom': self.zoom
        }

    def set_state(self, x: float = None, y: float = None, width: int = None, height: int = None, zoom: float = None):
        """Set one or more viewport properties."""
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if zoom is not None:
            self.zoom = zoom 

    def world_to_screen(self, wx: float, wy: float) -> (float, float):
        """
        Convert world coordinates (wx, wy) to screen coordinates (sx, sy).
        """
        sx = (wx - self.x) * self.zoom
        sy = (wy - self.y) * self.zoom
        return sx, sy

    def screen_to_world(self, sx: float, sy: float) -> (float, float):
        """
        Convert screen coordinates (sx, sy) to world coordinates (wx, wy).
        """
        wx = sx / self.zoom + self.x
        wy = sy / self.zoom + self.y
        return wx, wy

    def pan(self, dx: float, dy: float):
        """
        Move the viewport by (dx, dy) in world coordinates.
        """
        self.x += dx
        self.y += dy

    def zoom_at(self, factor: float, center_x: float = None, center_y: float = None):
        """
        Zoom in/out by a factor, optionally around a world coordinate (center_x, center_y).
        If center_x/center_y is None, use the center of the current viewport.
        Adjust x/y so the zoom center remains fixed on screen.
        """
        if factor == 1.0:
            return  # No change
        if center_x is None or center_y is None:
            # Use center of viewport in world coordinates
            center_x = self.x + (self.width / 2) / self.zoom
            center_y = self.y + (self.height / 2) / self.zoom
        # Compute new zoom
        old_zoom = self.zoom
        self.zoom *= factor
        # Prevent zoom from being zero or negative
        if self.zoom <= 0:
            self.zoom = old_zoom
            return
        # Adjust x/y so (center_x, center_y) stays at same screen position
        self.x = center_x - (center_x - self.x) * (old_zoom / self.zoom)
        self.y = center_y - (center_y - self.y) * (old_zoom / self.zoom)

    def fit_content(self, map_width: float, map_height: float, padding: float = 0.0):
        """
        Adjust the viewport to fit the entire map content, with optional padding.
        Args:
            map_width: Width of the map in world units
            map_height: Height of the map in world units
            padding: Extra space (in world units) to add around the map edges
        """
        # Calculate the area to fit
        fit_width = map_width + 2 * padding
        fit_height = map_height + 2 * padding
        # Calculate optimal zoom to fit map
        zoom_x = self.width / fit_width
        zoom_y = self.height / fit_height
        target_zoom = min(zoom_x, zoom_y)
        # Prevent zoom from being zero or negative
        if target_zoom <= 0:
            target_zoom = 1.0
        self.zoom = target_zoom
        # Center position
        self.x = (map_width - self.width / self.zoom) / 2
        self.y = (map_height - self.height / self.zoom) / 2 