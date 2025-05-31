#This module manages status effect application and resolution in both RAM-based combatants and Firebase-based participants. It handles turn-based effect decay, source tracking, and persistence syncing.
#It supports the combat, firebase, and npc systems.

from datetime import datetime
# from firebase_admin import db  # TODO: Replace with proper database integration

def apply_status_effect(combatant, effect_name, duration=3, source=None, value=None):
    """
    Apply a status effect to a combatant or participant (works with both RAM and Firebase objects).
    
    Args:
        combatant: Combatant object or participant dictionary
        effect_name: Name of the effect to apply
        duration: Number of turns the effect should last
        source: ID of the source that applied the effect
        value: Optional value associated with the effect
        
    Returns:
        dict: The created effect object
    """
    effect = {
        "name": effect_name,
        "duration": duration,
        "applied_by": source,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if value is not None:
        effect["value"] = value
    
    # Handle application to a combat class instance
    if hasattr(combatant, 'status_effects') and hasattr(combatant, 'attributes'):
        combatant.status_effects.append(effect)
        combatant.attributes["status_effects"] = combatant.status_effects
        
        # Sync to Firebase for persistent NPCs
        if duration > 20 and hasattr(combatant, 'character_id'):
            db.reference(f"/npcs/{combatant.character_id}/status_effects").push(effect)
    
    # Handle application to a dictionary participant (Firebase combat)
    elif isinstance(combatant, dict):
        combatant.setdefault("status_effects", []).append(effect)
    
    return effect

def tick_status_effects(combatant):
    """
    Decrement status effect durations and remove expired effects from a combatant.
    
    Args:
        combatant: Combatant object with status_effects attribute
        
    Returns:
        list: Effects that expired this turn
    """
    if not hasattr(combatant, 'status_effects'):
        return []
        
    updated = []
    expired = []
    
    for effect in combatant.status_effects:
        effect["duration"] -= 1
        if effect["duration"] > 0:
            updated.append(effect)
        else:
            expired.append(effect["name"])
            
    combatant.status_effects = updated
    combatant.attributes["status_effects"] = updated
    
    return expired

def resolve_status_effects(target_id):
    """
    Ticks down duration of active status effects on a combat participant in Firebase.
    Removes expired effects and updates Firebase.
    
    Args:
        target_id: ID of the participant to update
        
    Returns:
        dict: Information about expired and active effects
    """
    ref = db.reference("/combat_state")
    combat_states = ref.get()

    for battle_id, battle in (combat_states or {}).items():
        participants = battle.get("participants", {})
        if target_id in participants:
            participant = participants[target_id]
            effects = participant.get("status_effects", [])
            updated = []
            expired = []

            for e in effects:
                e["duration"] -= 1
                if e["duration"] > 0:
                    updated.append(e)
                else:
                    expired.append(e["name"])

            participant["status_effects"] = updated
            participants[target_id] = participant

            db.reference(f"/combat_state/{battle_id}/participants").set(participants)

            return {
                "target_id": target_id,
                "expired": expired,
                "active": [e["name"] for e in updated]
            }

    return {"target_id": target_id, "error": "Not found in any active combat."}

def remove_status_effect(target_id, effect_name):
    """
    Remove a specific status effect from a combat participant.
    
    Args:
        target_id: ID of the target
        effect_name: Name of the effect to remove
        
    Returns:
        bool: Whether the effect was successfully removed
    """
    ref = db.reference("/combat_state")
    combat_states = ref.get()

    for battle_id, battle in (combat_states or {}).items():
        participants = battle.get("participants", {})
        if target_id in participants:
            target = participants[target_id]
            effects = target.get("status_effects", [])
            
            # Filter out the effect to remove
            updated_effects = [e for e in effects if e.get("name") != effect_name]
            
            # If we removed something, update the participant
            if len(updated_effects) < len(effects):
                target["status_effects"] = updated_effects
                participants[target_id] = target
                db.reference(f"/combat_state/{battle_id}/participants").set(participants)
                return True
    
    return False
