from enum import Enum
from typing import Dict, List, Optional, Tuple, Union, Any
import math
import random

from HexCell import HexCell, TerrainType, WeatherType


class RegionType(Enum):
    """Enum representing region types in the game world."""
    WILDERNESS = 'wilderness'
    KINGDOM = 'kingdom'
    EMPIRE = 'empire'
    WASTELAND = 'wasteland'
    FRONTIER = 'frontier'


class RegionData:
    """Class representing structured region data."""
    
    def __init__(
        self, 
        name: str, 
        type: RegionType, 
        cells: List[HexCell], 
        discovered_percentage: float, 
        danger_level: float, 
        faction_influence: Optional[Dict[str, float]] = None
    ):
        self.name = name
        self.type = type
        self.cells = cells
        self.discovered_percentage = discovered_percentage
        self.danger_level = danger_level
        self.faction_influence = faction_influence


class Point:
    """Class representing a 2D point."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class POI:
    """Class representing a Point of Interest on the map."""
    
    def __init__(
        self, 
        name: str, 
        description: str, 
        position: Dict[str, float], 
        poi_type: str, 
        discovered: bool = False
    ):
        self.name = name
        self.description = description
        self.position = position
        self.type = poi_type
        self.discovered = discovered


class RegionMap:
    """Class representing a region on the game map."""
    
    def __init__(
        self, 
        name: str, 
        region_type: RegionType = RegionType.WILDERNESS, 
        width: int = 20, 
        height: int = 20
    ):
        self._name = name
        self._type = region_type
        self._width = width
        self._height = height
        self._cells = {}  # Using a dict instead of Map<string, HexCell>
        self._pois = []
        self._neighbor_regions = {}
        
        self._initialize_empty_cells()
    
    def _initialize_empty_cells(self) -> None:
        """Create a basic grid of plain cells."""
        for q in range(self._width):
            for r in range(self._height):
                cell = HexCell(q, r)
                self.set_cell(cell)
    
    def _get_cell_key(self, q: float, r: float) -> str:
        """Generate a unique key for a cell based on its coordinates."""
        return f"{q},{r}"
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        self._name = value
    
    @property
    def type(self) -> RegionType:
        return self._type
    
    def set_cell(self, cell: HexCell) -> None:
        """Add or update a cell in the region."""
        key = self._get_cell_key(cell.q, cell.r)
        self._cells[key] = cell
    
    def get_cell(self, q: float, r: float) -> Optional[HexCell]:
        """Get a cell at the specified coordinates if it exists."""
        key = self._get_cell_key(q, r)
        return self._cells.get(key)
    
    def get_cells(self) -> List[HexCell]:
        """Get all cells in this region."""
        return list(self._cells.values())
    
    def add_poi(self, poi: POI) -> None:
        """Add a Point of Interest to the region."""
        self._pois.append(poi)
    
    def get_pois(self) -> List[POI]:
        """Get all Points of Interest in this region."""
        return self._pois
    
    def discover_poi(self, q: float, r: float, radius: float = 1) -> int:
        """Discover POIs within a radius of the given coordinates."""
        discovered = 0
        
        for poi in self._pois:
            if not poi.discovered:
                distance = self.calculate_distance(
                    poi.position["q"], 
                    poi.position["r"], 
                    q, 
                    r
                )
                if distance <= radius:
                    poi.discovered = True
                    discovered += 1
        
        return discovered
    
    def calculate_distance(self, q1: float, r1: float, q2: float, r2: float) -> float:
        """Calculate hex grid distance between two coordinates."""
        return (abs(q1 - q2) + abs(r1 - r2) + abs(q1 + r1 - q2 - r2)) / 2
    
    def generate_random_terrain(
        self,
        plains_probability: float = 0.5,
        forest_probability: float = 0.2,
        mountain_probability: float = 0.1,
        water_probability: float = 0.1
    ) -> None:
        """Generate random terrain for all cells in the region."""
        for cell in self._cells.values():
            rand = random.random()
            
            if rand < plains_probability:
                cell.terrain = 'plains'
            elif rand < plains_probability + forest_probability:
                cell.terrain = 'forest'
            elif rand < plains_probability + forest_probability + mountain_probability:
                cell.terrain = 'mountain'
            elif rand < plains_probability + forest_probability + mountain_probability + water_probability:
                cell.terrain = 'water'
            else:
                cell.terrain = 'desert'
            
            # Set random elevation
            cell.elevation = random.random()
            
            # Set random moisture
            cell.moisture = random.random()
            
            # Set random temperature
            cell.temperature = random.random()
    
    def add_neighbor_region(self, direction: str, region_name: str) -> None:
        """Set a neighboring region in the specified direction."""
        self._neighbor_regions[direction] = region_name
    
    def get_neighbor_region(self, direction: str) -> Optional[str]:
        """Get the neighboring region in the specified direction if it exists."""
        return self._neighbor_regions.get(direction)
    
    def to_json(self) -> RegionData:
        """Convert this region to a RegionData object for serialization."""
        cells = self.get_cells()
        discovered_cells = [cell for cell in cells if cell.is_discovered]
        discovered_percentage = (len(discovered_cells) / len(cells)) * 100
        
        return RegionData(
            name=self._name,
            type=self._type,
            cells=cells,
            discovered_percentage=discovered_percentage,
            danger_level=self._calculate_danger_level()
        )
    
    def _calculate_danger_level(self) -> float:
        """Calculate the danger level of this region based on terrain and features."""
        # Calculate danger level based on terrain types and other factors
        danger_score = 0
        
        for cell in self._cells.values():
            if cell.terrain == 'mountain':
                danger_score += 2
            elif cell.terrain == 'forest':
                danger_score += 1
            elif cell.terrain == 'water':
                danger_score += 1.5
            elif cell.terrain == 'desert':
                danger_score += 1.8
            else:
                danger_score += 0.5
            
            if cell.has_feature:
                danger_score += 1
        
        # Normalize to a 1-10 scale
        return min(10, max(1, danger_score / (len(self._cells) / 10)))
    
    @staticmethod
    def create_random_wilderness(name: str, width: int = 20, height: int = 20) -> 'RegionMap':
        """Static factory method to create a random wilderness region."""
        region = RegionMap(name, RegionType.WILDERNESS, width, height)
        region.generate_random_terrain()
        
        # Add some random POIs
        poi_count = math.floor(random.random() * 5) + 3
        for i in range(poi_count):
            q = math.floor(random.random() * width)
            r = math.floor(random.random() * height)
            poi_types = ['settlement', 'ruin', 'landmark', 'dungeon']
            poi_type = poi_types[math.floor(random.random() * 4)]
            
            region.add_poi(POI(
                name=f"POI {i + 1}",
                description="A point of interest in the wilderness.",
                position={"q": q, "r": r},
                poi_type=poi_type,
                discovered=False
            ))
        
        return region 