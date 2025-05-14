"""Region data and state management module."""

from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
from shapely.geometry import Polygon, Point
from rtree import index
import numpy as np

@dataclass
class RegionProperties:
    """Properties of a region."""
    name: str
    description: str
    color: Tuple[int, int, int]  # RGB color
    border_color: Tuple[int, int, int]  # RGB color
    z_index: int = 0
    is_visible: bool = True
    is_selected: bool = False
    is_hovered: bool = False

class Region:
    """Represents a region in the map system."""
    
    def __init__(
        self,
        region_id: str,
        boundary: List[Tuple[float, float]],  # List of (x, y) coordinates
        properties: RegionProperties
    ):
        """Initialize a region.
        
        Args:
            region_id: Unique identifier for the region
            boundary: List of (x, y) coordinates defining the region boundary
            properties: Region properties
        """
        self.id = region_id
        self.boundary = Polygon(boundary)
        self.properties = properties
        self._bbox = self.boundary.bounds  # (minx, miny, maxx, maxy)
        
    def contains_point(self, point: Tuple[float, float]) -> bool:
        """Check if a point is inside the region.
        
        Args:
            point: (x, y) coordinates to check
            
        Returns:
            bool: True if point is inside region
        """
        return self.boundary.contains(Point(point))
    
    def intersects_viewport(self, viewport_bounds: Tuple[float, float, float, float]) -> bool:
        """Check if region intersects with viewport.
        
        Args:
            viewport_bounds: (minx, miny, maxx, maxy) of viewport
            
        Returns:
            bool: True if region intersects viewport
        """
        return (
            self._bbox[0] < viewport_bounds[2] and
            self._bbox[2] > viewport_bounds[0] and
            self._bbox[1] < viewport_bounds[3] and
            self._bbox[3] > viewport_bounds[1]
        )
    
    def get_render_data(self) -> Dict:
        """Get data needed for rendering the region.
        
        Returns:
            Dict containing render data
        """
        return {
            "id": self.id,
            "boundary": list(self.boundary.exterior.coords),
            "color": self.properties.color,
            "border_color": self.properties.border_color,
            "z_index": self.properties.z_index,
            "is_visible": self.properties.is_visible,
            "is_selected": self.properties.is_selected,
            "is_hovered": self.properties.is_hovered
        }

class RegionManager:
    """Manages all regions in the system."""
    
    def __init__(self):
        """Initialize the region manager."""
        self.regions: Dict[str, Region] = {}
        self._spatial_index = index.Index()
        
    def add_region(self, region: Region) -> None:
        """Add a region to the manager.
        
        Args:
            region: Region to add
        """
        self.regions[region.id] = region
        self._spatial_index.insert(id=hash(region.id), coordinates=region._bbox)
        
    def remove_region(self, region_id: str) -> None:
        """Remove a region from the manager.
        
        Args:
            region_id: ID of region to remove
        """
        if region_id in self.regions:
            self._spatial_index.delete(id=hash(region_id), coordinates=self.regions[region_id]._bbox)
            del self.regions[region_id]
            
    def get_regions_in_viewport(
        self,
        viewport_bounds: Tuple[float, float, float, float],
        buffer: float = 0.1  # 10% buffer around viewport
    ) -> List[Region]:
        """Get all regions that intersect with the viewport.
        
        Args:
            viewport_bounds: (minx, miny, maxx, maxy) of viewport
            buffer: Fraction of viewport size to add as buffer
            
        Returns:
            List of regions intersecting the viewport
        """
        # Add buffer to viewport bounds
        width = viewport_bounds[2] - viewport_bounds[0]
        height = viewport_bounds[3] - viewport_bounds[1]
        buffered_bounds = (
            viewport_bounds[0] - width * buffer,
            viewport_bounds[1] - height * buffer,
            viewport_bounds[2] + width * buffer,
            viewport_bounds[3] + height * buffer
        )
        
        # Query spatial index for candidate regions
        candidates = self._spatial_index.intersection(buffered_bounds)
        
        # Filter candidates by actual intersection test
        return [
            self.regions[region_id]
            for region_id in (str(i) for i in candidates)
            if region_id in self.regions
            and self.regions[region_id].intersects_viewport(viewport_bounds)
        ]
    
    def get_region_at_point(self, point: Tuple[float, float]) -> Optional[Region]:
        """Get the topmost region containing a point.
        
        Args:
            point: (x, y) coordinates to check
            
        Returns:
            Region containing the point, or None if no region contains it
        """
        # Query spatial index for candidate regions
        candidates = self._spatial_index.intersection((point[0], point[1], point[0], point[1]))
        
        # Filter candidates by actual containment test and get highest z-index
        containing_regions = [
            self.regions[region_id]
            for region_id in (str(i) for i in candidates)
            if region_id in self.regions
            and self.regions[region_id].contains_point(point)
        ]
        
        if not containing_regions:
            return None
            
        return max(containing_regions, key=lambda r: r.properties.z_index)
    
    def update_region_property(
        self,
        region_id: str,
        property_name: str,
        value: Union[str, Tuple[int, int, int], int, bool]
    ) -> None:
        """Update a property of a region.
        
        Args:
            region_id: ID of region to update
            property_name: Name of property to update
            value: New value for property
        """
        if region_id in self.regions:
            setattr(self.regions[region_id].properties, property_name, value) 