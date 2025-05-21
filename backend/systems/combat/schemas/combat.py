from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class CombatEffectSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    duration: int  # Turns or time units
    tick_effect: Optional[Dict[str, Any]] = None # e.g. {"damage": 10, "type": "fire"}
    stacks: Optional[int] = 1
    caster_id: Optional[str] = None # ID of the entity that applied the effect

class CombatantSchema(BaseModel):
    id: str
    name: str
    hp: int
    max_hp: int
    stats: Dict[str, Any] # Placeholder for stats, e.g., from models/stats.py
    effects: List[CombatEffectSchema] = []
    is_active: bool = True
    team_id: Optional[str] = None

class CombatStateSchema(BaseModel):
    combat_id: str
    combatants: List[CombatantSchema] = []
    turn_order: List[str] # List of combatant IDs
    current_turn_combatant_id: Optional[str] = None
    current_round: int = 1
    is_combat_active: bool = True
    message_log: List[str] = []
    environment: Optional[Dict[str, Any]] = None 