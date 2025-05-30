"""
Core type definitions for the World State system.

This module defines all enums and types used throughout the World State system,
including change types, regions, categories, and data models.
"""
from typing import Dict, List, Optional, Any, Union, Set
from enum import Enum, auto
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid

class StateChangeType(Enum):
    """Types of state changes that can occur."""
    CREATED = auto()
    UPDATED = auto()
    DELETED = auto()
    MERGED = auto()
    CALCULATED = auto()

class WorldRegion(Enum):
    """Represents major world regions for state organization."""
    GLOBAL = auto()  # Global state affecting the entire world
    NORTHERN = auto()
    SOUTHERN = auto()
    EASTERN = auto()
    WESTERN = auto()
    CENTRAL = auto()

class StateCategory(Enum):
    """Categories for organizing state data."""
    POLITICAL = auto()
    ECONOMIC = auto()
    MILITARY = auto()
    SOCIAL = auto()
    ENVIRONMENTAL = auto()
    RELIGIOUS = auto()
    MAGICAL = auto()
    QUEST = auto()
    OTHER = auto()

class LocationType(Enum):
    """Types of locations in the world."""
    CITY = auto()
    VILLAGE = auto()
    DUNGEON = auto()
    WILDERNESS = auto()
    LANDMARK = auto()
    RUINS = auto()
    OUTPOST = auto()

class ResourceType(Enum):
    """Types of resources that can be found or produced."""
    GOLD = auto()
    FOOD = auto()
    TIMBER = auto()
    STONE = auto()
    ORE = auto()
    MAGIC = auto()
    POPULATION = auto()

class WorldStateChangeCustomData(BaseModel):
    """Custom data for specific types of world state changes."""
    custom_field: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class WorldStateChange(BaseModel):
    """
    Represents a change to the world state.
    
    Used for tracking historical changes and for applying batched changes.
    """
    id: str
    type: str  # e.g., "resource", "territory", "influence"
    location: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    old_value: Optional[Any] = None
    new_value: Any
    custom_data: Optional[WorldStateChangeCustomData] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class ActiveEffect(BaseModel):
    """An active effect on a state variable."""
    id: str
    type: str
    value: Any
    source: str
    expires_at: Optional[datetime] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class WorldState(BaseModel):
    """
    Top-level container for all world state.
    
    Acts as a convenient wrapper around all aspects of world state.
    """
    regions: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    factions: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    npcs: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    active_events: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

# State Change Record for history tracking
class StateChangeRecord(BaseModel):
    """
    Record of a change made to a state variable.
    
    This provides historical tracking of all changes for analysis,
    rollback capability, and narrative continuity.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    state_key: str
    old_value: Optional[Any] = None
    new_value: Any
    change_type: StateChangeType
    change_reason: Optional[str] = None
    entity_id: Optional[str] = None  # ID of entity that caused the change, if applicable
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class StateVariable(BaseModel):
    """
    A single state variable tracked in the world state.
    
    State variables have metadata to help with organization,
    querying, and semantic understanding of the data.
    """
    key: str
    value: Any
    category: StateCategory = StateCategory.OTHER
    region: WorldRegion = WorldRegion.GLOBAL
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    change_history: List[StateChangeRecord] = Field(default_factory=list)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __str__(self) -> str:
        """String representation of the state variable."""
        return f"{self.key}={self.value} ({self.category.value}, {self.region.value})" 