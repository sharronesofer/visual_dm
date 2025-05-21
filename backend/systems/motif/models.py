from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import uuid4

class MotifScope(str, Enum):
    """Defines the scope/reach of a motif in the world."""
    GLOBAL = "global"  # Affects the entire world
    REGIONAL = "regional"  # Affects a specific region
    LOCAL = "local"  # Affects a specific location/POI

class MotifLifecycle(str, Enum):
    """Defines the lifecycle state of a motif."""
    EMERGING = "emerging"  # Growing in strength
    STABLE = "stable"  # At full strength
    WANING = "waning"  # Decreasing in strength
    DORMANT = "dormant"  # Inactive but can re-emerge

class MotifCategory(str, Enum):
    """Categorizes motifs by their narrative impact."""
    ASCENSION = "ascension"
    BETRAYAL = "betrayal"
    CHAOS = "chaos"
    COLLAPSE = "collapse"
    COMPULSION = "compulsion"
    CONTROL = "control"
    DEATH = "death"
    DECEPTION = "deception"
    DEFIANCE = "defiance"
    DESIRE = "desire"
    DESTINY = "destiny"
    ECHO = "echo"
    EXPANSION = "expansion"
    FAITH = "faith"
    FEAR = "fear"
    FUTILITY = "futility"
    GRIEF = "grief"
    GUILT = "guilt"
    HOPE = "hope"
    HUNGER = "hunger"
    INNOCENCE = "innocence"
    INVENTION = "invention"
    ISOLATION = "isolation"
    JUSTICE = "justice"
    LOYALTY = "loyalty"
    MADNESS = "madness"
    OBSESSION = "obsession"
    PARANOIA = "paranoia"
    POWER = "power"
    PRIDE = "pride"
    PROTECTION = "protection"
    REBIRTH = "rebirth"
    REDEMPTION = "redemption"
    REGRET = "regret"
    REVELATION = "revelation"
    RUIN = "ruin"
    SACRIFICE = "sacrifice"
    SILENCE = "silence"
    SHADOW = "shadow"
    STAGNATION = "stagnation"
    TEMPTATION = "temptation"
    TIME = "time"
    TRANSFORMATION = "transformation"
    TRUTH = "truth"
    UNITY = "unity"
    VENGEANCE = "vengeance"
    WORSHIP = "worship"

class LocationInfo(BaseModel):
    """Defines the location information for a motif."""
    region_id: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    radius: float = 0.0  # Influence radius

class MotifEffectTarget(str, Enum):
    NPC = "npc"                   # Affects NPC behavior, dialogue, etc.
    EVENT = "event"               # Influences event generation and frequency
    QUEST = "quest"               # Modifies quest/arc generation and outcomes
    FACTION = "faction"           # Adjusts faction relationships and tension
    ENVIRONMENT = "environment"   # Alters weather patterns, ambient effects
    ECONOMY = "economy"           # Impacts economic factors like prices, resource availability
    NARRATIVE = "narrative"       # Provides context for narrative generation
    CUSTOM = "custom"             # Custom effect type

class MotifEffect(BaseModel):
    """Model for a specific effect a motif has on game systems"""
    target: MotifEffectTarget
    intensity: int = Field(1, ge=1, le=10)  # Strength of effect from 1-10
    description: str
    parameters: Optional[Dict[str, Any]] = None  # Additional parameters for the effect

class Motif(BaseModel):
    """Represents a narrative motif in the game world."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    category: MotifCategory
    scope: MotifScope
    lifecycle: MotifLifecycle = MotifLifecycle.EMERGING
    intensity: int = Field(5, ge=1, le=10)  # 1-10 scale
    
    # Duration and timing
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_days: int = 14  # Default duration in days
    
    # Location data for regional/local motifs
    location: Optional[LocationInfo] = None
    
    # Effects
    effects: List[MotifEffect] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # New fields for enhanced narrative integration
    tone: str = Field(default="neutral")
    narrative_direction: str = Field(default="steady")
    descriptors: List[str] = Field(default_factory=list)  # Key descriptive words
    
    # Optional fields for advanced synthesis
    associated_elements: List[str] = Field(default_factory=list)  # Elements associated with this motif
    opposing_themes: List[str] = Field(default_factory=list)  # Themes that conflict with this motif
    
    # Context for narrative generation
    narrative_guidance: Optional[str] = None  # Optional guidance for narrative/GPT systems
    
    # Tags for categorization and filtering
    tags: List[str] = Field(default_factory=list)

    def update_lifecycle(self, new_lifecycle: MotifLifecycle):
        """Update the lifecycle of the motif"""
        self.lifecycle = new_lifecycle
        self.updated_at = datetime.utcnow()
        return self

    def as_dict(self) -> Dict:
        """Convert the motif to a dictionary"""
        return self.dict()
    
    @validator('effects', pre=True, each_item=False)
    def ensure_effects_list(cls, v):
        if v is None:
            return []
        return v
    
    @validator('descriptors', pre=True, each_item=False)
    def ensure_descriptors_list(cls, v):
        if v is None:
            return []
        return v
    
    @validator('tags', pre=True, each_item=False)
    def ensure_tags_list(cls, v):
        if v is None:
            return []
        return v
    
    @validator('intensity')
    def validate_intensity(cls, v):
        return max(1, min(10, v))  # Clamp between 1-10

class MotifCreate(BaseModel):
    """Schema for creating a new motif."""
    name: str
    description: str
    category: MotifCategory
    scope: MotifScope
    lifecycle: MotifLifecycle = MotifLifecycle.EMERGING
    intensity: int = Field(5, ge=1, le=10)
    duration_days: int = 14
    location: Optional[LocationInfo] = None
    effects: List[MotifEffect] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MotifUpdate(BaseModel):
    """Schema for updating an existing motif."""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[MotifCategory] = None
    scope: Optional[MotifScope] = None
    lifecycle: Optional[MotifLifecycle] = None
    intensity: Optional[int] = None
    duration_days: Optional[int] = None
    location: Optional[LocationInfo] = None
    effects: Optional[List[MotifEffect]] = None
    metadata: Optional[Dict[str, Any]] = None

class MotifFilter(BaseModel):
    """Schema for filtering motifs."""
    category: Optional[Union[MotifCategory, List[MotifCategory]]] = None
    scope: Optional[Union[MotifScope, List[MotifScope]]] = None
    lifecycle: Optional[Union[MotifLifecycle, List[MotifLifecycle]]] = None
    min_intensity: Optional[int] = None
    max_intensity: Optional[int] = None
    region_id: Optional[str] = None
    effect_type: Optional[str] = None
    active_only: bool = True  # Only include non-dormant motifs
    ids: Optional[List[str]] = None
    themes: Optional[List[str]] = None
    region_ids: Optional[List[str]] = None
    is_global: Optional[bool] = None
    
    # New fields for advanced filtering
    metadata: Optional[Dict[str, Any]] = None  # Filter by metadata key-value pairs
    tags: Optional[List[str]] = None  # Filter by tags
    created_after: Optional[datetime] = None  # Filter by creation time
    created_before: Optional[datetime] = None  # Filter by creation time
    updated_after: Optional[datetime] = None  # Filter by last update time
    updated_before: Optional[datetime] = None  # Filter by last update time
    
    # Sorting options
    sort_by: Optional[str] = None  # Field to sort by
    sort_order: Optional[str] = "asc"  # "asc" or "desc"
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError('sort_order must be either "asc" or "desc"')
        return v

class MotifResponse(BaseModel):
    """Standard response format for motif operations."""
    success: bool
    message: str
    data: Optional[Union[Motif, List[Motif], Dict[str, Any]]] = None 