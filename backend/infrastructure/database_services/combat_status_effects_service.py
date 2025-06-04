"""
Combat Status Effects Database Service

This module provides database operations for status effects persistence.
Extracted from the combat system to separate technical infrastructure
from business logic.
"""

import logging
from typing import Dict, Any, List

from backend.infrastructure.database_adapters.combat_database_adapter import combat_db_adapter


def resolve_status_effects(target_id: str) -> Dict[str, Any]:
    """
    Ticks down duration of active status effects on a combat participant in database.
    Removes expired effects and updates database.
    
    Args:
        target_id: ID of the participant to update
        
    Returns:
        dict: Information about expired and active effects
    """
    try:
        combat_states = combat_db_adapter.get_combat_state()
        
        if not combat_states:
            return {"target_id": target_id, "error": "No active combat states found"}

        for battle_id, battle in combat_states.items():
            participants = battle.get("participants", {})
            if target_id in participants:
                participant = participants[target_id]
                effects = participant.get("status_effects", [])
                updated = []
                expired = []

                for e in effects:
                    if not isinstance(e, dict) or "duration" not in e:
                        continue
                        
                    e["duration"] -= 1
                    if e["duration"] > 0:
                        updated.append(e)
                    else:
                        expired.append(e.get("name", "Unknown Effect"))

                participant["status_effects"] = updated
                
                # Update in database
                success = combat_db_adapter.update_combat_participant(battle_id, target_id, participant)
                if not success:
                    logging.warning(f"Failed to update participant {target_id} in database")

                return {
                    "target_id": target_id,
                    "expired": expired,
                    "active": [e.get("name", "Unknown") for e in updated]
                }

        return {"target_id": target_id, "error": "Not found in any active combat."}
        
    except Exception as e:
        logging.error(f"Failed to resolve status effects for {target_id}: {str(e)}")
        return {"target_id": target_id, "error": f"Failed to resolve effects: {str(e)}"}


def remove_status_effect(target_id: str, effect_name: str) -> bool:
    """
    Remove a specific status effect from a combat participant in the database.
    
    Args:
        target_id: ID of the target
        effect_name: Name of the effect to remove
        
    Returns:
        bool: Whether the effect was successfully removed
    """
    if not target_id or not effect_name:
        return False
        
    try:
        combat_states = combat_db_adapter.get_combat_state()
        
        if not combat_states:
            return False

        for battle_id, battle in combat_states.items():
            participants = battle.get("participants", {})
            if target_id in participants:
                target = participants[target_id]
                effects = target.get("status_effects", [])
                
                # Filter out the effect to remove
                updated_effects = [e for e in effects if e.get("name") != effect_name]
                
                # If we removed something, update the participant
                if len(updated_effects) < len(effects):
                    target["status_effects"] = updated_effects
                    success = combat_db_adapter.update_combat_participant(battle_id, target_id, target)
                    if success:
                        logging.info(f"Removed status effect '{effect_name}' from {target_id}")
                    return success
        
        return False
        
    except Exception as e:
        logging.error(f"Failed to remove status effect '{effect_name}' from {target_id}: {str(e)}")
        return False


def sync_status_effects_to_database(combatant_id: str, effects: List[Dict[str, Any]], battle_id: str = None) -> bool:
    """
    Synchronize status effects from memory to the database.
    
    Args:
        combatant_id: ID of the combatant
        effects: List of status effects to sync
        battle_id: Optional battle ID for combat participants
        
    Returns:
        bool: Whether the sync was successful
    """
    try:
        if battle_id:
            # Update combat participant
            participant_data = {"status_effects": effects}
            return combat_db_adapter.update_combat_participant(battle_id, combatant_id, participant_data)
        else:
            # Update NPC status effects
            return combat_db_adapter.update_npc_status_effects(combatant_id, effects)
    except Exception as e:
        logging.error(f"Failed to sync status effects for {combatant_id}: {str(e)}")
        return False


def load_status_effects_from_database(combatant_id: str, battle_id: str = None) -> List[Dict[str, Any]]:
    """
    Load status effects for a combatant from the database.
    
    Args:
        combatant_id: ID of the combatant
        battle_id: Optional battle ID for combat participants
        
    Returns:
        List of status effects from database
    """
    try:
        if battle_id:
            # Load from combat state
            combat_states = combat_db_adapter.get_combat_state(battle_id)
            if battle_id in combat_states:
                participants = combat_states[battle_id].get("participants", {})
                if combatant_id in participants:
                    return participants[combatant_id].get("status_effects", [])
        
        # For non-combat or fallback, would need additional database queries
        # This is a placeholder for future implementation
        logging.warning(f"Loading status effects from database for {combatant_id} not fully implemented")
        return []
        
    except Exception as e:
        logging.error(f"Failed to load status effects for {combatant_id}: {str(e)}")
        return [] 