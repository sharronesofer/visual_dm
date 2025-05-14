"""Entity implementations for search functionality.

This module provides implementations of searchable entities for different game objects
like NPCs, Items, Locations, and Quests. Each entity type has its own data model and
mapping configuration for search indexing.
"""

from typing import Dict, Any, Optional, List, TypeVar, Generic, cast
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

from .service import SearchableEntity
from .models import EntityType, FacetType, FacetConfig, EntityMapping
from .exceptions import EntityValidationError

T = TypeVar('T', bound=BaseModel)

class EntityType(str, Enum):
    USER = "user"
    PROJECT = "project"
    TASK = "task"
    DOCUMENT = "document"
    COMMENT = "comment"
    NPC = "npc"
    ITEM = "item"
    LOCATION = "location"
    QUEST = "quest"
    FACTION = "faction"

class BaseGameEntity(BaseModel):
    """Base model for all game entities.
    
    Attributes:
        id: Unique identifier
        name: Display name
        description: Detailed description
        type: Type of entity
        tags: List of tags for categorization
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Detailed description")
    type: EntityType = Field(..., description="Type of entity")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

class NPC(BaseGameEntity):
    """NPC entity model.
    
    Attributes:
        level: NPC's level
        faction: Faction the NPC belongs to
        location: NPC's current location
        dialogue: Available dialogue options
        quests: Associated quests
        schedule: Daily schedule/routine
        inventory: Items carried
        stats: Character statistics
    """
    level: int = Field(..., description="NPC's level", ge=1)
    faction: str = Field(..., description="Faction the NPC belongs to")
    location: str = Field(..., description="NPC's current location")
    dialogue: List[str] = Field(default_factory=list, description="Available dialogue options")
    quests: List[str] = Field(default_factory=list, description="Associated quest IDs")
    schedule: Dict[str, str] = Field(default_factory=dict, description="Daily schedule/routine")
    inventory: List[str] = Field(default_factory=list, description="Item IDs in inventory")
    stats: Dict[str, Any] = Field(default_factory=dict, description="Character statistics")

class Item(BaseGameEntity):
    """Item entity model.
    
    Attributes:
        rarity: Item rarity level
        category: Item category
        level_requirement: Required level to use
        value: Base value in game currency
        stats: Item statistics
        effects: Special effects
        durability: Current/max durability
    """
    rarity: str = Field(..., description="Item rarity level")
    category: str = Field(..., description="Item category")
    level_requirement: int = Field(default=1, description="Required level to use", ge=1)
    value: int = Field(..., description="Base value in game currency", ge=0)
    stats: Dict[str, Any] = Field(default_factory=dict, description="Item statistics")
    effects: List[Dict[str, Any]] = Field(default_factory=list, description="Special effects")
    durability: Optional[Dict[str, int]] = Field(None, description="Current/max durability")

class Location(BaseGameEntity):
    """Location entity model.
    
    Attributes:
        region: Region the location is in
        terrain_type: Type of terrain
        danger_level: Danger level (1-10)
        npcs: NPCs in this location
        items: Items found here
        quests: Available quests
        connections: Connected locations
        resources: Available resources
    """
    region: str = Field(..., description="Region the location is in")
    terrain_type: str = Field(..., description="Type of terrain")
    danger_level: int = Field(..., description="Danger level", ge=1, le=10)
    npcs: List[str] = Field(default_factory=list, description="NPC IDs in location")
    items: List[str] = Field(default_factory=list, description="Item IDs in location")
    quests: List[str] = Field(default_factory=list, description="Quest IDs in location")
    connections: List[str] = Field(default_factory=list, description="Connected location IDs")
    resources: List[Dict[str, Any]] = Field(default_factory=list, description="Available resources")

class Quest(BaseGameEntity):
    """Quest entity model.
    
    Attributes:
        difficulty: Quest difficulty level
        status: Current status
        prerequisites: Required quests/conditions
        objectives: Quest objectives
        rewards: Quest rewards
        giver: Quest giver NPC
        location: Quest location
        time_limit: Optional time limit
    """
    difficulty: str = Field(..., description="Quest difficulty level")
    status: str = Field(..., description="Current status")
    prerequisites: List[Dict[str, Any]] = Field(default_factory=list, description="Required quests/conditions")
    objectives: List[Dict[str, Any]] = Field(..., description="Quest objectives")
    rewards: List[Dict[str, Any]] = Field(..., description="Quest rewards")
    giver: str = Field(..., description="Quest giver NPC ID")
    location: str = Field(..., description="Quest location ID")
    time_limit: Optional[int] = Field(None, description="Time limit in minutes")

class Faction(BaseGameEntity):
    """Faction entity model.
    
    Attributes:
        faction_type: Type of faction
        status: Current status
        influence: Influence level (0-100)
        relationships: Relationships with other factions
        leaders: Faction leaders
        headquarters: Faction HQ location
        ranks: Available ranks
        perks: Faction perks
    """
    faction_type: str = Field(..., description="Type of faction")
    status: str = Field(..., description="Current status")
    influence: int = Field(..., description="Influence level", ge=0, le=100)
    relationships: Dict[str, int] = Field(default_factory=dict, description="Relationships with other factions")
    leaders: List[str] = Field(..., description="Leader NPC IDs")
    headquarters: str = Field(..., description="HQ location ID")
    ranks: List[Dict[str, Any]] = Field(..., description="Available ranks")
    perks: List[Dict[str, Any]] = Field(default_factory=list, description="Faction perks")

# Entity type to model mapping
ENTITY_MODELS = {
    EntityType.NPC: NPC,
    EntityType.ITEM: Item,
    EntityType.LOCATION: Location,
    EntityType.QUEST: Quest,
    EntityType.FACTION: Faction
}

# Field types for validation
FIELD_TYPES = {
    EntityType.NPC: {
        "level": "integer",
        "faction": "keyword",
        "location": "keyword"
    },
    EntityType.ITEM: {
        "rarity": "keyword",
        "category": "keyword",
        "level_requirement": "integer",
        "value": "integer"
    },
    EntityType.LOCATION: {
        "region": "keyword",
        "terrain_type": "keyword",
        "danger_level": "integer"
    },
    EntityType.QUEST: {
        "difficulty": "keyword",
        "status": "keyword",
        "giver": "keyword",
        "location": "keyword"
    },
    EntityType.FACTION: {
        "faction_type": "keyword",
        "status": "keyword",
        "influence": "integer",
        "headquarters": "keyword"
    }
}

class SearchResult(BaseModel):
    items: List[BaseGameEntity]
    total: int
    facets: Optional[Dict[str, List[Dict[str, Any]]]] = None

    class Config:
        from_attributes = True

class NPCModel(BaseModel):
    """Data model for NPC entities.
    
    Attributes:
        id: Unique identifier for the NPC
        name: Name of the NPC
        description: Detailed description of the NPC
        personality_traits: List of personality traits with values
        faction: The faction this NPC belongs to
        level: The NPC's level
        location: Current location of the NPC
        tags: List of tags associated with the NPC
        created_at: Timestamp when the NPC was created
        updated_at: Timestamp when the NPC was last updated
    """
    id: str = Field(..., description="Unique identifier for the NPC")
    name: str = Field(..., min_length=1, description="Name of the NPC")
    description: str = Field(..., min_length=10, description="Detailed description of the NPC")
    personality_traits: List[Dict[str, Any]] = Field(
        ..., 
        description="List of personality traits with values"
    )
    faction: str = Field(..., description="The faction this NPC belongs to")
    level: int = Field(..., ge=1, description="The NPC's level")
    location: str = Field(..., description="Current location of the NPC")
    tags: List[str] = Field(default_factory=list, description="List of tags associated with the NPC")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('personality_traits')
    def validate_personality_traits(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validates personality traits structure."""
        for trait in v:
            if not isinstance(trait, dict):
                raise EntityValidationError("Personality trait must be a dictionary")
            if 'trait' not in trait or 'value' not in trait:
                raise EntityValidationError("Personality trait must have 'trait' and 'value' keys")
            if not isinstance(trait['value'], int):
                raise EntityValidationError("Personality trait value must be an integer")
        return v

class NPC(SearchableEntity[NPCModel]):
    """NPC entity implementation for search functionality.
    
    Provides mapping configuration and conversion methods for NPC entities.
    """
    
    def __init__(self):
        """Initialize NPC entity with search mapping configuration."""
        super().__init__(
            entity_type=EntityType.NPC,
            mapping=EntityMapping(
                mappings={
                    "properties": {
                        "id": {"type": "keyword"},
                        "name": {
                            "type": "text",
                            "analyzer": "game_analyzer",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            }
                        },
                        "description": {
                            "type": "text",
                            "analyzer": "game_analyzer"
                        },
                        "personality_traits": {
                            "type": "nested",
                            "properties": {
                                "trait": {"type": "keyword"},
                                "value": {"type": "integer"}
                            }
                        },
                        "faction": {"type": "keyword"},
                        "level": {"type": "integer"},
                        "location": {"type": "keyword"},
                        "tags": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                },
                facets=[
                    FacetConfig(
                        name="faction",
                        field="faction",
                        type=FacetType.TERMS,
                        display_name="Faction",
                        size=20
                    ),
                    FacetConfig(
                        name="level",
                        field="level",
                        type=FacetType.RANGE,
                        display_name="Level",
                        ranges=[
                            {"to": 10, "key": "Novice"},
                            {"from": 10, "to": 20, "key": "Intermediate"},
                            {"from": 20, "to": 30, "key": "Advanced"},
                            {"from": 30, "key": "Expert"}
                        ]
                    ),
                    FacetConfig(
                        name="location",
                        field="location",
                        type=FacetType.TERMS,
                        display_name="Location",
                        size=20
                    ),
                    FacetConfig(
                        name="personality",
                        field="personality_traits.trait",
                        type=FacetType.NESTED,
                        display_name="Personality Traits",
                        nested_path="personality_traits",
                        size=10
                    ),
                    FacetConfig(
                        name="tags",
                        field="tags",
                        type=FacetType.TERMS,
                        display_name="Tags",
                        size=20
                    )
                ]
            ),
            model_cls=NPCModel
        )

    def to_doc(self, instance: NPCModel) -> Dict[str, Any]:
        """Convert NPC instance to search document.
        
        Args:
            instance: The NPC model instance to convert
            
        Returns:
            A dictionary representation suitable for search indexing
        """
        return instance.model_dump()

    def from_doc(self, doc: Dict[str, Any]) -> NPCModel:
        """Create NPC instance from search document.
        
        Args:
            doc: The search document to convert
            
        Returns:
            An NPCModel instance
            
        Raises:
            EntityValidationError: If the document is invalid
        """
        try:
            return NPCModel(**doc)
        except Exception as e:
            raise EntityValidationError(f"Failed to create NPC from document: {str(e)}")

class ItemModel(BaseModel):
    """Data model for Item entities.
    
    Attributes:
        id: Unique identifier for the item
        name: Name of the item
        description: Detailed description of the item
        rarity: Rarity level of the item
        category: Category the item belongs to
        level_requirement: Required level to use the item
        stats: Dictionary of item statistics
        tags: List of tags associated with the item
        created_at: Timestamp when the item was created
        updated_at: Timestamp when the item was last updated
    """
    id: str = Field(..., description="Unique identifier for the item")
    name: str = Field(..., min_length=1, description="Name of the item")
    description: str = Field(..., min_length=10, description="Detailed description of the item")
    rarity: str = Field(..., description="Rarity level of the item")
    category: str = Field(..., description="Category the item belongs to")
    level_requirement: int = Field(..., ge=0, description="Required level to use the item")
    stats: Dict[str, float] = Field(..., description="Dictionary of item statistics")
    tags: List[str] = Field(default_factory=list, description="List of tags associated with the item")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('stats')
    def validate_stats(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validates item statistics."""
        valid_stats = {'damage', 'defense', 'speed'}
        invalid_stats = set(v.keys()) - valid_stats
        if invalid_stats:
            raise EntityValidationError(f"Invalid stats found: {invalid_stats}. Valid stats are: {valid_stats}")
        return v

class Item(SearchableEntity[ItemModel]):
    """Item entity implementation for search functionality.
    
    Provides mapping configuration and conversion methods for Item entities.
    """
    
    def __init__(self):
        """Initialize Item entity with search mapping configuration."""
        super().__init__(
            entity_type=EntityType.ITEM,
            mapping=EntityMapping(
                mappings={
                    "properties": {
                        "id": {"type": "keyword"},
                        "name": {
                            "type": "text",
                            "analyzer": "game_analyzer",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            }
                        },
                        "description": {
                            "type": "text",
                            "analyzer": "game_analyzer"
                        },
                        "rarity": {"type": "keyword"},
                        "category": {"type": "keyword"},
                        "level_requirement": {"type": "integer"},
                        "stats": {
                            "type": "object",
                            "properties": {
                                "damage": {"type": "float"},
                                "defense": {"type": "float"},
                                "speed": {"type": "float"}
                            }
                        },
                        "tags": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                },
                facets=[
                    FacetConfig(
                        name="rarity",
                        field="rarity",
                        type=FacetType.TERMS,
                        display_name="Rarity",
                        size=10
                    ),
                    FacetConfig(
                        name="category",
                        field="category",
                        type=FacetType.TERMS,
                        display_name="Category",
                        size=20
                    ),
                    FacetConfig(
                        name="level_requirement",
                        field="level_requirement",
                        type=FacetType.RANGE,
                        display_name="Level Requirement",
                        ranges=[
                            {"to": 10, "key": "Beginner"},
                            {"from": 10, "to": 20, "key": "Intermediate"},
                            {"from": 20, "to": 30, "key": "Advanced"},
                            {"from": 30, "key": "Expert"}
                        ]
                    ),
                    FacetConfig(
                        name="tags",
                        field="tags",
                        type=FacetType.TERMS,
                        display_name="Tags",
                        size=20
                    )
                ]
            ),
            model_cls=ItemModel
        )

    def to_doc(self, instance: ItemModel) -> Dict[str, Any]:
        """Convert Item instance to search document.
        
        Args:
            instance: The Item model instance to convert
            
        Returns:
            A dictionary representation suitable for search indexing
        """
        return instance.model_dump()

    def from_doc(self, doc: Dict[str, Any]) -> ItemModel:
        """Create Item instance from search document.
        
        Args:
            doc: The search document to convert
            
        Returns:
            An ItemModel instance
            
        Raises:
            EntityValidationError: If the document is invalid
        """
        try:
            return ItemModel(**doc)
        except Exception as e:
            raise EntityValidationError(f"Failed to create Item from document: {str(e)}")

class LocationModel(BaseModel):
    """Data model for Location entities.
    
    Attributes:
        id: Unique identifier for the location
        name: Name of the location
        description: Detailed description of the location
        region: Region the location belongs to
        terrain_type: Type of terrain at the location
        danger_level: Danger level of the location (1-10)
        connected_locations: List of connected location IDs
        tags: List of tags associated with the location
        created_at: Timestamp when the location was created
        updated_at: Timestamp when the location was last updated
    """
    id: str = Field(..., description="Unique identifier for the location")
    name: str = Field(..., min_length=1, description="Name of the location")
    description: str = Field(..., min_length=10, description="Detailed description of the location")
    region: str = Field(..., description="Region the location belongs to")
    terrain_type: str = Field(..., description="Type of terrain at the location")
    danger_level: int = Field(..., ge=1, le=10, description="Danger level of the location (1-10)")
    connected_locations: List[str] = Field(..., description="List of connected location IDs")
    tags: List[str] = Field(default_factory=list, description="List of tags associated with the location")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('connected_locations')
    def validate_connected_locations(cls, v: List[str]) -> List[str]:
        """Validates connected location IDs."""
        if len(set(v)) != len(v):
            raise EntityValidationError("Duplicate location IDs found in connected_locations")
        return v

class Location(SearchableEntity[LocationModel]):
    """Location entity implementation for search functionality.
    
    Provides mapping configuration and conversion methods for Location entities.
    """
    
    def __init__(self):
        """Initialize Location entity with search mapping configuration."""
        super().__init__(
            entity_type=EntityType.LOCATION,
            mapping=EntityMapping(
                mappings={
                    "properties": {
                        "id": {"type": "keyword"},
                        "name": {
                            "type": "text",
                            "analyzer": "game_analyzer",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            }
                        },
                        "description": {
                            "type": "text",
                            "analyzer": "game_analyzer"
                        },
                        "region": {"type": "keyword"},
                        "terrain_type": {"type": "keyword"},
                        "danger_level": {"type": "integer"},
                        "connected_locations": {"type": "keyword"},
                        "tags": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                },
                facets=[
                    FacetConfig(
                        name="region",
                        field="region",
                        type=FacetType.TERMS,
                        display_name="Region",
                        size=20
                    ),
                    FacetConfig(
                        name="terrain_type",
                        field="terrain_type",
                        type=FacetType.TERMS,
                        display_name="Terrain Type",
                        size=20
                    ),
                    FacetConfig(
                        name="danger_level",
                        field="danger_level",
                        type=FacetType.RANGE,
                        display_name="Danger Level",
                        ranges=[
                            {"to": 3, "key": "Safe"},
                            {"from": 3, "to": 6, "key": "Moderate"},
                            {"from": 6, "to": 8, "key": "Dangerous"},
                            {"from": 8, "key": "Deadly"}
                        ]
                    ),
                    FacetConfig(
                        name="tags",
                        field="tags",
                        type=FacetType.TERMS,
                        display_name="Tags",
                        size=20
                    )
                ]
            ),
            model_cls=LocationModel
        )

    def to_doc(self, instance: LocationModel) -> Dict[str, Any]:
        """Convert Location instance to search document.
        
        Args:
            instance: The Location model instance to convert
            
        Returns:
            A dictionary representation suitable for search indexing
        """
        return instance.model_dump()

    def from_doc(self, doc: Dict[str, Any]) -> LocationModel:
        """Create Location instance from search document.
        
        Args:
            doc: The search document to convert
            
        Returns:
            A LocationModel instance
            
        Raises:
            EntityValidationError: If the document is invalid
        """
        try:
            return LocationModel(**doc)
        except Exception as e:
            raise EntityValidationError(f"Failed to create Location from document: {str(e)}")

class QuestModel(BaseModel):
    """Data model for Quest entities.
    
    Attributes:
        id: Unique identifier for the quest
        name: Name of the quest
        description: Detailed description of the quest
        difficulty: Difficulty level of the quest
        level_range: Dictionary with min and max level requirements
        rewards: List of quest rewards
        status: Current status of the quest
        tags: List of tags associated with the quest
        created_at: Timestamp when the quest was created
        updated_at: Timestamp when the quest was last updated
    """
    id: str = Field(..., description="Unique identifier for the quest")
    name: str = Field(..., min_length=1, description="Name of the quest")
    description: str = Field(..., min_length=10, description="Detailed description of the quest")
    difficulty: str = Field(..., description="Difficulty level of the quest")
    level_range: Dict[str, int] = Field(..., description="Dictionary with min and max level requirements")
    rewards: List[Dict[str, Any]] = Field(..., description="List of quest rewards")
    status: str = Field(..., description="Current status of the quest")
    tags: List[str] = Field(default_factory=list, description="List of tags associated with the quest")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('level_range')
    def validate_level_range(cls, v: Dict[str, int]) -> Dict[str, int]:
        """Validates level range configuration."""
        if 'min' not in v or 'max' not in v:
            raise EntityValidationError("Level range must have 'min' and 'max' keys")
        if v['min'] > v['max']:
            raise EntityValidationError("Minimum level cannot be greater than maximum level")
        if v['min'] < 1:
            raise EntityValidationError("Minimum level cannot be less than 1")
        return v

    @validator('rewards')
    def validate_rewards(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validates quest rewards structure."""
        for reward in v:
            if not isinstance(reward, dict):
                raise EntityValidationError("Reward must be a dictionary")
            if 'type' not in reward or 'value' not in reward:
                raise EntityValidationError("Reward must have 'type' and 'value' keys")
            if not isinstance(reward['value'], (int, float)):
                raise EntityValidationError("Reward value must be a number")
        return v

class Quest(SearchableEntity[QuestModel]):
    """Quest entity implementation for search functionality.
    
    Provides mapping configuration and conversion methods for Quest entities.
    """
    
    def __init__(self):
        """Initialize Quest entity with search mapping configuration."""
        super().__init__(
            entity_type=EntityType.QUEST,
            mapping=EntityMapping(
                mappings={
                    "properties": {
                        "id": {"type": "keyword"},
                        "name": {
                            "type": "text",
                            "analyzer": "game_analyzer",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            }
                        },
                        "description": {
                            "type": "text",
                            "analyzer": "game_analyzer"
                        },
                        "difficulty": {"type": "keyword"},
                        "level_range": {
                            "type": "object",
                            "properties": {
                                "min": {"type": "integer"},
                                "max": {"type": "integer"}
                            }
                        },
                        "rewards": {
                            "type": "nested",
                            "properties": {
                                "type": {"type": "keyword"},
                                "value": {"type": "float"}
                            }
                        },
                        "status": {"type": "keyword"},
                        "tags": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                },
                facets=[
                    FacetConfig(
                        name="difficulty",
                        field="difficulty",
                        type=FacetType.TERMS,
                        display_name="Difficulty",
                        size=10
                    ),
                    FacetConfig(
                        name="level_range",
                        field="level_range.min",
                        type=FacetType.RANGE,
                        display_name="Level Range",
                        ranges=[
                            {"to": 10, "key": "Beginner"},
                            {"from": 10, "to": 20, "key": "Intermediate"},
                            {"from": 20, "to": 30, "key": "Advanced"},
                            {"from": 30, "key": "Expert"}
                        ]
                    ),
                    FacetConfig(
                        name="rewards",
                        field="rewards.type",
                        type=FacetType.NESTED,
                        display_name="Reward Types",
                        nested_path="rewards",
                        size=10
                    ),
                    FacetConfig(
                        name="status",
                        field="status",
                        type=FacetType.TERMS,
                        display_name="Status",
                        size=10
                    ),
                    FacetConfig(
                        name="tags",
                        field="tags",
                        type=FacetType.TERMS,
                        display_name="Tags",
                        size=20
                    )
                ]
            ),
            model_cls=QuestModel
        )

    def to_doc(self, instance: QuestModel) -> Dict[str, Any]:
        """Convert Quest instance to search document.
        
        Args:
            instance: The Quest model instance to convert
            
        Returns:
            A dictionary representation suitable for search indexing
        """
        return instance.model_dump()

    def from_doc(self, doc: Dict[str, Any]) -> QuestModel:
        """Create Quest instance from search document.
        
        Args:
            doc: The search document to convert
            
        Returns:
            A QuestModel instance
            
        Raises:
            EntityValidationError: If the document is invalid
        """
        try:
            return QuestModel(**doc)
        except Exception as e:
            raise EntityValidationError(f"Failed to create Quest from document: {str(e)}")

class FactionModel(BaseModel):
    """Data model for Faction entities.
    
    Attributes:
        id: Unique identifier for the faction
        name: Name of the faction
        description: Detailed description of the faction
        faction_type: Type of faction (kingdom, guild, etc.)
        status: Current status of the faction
        influence: Global influence score (0-100)
        resources: Dictionary of resource quantities
        territory: Territory control data
        traits: Faction characteristics
        tags: List of tags associated with the faction
        created_at: Timestamp when the faction was created
        updated_at: Timestamp when the faction was last updated
    """
    id: str = Field(..., description="Unique identifier for the faction")
    name: str = Field(..., min_length=1, description="Name of the faction")
    description: str = Field(..., min_length=10, description="Detailed description of the faction")
    faction_type: str = Field(..., description="Type of faction (kingdom, guild, etc.)")
    status: str = Field(..., description="Current status of the faction")
    influence: float = Field(..., ge=0.0, le=100.0, description="Global influence score (0-100)")
    resources: Dict[str, Any] = Field(default_factory=dict, description="Dictionary of resource quantities")
    territory: Dict[str, Any] = Field(default_factory=dict, description="Territory control data")
    traits: Dict[str, Any] = Field(default_factory=dict, description="Faction characteristics")
    tags: List[str] = Field(default_factory=list, description="List of tags associated with the faction")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('faction_type')
    def validate_faction_type(cls, v: str) -> str:
        """Validates faction type."""
        valid_types = {'kingdom', 'guild', 'tribe', 'religion', 'merchant', 'criminal', 'other'}
        if v.lower() not in valid_types:
            raise EntityValidationError(f"Invalid faction type: {v}. Valid types are: {valid_types}")
        return v.lower()

    @validator('status')
    def validate_status(cls, v: str) -> str:
        """Validates faction status."""
        valid_statuses = {'active', 'inactive', 'hidden', 'destroyed'}
        if v.lower() not in valid_statuses:
            raise EntityValidationError(f"Invalid faction status: {v}. Valid statuses are: {valid_statuses}")
        return v.lower()

class Faction(SearchableEntity[FactionModel]):
    """Faction entity implementation for search functionality.
    
    Provides mapping configuration and conversion methods for Faction entities.
    """
    
    def __init__(self):
        """Initialize Faction entity with search mapping configuration."""
        super().__init__(
            entity_type=EntityType.FACTION,
            mapping=EntityMapping(
                mappings={
                    "properties": {
                        "id": {"type": "keyword"},
                        "name": {
                            "type": "text",
                            "analyzer": "game_analyzer",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            }
                        },
                        "description": {
                            "type": "text",
                            "analyzer": "game_analyzer"
                        },
                        "faction_type": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "influence": {"type": "float"},
                        "resources": {
                            "type": "object",
                            "enabled": True
                        },
                        "territory": {
                            "type": "object",
                            "enabled": True
                        },
                        "traits": {
                            "type": "object",
                            "enabled": True
                        },
                        "tags": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                },
                facets=[
                    FacetConfig(
                        name="faction_type",
                        field="faction_type",
                        type=FacetType.TERMS,
                        display_name="Faction Type",
                        size=10
                    ),
                    FacetConfig(
                        name="status",
                        field="status",
                        type=FacetType.TERMS,
                        display_name="Status",
                        size=5
                    ),
                    FacetConfig(
                        name="influence",
                        field="influence",
                        type=FacetType.RANGE,
                        display_name="Influence",
                        ranges=[
                            {"to": 25, "key": "Minor"},
                            {"from": 25, "to": 50, "key": "Notable"},
                            {"from": 50, "to": 75, "key": "Major"},
                            {"from": 75, "key": "Dominant"}
                        ]
                    ),
                    FacetConfig(
                        name="tags",
                        field="tags",
                        type=FacetType.TERMS,
                        display_name="Tags",
                        size=20
                    )
                ]
            ),
            model_cls=FactionModel
        )

    def to_doc(self, instance: FactionModel) -> Dict[str, Any]:
        """Convert Faction instance to search document.
        
        Args:
            instance: The Faction model instance to convert
            
        Returns:
            A dictionary representation suitable for search indexing
        """
        return instance.model_dump()

    def from_doc(self, doc: Dict[str, Any]) -> FactionModel:
        """Create Faction instance from search document.
        
        Args:
            doc: The search document to convert
            
        Returns:
            A FactionModel instance
            
        Raises:
            EntityValidationError: If the document is invalid
        """
        try:
            return FactionModel(**doc)
        except Exception as e:
            raise EntityValidationError(f"Failed to create Faction from document: {str(e)}") 