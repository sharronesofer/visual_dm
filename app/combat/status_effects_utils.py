"""
Status effect utilities.
Provides functionality for managing combat status effects.
"""

from typing import Dict, List, Optional, Any, Tuple
from app.core.models.combat import CombatState, CombatParticipant, CombatEngine
from app.core.models.character import Character
from app.core.models.npc import NPC

def apply_status_effect(participant: CombatParticipant, effect: str, duration: int) -> None:
    """Apply a status effect to a participant."""
    participant.add_status_effect(effect, duration)
    db.session.commit()

def remove_status_effect(participant: CombatParticipant, effect: str) -> None:
    """Remove a status effect from a participant."""
    participant.remove_status_effect(effect)
    db.session.commit()

def get_active_effects(participant: CombatParticipant) -> List[Dict]:
    """Get all active status effects for a participant."""
    return participant.status_effects

def process_status_effects(combat_state: CombatState) -> None:
    """Process all status effects in combat."""
    for participant in combat_state.participants:
        # Process each effect
        for effect in participant.status_effects[:]:  # Create a copy to modify during iteration
            # Decrease duration
            effect['duration'] -= 1
            
            # Apply effect
            if effect['name'] == 'poisoned':
                participant.take_damage(1)  # Poison damage
            elif effect['name'] == 'blessed':
                # Add temporary hit points
                if participant.current_health < participant.max_health:
                    participant.heal(1)
            
            # Remove expired effects
            if effect['duration'] <= 0:
                participant.remove_status_effect(effect['name'])
        
        db.session.commit()

def get_effect_description(effect: str) -> str:
    """Get a description of a status effect."""
    descriptions = {
        'poisoned': 'Takes 1 damage at the start of each turn',
        'blessed': 'Gains 1 temporary hit point at the start of each turn',
        'stunned': 'Cannot take actions',
        'invisible': 'Cannot be targeted by attacks',
        'hasted': 'Gains an additional action each turn',
        'slowed': 'Loses one action each turn'
    }
    return descriptions.get(effect, 'Unknown effect')

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

def get_status_effect_modifiers(effects: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Get all active modifiers from status effects.
    
    Args:
        effects: List of status effect dictionaries
        
    Returns:
        Dict of modifier types and their combined values
    """
    modifiers = {
        'damage_multiplier': 1.0,
        'defense_multiplier': 1.0,
        'movement_multiplier': 1.0,
        'critical_multiplier': 1.0,
        'attack_bonus': 0.0,
        'defense_bonus': 0.0
    }
    
    if not effects:
        return modifiers
        
    for effect in effects:
        effect_type = effect.get('type', '')
        magnitude = effect.get('magnitude', 0)
        
        if effect_type == 'flanking':
            modifiers['damage_multiplier'] *= magnitude
            modifiers['critical_multiplier'] *= 1.2  # 20% increased crit chance when flanking
            
        elif effect_type == 'flanked':
            modifiers['defense_multiplier'] *= (1 - magnitude)  # Reduce defense when flanked
            
        elif effect_type == 'high_ground':
            modifiers['attack_bonus'] += 0.1  # +10% attack bonus from high ground
            
        elif effect_type == 'difficult_terrain':
            modifiers['movement_multiplier'] *= 0.5  # Half movement in difficult terrain
            
        elif effect_type == 'defensive_stance':
            modifiers['defense_multiplier'] *= 1.2  # +20% defense in defensive stance
            modifiers['damage_multiplier'] *= 0.8  # -20% damage in defensive stance
            
        elif effect_type == 'aggressive_stance':
            modifiers['damage_multiplier'] *= 1.2  # +20% damage in aggressive stance
            modifiers['defense_multiplier'] *= 0.8  # -20% defense in aggressive stance
            
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
