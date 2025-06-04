"""
Location utilities for distance calculations and spatial operations.
"""

from typing import Union, Tuple
from .coordinates import GlobalCoord, LocalCoord
import math

def get_distance(point1: Union[GlobalCoord, LocalCoord, Tuple[float, float]], 
                point2: Union[GlobalCoord, LocalCoord, Tuple[float, float]]) -> float:
    """Calculate the distance between two points.
    
    Args:
        point1: First point (coordinate object or tuple)
        point2: Second point (coordinate object or tuple)
        
    Returns:
        float: Distance between the points
    """
    # Convert tuples to coordinate objects if needed
    if isinstance(point1, tuple):
        if len(point1) == 2:
            point1 = GlobalCoord(point1[0], point1[1], 0.0)
        else:
            point1 = GlobalCoord(point1[0], point1[1], point1[2])
    
    if isinstance(point2, tuple):
        if len(point2) == 2:
            point2 = GlobalCoord(point2[0], point2[1], 0.0)
        else:
            point2 = GlobalCoord(point2[0], point2[1], point2[2])
    
    # Use the built-in distance calculation
    if hasattr(point1, 'distance_to'):
        return point1.distance_to(point2)
    
    # Fallback manual calculation
    dx = point2.x - point1.x
    dy = point2.y - point1.y
    dz = getattr(point2, 'z', 0.0) - getattr(point1, 'z', 0.0)
    
    return math.sqrt(dx*dx + dy*dy + dz*dz)

def get_distance_2d(point1: Union[GlobalCoord, LocalCoord, Tuple[float, float]], 
                   point2: Union[GlobalCoord, LocalCoord, Tuple[float, float]]) -> float:
    """Calculate the 2D distance between two points (ignoring Z coordinate).
    
    Args:
        point1: First point (coordinate object or tuple)
        point2: Second point (coordinate object or tuple)
        
    Returns:
        float: 2D distance between the points
    """
    # Convert to coordinate objects if needed
    if isinstance(point1, tuple):
        point1 = GlobalCoord(point1[0], point1[1], 0.0)
    if isinstance(point2, tuple):
        point2 = GlobalCoord(point2[0], point2[1], 0.0)
    
    dx = point2.x - point1.x
    dy = point2.y - point1.y
    
    return math.sqrt(dx*dx + dy*dy)

def is_within_range(point1: Union[GlobalCoord, LocalCoord, Tuple[float, float]], 
                   point2: Union[GlobalCoord, LocalCoord, Tuple[float, float]], 
                   max_distance: float) -> bool:
    """Check if two points are within a specified distance of each other.
    
    Args:
        point1: First point
        point2: Second point
        max_distance: Maximum allowed distance
        
    Returns:
        bool: True if points are within range
    """
    return get_distance(point1, point2) <= max_distance 