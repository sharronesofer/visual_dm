"""
Shared utility module for coordinates
Redirected from visual_client.core.utils.coordinates
"""

from typing import NamedTuple
import math

# Simple coordinate classes to avoid circular imports
class GlobalCoord(NamedTuple):
    """Global world coordinate (absolute position)."""
    x: float
    y: float
    z: float = 0.0
    
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

# Basic implementations - extend as needed
def secure_filename(filename: str) -> str:
    """Secure a filename by removing potentially dangerous characters."""
    import re
    filename = re.sub(r'[^\w\-_\.]', '', filename)
    return filename

class CoordinateSystem:
    """Basic coordinate system implementation."""
    def __init__(self, origin=(0, 0)):
        self.origin = origin
    
    def transform(self, point):
        return (point[0] - self.origin[0], point[1] - self.origin[1])

def load_data_file(file_path: str):
    """Basic data file loader."""
    import json
    from pathlib import Path
    
    path = Path(file_path)
    if path.suffix == '.json':
        with open(path, 'r') as f:
            return json.load(f)
    else:
        with open(path, 'r') as f:
            return f.read()
