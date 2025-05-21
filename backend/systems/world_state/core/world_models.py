"""
World Map Data Models

This module defines the core data models for world representation:
- TerrainType: Enumeration of supported terrain types
- Region: Geographic region with properties and points of interest
- PointOfInterest: Locations within regions that have special significance
- WorldMap: Container for the complete world map data and regions

Implementation follows the Development Bible guidelines for data representation.
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
import json
import numpy as np
from datetime import datetime

class TerrainType(str, Enum):
    """Enumeration of possible terrain types in the world."""
    OCEAN = "ocean"
    COAST = "coast"
    BEACH = "beach"
    GRASSLAND = "grassland"
    FOREST = "forest"
    JUNGLE = "jungle"
    MOUNTAIN = "mountain"
    HILL = "hill"
    DESERT = "desert"
    TUNDRA = "tundra"
    SNOW = "snow"
    SWAMP = "swamp"
    RIVER = "river"
    LAKE = "lake"
    MARSH = "marsh"
    WASTELAND = "wasteland"
    VOLCANIC = "volcanic"
    SAVANNA = "savanna"
    PLATEAU = "plateau"
    CANYON = "canyon"
    
    @classmethod
    def get_water_types(cls) -> Set[str]:
        """Return a set of terrain types that are water."""
        return {cls.OCEAN, cls.COAST, cls.RIVER, cls.LAKE, cls.MARSH}
    
    @classmethod
    def get_traversable_types(cls) -> Set[str]:
        """Return a set of terrain types that can be traversed normally."""
        return {cls.BEACH, cls.GRASSLAND, cls.FOREST, cls.DESERT, 
                cls.SAVANNA, cls.PLATEAU, cls.TUNDRA}
    
    @classmethod
    def get_difficult_types(cls) -> Set[str]:
        """Return a set of terrain types that are difficult to traverse."""
        return {cls.JUNGLE, cls.MOUNTAIN, cls.HILL, cls.SWAMP, 
                cls.SNOW, cls.VOLCANIC, cls.CANYON}

@dataclass
class PointOfInterest:
    """A special location within a region with unique properties."""
    id: str
    name: str
    type: str
    x: int  # Local x coordinate within region
    y: int  # Local y coordinate within region
    biome: str
    elevation: float
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "x": self.x,
            "y": self.y,
            "biome": self.biome,
            "elevation": self.elevation,
            "attributes": self.attributes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PointOfInterest':
        """Create from dictionary representation."""
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            x=data["x"],
            y=data["y"],
            biome=data["biome"],
            elevation=data["elevation"],
            attributes=data.get("attributes", {})
        )

@dataclass
class Region:
    """A geographic region within the world map."""
    id: str
    x: int  # Global x coordinate
    y: int  # Global y coordinate
    size: int  # Number of tiles per side
    continent_id: str
    world_seed: int
    
    # Terrain data
    elevation: np.ndarray = field(default=None, repr=False)
    moisture: np.ndarray = field(default=None, repr=False)
    temperature: np.ndarray = field(default=None, repr=False)
    biomes: List[List[str]] = field(default_factory=list, repr=False)
    rivers: List[List[bool]] = field(default_factory=list, repr=False)
    
    # Points of interest
    points_of_interest: List[PointOfInterest] = field(default_factory=list)
    
    # Metadata
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "size": self.size,
            "continent_id": self.continent_id,
            "world_seed": self.world_seed,
            "elevation": self.elevation.tolist() if self.elevation is not None else None,
            "moisture": self.moisture.tolist() if self.moisture is not None else None,
            "temperature": self.temperature.tolist() if self.temperature is not None else None,
            "biomes": self.biomes,
            "rivers": self.rivers,
            "points_of_interest": [poi.to_dict() for poi in self.points_of_interest],
            "generated_at": self.generated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Region':
        """Create from dictionary representation."""
        region = cls(
            id=data["id"],
            x=data["x"],
            y=data["y"],
            size=data["size"],
            continent_id=data["continent_id"],
            world_seed=data["world_seed"],
            generated_at=data.get("generated_at", datetime.utcnow().isoformat())
        )
        
        # Convert arrays if present
        if data.get("elevation") is not None:
            region.elevation = np.array(data["elevation"])
        if data.get("moisture") is not None:
            region.moisture = np.array(data["moisture"])
        if data.get("temperature") is not None:
            region.temperature = np.array(data["temperature"])
            
        region.biomes = data.get("biomes", [])
        region.rivers = data.get("rivers", [])
        
        # Convert points of interest
        poi_list = data.get("points_of_interest", [])
        region.points_of_interest = [
            PointOfInterest.from_dict(poi) if isinstance(poi, dict) else poi
            for poi in poi_list
        ]
        
        return region
        
@dataclass
class WorldMap:
    """Container for the world map and regions."""
    seed: int
    name: str
    ocean_level: float = 0.3
    regions: Dict[str, Region] = field(default_factory=dict)
    continents: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def add_region(self, region: Region) -> None:
        """Add a region to the world map."""
        self.regions[region.id] = region
        
        # Update continent data
        if region.continent_id not in self.continents:
            self.continents[region.continent_id] = {
                "id": region.continent_id,
                "name": f"Continent {len(self.continents) + 1}",
                "regions": []
            }
            
        self.continents[region.continent_id]["regions"].append(region.id)
        
    def get_region(self, x: int, y: int) -> Optional[Region]:
        """Get a region by its coordinates."""
        region_id = f"{x}:{y}"
        return self.regions.get(region_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "seed": self.seed,
            "name": self.name,
            "ocean_level": self.ocean_level,
            "regions": {k: v.to_dict() for k, v in self.regions.items()},
            "continents": self.continents
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldMap':
        """Create from dictionary representation."""
        world_map = cls(
            seed=data["seed"],
            name=data["name"],
            ocean_level=data.get("ocean_level", 0.3)
        )
        
        # Load continents
        world_map.continents = data.get("continents", {})
        
        # Load regions
        regions_data = data.get("regions", {})
        for region_id, region_data in regions_data.items():
            region = Region.from_dict(region_data)
            world_map.regions[region_id] = region
            
        return world_map
    
    def save_to_file(self, filename: str) -> None:
        """Save the world map to a file."""
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
            
    @classmethod
    def load_from_file(cls, filename: str) -> 'WorldMap':
        """Load a world map from a file."""
        with open(filename, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data) 