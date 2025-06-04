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
    PLAYER_CHARACTER = "player_character"  # Follows a specific player character

class MotifLifecycle(str, Enum):
    """Defines the lifecycle state of a motif."""
    EMERGING = "emerging"  # Growing in strength
    STABLE = "stable"  # At full strength
    WANING = "waning"  # Decreasing in strength
    DORMANT = "dormant"  # Inactive but can re-emerge
    CONCLUDED = "concluded"  # Finished/ended

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
    DESPAIR = "despair"
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
    PEACE = "peace"
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

class MotifEvolutionTrigger(str, Enum):
    """Types of events that can trigger motif evolution."""
    TIME_PASSAGE = "time_passage"
    WORLD_EVENT = "world_event"
    PLAYER_ACTION = "player_action"
    SYSTEM_FEEDBACK = "system_feedback"
    NARRATIVE_COMPLETION = "narrative_completion"
    CONFLICTING_MOTIF = "conflicting_motif"
    REINFORCEMENT = "reinforcement"
    EXTERNAL_FORCE = "external_force"

class MotifEvolutionRule(BaseModel):
    """Defines how a motif can evolve or transform."""
    trigger_type: MotifEvolutionTrigger
    trigger_condition: str  # Description of what triggers this evolution
    intensity_change: int = 0  # How much intensity changes (-10 to +10)
    lifecycle_change: Optional[MotifLifecycle] = None  # Target lifecycle state
    category_change: Optional[MotifCategory] = None  # Can transform into new category
    probability: float = Field(1.0, ge=0.0, le=1.0)  # Chance this evolution occurs
    requires_intensity_threshold: Optional[int] = None  # Minimum intensity required
    cooldown_hours: int = 0  # Hours before this rule can trigger again

class LocationInfo(BaseModel):
    """Defines the location information for a motif."""
    region_id: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    radius: float = 0.0  # Influence radius
    # Player Character motif tracking
    player_id: Optional[str] = None  # For PC motifs, which player they follow
    follows_player: bool = False  # Whether this motif moves with a player

class MotifEffectTarget(str, Enum):
    """Targets for motif effects."""
    NPC = "npc"  # Affects NPC behavior, dialogue, etc.
    EVENT = "event"  # Influences event generation and frequency
    QUEST = "quest"  # Modifies quest/arc generation and outcomes
    FACTION = "faction"  # Adjusts faction relationships and tension
    ENVIRONMENT = "environment"  # Alters weather patterns, ambient effects
    ECONOMY = "economy"  # Impacts economic factors like prices, resource availability
    NARRATIVE = "narrative"  # Provides context for narrative generation
    PLAYER_CHARACTER = "player_character"  # Affects player character interactions
    CUSTOM = "custom"  # Custom effect type

class MotifEffect(BaseModel):
    """Model for a specific effect a motif has on game systems"""
    target: MotifEffectTarget
    intensity: int = Field(1, ge=1, le=10)  # Strength of effect from 1-10
    description: str
    parameters: Optional[Dict[str, Any]] = None  # Additional parameters for the effect

class MotifTriggerContext(BaseModel):
    """Context for triggering motifs."""
    character_ids: List[str] = Field(default_factory=list)
    location_id: Optional[str] = None
    trigger_strength: float = 1.0
    context: str = ""

class MotifConflict(BaseModel):
    """Represents a conflict between opposing motifs."""
    motif_a_id: str
    motif_b_id: str
    conflict_type: str  # "opposing", "contradictory", "competing"
    conflict_intensity: float = Field(ge=0.0, le=10.0)
    resolution_strategy: str = "tension"  # "cancel", "tension", "synthesis", "dominance"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MotifSynthesis(BaseModel):
    """Represents a synthesis of multiple motifs into a cohesive narrative theme."""
    contributing_motif_ids: List[str]
    synthesized_theme: str
    primary_category: MotifCategory
    blended_intensity: float
    narrative_guidance: str
    descriptors: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Motif(BaseModel):
    """Represents a narrative motif in the game world."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    category: MotifCategory
    scope: MotifScope
    theme: str = "general"  # Theme/topic of the motif
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
    
    # Enhanced Evolution System
    evolution_rules: List[MotifEvolutionRule] = Field(default_factory=list)
    last_evolution: Optional[datetime] = None
    evolution_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Conflict and Interaction Tracking
    conflicting_motifs: List[str] = Field(default_factory=list)  # IDs of conflicting motifs
    reinforcing_motifs: List[str] = Field(default_factory=list)  # IDs of reinforcing motifs
    conflict_resolution_preference: str = "tension"  # How this motif handles conflicts
    
    # Dynamic Strength Tracking
    base_intensity: int = Field(5, ge=1, le=10)  # Original intensity
    intensity_modifiers: Dict[str, float] = Field(default_factory=dict)  # Temporary modifiers
    intensity_history: List[Dict[str, Any]] = Field(default_factory=list)  # Intensity over time
    
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
    
    # Player Character Motif Support
    source_event: Optional[str] = None  # What event/action created this motif
    influence_radius: float = 0.0  # How far this motif affects NPCs when PC-based

    def update_lifecycle(self, new_lifecycle: MotifLifecycle):
        """Update the lifecycle of the motif"""
        old_lifecycle = self.lifecycle
        self.lifecycle = new_lifecycle
        self.updated_at = datetime.utcnow()
        
        # Track evolution history
        self.evolution_history.append({
            "timestamp": self.updated_at,
            "change_type": "lifecycle",
            "old_value": old_lifecycle,
            "new_value": new_lifecycle,
            "trigger": "manual_update"
        })
        
        return self
    
    def apply_intensity_modifier(self, modifier_id: str, value: float, reason: str = ""):
        """Apply a temporary intensity modifier."""
        self.intensity_modifiers[modifier_id] = value
        self.updated_at = datetime.utcnow()
        
        # Track intensity change
        self.intensity_history.append({
            "timestamp": self.updated_at,
            "change_type": "modifier_applied",
            "modifier_id": modifier_id,
            "modifier_value": value,
            "reason": reason,
            "effective_intensity": self.get_effective_intensity()
        })
    
    def remove_intensity_modifier(self, modifier_id: str):
        """Remove a temporary intensity modifier."""
        if modifier_id in self.intensity_modifiers:
            old_value = self.intensity_modifiers.pop(modifier_id)
            self.updated_at = datetime.utcnow()
            
            # Track intensity change
            self.intensity_history.append({
                "timestamp": self.updated_at,
                "change_type": "modifier_removed",
                "modifier_id": modifier_id,
                "old_modifier_value": old_value,
                "effective_intensity": self.get_effective_intensity()
            })
    
    def get_effective_intensity(self) -> float:
        """Calculate the current effective intensity including all modifiers."""
        base = float(self.intensity)
        modifiers_sum = sum(self.intensity_modifiers.values())
        effective = max(0.0, min(10.0, base + modifiers_sum))
        return effective
    
    def add_evolution_rule(self, rule: MotifEvolutionRule):
        """Add an evolution rule to this motif."""
        self.evolution_rules.append(rule)
        self.updated_at = datetime.utcnow()
    
    def can_evolve(self, trigger_type: MotifEvolutionTrigger) -> List[MotifEvolutionRule]:
        """Check which evolution rules can be triggered."""
        current_time = datetime.utcnow()
        applicable_rules = []
        
        for rule in self.evolution_rules:
            # Check trigger type
            if rule.trigger_type != trigger_type:
                continue
                
            # Check intensity threshold
            if rule.requires_intensity_threshold and self.get_effective_intensity() < rule.requires_intensity_threshold:
                continue
                
            # Check cooldown
            if rule.cooldown_hours > 0 and self.last_evolution:
                hours_since_evolution = (current_time - self.last_evolution).total_seconds() / 3600
                if hours_since_evolution < rule.cooldown_hours:
                    continue
                    
            applicable_rules.append(rule)
        
        return applicable_rules

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
    """Schema for creating a motif."""
    name: str
    description: str
    category: MotifCategory
    scope: MotifScope
    theme: str = "general"
    lifecycle: MotifLifecycle = MotifLifecycle.EMERGING
    intensity: int = Field(5, ge=1, le=10)
    duration_days: int = 14
    location: Optional[LocationInfo] = None
    effects: List[MotifEffect] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    evolution_rules: List[MotifEvolutionRule] = Field(default_factory=list)
    source_event: Optional[str] = None
    influence_radius: float = 0.0

class MotifUpdate(BaseModel):
    """Schema for updating an existing motif."""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[MotifCategory] = None
    scope: Optional[MotifScope] = None
    theme: Optional[str] = None
    lifecycle: Optional[MotifLifecycle] = None
    intensity: Optional[int] = None
    duration_days: Optional[int] = None
    location: Optional[LocationInfo] = None
    effects: Optional[List[MotifEffect]] = None
    metadata: Optional[Dict[str, Any]] = None
    evolution_rules: Optional[List[MotifEvolutionRule]] = None

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
    player_id: Optional[str] = None  # Filter PC motifs by player
    
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

class PlayerCharacterMotif(BaseModel):
    """Specialized model for Player Character motifs that follow players."""
    player_id: str
    motif: Motif
    acquired_location: Optional[Dict[str, float]] = None  # Where PC gained this motif
    acquisition_event: Optional[str] = None  # What event triggered this motif
    npc_reactions: Dict[str, str] = Field(default_factory=dict)  # How NPCs react to this PC motif
    influence_range: float = 100.0  # How far this motif affects NPCs
    visibility: str = "hidden"  # "hidden", "subtle", "obvious" - how apparent to NPCs
    
class MotifEvolutionEvent(BaseModel):
    """Represents an evolution event that occurred to a motif."""
    motif_id: str
    trigger_type: MotifEvolutionTrigger
    trigger_description: str
    changes_applied: Dict[str, Any]  # What changed (intensity, lifecycle, etc.)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    context: Optional[Dict[str, Any]] = None  # Additional context about the evolution