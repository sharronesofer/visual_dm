from typing import Dict, Optional, Tuple
import random
from visual_client.game.character.character_calculations import (
    calculate_ability_modifier,
    calculate_proficiency_bonus
)

def calculate_damage(attacker: Dict, defender: Dict, attack_type: str) -> int:
    """Calculate damage for an attack.
    
    Args:
        attacker: Dictionary containing attacker's stats
        defender: Dictionary containing defender's stats
        attack_type: Type of attack (melee, ranged, spell)
        
    Returns:
        int: Calculated damage amount
    """
    base_damage = random.randint(1, 6)  # Example: 1d6 base damage
    attack_bonus = calculate_attack_bonus(attacker, attack_type)
    damage_reduction = defender.get('damage_reduction', 0)
    
    total_damage = max(0, base_damage + attack_bonus - damage_reduction)
    return total_damage

def calculate_attack_bonus(character: Dict, attack_type: str) -> int:
    """Calculate attack bonus for a character.
    
    Args:
        character: Dictionary containing character's stats
        attack_type: Type of attack (melee, ranged, spell)
        
    Returns:
        int: Attack bonus
    """
    base_bonus = character.get('base_attack_bonus', 0)
    ability_mod = calculate_ability_modifier(character, attack_type)
    proficiency_bonus = calculate_proficiency_bonus(character)
    
    return base_bonus + ability_mod + proficiency_bonus

def calculate_attack_roll(attacker: Dict, defender: Dict, attack_type: str) -> Tuple[bool, int]:
    """Calculate attack roll and determine if it hits.
    
    Args:
        attacker: Dictionary containing attacker's stats
        defender: Dictionary containing defender's stats
        attack_type: Type of attack (melee, ranged, spell)
        
    Returns:
        Tuple[bool, int]: (hit_success, roll_value)
    """
    roll = random.randint(1, 20)
    attack_bonus = calculate_attack_bonus(attacker, attack_type)
    total_roll = roll + attack_bonus
    
    target_ac = defender.get('armor_class', 10)
    hit_success = total_roll >= target_ac
    
    return hit_success, total_roll

def apply_damage(target: Dict, damage: int) -> Dict:
    """Apply damage to a target and update their state.
    
    Args:
        target: Dictionary containing target's stats
        damage: Amount of damage to apply
        
    Returns:
        Dict: Updated target state
    """
    current_hp = target.get('current_hp', 0)
    max_hp = target.get('max_hp', 0)
    
    new_hp = max(0, current_hp - damage)
    target['current_hp'] = new_hp
    target['is_dead'] = new_hp == 0
    
    return target

def resolve_turn(attacker: Dict, defender: Dict, action: str) -> Dict:
    """Resolve a combat turn between two characters.
    
    Args:
        attacker: Dictionary containing attacker's stats
        defender: Dictionary containing defender's stats
        action: Type of action being taken
        
    Returns:
        Dict: Updated combat state
    """
    hit_success, roll_value = calculate_attack_roll(attacker, defender, action)
    
    if hit_success:
        damage = calculate_damage(attacker, defender, action)
        defender = apply_damage(defender, damage)
        
    return {
        'hit_success': hit_success,
        'roll_value': roll_value,
        'damage': damage if hit_success else 0,
        'defender': defender
    } 