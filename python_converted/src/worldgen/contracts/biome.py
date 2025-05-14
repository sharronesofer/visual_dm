#!/usr/bin/env python3
"""
biome.py - Biome Data Contracts for World Generation System

This module defines the standardized data contracts for biome data,
including parameters, classifications, and transition rules.

Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
import uuid
import math

from .base import (
    WorldGenContract, 
    WorldGenContractError,
    ValidationError,
    WorldGenContractValidator as Validator,
    QueryResult
)

class BiomeClassification(Enum):
    """Classification of biomes by their general characteristics"""
    DRY = "dry"
    TEMPERATE = "temperate"
    COLD = "cold"
    TROPICAL = "tropical"
    WETLAND = "wetland"
    MOUNTAIN = "mountain"
    WATER = "water"
    TRANSITION = "transition"


class MoistureLevel(Enum):
    """Moisture level classifications"""
    VERY_DRY = 0
    DRY = 1
    MODERATE = 2
    MOIST = 3
    WET = 4
    VERY_WET = 5


class TemperatureLevel(Enum):
    """Temperature level classifications"""
    FREEZING = 0
    COLD = 1
    COOL = 2
    MILD = 3
    WARM = 4
    HOT = 5
    VERY_HOT = 6


class BiomeRelationshipType(Enum):
    """Types of relationships between biomes"""
    COMPATIBLE = "compatible"       # Biomes can be adjacent with no transition
    INCOMPATIBLE = "incompatible"   # Biomes should not be adjacent
    REQUIRES_TRANSITION = "requires_transition"  # Biomes can be adjacent with transition zone
    PARENT = "parent"               # Biome is a parent category of another
    CHILD = "child"                 # Biome is a specialized version of another


@dataclass(frozen=True)
class BiomeRelationship(WorldGenContract):
    """Relationship between two biomes"""
    source_biome_id: str
    target_biome_id: str
    relationship_type: BiomeRelationshipType
    transition_width: int = 0  # Only relevant for REQUIRES_TRANSITION
    transition_biome_ids: List[str] = field(default_factory=list)  # Potential biomes for transition zones
    weight: float = 1.0  # Relative likelihood of this relationship being used
    
    def __post_init__(self):
        """Validate the relationship after initialization"""
        data = {
            "source_biome_id": self.source_biome_id,
            "target_biome_id": self.target_biome_id,
            "relationship_type": self.relationship_type,
            "transition_width": self.transition_width,
            "transition_biome_ids": self.transition_biome_ids,
            "weight": self.weight
        }
        
        # Use the relationship type as a string for validation
        if isinstance(data["relationship_type"], BiomeRelationshipType):
            data["relationship_type"] = data["relationship_type"].value
        
        try:
            # Validate without setting (since dataclass is frozen)
            self._validate_and_populate_without_setting(data)
        except ValidationError as e:
            raise e
    
    def _validate_and_populate(self, data: Dict[str, Any]) -> None:
        """Validate relationship data"""
        self._validate_and_populate_without_setting(data)
        
        # Set fields manually (needed because dataclass is frozen)
        object.__setattr__(self, "source_biome_id", data["source_biome_id"])
        object.__setattr__(self, "target_biome_id", data["target_biome_id"])
        
        # Convert string to enum if needed
        rel_type = data["relationship_type"]
        if isinstance(rel_type, str):
            rel_type = BiomeRelationshipType(rel_type)
        object.__setattr__(self, "relationship_type", rel_type)
        
        object.__setattr__(self, "transition_width", data.get("transition_width", 0))
        object.__setattr__(self, "transition_biome_ids", data.get("transition_biome_ids", []))
        object.__setattr__(self, "weight", data.get("weight", 1.0))
    
    def _validate_and_populate_without_setting(self, data: Dict[str, Any]) -> None:
        """Validate relationship data without setting values"""
        # Check required fields
        missing = Validator.validate_required_fields(
            data, ["source_biome_id", "target_biome_id", "relationship_type"]
        )
        
        if missing["missing"]:
            raise ValidationError(
                f"Missing required fields for BiomeRelationship: {', '.join(missing['missing'])}",
                {"missing_fields": missing["missing"]}
            )
        
        # Validate field types and constraints
        errors = {}
        
        # Validate IDs
        if not Validator.validate_string(data.get("source_biome_id", ""), min_length=1):
            errors["source_biome_id"] = "source_biome_id must be a non-empty string"
        
        if not Validator.validate_string(data.get("target_biome_id", ""), min_length=1):
            errors["target_biome_id"] = "target_biome_id must be a non-empty string"
        
        # Validate relationship type
        rel_type = data.get("relationship_type")
        
        # Convert enum to string for validation if needed
        if isinstance(rel_type, BiomeRelationshipType):
            rel_type = rel_type.value
            
        if not isinstance(rel_type, str) or not any(rel_type == t.value for t in BiomeRelationshipType):
            errors["relationship_type"] = f"relationship_type must be one of: {', '.join(t.value for t in BiomeRelationshipType)}"
        
        # Validate transition width (only required for REQUIRES_TRANSITION)
        if rel_type == BiomeRelationshipType.REQUIRES_TRANSITION.value:
            if not Validator.validate_number(data.get("transition_width", 0), min_value=1, integer_only=True):
                errors["transition_width"] = "transition_width must be a positive integer for REQUIRES_TRANSITION relationships"
            
            # Validate transition biome IDs
            transition_biomes = data.get("transition_biome_ids", [])
            if not isinstance(transition_biomes, list):
                errors["transition_biome_ids"] = "transition_biome_ids must be a list of strings"
            elif len(transition_biomes) == 0:
                errors["transition_biome_ids"] = "transition_biome_ids must not be empty for REQUIRES_TRANSITION relationships"
            else:
                for i, biome_id in enumerate(transition_biomes):
                    if not Validator.validate_string(biome_id, min_length=1):
                        if "transition_biome_ids" not in errors or not isinstance(errors["transition_biome_ids"], list):
                            errors["transition_biome_ids"] = []
                        errors["transition_biome_ids"].append(f"Biome ID at index {i} must be a non-empty string")
        
        # Validate weight
        if "weight" in data and not Validator.validate_number(data["weight"], min_value=0):
            errors["weight"] = "weight must be a non-negative number"
        
        if errors:
            raise ValidationError("BiomeRelationship validation failed", errors)


@dataclass
class BiomeParametersContract(WorldGenContract):
    """Parameters defining the environmental conditions of a biome"""
    # Primary parameters
    temperature_range: Tuple[float, float]  # Min and max temperature in Celsius
    moisture_range: Tuple[float, float]     # Min and max moisture (0-1)
    elevation_range: Tuple[float, float]    # Min and max elevation in meters
    
    # Classification
    classification: BiomeClassification
    temperature_class: TemperatureLevel
    moisture_class: MoistureLevel
    
    # Optional parameters
    soil_fertility: float = 0.5     # 0-1 scale
    vegetation_density: float = 0.5 # 0-1 scale
    biodiversity: float = 0.5       # 0-1 scale
    
    # Aesthetic parameters
    base_color: str = "#7D9951"  # Default to a neutral green
    
    # Transitional properties
    is_transition_biome: bool = False
    transition_weight: float = 1.0  # How suitable as transition (higher = more suitable)
    
    def _validate_and_populate(self, data: Dict[str, Any]) -> None:
        """Validate biome parameters data"""
        # Check required fields
        missing = Validator.validate_required_fields(
            data, ["temperature_range", "moisture_range", "elevation_range", 
                  "classification", "temperature_class", "moisture_class"]
        )
        
        if missing["missing"]:
            raise ValidationError(
                f"Missing required fields for BiomeParametersContract: {', '.join(missing['missing'])}",
                {"missing_fields": missing["missing"]}
            )
        
        # Validate field types and constraints
        errors = {}
        
        # Validate ranges
        for range_name in ["temperature_range", "moisture_range", "elevation_range"]:
            range_val = data.get(range_name)
            
            if not isinstance(range_val, (list, tuple)) or len(range_val) != 2:
                errors[range_name] = f"{range_name} must be a tuple or list with exactly 2 elements"
            elif not all(isinstance(v, (int, float)) for v in range_val):
                errors[range_name] = f"Both values in {range_name} must be numbers"
            elif range_val[0] > range_val[1]:
                errors[range_name] = f"First value in {range_name} must be less than or equal to second value"
        
        # Validate specific range constraints
        if "moisture_range" not in errors:
            moisture_range = data.get("moisture_range")
            if moisture_range[0] < 0 or moisture_range[1] > 1:
                errors["moisture_range"] = "moisture_range values must be between 0 and 1"
        
        # Validate classification
        classification = data.get("classification")
        if isinstance(classification, BiomeClassification):
            classification = classification.value
            
        if not isinstance(classification, str) or not any(classification == c.value for c in BiomeClassification):
            errors["classification"] = f"classification must be one of: {', '.join(c.value for c in BiomeClassification)}"
        
        # Validate temperature class
        temp_class = data.get("temperature_class")
        if isinstance(temp_class, TemperatureLevel):
            temp_class = temp_class.value
            
        if not (isinstance(temp_class, (int, str)) and 
                (isinstance(temp_class, int) and 0 <= temp_class <= 6 or 
                 isinstance(temp_class, str) and any(temp_class == str(t.value) for t in TemperatureLevel))):
            errors["temperature_class"] = f"temperature_class must be one of TemperatureLevel values (0-6)"
        
        # Validate moisture class
        moisture_class = data.get("moisture_class")
        if isinstance(moisture_class, MoistureLevel):
            moisture_class = moisture_class.value
            
        if not (isinstance(moisture_class, (int, str)) and 
                (isinstance(moisture_class, int) and 0 <= moisture_class <= 5 or 
                 isinstance(moisture_class, str) and any(moisture_class == str(m.value) for m in MoistureLevel))):
            errors["moisture_class"] = f"moisture_class must be one of MoistureLevel values (0-5)"
        
        # Validate optional numeric parameters
        for param_name in ["soil_fertility", "vegetation_density", "biodiversity", "transition_weight"]:
            if param_name in data and not Validator.validate_number(data[param_name], min_value=0, max_value=1):
                errors[param_name] = f"{param_name} must be a number between 0 and 1"
        
        # Validate color
        if "base_color" in data and not Validator.validate_string(data["base_color"]) or \
           ("base_color" in data and not data["base_color"].startswith("#")):
            errors["base_color"] = "base_color must be a string in hex format (e.g., '#7D9951')"
        
        # Validate is_transition_biome
        if "is_transition_biome" in data and not isinstance(data["is_transition_biome"], bool):
            errors["is_transition_biome"] = "is_transition_biome must be a boolean"
        
        if errors:
            raise ValidationError("BiomeParametersContract validation failed", errors)
        
        # Populate fields
        self.temperature_range = data["temperature_range"]
        self.moisture_range = data["moisture_range"]
        self.elevation_range = data["elevation_range"]
        
        # Handle enum conversions
        if isinstance(data["classification"], str):
            self.classification = BiomeClassification(data["classification"])
        else:
            self.classification = data["classification"]
            
        if isinstance(data["temperature_class"], (int, str)):
            if isinstance(data["temperature_class"], str):
                self.temperature_class = TemperatureLevel(int(data["temperature_class"]))
            else:
                self.temperature_class = TemperatureLevel(data["temperature_class"])
        else:
            self.temperature_class = data["temperature_class"]
            
        if isinstance(data["moisture_class"], (int, str)):
            if isinstance(data["moisture_class"], str):
                self.moisture_class = MoistureLevel(int(data["moisture_class"]))
            else:
                self.moisture_class = MoistureLevel(data["moisture_class"])
        else:
            self.moisture_class = data["moisture_class"]
        
        # Populate optional fields
        self.soil_fertility = data.get("soil_fertility", 0.5)
        self.vegetation_density = data.get("vegetation_density", 0.5)
        self.biodiversity = data.get("biodiversity", 0.5)
        self.base_color = data.get("base_color", "#7D9951")
        self.is_transition_biome = data.get("is_transition_biome", False)
        self.transition_weight = data.get("transition_weight", 1.0)
    
    @property
    def avg_temperature(self) -> float:
        """Calculate the average temperature"""
        return (self.temperature_range[0] + self.temperature_range[1]) / 2
    
    @property
    def avg_moisture(self) -> float:
        """Calculate the average moisture"""
        return (self.moisture_range[0] + self.moisture_range[1]) / 2
    
    @property
    def avg_elevation(self) -> float:
        """Calculate the average elevation"""
        return (self.elevation_range[0] + self.elevation_range[1]) / 2


class BiomeContract(WorldGenContract):
    """Contract for a biome in the world generation system"""
    
    def __init__(self, id: str = None, name: str = ""):
        super().__init__()
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = ""
        self.parameters = None
        self.relationships: List[BiomeRelationship] = []
        self.flora: List[str] = []
        self.fauna: List[str] = []
        self.resources: List[str] = []
        self.metadata: Dict[str, Any] = {}
    
    def _validate_and_populate(self, data: Dict[str, Any]) -> None:
        """Validate biome data"""
        # Check required fields
        missing = Validator.validate_required_fields(
            data, ["id", "name", "parameters"]
        )
        
        if missing["missing"]:
            raise ValidationError(
                f"Missing required fields for BiomeContract: {', '.join(missing['missing'])}",
                {"missing_fields": missing["missing"]}
            )
        
        # Validate field types and constraints
        errors = {}
        
        # Validate ID and name
        if not Validator.validate_string(data.get("id", ""), min_length=1):
            errors["id"] = "id must be a non-empty string"
        
        if not Validator.validate_string(data.get("name", ""), min_length=1):
            errors["name"] = "name must be a non-empty string"
        
        # Validate parameters
        parameters = data.get("parameters")
        if parameters is None:
            errors["parameters"] = "parameters are required"
        else:
            try:
                if isinstance(parameters, dict):
                    self.parameters = BiomeParametersContract.from_dict(parameters)
                elif isinstance(parameters, BiomeParametersContract):
                    self.parameters = parameters
                else:
                    errors["parameters"] = "parameters must be a BiomeParametersContract or dictionary"
            except Exception as e:
                errors["parameters"] = f"Invalid parameters: {str(e)}"
        
        # Validate relationships if present
        if "relationships" in data:
            relationships = data.get("relationships", [])
            if not isinstance(relationships, list):
                errors["relationships"] = "relationships must be a list"
            else:
                validated_relationships = []
                for i, rel_data in enumerate(relationships):
                    try:
                        rel = BiomeRelationship.from_dict(rel_data) if isinstance(rel_data, dict) else rel_data
                        validated_relationships.append(rel)
                    except Exception as e:
                        if "relationships" not in errors or not isinstance(errors["relationships"], list):
                            errors["relationships"] = []
                        errors["relationships"].append(f"Invalid relationship at index {i}: {str(e)}")
        
        # Validate list fields
        for field_name in ["flora", "fauna", "resources"]:
            if field_name in data:
                field_value = data.get(field_name, [])
                if not isinstance(field_value, list):
                    errors[field_name] = f"{field_name} must be a list of strings"
                else:
                    for i, item in enumerate(field_value):
                        if not Validator.validate_string(item):
                            if field_name not in errors or not isinstance(errors[field_name], list):
                                errors[field_name] = []
                            errors[field_name].append(f"Item at index {i} must be a string")
        
        if errors:
            raise ValidationError("BiomeContract validation failed", errors)
        
        # Populate fields
        self.id = data["id"]
        self.name = data["name"]
        self.description = data.get("description", "")
        # parameters already populated above
        self.relationships = validated_relationships if "validated_relationships" in locals() else data.get("relationships", [])
        self.flora = data.get("flora", [])
        self.fauna = data.get("fauna", [])
        self.resources = data.get("resources", [])
        self.metadata = data.get("metadata", {})
        
        # Freeze to prevent modifications
        self._freeze()
    
    def is_compatible_with(self, other_biome: 'BiomeContract') -> bool:
        """
        Check if this biome is compatible with another biome
        
        Args:
            other_biome: The biome to check compatibility with
            
        Returns:
            True if compatible, False otherwise
        """
        # Check direct relationships
        for rel in self.relationships:
            if rel.target_biome_id == other_biome.id:
                return rel.relationship_type == BiomeRelationshipType.COMPATIBLE
        
        # Check relationships from other biome
        for rel in other_biome.relationships:
            if rel.target_biome_id == self.id:
                return rel.relationship_type == BiomeRelationshipType.COMPATIBLE
        
        # Default to incompatible if no relationship found
        return False
    
    def get_transition_biomes(self, other_biome: 'BiomeContract') -> List[str]:
        """
        Get the transition biomes between this biome and another
        
        Args:
            other_biome: The target biome
            
        Returns:
            List of biome IDs suitable for transition, empty if none found
        """
        # Check direct relationships
        for rel in self.relationships:
            if rel.target_biome_id == other_biome.id and rel.relationship_type == BiomeRelationshipType.REQUIRES_TRANSITION:
                return rel.transition_biome_ids
        
        # Check relationships from other biome
        for rel in other_biome.relationships:
            if rel.target_biome_id == self.id and rel.relationship_type == BiomeRelationshipType.REQUIRES_TRANSITION:
                return rel.transition_biome_ids
        
        # No transition biomes found
        return []


class BiomeQueryType(Enum):
    """Types of biome queries"""
    BY_ID = "by_id"
    BY_NAME = "by_name"
    BY_CLASSIFICATION = "by_classification"
    BY_TEMPERATURE = "by_temperature"
    BY_MOISTURE = "by_moisture"
    BY_ELEVATION = "by_elevation"
    BY_RESOURCE = "by_resource"
    BY_TRANSITION = "by_transition"
    COMPATIBLE_WITH = "compatible_with"
    ALL = "all"


@dataclass
class BiomeQuery:
    """Query parameters for biome data"""
    query_type: BiomeQueryType
    
    # Query-specific parameters
    id: Optional[str] = None
    name: Optional[str] = None
    classification: Optional[str] = None
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None
    moisture_min: Optional[float] = None
    moisture_max: Optional[float] = None
    elevation_min: Optional[float] = None
    elevation_max: Optional[float] = None
    resource: Optional[str] = None
    is_transition: Optional[bool] = None
    compatible_with_id: Optional[str] = None
    
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
        if self.query_type == BiomeQueryType.BY_ID and not self.id:
            errors["id"] = "id is required for BY_ID queries"
        
        elif self.query_type == BiomeQueryType.BY_NAME and not self.name:
            errors["name"] = "name is required for BY_NAME queries"
        
        elif self.query_type == BiomeQueryType.BY_CLASSIFICATION and not self.classification:
            errors["classification"] = "classification is required for BY_CLASSIFICATION queries"
        
        elif self.query_type == BiomeQueryType.BY_TEMPERATURE and (self.temperature_min is None and self.temperature_max is None):
            errors["temperature"] = "at least one of temperature_min or temperature_max is required for BY_TEMPERATURE queries"
        
        elif self.query_type == BiomeQueryType.BY_MOISTURE and (self.moisture_min is None and self.moisture_max is None):
            errors["moisture"] = "at least one of moisture_min or moisture_max is required for BY_MOISTURE queries"
        
        elif self.query_type == BiomeQueryType.BY_ELEVATION and (self.elevation_min is None and self.elevation_max is None):
            errors["elevation"] = "at least one of elevation_min or elevation_max is required for BY_ELEVATION queries"
        
        elif self.query_type == BiomeQueryType.BY_RESOURCE and not self.resource:
            errors["resource"] = "resource is required for BY_RESOURCE queries"
        
        elif self.query_type == BiomeQueryType.BY_TRANSITION and self.is_transition is None:
            errors["is_transition"] = "is_transition is required for BY_TRANSITION queries"
        
        elif self.query_type == BiomeQueryType.COMPATIBLE_WITH and not self.compatible_with_id:
            errors["compatible_with_id"] = "compatible_with_id is required for COMPATIBLE_WITH queries"
        
        # Validate numeric ranges
        if self.temperature_min is not None and self.temperature_max is not None and self.temperature_min > self.temperature_max:
            errors["temperature_range"] = "temperature_min must be less than or equal to temperature_max"
        
        if self.moisture_min is not None and self.moisture_max is not None and self.moisture_min > self.moisture_max:
            errors["moisture_range"] = "moisture_min must be less than or equal to moisture_max"
        
        if self.elevation_min is not None and self.elevation_max is not None and self.elevation_min > self.elevation_max:
            errors["elevation_range"] = "elevation_min must be less than or equal to elevation_max"
        
        # Validate pagination parameters
        if not isinstance(self.limit, int) or self.limit <= 0:
            errors["limit"] = "limit must be a positive integer"
        
        if not isinstance(self.offset, int) or self.offset < 0:
            errors["offset"] = "offset must be a non-negative integer"
        
        return errors


# Type alias for biome query results
BiomeResult = QueryResult[BiomeContract] 