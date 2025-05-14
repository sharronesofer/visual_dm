#!/usr/bin/env python3
"""
poi.py - Point of Interest Data Contracts for World Generation System

This module defines the standardized data contracts for point of interest (POI) data,
including templates, modifiers, content, and state information.

Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
import uuid
from datetime import datetime

from .base import (
    WorldGenContract, 
    WorldGenContractError,
    ValidationError,
    WorldGenContractValidator as Validator,
    QueryResult
)


class POIType(Enum):
    """Types of points of interest"""
    SHOP = "shop"
    TEMPLE = "temple"
    RUIN = "ruin"
    CAMP = "camp"
    OUTPOST = "outpost"
    CAVE = "cave"
    DUNGEON = "dungeon"
    SETTLEMENT = "settlement"
    LANDMARK = "landmark"
    NATURAL = "natural"
    QUEST = "quest"
    OTHER = "other"


@dataclass
class POITemplateContract(WorldGenContract):
    """Template for a point of interest"""
    id: str
    name: str
    type: POIType
    base_description: str
    base_loot: List[str] = field(default_factory=list)
    base_npcs: List[str] = field(default_factory=list)
    rarity: float = 1.0  # Higher value = more common
    tags: List[str] = field(default_factory=list)
    
    def _validate_and_populate(self, data: Dict[str, Any]) -> None:
        """Validate POI template data"""
        # Check required fields
        missing = Validator.validate_required_fields(
            data, ["id", "name", "type", "base_description"]
        )
        
        if missing["missing"]:
            raise ValidationError(
                f"Missing required fields for POITemplateContract: {', '.join(missing['missing'])}",
                {"missing_fields": missing["missing"]}
            )
        
        # Validate field types and constraints
        errors = {}
        
        # Validate ID and name
        if not Validator.validate_string(data.get("id", ""), min_length=1):
            errors["id"] = "id must be a non-empty string"
        
        if not Validator.validate_string(data.get("name", ""), min_length=1):
            errors["name"] = "name must be a non-empty string"
        
        # Validate type
        poi_type = data.get("type")
        if isinstance(poi_type, POIType):
            poi_type = poi_type.value
            
        if not isinstance(poi_type, str) or not any(poi_type == t.value for t in POIType):
            errors["type"] = f"type must be one of: {', '.join(t.value for t in POIType)}"
        
        # Validate description
        if not Validator.validate_string(data.get("base_description", ""), min_length=1):
            errors["base_description"] = "base_description must be a non-empty string"
        
        # Validate list fields
        for field_name in ["base_loot", "base_npcs", "tags"]:
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
        
        # Validate rarity
        if "rarity" in data and not Validator.validate_number(data["rarity"], min_value=0):
            errors["rarity"] = "rarity must be a non-negative number"
        
        if errors:
            raise ValidationError("POITemplateContract validation failed", errors)
        
        # Populate fields
        self.id = data["id"]
        self.name = data["name"]
        
        # Handle enum conversion
        if isinstance(data["type"], str):
            self.type = POIType(data["type"])
        else:
            self.type = data["type"]
            
        self.base_description = data["base_description"]
        self.base_loot = data.get("base_loot", [])
        self.base_npcs = data.get("base_npcs", [])
        self.rarity = data.get("rarity", 1.0)
        self.tags = data.get("tags", [])


@dataclass
class POIModifierContract(WorldGenContract):
    """A modifier that can be applied to a POI template"""
    id: str
    name: str
    description: str
    loot_modifier: Optional[str] = None  # Description of how loot is modified
    npc_modifier: Optional[str] = None   # Description of how NPCs are modified
    quest_hook: Optional[str] = None     # Potential quest hook added by this modifier
    effects: List[Dict[str, Any]] = field(default_factory=list)  # Additional gameplay effects
    tags: List[str] = field(default_factory=list)
    compatible_types: List[POIType] = field(default_factory=list)  # POI types this can be applied to
    
    def _validate_and_populate(self, data: Dict[str, Any]) -> None:
        """Validate POI modifier data"""
        # Check required fields
        missing = Validator.validate_required_fields(
            data, ["id", "name", "description"]
        )
        
        if missing["missing"]:
            raise ValidationError(
                f"Missing required fields for POIModifierContract: {', '.join(missing['missing'])}",
                {"missing_fields": missing["missing"]}
            )
        
        # Validate field types and constraints
        errors = {}
        
        # Validate ID, name, and description
        if not Validator.validate_string(data.get("id", ""), min_length=1):
            errors["id"] = "id must be a non-empty string"
        
        if not Validator.validate_string(data.get("name", ""), min_length=1):
            errors["name"] = "name must be a non-empty string"
        
        if not Validator.validate_string(data.get("description", ""), min_length=1):
            errors["description"] = "description must be a non-empty string"
        
        # Validate optional string fields
        for field_name in ["loot_modifier", "npc_modifier", "quest_hook"]:
            if field_name in data and data[field_name] is not None and not Validator.validate_string(data[field_name]):
                errors[field_name] = f"{field_name} must be a string"
        
        # Validate list fields
        if "effects" in data:
            effects = data.get("effects", [])
            if not isinstance(effects, list):
                errors["effects"] = "effects must be a list of dictionaries"
            else:
                for i, effect in enumerate(effects):
                    if not isinstance(effect, dict):
                        if "effects" not in errors or not isinstance(errors["effects"], list):
                            errors["effects"] = []
                        errors["effects"].append(f"Effect at index {i} must be a dictionary")
        
        if "tags" in data:
            tags = data.get("tags", [])
            if not isinstance(tags, list):
                errors["tags"] = "tags must be a list of strings"
            else:
                for i, tag in enumerate(tags):
                    if not Validator.validate_string(tag):
                        if "tags" not in errors or not isinstance(errors["tags"], list):
                            errors["tags"] = []
                        errors["tags"].append(f"Tag at index {i} must be a string")
        
        # Validate compatible types
        if "compatible_types" in data:
            compatible_types = data.get("compatible_types", [])
            if not isinstance(compatible_types, list):
                errors["compatible_types"] = "compatible_types must be a list of POIType values"
            else:
                validated_types = []
                for i, poi_type in enumerate(compatible_types):
                    try:
                        if isinstance(poi_type, str):
                            validated_types.append(POIType(poi_type))
                        elif isinstance(poi_type, POIType):
                            validated_types.append(poi_type)
                        else:
                            if "compatible_types" not in errors or not isinstance(errors["compatible_types"], list):
                                errors["compatible_types"] = []
                            errors["compatible_types"].append(f"Type at index {i} must be a POIType value")
                    except ValueError:
                        if "compatible_types" not in errors or not isinstance(errors["compatible_types"], list):
                            errors["compatible_types"] = []
                        errors["compatible_types"].append(f"Invalid POIType value at index {i}: {poi_type}")
        
        if errors:
            raise ValidationError("POIModifierContract validation failed", errors)
        
        # Populate fields
        self.id = data["id"]
        self.name = data["name"]
        self.description = data["description"]
        self.loot_modifier = data.get("loot_modifier")
        self.npc_modifier = data.get("npc_modifier")
        self.quest_hook = data.get("quest_hook")
        self.effects = data.get("effects", [])
        self.tags = data.get("tags", [])
        
        # Handle enum conversion for compatible types
        self.compatible_types = []
        for poi_type in data.get("compatible_types", []):
            if isinstance(poi_type, str):
                self.compatible_types.append(POIType(poi_type))
            else:
                self.compatible_types.append(poi_type)


class POIContract(WorldGenContract):
    """Contract for a complete point of interest instance"""
    
    def __init__(self, id: str = None, template_id: str = "", x: int = 0, y: int = 0):
        super().__init__()
        self.id = id or str(uuid.uuid4())
        self.template_id = template_id
        self.x = x
        self.y = y
        self.name = ""
        self.description = ""
        self.modifiers: List[str] = []  # List of modifier IDs
        self.loot: List[str] = []
        self.npcs: List[str] = []
        self.quests: List[str] = []
        self.state: Dict[str, Any] = {}  # Current state of the POI (visited, modified, etc.)
        self.tags: List[str] = []
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def _validate_and_populate(self, data: Dict[str, Any]) -> None:
        """Validate POI data"""
        # Check required fields
        missing = Validator.validate_required_fields(
            data, ["id", "template_id", "x", "y"]
        )
        
        if missing["missing"]:
            raise ValidationError(
                f"Missing required fields for POIContract: {', '.join(missing['missing'])}",
                {"missing_fields": missing["missing"]}
            )
        
        # Validate field types and constraints
        errors = {}
        
        # Validate ID and template_id
        if not Validator.validate_string(data.get("id", ""), min_length=1):
            errors["id"] = "id must be a non-empty string"
        
        if not Validator.validate_string(data.get("template_id", ""), min_length=1):
            errors["template_id"] = "template_id must be a non-empty string"
        
        # Validate coordinates
        if not Validator.validate_number(data.get("x", 0), integer_only=True):
            errors["x"] = "x must be an integer"
        
        if not Validator.validate_number(data.get("y", 0), integer_only=True):
            errors["y"] = "y must be an integer"
        
        # Validate optional string fields
        for field_name in ["name", "description"]:
            if field_name in data and not Validator.validate_string(data[field_name]):
                errors[field_name] = f"{field_name} must be a string"
        
        # Validate list fields
        for field_name in ["modifiers", "loot", "npcs", "quests", "tags"]:
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
        
        # Validate state
        if "state" in data and not isinstance(data["state"], dict):
            errors["state"] = "state must be a dictionary"
        
        # Validate metadata
        if "metadata" in data and not isinstance(data["metadata"], dict):
            errors["metadata"] = "metadata must be a dictionary"
        
        if errors:
            raise ValidationError("POIContract validation failed", errors)
        
        # Populate fields
        self.id = data["id"]
        self.template_id = data["template_id"]
        self.x = data["x"]
        self.y = data["y"]
        self.name = data.get("name", "")
        self.description = data.get("description", "")
        self.modifiers = data.get("modifiers", [])
        self.loot = data.get("loot", [])
        self.npcs = data.get("npcs", [])
        self.quests = data.get("quests", [])
        self.state = data.get("state", {})
        self.tags = data.get("tags", [])
        self.metadata = data.get("metadata", {})
        self.created_at = data.get("created_at", datetime.now().isoformat())
        self.updated_at = data.get("updated_at", datetime.now().isoformat())
        
        # Freeze to prevent modifications
        self._freeze()
    
    @property
    def coordinates(self) -> Tuple[int, int]:
        """Get the POI coordinates as a tuple"""
        return (self.x, self.y)
    
    def has_tag(self, tag: str) -> bool:
        """Check if the POI has the specified tag"""
        return tag in self.tags
    
    def has_modifier(self, modifier_id: str) -> bool:
        """Check if the POI has the specified modifier"""
        return modifier_id in self.modifiers
    
    def is_visited(self) -> bool:
        """Check if the POI has been visited"""
        return self.state.get("visited", False)
    
    def get_quest_status(self, quest_id: str) -> Optional[str]:
        """Get the status of a quest associated with this POI"""
        return self.state.get("quests", {}).get(quest_id)


class POIQueryType(Enum):
    """Types of POI queries"""
    BY_ID = "by_id"
    BY_TEMPLATE = "by_template"
    BY_COORDINATES = "by_coordinates"
    BY_AREA = "by_area"
    BY_TYPE = "by_type"
    BY_TAG = "by_tag"
    BY_MODIFIER = "by_modifier"
    BY_NPC = "by_npc"
    BY_LOOT = "by_loot"
    BY_QUEST = "by_quest"


@dataclass
class POIQuery:
    """Query parameters for POI data"""
    query_type: POIQueryType
    
    # Query-specific parameters
    id: Optional[str] = None
    template_id: Optional[str] = None
    poi_type: Optional[POIType] = None
    x: Optional[int] = None
    y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    tag: Optional[str] = None
    modifier_id: Optional[str] = None
    npc_id: Optional[str] = None
    loot_id: Optional[str] = None
    quest_id: Optional[str] = None
    include_visited: bool = True
    include_state: bool = True
    
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
        if self.query_type == POIQueryType.BY_ID and not self.id:
            errors["id"] = "id is required for BY_ID queries"
        
        elif self.query_type == POIQueryType.BY_TEMPLATE and not self.template_id:
            errors["template_id"] = "template_id is required for BY_TEMPLATE queries"
        
        elif self.query_type == POIQueryType.BY_COORDINATES and (self.x is None or self.y is None):
            errors["coordinates"] = "x and y are required for BY_COORDINATES queries"
        
        elif self.query_type == POIQueryType.BY_AREA and (self.x is None or self.y is None or self.width is None or self.height is None):
            errors["area"] = "x, y, width, and height are required for BY_AREA queries"
        
        elif self.query_type == POIQueryType.BY_TYPE and self.poi_type is None:
            errors["poi_type"] = "poi_type is required for BY_TYPE queries"
        
        elif self.query_type == POIQueryType.BY_TAG and not self.tag:
            errors["tag"] = "tag is required for BY_TAG queries"
        
        elif self.query_type == POIQueryType.BY_MODIFIER and not self.modifier_id:
            errors["modifier_id"] = "modifier_id is required for BY_MODIFIER queries"
        
        elif self.query_type == POIQueryType.BY_NPC and not self.npc_id:
            errors["npc_id"] = "npc_id is required for BY_NPC queries"
        
        elif self.query_type == POIQueryType.BY_LOOT and not self.loot_id:
            errors["loot_id"] = "loot_id is required for BY_LOOT queries"
        
        elif self.query_type == POIQueryType.BY_QUEST and not self.quest_id:
            errors["quest_id"] = "quest_id is required for BY_QUEST queries"
        
        # Validate numeric parameters
        if self.x is not None and not isinstance(self.x, int):
            errors["x"] = "x must be an integer"
        
        if self.y is not None and not isinstance(self.y, int):
            errors["y"] = "y must be an integer"
        
        if self.width is not None and (not isinstance(self.width, int) or self.width <= 0):
            errors["width"] = "width must be a positive integer"
        
        if self.height is not None and (not isinstance(self.height, int) or self.height <= 0):
            errors["height"] = "height must be a positive integer"
        
        # Validate POI type
        if self.poi_type is not None and not isinstance(self.poi_type, POIType):
            try:
                if isinstance(self.poi_type, str):
                    POIType(self.poi_type)  # Try to convert to enum
                else:
                    errors["poi_type"] = "poi_type must be a POIType enum or string value"
            except ValueError:
                errors["poi_type"] = f"Invalid POIType value: {self.poi_type}"
        
        # Validate boolean parameters
        if not isinstance(self.include_visited, bool):
            errors["include_visited"] = "include_visited must be a boolean"
        
        if not isinstance(self.include_state, bool):
            errors["include_state"] = "include_state must be a boolean"
        
        # Validate pagination parameters
        if not isinstance(self.limit, int) or self.limit <= 0:
            errors["limit"] = "limit must be a positive integer"
        
        if not isinstance(self.offset, int) or self.offset < 0:
            errors["offset"] = "offset must be a non-negative integer"
        
        return errors


# Type alias for POI query results
POIResult = QueryResult[POIContract] 