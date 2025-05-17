from typing import Dict, List, Optional, Tuple, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

from .combat_system import ActionType, DamageType, CombatantType, StatusEffectType, TerrainType


class StatusEffectModel(BaseModel):
    """Model for representing a status effect in API responses"""
    effect_type: str
    duration: int
    source_id: str
    intensity: int
    effects: Dict[str, Any] = {}
    applied_at: str


class CombatantModel(BaseModel):
    """Model for representing a combatant in API responses"""
    id: str
    name: str
    type: str
    initiative_bonus: int
    hp: int
    max_hp: int
    armor_class: int
    stats: Dict[str, int]
    position: Tuple[int, int]
    initiative_roll: int
    status_effects: List[StatusEffectModel] = []
    action_points: Dict[str, int]


class CombatLogEntryModel(BaseModel):
    """Model for representing a combat log entry in API responses"""
    timestamp: str
    type: str
    # Additional fields will be included dynamically based on entry type


class CombatStateModel(BaseModel):
    """Model for representing the current state of a combat session"""
    combatants: List[CombatantModel]
    initiative_order: List[str]
    current_turn_index: int
    round_number: int
    combat_active: bool
    battlefield: Dict[str, str]  # Position string -> terrain type string
    combat_log: Dict[str, List[CombatLogEntryModel]]


class CombatSessionResponse(BaseModel):
    """Response model for creating a combat session"""
    combat_id: str


class StatusResponse(BaseModel):
    """Basic status response"""
    status: str


class AttackResultModel(BaseModel):
    """Model for representing the result of an attack"""
    attacker_id: str
    attacker_name: str
    target_id: str
    target_name: str
    hits: bool
    is_critical: bool
    damage: Optional[Dict[str, Any]] = None


class CombatStartResponse(BaseModel):
    """Response model for starting combat"""
    status: str
    initiative_order: List[str]
    current_turn: Optional[CombatantModel] = None


class NextTurnResponse(BaseModel):
    """Response model for advancing to the next turn"""
    status: str
    round: int
    current_turn: CombatantModel


class AddStatusEffectResponse(BaseModel):
    """Response model for adding a status effect"""
    status: str
    added_new: bool
    combatant: CombatantModel


class RemoveStatusEffectResponse(BaseModel):
    """Response model for removing a status effect"""
    status: str
    combatant: CombatantModel


class TerrainUpdateResponse(BaseModel):
    """Response model for updating terrain"""
    status: str
    position: Tuple[int, int]
    terrain_type: str


class CombatLogResponse(BaseModel):
    """Response model for getting the combat log"""
    entries: List[CombatLogEntryModel] 