"""
World State Types and Models

This module defines the core types and data structures for the world state system.
Updated to fix enum serialization issues and align with JSON schema requirements.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4


class StateChangeType(Enum):
    """Types of state changes that can occur."""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    MERGED = "merged"
    CALCULATED = "calculated"
    
    def __str__(self):
        return self.value


class WorldRegion(Enum):
    """Represents major world regions for state organization."""
    GLOBAL = "global"
    NORTHERN = "northern"
    SOUTHERN = "southern"
    EASTERN = "eastern"
    WESTERN = "western"
    CENTRAL = "central"
    
    def __str__(self):
        return self.value


class StateCategory(Enum):
    """Categories for organizing state data."""
    POLITICAL = "political"
    ECONOMIC = "economic"
    MILITARY = "military"
    SOCIAL = "social"
    ENVIRONMENTAL = "environmental"
    RELIGIOUS = "religious"
    MAGICAL = "magical"
    QUEST = "quest"
    OTHER = "other"
    
    def __str__(self):
        return self.value


class LocationType(Enum):
    """Types of locations in the world."""
    CITY = "city"
    TOWN = "town"
    VILLAGE = "village"
    CASTLE = "castle"
    DUNGEON = "dungeon"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    DESERT = "desert"
    OCEAN = "ocean"
    PLAIN = "plain"
    
    def __str__(self):
        return self.value


class ResourceType(Enum):
    """Types of resources in the world."""
    GOLD = "gold"
    FOOD = "food"
    WOOD = "wood"
    STONE = "stone"
    IRON = "iron"
    MAGIC = "magic"
    POPULATION = "population"
    
    def __str__(self):
        return self.value


class ActiveEffect(BaseModel):
    """Represents an active effect in the world state."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: Optional[str] = None
    effect_type: str
    target: str
    magnitude: float = 1.0
    duration: Optional[int] = None  # in game time units
    started_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    source: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('effect_type')
    def validate_effect_type(cls, v):
        """Validate effect type against JSON schema"""
        valid_types = ['buff', 'debuff', 'environmental', 'quest', 'event']
        if v not in valid_types:
            raise ValueError(f"Effect type must be one of {valid_types}")
        return v


class WorldStateChangeCustomData(BaseModel):
    """Custom data for world state changes."""
    change_source: Optional[str] = None
    affected_systems: List[str] = Field(default_factory=list)
    rollback_data: Optional[Dict[str, Any]] = None
    validation_rules: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorldStateChange(BaseModel):
    """Represents a change to the world state."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    change_type: StateChangeType
    state_key: str
    old_value: Optional[Any] = None
    new_value: Any
    region: WorldRegion = WorldRegion.GLOBAL
    category: StateCategory = StateCategory.OTHER
    entity_id: Optional[str] = None
    reason: Optional[str] = None
    custom_data: Optional[WorldStateChangeCustomData] = None
    
    class Config:
        use_enum_values = True  # Ensures enums are serialized as their values
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            StateChangeType: lambda v: v.value,
            WorldRegion: lambda v: v.value,
            StateCategory: lambda v: v.value
        }
    
    @validator('state_key')
    def validate_state_key(cls, v):
        """Ensure state key is not empty"""
        if not v or not v.strip():
            raise ValueError("State key cannot be empty")
        return v.strip()
    
    @validator('reason')
    def validate_reason_length(cls, v):
        """Validate reason length as per JSON schema"""
        if v and len(v) > 500:
            raise ValueError("Reason cannot exceed 500 characters")
        return v


class WorldState(BaseModel):
    """
    Main world state model containing all world data.
    Updated to align with JSON schema requirements.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = "Default World"
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Time and Calendar
    current_time: datetime = Field(default_factory=datetime.utcnow)
    game_day: int = 1
    season: str = "spring"
    year: int = 1
    
    # Global State Variables
    state_variables: Dict[str, Any] = Field(default_factory=dict)
    
    # Regional Data
    regions: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Resources
    global_resources: Dict[ResourceType, float] = Field(default_factory=dict)
    regional_resources: Dict[str, Dict[ResourceType, float]] = Field(default_factory=dict)
    
    # Politics and Factions
    faction_relations: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    territorial_control: Dict[str, str] = Field(default_factory=dict)  # region -> faction_id
    
    # Active Effects
    active_effects: List[ActiveEffect] = Field(default_factory=list)
    
    # Events and History
    recent_events: List[Dict[str, Any]] = Field(default_factory=list)
    change_history: List[WorldStateChange] = Field(default_factory=list)
    
    # Environment
    weather: Dict[str, Any] = Field(default_factory=dict)
    environmental_conditions: Dict[str, Any] = Field(default_factory=dict)
    
    # Configuration
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ResourceType: lambda v: v.value,
            StateChangeType: lambda v: v.value,
            WorldRegion: lambda v: v.value,
            StateCategory: lambda v: v.value
        }
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name length as per JSON schema"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Name cannot be empty")
        if len(v) > 100:
            raise ValueError("Name cannot exceed 100 characters")
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        """Validate description length as per JSON schema"""
        if v and len(v) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")
        return v
    
    @validator('game_day')
    def validate_game_day(cls, v):
        """Game day must be positive"""
        if v < 1:
            raise ValueError("Game day must be at least 1")
        return v
    
    @validator('year')
    def validate_year(cls, v):
        """Year must be positive"""
        if v < 1:
            raise ValueError("Year must be at least 1")
        return v
    
    @validator('season')
    def validate_season(cls, v):
        """Validate season against JSON schema"""
        valid_seasons = ['spring', 'summer', 'autumn', 'winter']
        if v not in valid_seasons:
            raise ValueError(f"Season must be one of {valid_seasons}")
        return v
    
    @validator('state_variables')
    def validate_state_variables(cls, v):
        """Apply business rules to state variables"""
        for key, value in v.items():
            # Population values must be non-negative
            if 'population' in key.lower() and isinstance(value, (int, float)) and value < 0:
                raise ValueError(f"Population values cannot be negative: {key} = {value}")
            
            # Resource values must be within limits
            if 'resource' in key.lower() and isinstance(value, (int, float)):
                if value < 0:
                    raise ValueError(f"Resource values cannot be negative: {key} = {value}")
                if value > 1000000:
                    raise ValueError(f"Resource values cannot exceed 1,000,000: {key} = {value}")
        
        return v
    
    @validator('global_resources', 'regional_resources')
    def validate_resources(cls, v):
        """Validate resource values are non-negative"""
        if isinstance(v, dict):
            for region_or_type, resources in v.items():
                if isinstance(resources, dict):
                    for resource, amount in resources.items():
                        if isinstance(amount, (int, float)) and amount < 0:
                            raise ValueError(f"Resource amounts cannot be negative: {resource} = {amount}")
                elif isinstance(resources, (int, float)) and resources < 0:
                    raise ValueError(f"Resource amounts cannot be negative: {region_or_type} = {resources}")
        return v
    
    def get_state_variable(self, key: str, default: Any = None) -> Any:
        """Get a state variable by key."""
        return self.state_variables.get(key, default)
    
    def set_state_variable(self, key: str, value: Any) -> None:
        """Set a state variable."""
        self.state_variables[key] = value
        self.updated_at = datetime.utcnow()
    
    def add_active_effect(self, effect: ActiveEffect) -> None:
        """Add an active effect to the world state."""
        self.active_effects.append(effect)
        self.updated_at = datetime.utcnow()
    
    def remove_expired_effects(self) -> List[ActiveEffect]:
        """Remove and return expired effects."""
        now = datetime.utcnow()
        expired = [e for e in self.active_effects if e.expires_at and e.expires_at <= now]
        self.active_effects = [e for e in self.active_effects if e not in expired]
        if expired:
            self.updated_at = datetime.utcnow()
        return expired
    
    def dict(self, **kwargs) -> Dict[str, Any]:
        """Override dict method to ensure proper enum serialization"""
        data = super().dict(**kwargs)
        
        # Ensure enums are properly serialized as strings
        def convert_enums(obj):
            if isinstance(obj, dict):
                return {k: convert_enums(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_enums(v) for v in obj]
            elif isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        
        return convert_enums(data)


# Export all types
__all__ = [
    "StateChangeType",
    "WorldRegion", 
    "StateCategory",
    "LocationType",
    "ResourceType",
    "ActiveEffect",
    "WorldStateChangeCustomData",
    "WorldStateChange",
    "WorldState"
] 