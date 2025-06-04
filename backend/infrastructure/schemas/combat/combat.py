from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class StatusEffectItemSchema(BaseModel):
    type: str
    severity: Optional[str] = None
    value: Optional[Any] = None

class StatusEffectSchema(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    duration: int
    category: str  # "buff", "debuff", "condition"
    effects: List[StatusEffectItemSchema] = []
    stackable: bool = False
    dispellable: bool = True
    source_id: Optional[str] = None
    combatant_id: Optional[str] = None
    tags: List[str] = []

class CombatantSchema(BaseModel):
    id: str
    character_id: Optional[str] = None
    name: str
    team: str = "neutral"  # "player", "hostile", "neutral"
    combatant_type: str = "character"  # "character", "npc", "creature"
    
    # Combat Stats
    current_hp: int = 20
    max_hp: int = 20
    armor_class: int = 10
    initiative: int = 0
    dex_modifier: int = 0
    
    # Combat State
    is_active: bool = True
    is_conscious: bool = True
    position: Optional[Dict[str, float]] = None
    
    # Status Effects
    status_effects: List[StatusEffectSchema] = []
    
    # Action Economy
    has_used_standard_action: bool = False
    has_used_bonus_action: bool = False
    has_used_reaction: bool = False
    remaining_movement: float = 30.0
    
    # Equipment and Abilities
    equipped_weapons: List[str] = []
    equipped_armor: Optional[str] = None
    available_spells: List[str] = []
    class_features: List[str] = []
    
    # Metadata
    properties: Dict[str, Any] = {}

class CombatActionSchema(BaseModel):
    id: str
    action_id: str
    action_name: str
    actor_id: str
    actor_name: str
    target_ids: List[str] = []
    target_name: Optional[str] = None
    success: bool = False
    encounter_id: Optional[str] = None
    round_number: int = 1
    turn_number: int = 0
    damage_dealt: int = 0
    healing_applied: int = 0
    status_effects_applied: List[str] = []
    executed_at: datetime

class CombatLogEntrySchema(BaseModel):
    round: int
    turn: int
    timestamp: str
    message: str
    data: Dict[str, Any] = {}

class CombatStateSchema(BaseModel):
    combat_id: str
    name: str = "Combat Encounter"
    description: Optional[str] = None
    status: str = "pending"  # "pending", "active", "completed", "aborted"
    round_number: int = 1
    current_turn: int = 0
    
    # Participants
    participants: List[CombatantSchema] = []
    initiative_order: List[CombatantSchema] = []
    
    # History and Logging
    combat_log: List[CombatLogEntrySchema] = []
    actions_taken: List[CombatActionSchema] = []
    
    # Metadata
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    properties: Dict[str, Any] = {}

# Legacy support for backward compatibility
class CombatEffectSchema(BaseModel):
    """Legacy schema - use StatusEffectSchema instead"""
    id: str
    name: str
    description: Optional[str] = None
    duration: int
    tick_effect: Optional[Dict[str, Any]] = None
    stacks: Optional[int] = 1
    caster_id: Optional[str] = None

# Action Definition Schemas for Configuration
class ActionDefinitionSchema(BaseModel):
    id: str
    name: str
    description: str
    action_type: str  # "standard", "bonus", "reaction", "free"
    target_type: str  # "single_enemy", "single_ally", "self", "area"
    category: str  # "attack", "spell", "utility", "movement"
    
    # Range and Requirements
    min_range: int = 0
    max_range: int = 5
    range_feet: int = 5
    requires_line_of_sight: bool = True
    
    # Damage and Effects
    base_damage: int = 0
    damage_type: Optional[str] = None
    damage_modifier: Optional[str] = None
    cooldown_rounds: int = 0
    
    # Requirements and Costs
    resource_cost: Dict[str, int] = {}
    required_weapon_types: List[str] = []
    required_class_features: List[str] = []
    required_spells: List[str] = []
    
    # Effects
    applies_status_effects: List[str] = []
    tags: List[str] = []
    properties: Dict[str, Any] = {}

class ActionResultSchema(BaseModel):
    success: bool = False
    message: str = ""
    damage_dealt: int = 0
    healing_applied: int = 0
    targets_affected: List[str] = []
    status_effects_applied: List[str] = []
    additional_data: Dict[str, Any] = {}

# Request/Response Schemas for API
class CreateCombatRequest(BaseModel):
    name: str
    description: Optional[str] = None
    properties: Dict[str, Any] = {}

class AddCombatantRequest(BaseModel):
    character_id: Optional[str] = None
    name: str
    team: str = "neutral"
    combatant_type: str = "character"
    current_hp: int = 20
    max_hp: int = 20
    armor_class: int = 10
    dex_modifier: int = 0
    equipped_weapons: List[str] = []
    available_spells: List[str] = []
    class_features: List[str] = []

class ExecuteActionRequest(BaseModel):
    actor_id: str
    action_id: str
    target_ids: List[str] = []
    additional_data: Dict[str, Any] = {}

class SetInitiativeRequest(BaseModel):
    initiative_rolls: Dict[str, int]  # combatant_id -> initiative_value

class CombatSummarySchema(BaseModel):
    combat_id: str
    name: str
    status: str
    round_number: int
    total_participants: int
    active_participants: int
    actions_taken: int
    duration_seconds: Optional[float] = None
    teams: Dict[str, Dict[str, Any]] = {} 