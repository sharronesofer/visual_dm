"""
Status effect utilities.
Provides functionality for managing combat status effects.
"""

from typing import Dict, List, Optional, Any, Tuple
from app.core.models.character import Character
from app.core.models.npc import NPC
from app.combat.status_effects_manager import StatusEffectManager
from app.core.database import db

# Shared manager instance for utilities
status_effect_manager = StatusEffectManager(db)

def apply_status_effect(participant, effect_id: str, stacking: str = "refresh") -> Optional[str]:
    """Apply a status effect to a participant using the new system."""
    return status_effect_manager.apply_effect(participant, effect_id, stacking)

def remove_status_effect(participant, effect_id: str) -> bool:
    """Remove a status effect from a participant using the new system."""
    return status_effect_manager.remove_effect(participant, effect_id)

def get_active_effects(participant) -> List[Any]:
    """Get all active status effect instances for a participant."""
    return status_effect_manager.system.get_active_effects(str(participant.id))

def process_status_effects(combat_state) -> None:
    """Process all status effects in combat using the new system."""
    for participant in combat_state.participants:
        status_effect_manager.decrement_durations(participant)
        status_effect_manager.process_start_of_turn(participant)
        status_effect_manager.process_end_of_turn(participant)
        db.session.commit()

def get_effect_description(effect_id: str) -> str:
    """Get a description of a status effect from the registry."""
    effect = status_effect_manager.system.get_effect(effect_id)
    if effect:
        return effect.description
    return 'Unknown effect'

def check_flanking(
    pos1: Tuple[int, int],
    pos2: Tuple[int, int],
    target_pos: Tuple[int, int]
) -> bool:
    """
    Check if two positions are flanking a target position.
    
    Args:
        pos1: Position of first participant (q, r)
        pos2: Position of second participant (q, r)
        target_pos: Position of the target (q, r)
        
    Returns:
        Boolean indicating if the positions create a flanking situation
    """
    # Extract coordinates
    q1, r1 = pos1
    q2, r2 = pos2
    tq, tr = target_pos
    
    # Calculate relative positions
    rel1_q = q1 - tq
    rel1_r = r1 - tr
    rel2_q = q2 - tq
    rel2_r = r2 - tr
    
    # Check if positions are on opposite sides
    # This uses hex grid geometry to determine if the positions form a flanking pattern
    if (rel1_q == -rel2_q and rel1_r == -rel2_r):
        return True
        
    # Check diagonal flanking
    if (rel1_q == -rel2_q and abs(rel1_r) == 1 and abs(rel2_r) == 1):
        return True
        
    if (rel1_r == -rel2_r and abs(rel1_q) == 1 and abs(rel2_q) == 1):
        return True
        
    return False

def get_status_effect_modifiers(participant) -> Dict[str, float]:
    """
    Get all active modifiers from status effects for a participant using the new system.
    Returns a dict of attribute names and their total modification values.
    """
    effects = get_active_effects(participant)
    modifiers = {}
    for inst in effects:
        for mod in inst.effect.modifiers:
            total = mod.value * inst.current_stacks
            if mod.attribute in modifiers:
                modifiers[mod.attribute] += total
            else:
                modifiers[mod.attribute] = total
    return modifiers

def tick_status_effects(effects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Update durations of status effects and remove expired ones.
    
    Args:
        effects: List of status effect dictionaries
        
    Returns:
        Updated list of status effects with expired ones removed
    """
    if not effects:
        return []
        
    updated_effects = []
    for effect in effects:
        duration = effect.get('duration', 0)
        
        # Skip permanent effects (duration < 0)
        if duration < 0:
            updated_effects.append(effect)
            continue
            
        # Decrement duration
        if duration > 0:
            effect['duration'] -= 1
            if effect['duration'] > 0:
                updated_effects.append(effect)
                
    return updated_effects

def apply_terrain_effects(
    effects: List[Dict[str, Any]],
    terrain_type: str,
    elevation_difference: int
) -> List[Dict[str, Any]]:
    """
    Apply terrain-based status effects.
    
    Args:
        effects: Current list of status effects
        terrain_type: Type of terrain the unit is on
        elevation_difference: Difference in elevation compared to enemies
        
    Returns:
        Updated list of status effects
    """
    new_effects = effects.copy() if effects else []
    
    # Clear existing terrain effects
    new_effects = [e for e in new_effects if e['type'] not in [
        'high_ground', 'cover', 'difficult_terrain', 'exposed'
    ]]
    
    # Apply elevation effects
    if elevation_difference >= 2:
        new_effects.append({
            'type': 'high_ground',
            'duration': 1,  # Lasts until position changes
            'magnitude': 0.2
        })
    elif elevation_difference <= -2:
        new_effects.append({
            'type': 'exposed',
            'duration': 1,
            'magnitude': 0.2
        })
        
    # Apply terrain type effects
    if terrain_type == 'forest':
        new_effects.append({
            'type': 'cover',
            'duration': 1,
            'magnitude': 0.3
        })
    elif terrain_type == 'swamp':
        new_effects.append({
            'type': 'difficult_terrain',
            'duration': 1,
            'magnitude': 0.5
        })
    elif terrain_type == 'rocks':
        new_effects.append({
            'type': 'cover',
            'duration': 1,
            'magnitude': 0.2
        })
        
    return new_effects
