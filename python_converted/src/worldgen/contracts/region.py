#!/usr/bin/env python3
"""
region.py - Region Data Contracts for World Generation System

This module defines the standardized data contracts for region data,
including metadata, cells, and query interfaces.

Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Set, Tuple
from enum import Enum
from dataclasses import dataclass, field
import uuid
from datetime import datetime
import math

from .base import (
    WorldGenContract, 
    WorldGenContractError,
    ValidationError,
    WorldGenContractValidator as Validator,
    QueryResult
)

class TerrainType(Enum):
    """Enumeration of terrain types"""
    WATER = "water"
    MOUNTAIN = "mountain"
    FOREST = "forest"
    DESERT = "desert"
    PLAINS = "plains"
    URBAN = "urban"
    SWAMP = "swamp"
    TUNDRA = "tundra"
    BEACH = "beach"
    CLIFF = "cliff"
    CAVE = "cave"


class FeatureType(Enum):
    """Enumeration of cell features"""
    NONE = "none"
    TREE = "tree"
    ROCK = "rock"
    BUSH = "bush"
    GRASS = "grass"
    FLOWER = "flower"
    MUSHROOM = "mushroom"
    ROAD = "road"
    PATH = "path"
    RIVER = "river"
    LAKE = "lake"
    BUILDING = "building"
    RUIN = "ruin"
    MONUMENT = "monument"


@dataclass(frozen=True)
class RegionCellContract(WorldGenContract):
    """
    Contract for a single cell within a region
    """
    x: int
    y: int
    terrain_type: str  # One of TerrainType values
    elevation: float
    moisture: float
    temperature: float
    biome: str
    features: List[str] = field(default_factory=list)
    passable: bool = True
    cost: float = 1.0
    
    def __post_init__(self):
        # Force validation as part of initialization
        data = {
            "x": self.x,
            "y": self.y,
            "terrain_type": self.terrain_type,
            "elevation": self.elevation,
            "moisture": self.moisture,
            "temperature": self.temperature,
            "biome": self.biome,
            "features": self.features,
            "passable": self.passable,
            "cost": self.cost
        }
        
        try:
            # Uses _validate_and_populate to validate without changing values
            # (since the dataclass is frozen)
            self._validate_and_populate_without_setting(data)
        except ValidationError as e:
            # Re-raise the error so it's not lost
            raise e
    
    def _validate_and_populate(self, data: Dict[str, Any]) -> None:
        """Validate cell data (used for from_dict method)"""
        self._validate_and_populate_without_setting(data)
        
        # Set fields manually (needed because dataclass is frozen)
        object.__setattr__(self, "x", data.get("x", 0))
        object.__setattr__(self, "y", data.get("y", 0))
        object.__setattr__(self, "terrain_type", data.get("terrain_type", "plains"))
        object.__setattr__(self, "elevation", data.get("elevation", 0.0))
        object.__setattr__(self, "moisture", data.get("moisture", 0.5))
        object.__setattr__(self, "temperature", data.get("temperature", 0.0))
        object.__setattr__(self, "biome", data.get("biome", ""))
        object.__setattr__(self, "features", data.get("features", []))
        object.__setattr__(self, "passable", data.get("passable", True))
        object.__setattr__(self, "cost", data.get("cost", 1.0))
    
    def _validate_and_populate_without_setting(self, data: Dict[str, Any]) -> None:
        """Validate cell data without setting values"""
        # Check required fields
        missing = Validator.validate_required_fields(
            data, ["x", "y", "terrain_type", "elevation", "moisture", "temperature", "biome"]
        )
        
        if missing["missing"]:
            raise ValidationError(
                f"Missing required fields for RegionCellContract: {', '.join(missing['missing'])}",
                {"missing_fields": missing["missing"]}
            )
        
        # Validate field types and constraints
        errors = {}
        
        # Validate coordinates
        if not Validator.validate_number(data.get("x", 0), integer_only=True):
            errors["x"] = "x must be an integer"
        
        if not Validator.validate_number(data.get("y", 0), integer_only=True):
            errors["y"] = "y must be an integer"
        
        # Validate terrain type
        terrain = data.get("terrain_type", "")
        if not Validator.validate_string(terrain) or not any(terrain == t.value for t in TerrainType):
            errors["terrain_type"] = f"terrain_type must be one of: {', '.join(t.value for t in TerrainType)}"
        
        # Validate numeric ranges
        if not Validator.validate_number(data.get("elevation", 0), min_value=-100, max_value=10000):
            errors["elevation"] = "elevation must be a number between -100 and 10000"
        
        if not Validator.validate_number(data.get("moisture", 0), min_value=0, max_value=1):
            errors["moisture"] = "moisture must be a number between 0 and 1"
        
        if not Validator.validate_number(data.get("temperature", 0), min_value=-50, max_value=50):
            errors["temperature"] = "temperature must be a number between -50 and 50"
        
        # Validate biome
        if not Validator.validate_string(data.get("biome", ""), min_length=1):
            errors["biome"] = "biome must be a non-empty string"
        
        # Validate features if present
        features = data.get("features", [])
        if not isinstance(features, list):
            errors["features"] = "features must be a list of strings"
        else:
            for i, feature in enumerate(features):
                if not Validator.validate_string(feature):
                    if "features" not in errors:
                        errors["features"] = []
                    errors["features"].append(f"feature at index {i} must be a string")
        
        # Validate passable
        if "passable" in data and not isinstance(data["passable"], bool):
            errors["passable"] = "passable must be a boolean"
        
        # Validate cost
        if "cost" in data and not Validator.validate_number(data["cost"], min_value=0):
            errors["cost"] = "cost must be a number greater than or equal to 0"
        
        if errors:
            raise ValidationError("RegionCellContract validation failed", errors)
        
    @property
    def coordinates(self) -> Tuple[int, int]:
        """Get the cell coordinates as a tuple"""
        return (self.x, self.y)
    
    def distance_to(self, other: 'RegionCellContract') -> float:
        """Calculate the Manhattan distance to another cell"""
        return abs(self.x - other.x) + abs(self.y - other.y)
    
    def euclidean_distance_to(self, other: 'RegionCellContract') -> float:
        """Calculate the Euclidean distance to another cell"""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


@dataclass
class ResourceContract(WorldGenContract):
    """Contract for a resource within a region"""
    resource_type: str
    x: int
    y: int
    quantity: float = 1.0
    quality: float = 1.0
    
    def _validate_and_populate(self, data: Dict[str, Any]) -> None:
        """Validate resource data"""
        # Check required fields
        missing = Validator.validate_required_fields(
            data, ["resource_type", "x", "y"]
        )
        
        if missing["missing"]:
            raise ValidationError(
                f"Missing required fields for ResourceContract: {', '.join(missing['missing'])}",
                {"missing_fields": missing["missing"]}
            )
        
        # Validate field types and constraints
        errors = {}
        
        # Validate resource type
        if not Validator.validate_string(data.get("resource_type", ""), min_length=1):
            errors["resource_type"] = "resource_type must be a non-empty string"
        
        # Validate coordinates
        if not Validator.validate_number(data.get("x", 0), integer_only=True):
            errors["x"] = "x must be an integer"
        
        if not Validator.validate_number(data.get("y", 0), integer_only=True):
            errors["y"] = "y must be an integer"
        
        # Validate quantity and quality
        if "quantity" in data and not Validator.validate_number(data["quantity"], min_value=0):
            errors["quantity"] = "quantity must be a number greater than or equal to 0"
        
        if "quality" in data and not Validator.validate_number(data["quality"], min_value=0, max_value=1):
            errors["quality"] = "quality must be a number between 0 and 1"
        
        if errors:
            raise ValidationError("ResourceContract validation failed", errors)
        
        # Populate fields
        self.resource_type = data.get("resource_type", "")
        self.x = data.get("x", 0)
        self.y = data.get("y", 0)
        self.quantity = data.get("quantity", 1.0)
        self.quality = data.get("quality", 1.0)


class RegionContract(WorldGenContract):
    """
    Contract for a complete region
    """
    def __init__(self, id: str = None, name: str = "", width: int = 0, height: int = 0):
        super().__init__()
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.width = width
        self.height = height
        self.cells: List[RegionCellContract] = []
        self.points_of_interest: List[Dict[str, Any]] = []
        self.resources: List[ResourceContract] = []
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def _validate_and_populate(self, data: Dict[str, Any]) -> None:
        """Validate region data"""
        # Check required fields
        missing = Validator.validate_required_fields(
            data, ["id", "name", "width", "height", "cells"]
        )
        
        if missing["missing"]:
            raise ValidationError(
                f"Missing required fields for RegionContract: {', '.join(missing['missing'])}",
                {"missing_fields": missing["missing"]}
            )
        
        # Validate field types and constraints
        errors = {}
        
        # Validate ID
        if not Validator.validate_string(data.get("id", ""), min_length=1):
            errors["id"] = "id must be a non-empty string"
        
        # Validate name
        if not Validator.validate_string(data.get("name", ""), min_length=1):
            errors["name"] = "name must be a non-empty string"
        
        # Validate dimensions
        if not Validator.validate_number(data.get("width", 0), min_value=1, integer_only=True):
            errors["width"] = "width must be a positive integer"
        
        if not Validator.validate_number(data.get("height", 0), min_value=1, integer_only=True):
            errors["height"] = "height must be a positive integer"
        
        # Validate cells
        cells_data = data.get("cells", [])
        if not isinstance(cells_data, list):
            errors["cells"] = "cells must be a list"
        else:
            # Check cell count
            expected_count = data.get("width", 0) * data.get("height", 0)
            if len(cells_data) != expected_count:
                errors["cells"] = f"cell count does not match dimensions: expected {expected_count}, got {len(cells_data)}"
            
            # Validate individual cells
            validated_cells = []
            cell_coords = set()
            for i, cell_data in enumerate(cells_data):
                try:
                    cell = RegionCellContract.from_dict(cell_data) if isinstance(cell_data, dict) else cell_data
                    validated_cells.append(cell)
                    
                    # Check for duplicate coordinates
                    coords = (cell.x, cell.y)
                    if coords in cell_coords:
                        if "duplicate_coords" not in errors:
                            errors["duplicate_coords"] = []
                        errors["duplicate_coords"].append(f"Duplicate coordinates at {coords}")
                    cell_coords.add(coords)
                    
                    # Check coordinates are within bounds
                    if cell.x < 0 or cell.x >= data.get("width", 0) or cell.y < 0 or cell.y >= data.get("height", 0):
                        if "out_of_bounds" not in errors:
                            errors["out_of_bounds"] = []
                        errors["out_of_bounds"].append(f"Cell at {coords} is out of bounds")
                    
                except Exception as e:
                    if "cells" not in errors:
                        errors["cells"] = []
                    errors["cells"].append(f"Invalid cell at index {i}: {str(e)}")
        
        # Validate resources if present
        if "resources" in data:
            resources_data = data.get("resources", [])
            if not isinstance(resources_data, list):
                errors["resources"] = "resources must be a list"
            else:
                validated_resources = []
                for i, resource_data in enumerate(resources_data):
                    try:
                        resource = ResourceContract.from_dict(resource_data) if isinstance(resource_data, dict) else resource_data
                        validated_resources.append(resource)
                        
                        # Check coordinates are within bounds
                        if resource.x < 0 or resource.x >= data.get("width", 0) or resource.y < 0 or resource.y >= data.get("height", 0):
                            if "resource_coords" not in errors:
                                errors["resource_coords"] = []
                            errors["resource_coords"].append(f"Resource at ({resource.x}, {resource.y}) is out of bounds")
                    
                    except Exception as e:
                        if "resources" not in errors:
                            errors["resources"] = []
                        errors["resources"].append(f"Invalid resource at index {i}: {str(e)}")
        
        if errors:
            raise ValidationError("RegionContract validation failed", errors)
        
        # Populate fields
        self.id = data.get("id")
        self.name = data.get("name")
        self.width = data.get("width")
        self.height = data.get("height")
        self.cells = validated_cells if "validated_cells" in locals() else []
        self.points_of_interest = data.get("points_of_interest", [])
        self.resources = validated_resources if "validated_resources" in locals() else []
        self.metadata = data.get("metadata", {})
        self.created_at = data.get("created_at", datetime.now().isoformat())
        self.updated_at = data.get("updated_at", datetime.now().isoformat())
        
        # Freeze to prevent modifications
        self._freeze()
    
    def get_cell(self, x: int, y: int) -> Optional[RegionCellContract]:
        """
        Get a cell by coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Cell at the specified coordinates, or None if not found
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        
        for cell in self.cells:
            if cell.x == x and cell.y == y:
                return cell
        
        return None
    
    def get_cells_by_terrain(self, terrain_type: str) -> List[RegionCellContract]:
        """
        Get all cells with the specified terrain type
        
        Args:
            terrain_type: Terrain type to filter by
            
        Returns:
            List of cells with the specified terrain type
        """
        return [cell for cell in self.cells if cell.terrain_type == terrain_type]
    
    def get_cells_by_biome(self, biome: str) -> List[RegionCellContract]:
        """
        Get all cells with the specified biome
        
        Args:
            biome: Biome to filter by
            
        Returns:
            List of cells with the specified biome
        """
        return [cell for cell in self.cells if cell.biome == biome]
    
    def get_resource_at(self, x: int, y: int) -> Optional[ResourceContract]:
        """
        Get a resource at the specified coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Resource at the specified coordinates, or None if not found
        """
        for resource in self.resources:
            if resource.x == x and resource.y == y:
                return resource
        
        return None
    
    def get_resources_by_type(self, resource_type: str) -> List[ResourceContract]:
        """
        Get all resources of the specified type
        
        Args:
            resource_type: Resource type to filter by
            
        Returns:
            List of resources of the specified type
        """
        return [resource for resource in self.resources if resource.resource_type == resource_type]


class RegionQueryType(Enum):
    """Types of region queries"""
    BY_ID = "by_id"
    BY_NAME = "by_name"
    BY_COORDINATES = "by_coordinates"
    BY_AREA = "by_area"
    BY_BIOME = "by_biome"
    BY_TERRAIN = "by_terrain"
    BY_FEATURE = "by_feature"
    BY_RESOURCE = "by_resource"


@dataclass
class RegionQuery:
    """Query parameters for region data"""
    query_type: RegionQueryType
    
    # Query-specific parameters
    id: Optional[str] = None
    name: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    biome: Optional[str] = None
    terrain_type: Optional[str] = None
    feature: Optional[str] = None
    resource_type: Optional[str] = None
    
    # Pagination parameters
    limit: int = 10
    offset: int = 0
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate the query parameters
        
        Returns:
            Dictionary of validation errors, empty if valid
        """
        errors = {}
        
        # Check required parameters based on query type
        if self.query_type == RegionQueryType.BY_ID and not self.id:
            errors["id"] = "id is required for BY_ID queries"
        
        elif self.query_type == RegionQueryType.BY_NAME and not self.name:
            errors["name"] = "name is required for BY_NAME queries"
        
        elif self.query_type == RegionQueryType.BY_COORDINATES and (self.x is None or self.y is None):
            errors["coordinates"] = "x and y are required for BY_COORDINATES queries"
        
        elif self.query_type == RegionQueryType.BY_AREA and (self.x is None or self.y is None or self.width is None or self.height is None):
            errors["area"] = "x, y, width, and height are required for BY_AREA queries"
        
        elif self.query_type == RegionQueryType.BY_BIOME and not self.biome:
            errors["biome"] = "biome is required for BY_BIOME queries"
        
        elif self.query_type == RegionQueryType.BY_TERRAIN and not self.terrain_type:
            errors["terrain_type"] = "terrain_type is required for BY_TERRAIN queries"
        
        elif self.query_type == RegionQueryType.BY_FEATURE and not self.feature:
            errors["feature"] = "feature is required for BY_FEATURE queries"
        
        elif self.query_type == RegionQueryType.BY_RESOURCE and not self.resource_type:
            errors["resource_type"] = "resource_type is required for BY_RESOURCE queries"
        
        # Validate numeric parameters
        if self.x is not None and not isinstance(self.x, int):
            errors["x"] = "x must be an integer"
        
        if self.y is not None and not isinstance(self.y, int):
            errors["y"] = "y must be an integer"
        
        if self.width is not None and (not isinstance(self.width, int) or self.width <= 0):
            errors["width"] = "width must be a positive integer"
        
        if self.height is not None and (not isinstance(self.height, int) or self.height <= 0):
            errors["height"] = "height must be a positive integer"
        
        # Validate pagination parameters
        if not isinstance(self.limit, int) or self.limit <= 0:
            errors["limit"] = "limit must be a positive integer"
        
        if not isinstance(self.offset, int) or self.offset < 0:
            errors["offset"] = "offset must be a non-negative integer"
        
        return errors


# Type alias for region query results
RegionResult = QueryResult[RegionContract] 