"""
Combat special effects utilities for the Visual DM combat system.

This module provides utilities for applying and managing combat-specific effects
such as fumbles, critical hits, and special abilities. Uses status_effects_utils
for the actual application of status effects.
"""

import random
from datetime import datetime
from backend.systems.combat.status_effects_utils import apply_status_effect, remove_status_effect


def roll_fumble_effect():
    """
    Generate a random fumble effect for critical misses.
    
    Returns:
        dict: Details of the fumble effect
    """
    effects = {
        "disarm": {"status": {"disarmed": True}},
        "prone": {"status": {"prone": True}},
        "dazed": {"status": {"dazed_rounds": 1}},
        "exposed": {"status": {"exposed": True}}
    }
    label = random.choice(list(effects.keys()))
    return {"type": label, **effects[label]}


def apply_fumble(attacker_id, battle_id=None):
    """
    Apply a random fumble effect to an attacker.
    
    Args:
        attacker_id: ID of the attacker who fumbled
        battle_id: Optional battle ID to target
        
    Returns:
        dict: Description of the applied fumble effect
    """
    fumble = roll_fumble_effect()
    
    # Get the first effect name/value from the status dictionary
    effect_name, effect_value = next(iter(fumble["status"].items()))
    
    # Apply the effect using the centralized status effects utility
    # Pull the target from the appropriate battle context if needed
    from backend.systems.combat.combat_utils import get_active_combat
    if battle_id:
        combat = get_active_combat(battle_id)
        if combat:
            target = next((p for p in combat.participants if p.character_id == attacker_id), None)
            if target:
                apply_status_effect(target, effect_name, duration=2, value=effect_value)
    
    # For Firebase-based participants
    from firebase_admin import db
    ref = db.reference("/combat_state")
    combat_states = ref.get()
    
    for b_id, battle in (combat_states or {}).items():
        if not battle_id or b_id == battle_id:
            participants = battle.get("participants", {})
            if attacker_id in participants:
                target = participants[attacker_id]
                apply_status_effect(target, effect_name, duration=2, value=effect_value)
                db.reference(f"/combat_state/{b_id}/participants/{attacker_id}").set(target)
                break
    
    return {
        "character_id": attacker_id,
        "fumble_type": fumble["type"],
        "effects": fumble["status"],
        "description": f"Fumbled and is now {fumble['type']}"
    }


def apply_critical_hit_effect(target_id, damage_type, battle_id=None):
    """
    Apply a critical hit effect based on damage type.
    
    Args:
        target_id: ID of the target
        damage_type: Type of damage (slashing, bludgeoning, etc.)
        battle_id: Optional battle ID to target
        
    Returns:
        dict: Description of the applied critical effect
    """
    crit_effects = {
        "slashing": {"bleeding": True},
        "bludgeoning": {"stunned": True},
        "piercing": {"punctured": True},
        "fire": {"burning": True},
        "cold": {"chilled": True},
        "lightning": {"shocked": True},
        "force": {"disoriented": True},
        "psychic": {"confused": True}
    }
    
    effect = crit_effects.get(damage_type, {"wounded": True})
    effect_name, effect_value = next(iter(effect.items()))
    
    # Apply the effect using the centralized status effects utility
    # Handle RAM-based combat first
    from backend.systems.combat.combat_utils import get_active_combat
    if battle_id:
        combat = get_active_combat(battle_id)
        if combat:
            target = next((p for p in combat.participants if p.character_id == target_id), None)
            if target:
                apply_status_effect(target, effect_name, duration=3, value=effect_value)
    
    # For Firebase-based participants
    from firebase_admin import db
    ref = db.reference("/combat_state")
    combat_states = ref.get()
    
    for b_id, battle in (combat_states or {}).items():
        if not battle_id or b_id == battle_id:
            participants = battle.get("participants", {})
            if target_id in participants:
                target = participants[target_id]
                apply_status_effect(target, effect_name, duration=3, value=effect_value)
                db.reference(f"/combat_state/{b_id}/participants/{target_id}").set(target)
                break
    
    return {
        "character_id": target_id,
        "crit_effect": effect_name,
        "effects": effect,
        "description": f"Suffered a critical {damage_type} hit and is now {effect_name}"
    }


def apply_area_effect(battle_id, effect_data, source_id=None):
    """
    Apply an effect to multiple targets in a battle area.
    
    Args:
        battle_id: ID of the battle
        effect_data: Dictionary with effect details (name, value, targets, etc.)
        source_id: ID of the source of the effect
        
    Returns:
        dict: Details of which targets were affected
    """
    effect_name = effect_data.get("name", "generic_effect")
    effect_value = effect_data.get("value", True)
    duration = effect_data.get("duration", 2)
    target_team = effect_data.get("target_team", "all")  # "friendly", "hostile", "all"
    targets = effect_data.get("specific_targets", [])
    
    affected = []
    
    # Handle RAM-based combat
    from backend.systems.combat.combat_utils import get_active_combat
    combat = get_active_combat(battle_id)
    if combat:
        for p in combat.participants:
            if targets and p.character_id not in targets:
                continue
            if target_team != "all" and p.team != target_team:
                continue
            
            apply_status_effect(p, effect_name, duration=duration, value=effect_value, source=source_id)
            affected.append(p.character_id)
    
    # For Firebase-based battles
    from firebase_admin import db
    ref = db.reference(f"/combat_state/{battle_id}")
    battle = ref.get()
    
    if battle:
        participants = battle.get("participants", {})
        for pid, p in participants.items():
            if targets and pid not in targets:
                continue
            if target_team != "all" and p.get("team") != target_team:
                continue
                
            apply_status_effect(p, effect_name, duration=duration, value=effect_value, source=source_id)
            participants[pid] = p
            affected.append(pid)
            
        if affected:
            db.reference(f"/combat_state/{battle_id}/participants").set(participants)
    
    return {
        "effect": effect_name,
        "affected_targets": affected,
        "duration": duration,
        "source": source_id
    } 