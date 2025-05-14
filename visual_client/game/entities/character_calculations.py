from typing import Dict, Optional
import random

def calculate_ability_modifier(character: Dict, ability: str) -> int:
    """Calculate ability modifier for a character.
    
    Args:
        character: Dictionary containing character's stats
        ability: Ability name (e.g., 'strength', 'dexterity')
        
    Returns:
        int: Ability modifier
    """
    ability_score = character.get(ability, 10)
    return (ability_score - 10) // 2

def calculate_proficiency_bonus(character: Dict) -> int:
    """Calculate proficiency bonus based on character level.
    
    Args:
        character: Dictionary containing character's stats
        
    Returns:
        int: Proficiency bonus
    """
    level = character.get('level', 1)
    return 2 + (level - 1) // 4

def calculate_hit_points(character: Dict) -> int:
    """Calculate maximum hit points for a character.
    
    Args:
        character: Dictionary containing character's stats
        
    Returns:
        int: Maximum hit points
    """
    level = character.get('level', 1)
    hit_dice = character.get('hit_dice', 8)  # Default to d8
    con_mod = calculate_ability_modifier(character, 'constitution')
    
    # First level gets max hit dice
    hp = hit_dice + con_mod
    
    # Additional levels roll hit dice
    for _ in range(level - 1):
        hp += random.randint(1, hit_dice) + con_mod
    
    return max(1, hp)  # Ensure at least 1 HP

def roll_dice(num_dice: int, dice_size: int, modifier: int = 0) -> int:
    """Roll dice and apply modifier.
    
    Args:
        num_dice: Number of dice to roll
        dice_size: Size of each die
        modifier: Modifier to add to the result
        
    Returns:
        int: Total roll result
    """
    total = 0
    for _ in range(num_dice):
        total += random.randint(1, dice_size)
    return total + modifier

def should_abandon(character: Dict, situation: Dict) -> bool:
    """Determine if a character should abandon their current task.
    
    Args:
        character: Dictionary containing character's stats
        situation: Dictionary containing current situation
        
    Returns:
        bool: Whether the character should abandon
    """
    # Calculate loyalty score
    loyalty = character.get('loyalty', 0)
    morale = character.get('morale', 0)
    wisdom_mod = calculate_ability_modifier(character, 'wisdom')
    
    # Calculate danger level
    danger_level = situation.get('danger_level', 0)
    health_percent = character.get('current_hp', 0) / character.get('max_hp', 1)
    
    # Combine factors
    abandon_score = (loyalty + morale + wisdom_mod) - (danger_level * 2)
    health_factor = 1.0 - health_percent
    
    # More likely to abandon at low health
    final_score = abandon_score - (health_factor * 10)
    
    return final_score < 0 