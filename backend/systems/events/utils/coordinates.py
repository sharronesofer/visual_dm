"""
Coordinate system utilities for large-scale world environments.
Includes classes and functions for handling global and local coordinates
with floating origin support to prevent precision errors.

Constants:
    SHIFT_THRESHOLD: Distance from origin at which an origin shift is triggered (default: 1000.0 units).
    MAX_SAFE_COORDINATE: Maximum coordinate value before potential floating-point precision issues (default: 100000.0 units).
    COORD_EPSILON: Epsilon for float comparisons to avoid precision artifacts.

Classes:
    GlobalCoord: Represents an absolute world position.
    LocalCoord: Represents a position relative to the current floating origin.
    CoordinateSystem: Handles conversion between global/local coordinates, manages origin, and triggers shifts.

See README_floating_origin.md for integration details.
"""

from typing import Tuple, Dict, Optional, List, Set, Any, NamedTuple
import math
import numpy as np

# Constants
SHIFT_THRESHOLD = 1000.0  # Shift origin when player is 1000 units away
MAX_SAFE_COORDINATE = 100000.0  # Maximum coordinate value before potential precision issues
COORD_EPSILON = 1e-10  # Epsilon for float comparisons

class GlobalCoord(NamedTuple):
    """Global world coordinate (absolute position)."""
    x: float
    y: float
    z: float = 0.0  # Default to 0 for 2D; can be used for 3D worlds
    
    def __str__(self) -> str:
        return f"G({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"
    
    def distance_to(self, other: 'GlobalCoord') -> float:
        """Calculate distance to another global coordinate."""
        return math.sqrt((self.x - other.x)**2 + 
                        (self.y - other.y)**2 + 
                        (self.z - other.z)**2)

class LocalCoord(NamedTuple):
    """Local coordinate relative to current origin."""
    x: float
    y: float
    z: float = 0.0
    
    def __str__(self) -> str:
        return f"L({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"
    
    def distance_to(self, other: 'LocalCoord') -> float:
        """Calculate distance to another local coordinate."""
        return math.sqrt((self.x - other.x)**2 + 
                        (self.y - other.y)**2 + 
                        (self.z - other.z)**2)

class CoordinateSystemOrigin:
    """Maintains the origin point of the coordinate system."""
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        """Initialize with origin at specified position."""
        self.global_x = x
        self.global_y = y
        self.global_z = z
        self.shift_count = 0
        self.shift_history = []  # List of (timestamp, old_origin, new_origin) tuples
    
    def get_origin(self) -> GlobalCoord:
        """Get current origin as GlobalCoord."""
        return GlobalCoord(self.global_x, self.global_y, self.global_z)
    
    def shift_origin(self, reference_point: GlobalCoord) -> Tuple[float, float, float]:
        """
        Shift origin to be close to the reference point.
        Returns offset amounts (dx, dy, dz) that were applied.
        """
        dx = reference_point.x - self.global_x
        dy = reference_point.y - self.global_y
        dz = reference_point.z - self.global_z
        
        old_origin = self.get_origin()
        
        # Update origin to new reference point
        self.global_x = reference_point.x
        self.global_y = reference_point.y
        self.global_z = reference_point.z
        
        # Log the shift
        self.shift_count += 1
        self.shift_history.append({
            'id': self.shift_count,
            'old_origin': old_origin,
            'new_origin': self.get_origin(),
            'delta': (dx, dy, dz)
        })
        
        return (dx, dy, dz)

class CoordinateSystem:
    """
    Main coordinate system handler for floating origin implementation.
    Manages conversion between global and local coordinate spaces.
    """
    
    def __init__(self):
        """Initialize coordinate system with origin at (0,0,0)."""
        self.origin = CoordinateSystemOrigin()
        self.shift_listeners = set()  # Callbacks for origin shift events
    
    def add_shift_listener(self, listener) -> None:
        """Add a callback function to be called when origin shifts."""
        self.shift_listeners.add(listener)
    
    def remove_shift_listener(self, listener) -> None:
        """Remove a shift listener callback."""
        if listener in self.shift_listeners:
            self.shift_listeners.remove(listener)
    
    def global_to_local(self, global_coord: GlobalCoord) -> LocalCoord:
        """Convert global coordinates to local coordinates."""
        origin = self.origin.get_origin()
        return LocalCoord(
            global_coord.x - origin.x,
            global_coord.y - origin.y,
            global_coord.z - origin.z
        )
    
    def local_to_global(self, local_coord: LocalCoord) -> GlobalCoord:
        """Convert local coordinates to global coordinates."""
        origin = self.origin.get_origin()
        return GlobalCoord(
            local_coord.x + origin.x,
            local_coord.y + origin.y,
            local_coord.z + origin.z
        )
    
    def check_shift_needed(self, player_global_pos: GlobalCoord) -> bool:
        """Check if an origin shift is needed based on player position."""
        local_pos = self.global_to_local(player_global_pos)
        distance_from_origin = math.sqrt(local_pos.x**2 + local_pos.y**2 + local_pos.z**2)
        return distance_from_origin > SHIFT_THRESHOLD
    
    def shift_origin(self, reference_pos: GlobalCoord) -> Tuple[float, float, float]:
        """
        Shift the coordinate system origin to be centered around the reference position.
        Returns the delta that was applied (dx, dy, dz).
        """
        delta = self.origin.shift_origin(reference_pos)
        
        # Notify all listeners about the shift
        for listener in self.shift_listeners:
            try:
                listener(delta)
            except Exception as e:
                print(f"Error in shift listener: {e}")
        
        return delta
    
    def get_shift_history(self) -> List[Dict]:
        """Get history of all origin shifts."""
        return self.origin.shift_history.copy()
    
    def get_total_shift(self) -> Tuple[float, float, float]:
        """Calculate total accumulated shift since initialization."""
        x_shift = self.origin.global_x
        y_shift = self.origin.global_y
        z_shift = self.origin.global_z
        return (x_shift, y_shift, z_shift)

# Create global instance for convenience
coordinate_system = CoordinateSystem() 