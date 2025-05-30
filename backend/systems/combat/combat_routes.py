"""
Combat routes module for the Visual DM combat system.

This module provides the API routes for the combat system,
allowing external systems to interact with combat functionality.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from fastapi import APIRouter, HTTPException, Body

from .combat_class import Combat
from .effect_pipeline import (
    CombatEffect, BuffEffect, DebuffEffect, 
    DamageOverTimeEffect, HealOverTimeEffect,
    ConditionEffect, ResistanceEffect, VulnerabilityEffect, 
    ImmunityEffect, EffectType, EffectStackingBehavior
)
try:
    from .combat_debug_interface import combat_debug_interface
except ImportError:
    combat_debug_interface = None

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/combat",
    tags=["combat"],
    responses={404: {"description": "Not found"}},
)

# Store active combats
active_combats: Dict[str, Combat] = {}

@router.post("/create")
async def create_combat(characters: Dict[str, Any] = Body(...)):
    """
    Create a new combat instance with the provided characters.
    
    Args:
        characters: Dictionary of characters to include in combat
        
    Returns:
        Combat state
    """
    combat = Combat(character_dict=characters)
    combat_id = combat.combat_id
    active_combats[combat_id] = combat
    
    logger.info(f"Created combat {combat_id}")
    
    return {"combat_id": combat_id, "message": "Combat created"}

@router.post("/start/{combat_id}")
async def start_combat(combat_id: str):
    """
    Start a combat instance.
    
    Args:
        combat_id: ID of the combat to start
        
    Returns:
        Initial combat state
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    combat = active_combats[combat_id]
    state = combat.start_combat()
    
    logger.info(f"Started combat {combat_id}")
    
    return {"state": state, "message": "Combat started"}

@router.get("/state/{combat_id}")
async def get_combat_state(combat_id: str):
    """
    Get the current state of a combat instance.
    
    Args:
        combat_id: ID of the combat
        
    Returns:
        Current combat state
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    combat = active_combats[combat_id]
    state = combat.get_combat_state()
    
    return {"state": state}

@router.post("/next_turn/{combat_id}")
async def next_turn(combat_id: str):
    """
    Advance to the next turn in combat.
    
    Args:
        combat_id: ID of the combat
        
    Returns:
        Updated combat state
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    combat = active_combats[combat_id]
    state = combat.next_turn()
    
    logger.info(f"Advanced to next turn in combat {combat_id}")
    
    return {"state": state, "message": "Advanced to next turn"}

@router.post("/take_action/{combat_id}")
async def take_action(
    combat_id: str,
    character_id: str = Body(...),
    action_id: str = Body(...),
    target_id: Optional[str] = Body(None)
):
    """
    Have a character take an action in combat.
    
    Args:
        combat_id: ID of the combat
        character_id: ID of the character taking the action
        action_id: ID of the action to take
        target_id: Optional ID of the target
        
    Returns:
        Action result and updated combat state
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    combat = active_combats[combat_id]
    
    try:
        result = combat.take_action(character_id, action_id, target_id)
        
        logger.info(f"Character {character_id} took action {action_id} in combat {combat_id}")
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/apply_effect/{combat_id}")
async def apply_effect(
    combat_id: str,
    source_id: Optional[str] = Body(None),
    target_id: str = Body(...),
    effect_type: str = Body(...),
    effect_params: Dict[str, Any] = Body({})
):
    """
    Apply an effect to a target in combat.
    
    Args:
        combat_id: ID of the combat
        source_id: ID of the source character (None for system effects)
        target_id: ID of the target character
        effect_type: Type of effect to apply
        effect_params: Parameters for the effect
        
    Returns:
        Effect result and updated combat state
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    combat = active_combats[combat_id]
    
    # Create the appropriate effect
    effect = None
    
    # Set some default parameters if not provided
    if "name" not in effect_params:
        effect_params["name"] = f"{effect_type.capitalize()} Effect"
    if "description" not in effect_params:
        effect_params["description"] = f"A {effect_type} effect"
    if "duration" not in effect_params:
        effect_params["duration"] = 3
    if "intensity" not in effect_params:
        effect_params["intensity"] = 1.0
        
    # Create specific effect type
    if effect_type.lower() == "buff":
        effect = BuffEffect(**effect_params)
    elif effect_type.lower() == "debuff":
        effect = DebuffEffect(**effect_params)
    elif effect_type.lower() == "damage_over_time" or effect_type.lower() == "dot":
        if "damage_per_turn" not in effect_params:
            effect_params["damage_per_turn"] = 5.0
        if "damage_type" not in effect_params:
            effect_params["damage_type"] = "fire"
        effect = DamageOverTimeEffect(**effect_params)
    elif effect_type.lower() == "heal_over_time" or effect_type.lower() == "hot":
        if "heal_per_turn" not in effect_params:
            effect_params["heal_per_turn"] = 5.0
        effect = HealOverTimeEffect(**effect_params)
    elif effect_type.lower() == "condition":
        if "condition" not in effect_params:
            effect_params["condition"] = "stunned"
        effect = ConditionEffect(**effect_params)
    elif effect_type.lower() == "resistance":
        if "damage_types" not in effect_params:
            effect_params["damage_types"] = ["fire"]
        if "resistance_multiplier" not in effect_params:
            effect_params["resistance_multiplier"] = 0.5
        effect = ResistanceEffect(**effect_params)
    elif effect_type.lower() == "vulnerability":
        if "damage_types" not in effect_params:
            effect_params["damage_types"] = ["fire"]
        if "vulnerability_multiplier" not in effect_params:
            effect_params["vulnerability_multiplier"] = 2.0
        effect = VulnerabilityEffect(**effect_params)
    elif effect_type.lower() == "immunity":
        if "damage_types" not in effect_params:
            effect_params["damage_types"] = ["fire"]
        effect = ImmunityEffect(**effect_params)
    else:
        # Generic effect
        effect = CombatEffect(**effect_params)
    
    try:
        result = combat.apply_effect(source_id, target_id, effect)
        
        logger.info(f"Applied {effect_type} effect to {target_id} in combat {combat_id}")
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/apply_damage/{combat_id}")
async def apply_damage(
    combat_id: str,
    source_id: Optional[str] = Body(None),
    target_id: str = Body(...),
    damage: float = Body(...),
    damage_type: str = Body(...)
):
    """
    Apply damage to a target in combat.
    
    Args:
        combat_id: ID of the combat
        source_id: ID of the source character (None for environmental damage)
        target_id: ID of the target character
        damage: Amount of damage to apply
        damage_type: Type of damage
        
    Returns:
        Damage result and updated combat state
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    combat = active_combats[combat_id]
    
    try:
        result = combat.apply_damage(source_id, target_id, damage, damage_type)
        
        logger.info(f"Applied {damage} {damage_type} damage to {target_id} in combat {combat_id}")
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/apply_healing/{combat_id}")
async def apply_healing(
    combat_id: str,
    source_id: Optional[str] = Body(None),
    target_id: str = Body(...),
    healing: float = Body(...)
):
    """
    Apply healing to a target in combat.
    
    Args:
        combat_id: ID of the combat
        source_id: ID of the source character (None for environmental healing)
        target_id: ID of the target character
        healing: Amount of healing to apply
        
    Returns:
        Healing result and updated combat state
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    combat = active_combats[combat_id]
    
    try:
        result = combat.apply_healing(source_id, target_id, healing)
        
        logger.info(f"Applied {healing} healing to {target_id} in combat {combat_id}")
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/available_actions/{combat_id}/{character_id}")
async def get_available_actions(combat_id: str, character_id: str):
    """
    Get available actions for a character in combat.
    
    Args:
        combat_id: ID of the combat
        character_id: ID of the character
        
    Returns:
        List of available actions
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    combat = active_combats[combat_id]
    
    try:
        result = combat.get_available_actions(character_id)
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/end/{combat_id}")
async def end_combat(combat_id: str):
    """
    End a combat instance.
    
    Args:
        combat_id: ID of the combat to end
        
    Returns:
        Final combat state
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    combat = active_combats[combat_id]
    state = combat.end_combat()
    
    # Don't remove from active_combats yet to allow reviewing the final state
    logger.info(f"Ended combat {combat_id}")
    
    return {"state": state, "message": "Combat ended"}

@router.delete("/{combat_id}")
async def delete_combat(combat_id: str):
    """
    Delete a combat instance.
    
    Args:
        combat_id: ID of the combat to delete
        
    Returns:
        Confirmation message
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    del active_combats[combat_id]
    
    logger.info(f"Deleted combat {combat_id}")
    
    return {"message": f"Combat {combat_id} deleted"}

@router.get("/list")
async def list_combats():
    """
    List all active combat instances.
    
    Returns:
        List of combat IDs and basic info
    """
    combats = []
    
    for combat_id, combat in active_combats.items():
        state = combat.get_combat_state()
        
        combats.append({
            "combat_id": combat_id,
            "round": state.get("round", 0),
            "current_character": state.get("current_character", None),
            "character_count": len(state.get("characters", {}))
        })
    
    return {"combats": combats}

# New routes for combat area, fog of war, and animation systems

@router.post("/move/{combat_id}")
async def move_character(
    combat_id: str,
    character_id: str = Body(...),
    destination: List[float] = Body(...),
    avoid_others: bool = Body(True)
):
    """
    Move a character to a new position in combat.
    
    Args:
        combat_id: ID of the combat
        character_id: ID of the character to move
        destination: Target position [x, y, z] or [x, z]
        avoid_others: Whether to avoid other characters
        
    Returns:
        Movement result and updated combat state
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    combat = active_combats[combat_id]
    
    try:
        result = combat.move_character(character_id, destination, avoid_others)
        
        logger.info(f"Character {character_id} moved to {destination} in combat {combat_id}")
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/visible_entities/{combat_id}/{observer_id}")
async def get_visible_entities(combat_id: str, observer_id: str):
    """
    Get all entities visible to an observer in combat.
    
    Args:
        combat_id: ID of the combat
        observer_id: ID of the observing character
        
    Returns:
        Dictionary of visible entities and their visibility levels
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    combat = active_combats[combat_id]
    
    try:
        visible_entities = combat.get_visible_entities(observer_id)
        
        return {"visible_entities": visible_entities}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/perception_check/{combat_id}")
async def perception_check(
    combat_id: str,
    observer_id: str = Body(...),
    target_id: str = Body(...),
    bonus: float = Body(0.0)
):
    """
    Perform a perception check in combat.
    
    Args:
        combat_id: ID of the combat
        observer_id: ID of the observing character
        target_id: ID of the target character
        bonus: Bonus to the check
        
    Returns:
        Perception check result and updated combat state
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    combat = active_combats[combat_id]
    
    try:
        result = combat.execute_perception_check(observer_id, target_id, bonus)
        
        logger.info(f"Perception check: {observer_id} -> {target_id} in combat {combat_id}")
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/toggle_debug/{combat_id}")
async def toggle_debug_mode(combat_id: str):
    """
    Toggle debug mode for a combat instance.
    
    Args:
        combat_id: ID of the combat
        
    Returns:
        Updated combat state
    """
    if combat_id not in active_combats:
        raise HTTPException(status_code=404, detail=f"Combat {combat_id} not found")
    
    combat = active_combats[combat_id]
    
    result = combat.toggle_debug_mode()
    
    logger.info(f"Toggled debug mode for combat {combat_id}")
    
    return {"state": result, "message": "Debug mode toggled"}

# Debug interface routes (only available if debug interface is loaded)

@router.get("/debug/available")
async def is_debug_available():
    """
    Check if debug interface is available.
    
    Returns:
        Whether debug interface is available
    """
    return {"available": combat_debug_interface is not None}

@router.post("/debug/create_test_combat")
async def create_test_combat():
    """
    Create a test combat for debugging.
    
    Returns:
        Combat ID and initial state
    """
    if not combat_debug_interface:
        raise HTTPException(status_code=404, detail="Debug interface not available")
    
    try:
        combat_id = combat_debug_interface.create_test_combat()
        combat = combat_debug_interface.active_combat
        
        # Add to active combats to make it accessible through regular routes
        active_combats[combat_id] = combat
        
        return {
            "combat_id": combat_id,
            "state": combat.get_combat_state(),
            "message": "Test combat created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/debug/add_test_character")
async def add_test_character(character_type: str = Body(...)):
    """
    Add a test character to the active debug combat.
    
    Args:
        character_type: Type of character to add
        
    Returns:
        Character ID and updated combat state
    """
    if not combat_debug_interface:
        raise HTTPException(status_code=404, detail="Debug interface not available")
    
    if not combat_debug_interface.active_combat:
        raise HTTPException(status_code=400, detail="No active debug combat")
    
    try:
        character_id = combat_debug_interface.add_test_character(character_type)
        
        return {
            "character_id": character_id,
            "state": combat_debug_interface.active_combat.get_combat_state(),
            "message": f"Added test {character_type} character"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/debug/apply_test_effect")
async def apply_test_effect(
    effect_type: str = Body(...),
    source_id: Optional[str] = Body(None),
    target_id: Optional[str] = Body(None)
):
    """
    Apply a test effect in the active debug combat.
    
    Args:
        effect_type: Type of effect to apply
        source_id: Optional source character ID
        target_id: Optional target character ID
        
    Returns:
        Effect ID and updated combat state
    """
    if not combat_debug_interface:
        raise HTTPException(status_code=404, detail="Debug interface not available")
    
    if not combat_debug_interface.active_combat:
        raise HTTPException(status_code=400, detail="No active debug combat")
    
    try:
        effect_id = combat_debug_interface.apply_test_effect(effect_type, source_id, target_id)
        
        return {
            "effect_id": effect_id,
            "state": combat_debug_interface.active_combat.get_combat_state(),
            "message": f"Applied test {effect_type} effect"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/debug/next_turn")
async def debug_next_turn():
    """
    Force the next turn in the active debug combat.
    
    Returns:
        Updated combat state
    """
    if not combat_debug_interface:
        raise HTTPException(status_code=404, detail="Debug interface not available")
    
    if not combat_debug_interface.active_combat:
        raise HTTPException(status_code=400, detail="No active debug combat")
    
    try:
        success = combat_debug_interface.force_next_turn()
        
        return {
            "success": success,
            "state": combat_debug_interface.active_combat.get_combat_state(),
            "message": "Advanced to next turn"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/debug/random_action")
async def debug_random_action(character_id: Optional[str] = Body(None)):
    """
    Make a character take a random action in the active debug combat.
    
    Args:
        character_id: Optional character ID (uses current turn character if None)
        
    Returns:
        Action result and updated combat state
    """
    if not combat_debug_interface:
        raise HTTPException(status_code=404, detail="Debug interface not available")
    
    if not combat_debug_interface.active_combat:
        raise HTTPException(status_code=400, detail="No active debug combat")
    
    try:
        success = combat_debug_interface.take_random_action(character_id)
        
        return {
            "success": success,
            "state": combat_debug_interface.active_combat.get_combat_state(),
            "message": "Random action taken"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/debug/stress_test")
async def debug_stress_test(rounds: int = Body(5)):
    """
    Run a stress test on the active debug combat.
    
    Args:
        rounds: Number of rounds to simulate
        
    Returns:
        Stress test results
    """
    if not combat_debug_interface:
        raise HTTPException(status_code=404, detail="Debug interface not available")
    
    if not combat_debug_interface.active_combat:
        raise HTTPException(status_code=400, detail="No active debug combat")
    
    try:
        results = combat_debug_interface.run_stress_test(rounds)
        
        return {
            "results": results,
            "state": combat_debug_interface.active_combat.get_combat_state(),
            "message": f"Stress test completed: {rounds} rounds"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug/log")
async def get_debug_log():
    """
    Get the current debug log.
    
    Returns:
        List of log messages
    """
    if not combat_debug_interface:
        raise HTTPException(status_code=404, detail="Debug interface not available")
    
    try:
        log = combat_debug_interface.get_debug_log()
        
        return {"log": log}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/debug/clear_log")
async def clear_debug_log():
    """
    Clear the debug log.
    
    Returns:
        Success message
    """
    if not combat_debug_interface:
        raise HTTPException(status_code=404, detail="Debug interface not available")
    
    try:
        combat_debug_interface.clear_debug_log()
        
        return {"message": "Debug log cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug/state")
async def get_debug_state():
    """
    Get the current debug state.
    
    Returns:
        Debug state information
    """
    if not combat_debug_interface:
        raise HTTPException(status_code=404, detail="Debug interface not available")
    
    try:
        state = combat_debug_interface.get_debug_state()
        
        return {"state": state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/debug/reset_combat")
async def debug_reset_combat():
    """
    Reset the active debug combat.
    
    Returns:
        Updated combat state
    """
    if not combat_debug_interface:
        raise HTTPException(status_code=404, detail="Debug interface not available")
    
    if not combat_debug_interface.active_combat:
        raise HTTPException(status_code=400, detail="No active debug combat")
    
    try:
        success = combat_debug_interface.reset_combat()
        
        return {
            "success": success,
            "state": combat_debug_interface.active_combat.get_combat_state(),
            "message": "Combat reset"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
