"""
Coordinate Utilities Library
Provides standardized functions for coordinate operations, conversions, and validations.
Builds upon the floating origin system for consistent coordinate handling across all game systems.

NOTE: All conversion functions are floating origin aware. Use local coordinates for all rendering, physics, and third-party integrations.
"""

import math
import numpy as np
from typing import Tuple, Dict, List, Union, Optional, Any, TypeVar, Callable
from .coordinates import (
    GlobalCoord, LocalCoord, CoordinateSystem, coordinate_system,
    SHIFT_THRESHOLD, MAX_SAFE_COORDINATE, COORD_EPSILON
)
from .floating_origin import FloatingOrigin, floating_origin

# Type definitions for cleaner type hinting
Vector2 = Tuple[float, float]
Vector3 = Tuple[float, float, float]
Vector = Union[Vector2, Vector3]
Matrix3x3 = List[List[float]]  # 3x3 matrix

T = TypeVar('T', GlobalCoord, LocalCoord)  # For generic coordinate functions

# ==============================
# Vector/Matrix Operations
# ==============================

def vec2_to_vec3(v: Vector2, z: float = 0.0) -> Vector3:
    """Convert a 2D vector to a 3D vector with specified z value."""
    return (v[0], v[1], z)

def vec3_to_vec2(v: Vector3) -> Vector2:
    """Convert a 3D vector to a 2D vector (discards z component)."""
    return (v[0], v[1])

def vec_add(v1: Vector, v2: Vector) -> Vector:
    """Add two vectors of same dimension."""
    if len(v1) == 2 and len(v2) == 2:
        return (v1[0] + v2[0], v1[1] + v2[1])
    return (v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2])

def vec_subtract(v1: Vector, v2: Vector) -> Vector:
    """Subtract v2 from v1."""
    if len(v1) == 2 and len(v2) == 2:
        return (v1[0] - v2[0], v1[1] - v2[1])
    return (v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2])

def vec_scale(v: Vector, scale: float) -> Vector:
    """Scale a vector by a scalar value."""
    if len(v) == 2:
        return (v[0] * scale, v[1] * scale)
    return (v[0] * scale, v[1] * scale, v[2] * scale)

def vec_magnitude(v: Vector) -> float:
    """Calculate the magnitude (length) of a vector."""
    if len(v) == 2:
        return math.sqrt(v[0] * v[0] + v[1] * v[1])
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

def vec_normalize(v: Vector) -> Vector:
    """Normalize a vector to unit length."""
    mag = vec_magnitude(v)
    if mag < COORD_EPSILON:
        return v  # Avoid division by near-zero
    return vec_scale(v, 1.0 / mag)

def vec_dot(v1: Vector, v2: Vector) -> float:
    """Calculate dot product of two vectors."""
    if len(v1) == 2 and len(v2) == 2:
        return v1[0] * v2[0] + v1[1] * v2[1]
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

def vec_cross(v1: Vector3, v2: Vector3) -> Vector3:
    """Calculate cross product of two 3D vectors."""
    return (
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    )

def vec_distance(v1: Vector, v2: Vector) -> float:
    """Calculate distance between two vectors."""
    return vec_magnitude(vec_subtract(v1, v2))

def vec_lerp(v1: Vector, v2: Vector, t: float) -> Vector:
    """Linearly interpolate between two vectors."""
    # Clamp t to [0, 1]
    t = max(0.0, min(1.0, t))
    return vec_add(vec_scale(v1, 1.0 - t), vec_scale(v2, t))

def matrix_multiply(m: Matrix3x3, v: Vector3) -> Vector3:
    """Multiply a 3x3 matrix by a vector."""
    return (
        m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
        m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
        m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2]
    )

# ==============================
# Coordinate Conversion Functions
# ==============================

def tuple_to_global(coord: Vector) -> GlobalCoord:
    """Convert a tuple (x, y) or (x, y, z) to GlobalCoord."""
    if len(coord) == 2:
        return GlobalCoord(coord[0], coord[1])
    return GlobalCoord(coord[0], coord[1], coord[2])

def tuple_to_local(coord: Vector) -> LocalCoord:
    """Convert a tuple (x, y) or (x, y, z) to LocalCoord."""
    if len(coord) == 2:
        return LocalCoord(coord[0], coord[1])
    return LocalCoord(coord[0], coord[1], coord[2])

def global_to_tuple(coord: GlobalCoord) -> Vector3:
    """Convert GlobalCoord to tuple (x, y, z)."""
    return (coord.x, coord.y, coord.z)

def local_to_tuple(coord: LocalCoord) -> Vector3:
    """Convert LocalCoord to tuple (x, y, z)."""
    return (coord.x, coord.y, coord.z)

def global_to_local(coord: GlobalCoord, coord_system: Optional[CoordinateSystem] = None) -> LocalCoord:
    """Convert global coordinates to local coordinates using the specified or default coordinate system."""
    cs = coord_system or coordinate_system
    return cs.global_to_local(coord)

def local_to_global(coord: LocalCoord, coord_system: Optional[CoordinateSystem] = None) -> GlobalCoord:
    """Convert local coordinates to global coordinates using the specified or default coordinate system."""
    cs = coord_system or coordinate_system
    return cs.local_to_global(coord)

def coord_round(coord: T, decimals: int = 0) -> T:
    """Round coordinate components to specified number of decimal places."""
    if isinstance(coord, GlobalCoord):
        return GlobalCoord(
            round(coord.x, decimals),
            round(coord.y, decimals),
            round(coord.z, decimals)
        )
    elif isinstance(coord, LocalCoord):
        return LocalCoord(
            round(coord.x, decimals),
            round(coord.y, decimals),
            round(coord.z, decimals)
        )
    raise TypeError(f"Unsupported coordinate type: {type(coord)}")

def coord_floor(coord: T) -> T:
    """Floor coordinate components to integer values."""
    if isinstance(coord, GlobalCoord):
        return GlobalCoord(
            math.floor(coord.x),
            math.floor(coord.y),
            math.floor(coord.z)
        )
    elif isinstance(coord, LocalCoord):
        return LocalCoord(
            math.floor(coord.x),
            math.floor(coord.y),
            math.floor(coord.z)
        )
    raise TypeError(f"Unsupported coordinate type: {type(coord)}")

def coord_ceil(coord: T) -> T:
    """Ceiling coordinate components to integer values."""
    if isinstance(coord, GlobalCoord):
        return GlobalCoord(
            math.ceil(coord.x),
            math.ceil(coord.y),
            math.ceil(coord.z)
        )
    elif isinstance(coord, LocalCoord):
        return LocalCoord(
            math.ceil(coord.x),
            math.ceil(coord.y),
            math.ceil(coord.z)
        )
    raise TypeError(f"Unsupported coordinate type: {type(coord)}")

# ==============================
# Specialized Conversion Functions
# ==============================

def world_to_grid(coord: GlobalCoord, grid_size: float = 1.0) -> Tuple[int, int]:
    """Convert world coordinates to grid cell coordinates."""
    return (int(coord.x / grid_size), int(coord.y / grid_size))

def grid_to_world(grid_x: int, grid_y: int, grid_size: float = 1.0) -> GlobalCoord:
    """Convert grid cell coordinates to world coordinates (cell center)."""
    return GlobalCoord(
        (grid_x + 0.5) * grid_size,
        (grid_y + 0.5) * grid_size
    )

def world_to_screen(
    world_coord: Union[GlobalCoord, LocalCoord],
    view_pos: Vector2,
    view_size: Vector2,
    screen_size: Vector2,
    use_local: bool = True,
    coord_system: Optional[CoordinateSystem] = None
) -> Vector2:
    """
    Convert world coordinates to screen coordinates (floating origin aware).
    Args:
        world_coord: The world coordinates to convert (GlobalCoord or LocalCoord)
        view_pos: The center position of the viewport in world space
        view_size: The size of the viewport in world space
        screen_size: The size of the screen in pixels
        use_local: If True, converts to local coordinates before processing
        coord_system: Optional coordinate system to use
    Returns:
        Screen coordinates as (x, y) tuple
    NOTE: Always use local coordinates for rendering and physics systems.
    """
    cs = coord_system or coordinate_system
    
    # Convert to local if needed
    local_coord = world_coord
    if not isinstance(world_coord, LocalCoord) and use_local:
        local_coord = cs.global_to_local(world_coord)
    
    # Calculate screen position
    screen_x = ((local_coord.x - view_pos[0]) / view_size[0] + 0.5) * screen_size[0]
    screen_y = ((local_coord.y - view_pos[1]) / view_size[1] + 0.5) * screen_size[1]
    
    return (screen_x, screen_y)

def screen_to_world(
    screen_coord: Vector2,
    view_pos: Vector2,
    view_size: Vector2,
    screen_size: Vector2,
    return_global: bool = True,
    coord_system: Optional[CoordinateSystem] = None
) -> Union[GlobalCoord, LocalCoord]:
    """
    Convert screen coordinates to world coordinates (floating origin aware).
    Args:
        screen_coord: The screen coordinates to convert (x, y)
        view_pos: The center position of the viewport in world space
        view_size: The size of the viewport in world space
        screen_size: The size of the screen in pixels
        return_global: If True, returns GlobalCoord, otherwise LocalCoord
        coord_system: Optional coordinate system to use
    Returns:
        World coordinates as GlobalCoord or LocalCoord
    NOTE: Always use local coordinates for rendering and physics systems.
    """
    cs = coord_system or coordinate_system
    
    # Calculate local world position
    local_x = ((screen_coord[0] / screen_size[0]) - 0.5) * view_size[0] + view_pos[0]
    local_y = ((screen_coord[1] / screen_size[1]) - 0.5) * view_size[1] + view_pos[1]
    
    local_coord = LocalCoord(local_x, local_y)
    
    # Convert to global if requested
    if return_global:
        return cs.local_to_global(local_coord)
    
    return local_coord

# ==============================
# Serialization/Deserialization
# ==============================

def serialize_coord(coord: Union[GlobalCoord, LocalCoord]) -> Dict[str, float]:
    """Serialize a coordinate object to a dictionary."""
    if isinstance(coord, (GlobalCoord, LocalCoord)):
        return {
            'x': coord.x,
            'y': coord.y,
            'z': coord.z,
            'type': 'global' if isinstance(coord, GlobalCoord) else 'local'
        }
    raise TypeError(f"Unsupported coordinate type: {type(coord)}")

def deserialize_coord(data: Dict[str, Any]) -> Union[GlobalCoord, LocalCoord]:
    """Deserialize a dictionary to a coordinate object."""
    if not all(k in data for k in ('x', 'y', 'type')):
        raise ValueError("Invalid coordinate data: missing required fields")
    
    if data['type'] == 'global':
        return GlobalCoord(data['x'], data['y'], data.get('z', 0.0))
    elif data['type'] == 'local':
        return LocalCoord(data['x'], data['y'], data.get('z', 0.0))
    
    raise ValueError(f"Unknown coordinate type: {data['type']}")

# ==============================
# Validation Functions
# ==============================

def is_valid_coord(coord: Any) -> bool:
    """Check if an object is a valid coordinate (GlobalCoord or LocalCoord)."""
    return isinstance(coord, (GlobalCoord, LocalCoord))

def is_within_bounds(coord: GlobalCoord, bounds: Tuple[float, float, float, float]) -> bool:
    """
    Check if a global coordinate is within the specified bounds.
    
    Args:
        coord: The coordinate to check
        bounds: (min_x, min_y, max_x, max_y)
    
    Returns:
        True if the coordinate is within bounds
    """
    min_x, min_y, max_x, max_y = bounds
    return (
        min_x <= coord.x <= max_x and
        min_y <= coord.y <= max_y
    )

def is_safe_coordinate(coord: GlobalCoord) -> bool:
    """Check if a global coordinate is within safe limits to avoid precision issues."""
    return (
        abs(coord.x) <= MAX_SAFE_COORDINATE and
        abs(coord.y) <= MAX_SAFE_COORDINATE and
        abs(coord.z) <= MAX_SAFE_COORDINATE
    )

def assert_valid_coord(coord: Any, name: str = "coordinate") -> None:
    """Assert that an object is a valid coordinate, raise detailed exception if not."""
    if not is_valid_coord(coord):
        raise TypeError(f"Invalid {name}: expected GlobalCoord or LocalCoord, got {type(coord)}")

def assert_global_coord(coord: Any, name: str = "coordinate") -> None:
    """Assert that an object is a GlobalCoord, raise detailed exception if not."""
    if not isinstance(coord, GlobalCoord):
        raise TypeError(f"Invalid {name}: expected GlobalCoord, got {type(coord)}")

def assert_local_coord(coord: Any, name: str = "coordinate") -> None:
    """Assert that an object is a LocalCoord, raise detailed exception if not."""
    if not isinstance(coord, LocalCoord):
        raise TypeError(f"Invalid {name}: expected LocalCoord, got {type(coord)}")

def assert_safe_coordinate(coord: GlobalCoord, name: str = "coordinate") -> None:
    """Assert that a global coordinate is within safe limits."""
    if not is_safe_coordinate(coord):
        raise ValueError(
            f"Unsafe {name} ({coord}): values exceed MAX_SAFE_COORDINATE ({MAX_SAFE_COORDINATE})"
        )

# ==============================
# Debug Visualization Helpers
# ==============================

def format_coord(
    coord: Union[GlobalCoord, LocalCoord], 
    precision: int = 2, 
    include_type: bool = True
) -> str:
    """Format a coordinate as a human-readable string with specified precision."""
    coord_type = "G" if isinstance(coord, GlobalCoord) else "L"
    if include_type:
        return f"{coord_type}({coord.x:.{precision}f}, {coord.y:.{precision}f}, {coord.z:.{precision}f})"
    return f"({coord.x:.{precision}f}, {coord.y:.{precision}f}, {coord.z:.{precision}f})"

def format_vector(vector: Vector, precision: int = 2) -> str:
    """Format a vector tuple as a human-readable string."""
    if len(vector) == 2:
        return f"({vector[0]:.{precision}f}, {vector[1]:.{precision}f})"
    return f"({vector[0]:.{precision}f}, {vector[1]:.{precision}f}, {vector[2]:.{precision}f})"

def debug_coord_info(
    coord: Union[GlobalCoord, LocalCoord],
    coord_system: Optional[CoordinateSystem] = None
) -> Dict[str, Any]:
    """
    Generate debug information about a coordinate.
    
    Returns a dictionary with:
    - original: The original coordinate
    - other_space: The coordinate converted to the other space
    - origin_distance: Distance from coordinate system origin
    - is_safe: Whether the coordinate is within safe limits
    """
    cs = coord_system or coordinate_system
    
    result = {
        'original': coord,
        'origin_distance': None,
        'is_safe': None,
        'other_space': None
    }
    
    if isinstance(coord, GlobalCoord):
        result['other_space'] = cs.global_to_local(coord)
        result['origin_distance'] = cs.global_to_local(coord).distance_to(LocalCoord(0, 0, 0))
        result['is_safe'] = is_safe_coordinate(coord)
    else:
        result['other_space'] = cs.local_to_global(coord)
        result['origin_distance'] = coord.distance_to(LocalCoord(0, 0, 0))
        result['is_safe'] = is_safe_coordinate(cs.local_to_global(coord))
    
    return result

def get_coord_system_info(coord_system: Optional[CoordinateSystem] = None) -> Dict[str, Any]:
    """Get information about the current state of the coordinate system."""
    cs = coord_system or coordinate_system
    
    origin = cs.origin.get_origin()
    shift_history = cs.get_shift_history()
    total_shift = cs.get_total_shift()
    
    return {
        'current_origin': origin,
        'total_shift': total_shift,
        'shift_count': len(shift_history),
        'last_shift': shift_history[-1] if shift_history else None
    }

def debug_entity_state(entity_manager, region_manager=None, max_entities=20):
    """
    Print a summary of all registered entities, their local/global positions, and region assignments.
    Args:
        entity_manager: The EntityPositionManager instance
        region_manager: (Optional) The RegionManager instance
        max_entities: Max number of entities to print (for brevity)
    Returns:
        List of dicts with entity_id, local_pos, global_pos, region (if available)
    """
    summary = []
    entities = list(entity_manager.get_registered_entities())[:max_entities]
    for eid in entities:
        info = entity_manager.entities[eid]
        local_pos = info.get_pos()
        global_pos = None
        try:
            global_pos = local_to_global(local_pos)
        except Exception:
            pass
        region = None
        if region_manager:
            region = region_manager.get_region_for_entity(local_pos) if hasattr(region_manager, 'get_region_for_entity') else None
        entry = {
            'entity_id': eid,
            'local_pos': local_pos,
            'global_pos': global_pos,
            'region': getattr(region, 'region_coord', None) if region else None
        }
        summary.append(entry)
    for entry in summary:
        print(f"Entity {entry['entity_id']}: local={format_coord(entry['local_pos'])}, global={format_coord(entry['global_pos']) if entry['global_pos'] else 'N/A'}, region={entry['region']}")
    return summary

def debug_precision_limits(entity_manager, threshold=0.9, region_manager=None, max_entities=20):
    """
    Print or log entities that are approaching the floating origin shift threshold or precision limits.
    Args:
        entity_manager: The EntityPositionManager instance
        threshold: Fraction of SHIFT_THRESHOLD or MAX_SAFE_COORDINATE to warn at (default: 0.9)
        region_manager: (Optional) The RegionManager instance
        max_entities: Max number of entities to print (for brevity)
    Returns:
        List of dicts with entity_id, local_pos, global_pos, region (if available), and warning type
    """
    from .coordinates import SHIFT_THRESHOLD, MAX_SAFE_COORDINATE
    summary = []
    entities = list(entity_manager.get_registered_entities())[:max_entities]
    for eid in entities:
        info = entity_manager.entities[eid]
        local_pos = info.get_pos()
        global_pos = None
        try:
            global_pos = local_to_global(local_pos)
        except Exception:
            pass
        region = None
        if region_manager:
            region = region_manager.get_region_for_entity(local_pos) if hasattr(region_manager, 'get_region_for_entity') else None
        # Check for proximity to shift threshold or max safe coordinate
        warnings = []
        dist = (local_pos.x**2 + local_pos.y**2 + getattr(local_pos, 'z', 0.0)**2) ** 0.5
        if dist > threshold * SHIFT_THRESHOLD:
            warnings.append('near_shift_threshold')
        if global_pos and (abs(global_pos.x) > threshold * MAX_SAFE_COORDINATE or abs(global_pos.y) > threshold * MAX_SAFE_COORDINATE):
            warnings.append('near_max_safe_coordinate')
        entry = {
            'entity_id': eid,
            'local_pos': local_pos,
            'global_pos': global_pos,
            'region': getattr(region, 'region_coord', None) if region else None,
            'warnings': warnings
        }
        summary.append(entry)
    for entry in summary:
        if entry['warnings']:
            print(f"[PRECISION WARNING] Entity {entry['entity_id']}: local={format_coord(entry['local_pos'])}, global={format_coord(entry['global_pos']) if entry['global_pos'] else 'N/A'}, region={entry['region']}, warnings={entry['warnings']}")
    return summary 