from typing import Dict, List, Optional, Any, Tuple
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field, validator
import uuid
from enum import Enum
from datetime import datetime
import logging
import json

from .combat_system import (
    CombatManager, Combatant, StatusEffect, StatusEffectType,
    ActionType, DamageType, CombatantType, TerrainType
)

# Setup logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/combat",
    tags=["combat"],
    responses={404: {"description": "Not found"}}
)

# In-memory store for active combat sessions
# In a production environment, this would be stored in a database or Redis
active_combats: Dict[str, CombatManager] = {}


# ---------- Pydantic Models ---------- #

class CombatantCreate(BaseModel):
    """Model for creating a new combatant"""
    name: str
    type: CombatantType
    initiative_bonus: int = Field(..., ge=-5, le=20)
    hp: int = Field(..., gt=0)
    max_hp: int = Field(..., gt=0)
    armor_class: int = Field(..., ge=0, le=30)
    stats: Dict[str, int]
    position: Tuple[int, int] = (0, 0)
    
    @validator('stats')
    def validate_stats(cls, v):
        required_stats = {'strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'}
        if not all(stat in v for stat in required_stats):
            missing = required_stats - set(v.keys())
            raise ValueError(f"Missing required stats: {missing}")
        return v
    
    @validator('hp')
    def validate_hp(cls, v, values):
        if 'max_hp' in values and v > values['max_hp']:
            raise ValueError("HP cannot be greater than max_hp")
        return v


class StatusEffectCreate(BaseModel):
    """Model for creating a new status effect"""
    effect_type: StatusEffectType
    duration: int = Field(..., ge=1)
    source_id: str
    intensity: int = Field(1, ge=1, le=10)
    effects: Dict[str, Any] = {}


class AttackRequest(BaseModel):
    """Model for performing an attack"""
    attacker_id: str
    target_id: str
    attack_bonus: int = Field(..., ge=-5, le=20)
    damage_dice: str
    damage_type: DamageType
    advantage: bool = False
    disadvantage: bool = False


class TerrainUpdate(BaseModel):
    """Model for updating terrain"""
    position: Tuple[int, int]
    terrain_type: TerrainType


# ---------- Helper Functions ---------- #

def get_combat_manager(combat_id: str) -> CombatManager:
    """Get an active combat manager by ID, or raise 404"""
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail="Combat session not found")
    return active_combats[combat_id]


# ---------- Route Handlers ---------- #

@router.post("/", response_model=Dict[str, str])
async def create_combat_session() -> Dict[str, str]:
    """Create a new combat session"""
    combat_id = str(uuid.uuid4())
    active_combats[combat_id] = CombatManager()
    logger.info(f"Created new combat session: {combat_id}")
    return {"combat_id": combat_id}


@router.delete("/{combat_id}")
async def delete_combat_session(combat_id: str):
    """End and delete a combat session"""
    if combat_id in active_combats:
        # Get the combat manager before deleting
        combat = active_combats[combat_id]
        
        # End combat if active
        if combat.combat_active:
            combat.end_combat()
        
        # Delete the combat session
        del active_combats[combat_id]
        logger.info(f"Deleted combat session: {combat_id}")
    
    return {"status": "success"}


@router.get("/{combat_id}")
async def get_combat_state(combat_id: str):
    """Get the current state of a combat session"""
    combat = get_combat_manager(combat_id)
    return combat.to_dict()


@router.post("/{combat_id}/combatants")
async def add_combatant(combat_id: str, combatant: CombatantCreate):
    """Add a new combatant to the combat"""
    combat = get_combat_manager(combat_id)
    
    # Generate a unique ID for the combatant
    combatant_id = str(uuid.uuid4())
    
    # Create the Combatant object
    new_combatant = Combatant(
        id=combatant_id,
        name=combatant.name,
        type=combatant.type,
        initiative_bonus=combatant.initiative_bonus,
        hp=combatant.hp,
        max_hp=combatant.max_hp,
        armor_class=combatant.armor_class,
        stats=combatant.stats,
        position=combatant.position
    )
    
    # Add it to the combat
    combat.add_combatant(new_combatant)
    
    return new_combatant.to_dict()


@router.delete("/{combat_id}/combatants/{combatant_id}")
async def remove_combatant(combat_id: str, combatant_id: str):
    """Remove a combatant from the combat"""
    combat = get_combat_manager(combat_id)
    
    if combat.remove_combatant(combatant_id):
        return {"status": "success"}
    else:
        raise HTTPException(status_code=404, detail="Combatant not found")


@router.get("/{combat_id}/combatants")
async def get_combatants(combat_id: str):
    """Get all combatants in the combat"""
    combat = get_combat_manager(combat_id)
    return [c.to_dict() for c in combat.combatants]


@router.get("/{combat_id}/combatants/{combatant_id}")
async def get_combatant(combat_id: str, combatant_id: str):
    """Get a specific combatant by ID"""
    combat = get_combat_manager(combat_id)
    combatant = combat.get_combatant(combatant_id)
    
    if combatant:
        return combatant.to_dict()
    else:
        raise HTTPException(status_code=404, detail="Combatant not found")


@router.post("/{combat_id}/start")
async def start_combat(combat_id: str):
    """Start the combat encounter"""
    combat = get_combat_manager(combat_id)
    
    if combat.combat_active:
        raise HTTPException(status_code=400, detail="Combat is already active")
    
    try:
        combat.start_combat()
        return {
            "status": "success",
            "initiative_order": combat.initiative_order,
            "current_turn": combat.get_current_combatant().to_dict() if combat.get_current_combatant() else None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{combat_id}/end")
async def end_combat(combat_id: str):
    """End the combat encounter"""
    combat = get_combat_manager(combat_id)
    
    if not combat.combat_active:
        raise HTTPException(status_code=400, detail="Combat is not active")
    
    combat.end_combat()
    return {"status": "success"}


@router.post("/{combat_id}/next-turn")
async def next_turn(combat_id: str):
    """Advance to the next turn in the initiative order"""
    combat = get_combat_manager(combat_id)
    
    if not combat.combat_active:
        raise HTTPException(status_code=400, detail="Combat is not active")
    
    next_combatant = combat.next_turn()
    
    if next_combatant:
        return {
            "status": "success",
            "round": combat.round_number,
            "current_turn": next_combatant.to_dict()
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to advance to next turn")


@router.post("/{combat_id}/combatants/{combatant_id}/status-effects")
async def add_status_effect(combat_id: str, combatant_id: str, effect: StatusEffectCreate):
    """Add a status effect to a combatant"""
    combat = get_combat_manager(combat_id)
    combatant = combat.get_combatant(combatant_id)
    
    if not combatant:
        raise HTTPException(status_code=404, detail="Combatant not found")
    
    status_effect = StatusEffect(
        effect_type=effect.effect_type,
        duration=effect.duration,
        source_id=effect.source_id,
        intensity=effect.intensity,
        effects=effect.effects
    )
    
    added = combatant.add_status_effect(status_effect)
    
    return {
        "status": "success",
        "added_new": added,
        "combatant": combatant.to_dict()
    }


@router.delete("/{combat_id}/combatants/{combatant_id}/status-effects/{effect_type}")
async def remove_status_effect(combat_id: str, combatant_id: str, effect_type: StatusEffectType):
    """Remove a status effect from a combatant"""
    combat = get_combat_manager(combat_id)
    combatant = combat.get_combatant(combatant_id)
    
    if not combatant:
        raise HTTPException(status_code=404, detail="Combatant not found")
    
    removed = combatant.remove_status_effect(effect_type)
    
    if removed:
        return {
            "status": "success",
            "combatant": combatant.to_dict()
        }
    else:
        raise HTTPException(status_code=404, detail=f"Status effect {effect_type} not found on combatant")


@router.post("/{combat_id}/attack")
async def perform_attack(combat_id: str, attack: AttackRequest):
    """Perform an attack action"""
    combat = get_combat_manager(combat_id)
    
    try:
        result = combat.perform_attack(
            attacker_id=attack.attacker_id,
            target_id=attack.target_id,
            attack_bonus=attack.attack_bonus,
            damage_dice=attack.damage_dice,
            damage_type=attack.damage_type,
            advantage=attack.advantage,
            disadvantage=attack.disadvantage
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{combat_id}/terrain")
async def update_terrain(combat_id: str, terrain: TerrainUpdate):
    """Update the terrain at a specific position"""
    combat = get_combat_manager(combat_id)
    combat.set_terrain(terrain.position, terrain.terrain_type)
    
    return {
        "status": "success",
        "position": terrain.position,
        "terrain_type": terrain.terrain_type.value
    }


@router.get("/{combat_id}/combat-log")
async def get_combat_log(combat_id: str, limit: int = Query(50, ge=1, le=1000)):
    """Get the combat log entries"""
    combat = get_combat_manager(combat_id)
    
    # Get the specified number of most recent entries
    entries = combat.combat_log.entries[-limit:] if limit < len(combat.combat_log.entries) else combat.combat_log.entries
    
    return {"entries": entries} 