#!/usr/bin/env python3
"""
IWorldGenerator.py - Interfaces and contracts for world generation

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol, TypeVar, Callable, Generic
from abc import ABC, abstractmethod
from enum import Enum
import json
import random
from abc import ABC, abstractmethod

# Enum for generator types
class GeneratorType(Enum):
    PROCEDURAL = "procedural"
    HANDCRAFTED = "handcrafted" 
    HYBRID = "hybrid"

# Region type definitions
class Cell:
    """A cell in a region"""
    def __init__(self, x: int, y: int, terrain_type: str, 
                 elevation: float = 0.0, moisture: float = 0.0,
                 temperature: float = 0.0, biome: str = ""):
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.elevation = elevation
        self.moisture = moisture
        self.temperature = temperature
        self.biome = biome
        self.features = []

class PointOfInterest:
    """A point of interest in a region"""
    def __init__(self, x: int, y: int, poi_type: str, 
                 name: str = "", description: str = ""):
        self.x = x
        self.y = y
        self.poi_type = poi_type
        self.name = name
        self.description = description
        self.attributes = {}

class Resource:
    """A resource in a region"""
    def __init__(self, resource_type: str, x: int, y: int, 
                 quantity: float = 1.0, quality: float = 1.0):
        self.resource_type = resource_type
        self.x = x
        self.y = y
        self.quantity = quantity
        self.quality = quality

class Region:
    """A region in the world"""
    def __init__(self, id: str, name: str, width: int, height: int):
        self.id = id
        self.name = name
        self.width = width
        self.height = height
        self.cells: List[Cell] = []
        self.points_of_interest: List[PointOfInterest] = []
        self.resources: List[Resource] = []
        self.metadata: Dict[str, Any] = {}

class RegionGeneratorOptions:
    """Options for generating a region"""
    def __init__(self, 
                 width: int = 32, 
                 height: int = 32,
                 seed: int = 0, 
                 region_type: str = "", 
                 template_id: Optional[str] = None,
                 terrain_complexity: float = 0.5,
                 resource_abundance: float = 0.5,
                 poi_density: float = 0.5,
                 is_coastal: bool = False,
                 is_mountainous: bool = False,
                 is_forested: bool = False,
                 is_arid: bool = False):
        self.width = width
        self.height = height
        self.seed = seed
        self.region_type = region_type
        self.template_id = template_id
        self.terrain_complexity = terrain_complexity
        self.resource_abundance = resource_abundance
        self.poi_density = poi_density
        self.is_coastal = is_coastal
        self.is_mountainous = is_mountainous
        self.is_forested = is_forested
        self.is_arid = is_arid
        self.additional_params: Dict[str, Any] = {}

class GenerationResult:
    """Result of a region generation operation"""
    def __init__(self, region: Region, success: bool = True, 
                 error: Optional[str] = None, generation_time: float = 0):
        self.region = region
        self.success = success
        self.error = error
        self.generation_time = generation_time
        self.metadata: Dict[str, Any] = {}

# Random number generation interfaces
class IRandomGenerator(Protocol):
    """Interface for random number generators"""
    def random(self) -> float: ...
    def random_int(self, min_val: int, max_val: int) -> int: ...
    def create_child(self, name: str) -> 'IRandomGenerator': ...

# The main generator interface
class IRegionGenerator(ABC):
    """Interface for region generators"""
    
    @abstractmethod
    def get_type(self) -> GeneratorType:
        """Get the type of generator"""
        pass
        
    @abstractmethod
    def generate(self, options: RegionGeneratorOptions) -> GenerationResult:
        """Generate a region"""
        pass
        
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of this generator"""
        pass

# Template interface for handcrafted generators
class RegionTemplate:
    """A template for generating a region"""
    def __init__(self, id: str, name: str, width: int, height: int,
                 description: str = "", cells: Optional[List[Dict]] = None,
                 points_of_interest: Optional[List[Dict]] = None,
                 resources: Optional[List[Dict]] = None):
        self.id = id
        self.name = name
        self.width = width
        self.height = height
        self.description = description
        self.cells = cells or []
        self.points_of_interest = points_of_interest or []
        self.resources = resources or []
        
    @classmethod
    def from_json(cls, json_str: str) -> 'RegionTemplate':
        """Create a template from a JSON string"""
        data = json.loads(json_str)
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            width=data.get('width', 32),
            height=data.get('height', 32),
            description=data.get('description', ''),
            cells=data.get('cells', []),
            points_of_interest=data.get('pointsOfInterest', []),
            resources=data.get('resources', [])
        )
        
    def to_json(self) -> str:
        """Convert the template to a JSON string"""
        return json.dumps({
            'id': self.id,
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'description': self.description,
            'cells': self.cells,
            'pointsOfInterest': self.points_of_interest,
            'resources': self.resources
        }, indent=2)

# Interface for handcrafted region generators
class IHandcraftedRegionGenerator(IRegionGenerator):
    """Interface for handcrafted region generators"""
    
    @abstractmethod
    def register_template(self, template: RegionTemplate) -> bool:
        """Register a template with this generator"""
        pass
        
    @abstractmethod
    def get_template(self, template_id: str) -> Optional[RegionTemplate]:
        """Get a template by ID"""
        pass
        
    @abstractmethod
    def get_templates(self) -> List[RegionTemplate]:
        """Get all templates"""
        pass

# Interface for procedural region generators
class IProceduralRegionGenerator(IRegionGenerator):
    """Interface for procedural region generators"""
    
    @abstractmethod
    def set_terrain_parameters(self, params: Dict[str, Any]) -> None:
        """Set parameters for terrain generation"""
        pass
        
    @abstractmethod
    def set_resource_parameters(self, params: Dict[str, Any]) -> None:
        """Set parameters for resource generation"""
        pass
        
    @abstractmethod
    def set_poi_parameters(self, params: Dict[str, Any]) -> None:
        """Set parameters for POI generation"""
        pass

# Pipeline stage interface
T = TypeVar('T')
U = TypeVar('U')

class IPipelineStage(Protocol, Generic[T, U]):
    """Interface for a pipeline stage"""
    def process(self, input_data: T, options: Dict[str, Any], 
                random: IRandomGenerator) -> U: ...
    def get_name(self) -> str: ...

# Registry interface
class IGeneratorRegistry(Protocol):
    """Interface for a generator registry"""
    def register_generator(self, name: str, generator: IRegionGenerator) -> bool: ...
    def get_generator(self, name: str) -> Optional[IRegionGenerator]: ...
    def get_generators(self) -> Dict[str, IRegionGenerator]: ...
    def get_generator_names(self) -> List[str]: ... 