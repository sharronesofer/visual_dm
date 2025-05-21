"""
Character Utility Functions
--------------------------
Common utility functions for character manipulation, validation, and calculation.
This file consolidates functionality from core/character_utils.py and other
utility files related to character operations.
"""

from typing import Dict, List, Optional, Any, Tuple, Union
import random
import math
from datetime import datetime
import os
import json

# Constants for character generation and validation
RACES = ['human', 'elf', 'dwarf', 'halfling', 'gnome', 'half-elf', 'half-orc', 'tiefling']
CLASSES = ['fighter', 'wizard', 'cleric', 'rogue', 'barbarian', 'bard', 'druid', 'monk', 'paladin', 'ranger', 'sorcerer', 'warlock']

# Balance constants (these should eventually be moved to a dedicated config module)
BALANCE_CONSTANTS = {
    'BASE_HIT_POINTS': 10,
    'BASE_MANA_POINTS': 8,
    'STARTING_SKILL_POINTS': 4,
    'STARTING_GOLD': 100,
    'MIN_ABILITY_SCORE': 8,
    'MAX_ABILITY_SCORE': 18,
    'MIN_LEVEL': 1,
    'MAX_LEVEL': 20,
    'BASE_XP': 300,
    'XP_SCALING_FACTOR': 1.5,
    'DEFAULT_CLASS': 'fighter',
    'DEFAULT_SPELLCASTER_CLASS': 'wizard',
    'DEFAULT_HIT_DIE': 8,
    'DEFAULT_MANA_DIE': 6,
    'SKILL_POINTS_PER_LEVEL': 2,
    'CLASS_HIT_DICE': {
        'barbarian': 12,
        'fighter': 10,
        'paladin': 10,
        'ranger': 10,
        'monk': 8,
        'rogue': 8,
        'bard': 8,
        'cleric': 8,
        'druid': 8,
        'warlock': 8,
        'wizard': 6,
        'sorcerer': 6
    },
    'CLASS_MANA_DICE': {
        'wizard': 8,
        'sorcerer': 8,
        'bard': 6,
        'warlock': 6,
        'cleric': 6,
        'druid': 6,
        'paladin': 4,
        'ranger': 4
    },
    'CLASS_SPELLCASTING_ABILITY': {
        'wizard': 'intelligence',
        'sorcerer': 'charisma',
        'bard': 'charisma',
        'warlock': 'charisma',
        'cleric': 'wisdom',
        'druid': 'wisdom',
        'paladin': 'charisma',
        'ranger': 'wisdom'
    }
}

# Constants
SKILL_TO_ABILITY = {
    "stealth": "DEX", 
    "pickpocket": "DEX", 
    "intimidate": "CHA", 
    "diplomacy": "CHA",
    "persuasion": "CHA", 
    "deception": "CHA", 
    "perception": "WIS", 
    "insight": "WIS", 
    "arcana": "INT"
}

def generate_character_stats() -> Dict[str, int]:
    """Generate random character statistics using balance constants."""
    min_score = BALANCE_CONSTANTS['MIN_ABILITY_SCORE']
    max_score = BALANCE_CONSTANTS['MAX_ABILITY_SCORE']
    return {
        'strength': random.randint(min_score, max_score),
        'dexterity': random.randint(min_score, max_score),
        'constitution': random.randint(min_score, max_score),
        'intelligence': random.randint(min_score, max_score),
        'wisdom': random.randint(min_score, max_score),
        'charisma': random.randint(min_score, max_score),
        'hit_points': BALANCE_CONSTANTS['BASE_HIT_POINTS'],
        'mana_points': BALANCE_CONSTANTS['BASE_MANA_POINTS'],
        'skill_points': BALANCE_CONSTANTS['STARTING_SKILL_POINTS']
    }

def generate_character_skills() -> Dict[str, bool]:
    """Generate random character skills."""
    all_skills = [
        'acrobatics', 'animal_handling', 'arcana', 'athletics',
        'deception', 'history', 'insight', 'intimidation',
        'investigation', 'medicine', 'nature', 'perception',
        'performance', 'persuasion', 'religion', 'sleight_of_hand',
        'stealth', 'survival'
    ]
    
    skills = {skill: False for skill in all_skills}
    num_proficient = random.randint(2, 4)
    proficient_skills = random.sample(all_skills, num_proficient)
    
    for skill in proficient_skills:
        skills[skill] = True
    
    return skills

def validate_character_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate character data for creation or updating.
    
    Args:
        data: Dictionary containing character data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['name', 'race']
    
    # Check for required fields
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
            
    # Validate name
    if not isinstance(data['name'], str) or len(data['name']) < 2:
        return False, "Name must be a string with at least 2 characters"
        
    # Validate race
    if data['race'] not in RACES:
        return False, f"Invalid race. Must be one of: {', '.join(RACES)}"
        
    # Validate class if present
    if 'class' in data and data['class'] not in CLASSES:
        return False, f"Invalid class. Must be one of: {', '.join(CLASSES)}"
    
    # Validate stats if present
    if 'stats' in data:
        is_valid, error = validate_character_stats(data['stats'])
        if not is_valid:
            return False, error
    
    return True, None

def validate_character_stats(stats: Dict[str, int]) -> Tuple[bool, Optional[str]]:
    """
    Validate character statistics.
    
    Args:
        stats: Dictionary containing character statistics
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    basic_stats = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
    min_score = BALANCE_CONSTANTS['MIN_ABILITY_SCORE']
    max_score = BALANCE_CONSTANTS['MAX_ABILITY_SCORE']
    
    for stat in basic_stats:
        if stat in stats:
            if not isinstance(stats[stat], int):
                return False, f"{stat} must be an integer"
            if stats[stat] < min_score or stats[stat] > max_score:
                return False, f"{stat} must be between {min_score} and {max_score}"
    
    return True, None

def calculate_level(xp: int) -> int:
    """Calculate character level from experience points using exponential progression."""
    if xp < 0:
        return BALANCE_CONSTANTS['MIN_LEVEL']
        
    # Standard exponential progression
    level = 1
    xp_threshold = 0
    while xp >= xp_threshold and level < BALANCE_CONSTANTS['MAX_LEVEL']:
        level += 1
        xp_threshold = BALANCE_CONSTANTS['BASE_XP'] * (level - 1) ** BALANCE_CONSTANTS['XP_SCALING_FACTOR']
    
    return level - 1

def calculate_ability_modifier(score: int) -> int:
    """Calculate ability score modifier using standard D&D formula."""
    return (max(1, score) - 10) // 2

def calculate_hit_points(level: int, constitution: int, class_: Optional[str] = None) -> int:
    """Calculate character hit points using class-specific hit dice."""
    if class_ is None:
        class_ = BALANCE_CONSTANTS['DEFAULT_CLASS']
        
    hit_die = BALANCE_CONSTANTS['CLASS_HIT_DICE'].get(class_, BALANCE_CONSTANTS['DEFAULT_HIT_DIE'])
    con_mod = calculate_ability_modifier(constitution)
    
    # First level gets maximum HP
    base_hp = hit_die + con_mod
    
    # Additional levels roll or take average
    if level > 1:
        avg_roll = math.floor(hit_die / 2) + 1  # Correct average roll calculation
        additional_hp = sum(avg_roll + con_mod for _ in range(level - 1))
        base_hp += additional_hp
        
    return max(1, int(base_hp))

def calculate_mana_points(level: int, wisdom: int, intelligence: int, class_: Optional[str] = None) -> int:
    """Calculate character mana points using class-specific mana dice."""
    if class_ is None:
        class_ = BALANCE_CONSTANTS['DEFAULT_SPELLCASTER_CLASS']
        
    if not has_spellcasting(class_):
        return 0
        
    mana_die = BALANCE_CONSTANTS['CLASS_MANA_DICE'].get(class_, BALANCE_CONSTANTS['DEFAULT_MANA_DIE'])
    spellcasting_ability = BALANCE_CONSTANTS['CLASS_SPELLCASTING_ABILITY'].get(class_, 'wisdom')
    
    # Use the appropriate ability score based on the class
    if spellcasting_ability == 'wisdom':
        ability_mod = calculate_ability_modifier(wisdom)
    else:  # intelligence or charisma - for simplicity, we're only checking wisdom vs. non-wisdom here
        ability_mod = calculate_ability_modifier(intelligence)
    
    # First level gets maximum mana
    base_mana = mana_die + ability_mod
    
    # Additional levels roll or take average
    if level > 1:
        avg_roll = math.floor(mana_die / 2) + 1
        additional_mana = sum(avg_roll + ability_mod for _ in range(level - 1))
        base_mana += additional_mana
        
    return max(0, int(base_mana))

def calculate_proficiency_bonus(level: int) -> int:
    """Calculate proficiency bonus based on level."""
    return 2 + ((level - 1) // 4)

def calculate_saving_throw(stat_value: int, proficient: bool, level: int) -> int:
    """Calculate saving throw bonus."""
    ability_mod = calculate_ability_modifier(stat_value)
    if proficient:
        return ability_mod + calculate_proficiency_bonus(level)
    return ability_mod

def calculate_skill_bonus(stat_value: int, proficient: bool, expertise: bool, level: int) -> int:
    """Calculate skill check bonus."""
    ability_mod = calculate_ability_modifier(stat_value)
    prof_bonus = calculate_proficiency_bonus(level)
    if expertise:
        return ability_mod + (prof_bonus * 2)
    elif proficient:
        return ability_mod + prof_bonus
    return ability_mod

def roll_dice(num: int, sides: int) -> int:
    """Roll dice with the specified number and sides."""
    if num <= 0 or sides <= 0:
        return 0
    return sum(random.randint(1, sides) for _ in range(num))

def has_spellcasting(class_name: str) -> bool:
    """Determine if a class has spellcasting abilities."""
    return class_name in BALANCE_CONSTANTS['CLASS_SPELLCASTING_ABILITY']

def apply_level_up_benefits(character_data: Dict) -> Dict:
    """
    Apply benefits when a character levels up.
    
    Args:
        character_data: Dictionary containing character data
        
    Returns:
        Updated character data dictionary
    """
    stats = character_data.get('stats', {})
    level = character_data.get('level', 1)
    class_ = character_data.get('class', BALANCE_CONSTANTS['DEFAULT_CLASS'])
    
    # Calculate HP gain
    con_score = stats.get('constitution', 10)
    con_mod = calculate_ability_modifier(con_score)
    hit_die = BALANCE_CONSTANTS['CLASS_HIT_DICE'].get(class_, BALANCE_CONSTANTS['DEFAULT_HIT_DIE'])
    hp_gain = max(1, roll_dice(1, hit_die) + con_mod)
    
    # Update character stats
    stats['hit_points'] = stats.get('hit_points', 0) + hp_gain
    
    # Calculate MP gain for spellcasters
    if has_spellcasting(class_):
        spellcasting_ability = BALANCE_CONSTANTS['CLASS_SPELLCASTING_ABILITY'].get(class_, 'wisdom')
        ability_score = stats.get(spellcasting_ability, 10)
        ability_mod = calculate_ability_modifier(ability_score)
        mana_die = BALANCE_CONSTANTS['CLASS_MANA_DICE'].get(class_, BALANCE_CONSTANTS['DEFAULT_MANA_DIE'])
        mp_gain = max(0, roll_dice(1, mana_die) + ability_mod)
        stats['mana_points'] = stats.get('mana_points', 0) + mp_gain
    
    # Update skill points
    stats['skill_points'] = stats.get('skill_points', 0) + BALANCE_CONSTANTS['SKILL_POINTS_PER_LEVEL']
    
    # Update character data
    character_data['stats'] = stats
    character_data['level'] = level + 1
    character_data['xp'] = calculate_xp_for_level(level + 1)
    
    return character_data

def calculate_xp_for_level(level: int) -> int:
    """
    Calculate the total XP required to reach a specific level.
    
    Args:
        level: The target level
        
    Returns:
        Total XP required
    """
    if level <= 1:
        return 0
    return int(BALANCE_CONSTANTS['BASE_XP'] * ((level - 1) ** BALANCE_CONSTANTS['XP_SCALING_FACTOR']))

def generate_random_name(race: str, gender: Optional[str] = None) -> str:
    """
    Generate a random name appropriate for the character's race and gender.
    
    Args:
        race: Character race
        gender: Character gender (optional)
        
    Returns:
        A randomly generated name
    """
    # These are placeholder name lists - in a real implementation, 
    # these would be much more extensive and come from a data file
    name_lists = {
        'human': {
            'male': ['Alaric', 'Bran', 'Cormac', 'Darian', 'Eamon'],
            'female': ['Adira', 'Brenna', 'Cora', 'Delia', 'Elara'],
            'neutral': ['Avery', 'Cameron', 'Drew', 'Finn', 'Jordan']
        },
        'elf': {
            'male': ['Adran', 'Berrian', 'Caeldrim', 'Daereth', 'Elrond'],
            'female': ['Althaea', 'Betrynna', 'Caelynn', 'Drusilia', 'Enna'],
            'neutral': ['Alyx', 'Eryn', 'Keyl', 'Luar', 'Nyx']
        },
        # Add more races as needed
    }
    
    # Default to human if race not found
    if race not in name_lists:
        race = 'human'
    
    # Default to a random gender if none specified
    if not gender:
        gender = random.choice(['male', 'female', 'neutral'])
    
    # If the gender-specific list doesn't exist, fall back to neutral
    if gender not in name_lists[race]:
        gender = 'neutral'
    
    # If even neutral doesn't exist, create a placeholder name
    if gender not in name_lists[race]:
        return f"{race.capitalize()}-{random.randint(100, 999)}"
    
    # Return a random name from the appropriate list
    return random.choice(name_lists[race][gender])

def parse_coords(loc: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse string coordinates in format 'x_y' into a tuple."""
    try:
        return tuple(map(int, loc.split("_")))
    except Exception:
        return None, None

def perform_skill_check(
    character: Dict[str, Any], 
    skill: str, 
    dc: int = 12
) -> Dict[str, Any]:
    """
    Perform a skill check for a character against a DC.
    
    Args:
        character: Character data dictionary
        skill: Skill name to check
        dc: Difficulty class (default: 12)
        
    Returns:
        Dictionary with roll results
    """
    ability = SKILL_TO_ABILITY.get(skill.lower(), "INT")
    modifier = (character.get(ability, 10) - 10) // 2
    
    # Add skill bonus if character has the skill
    if skill.lower() in [s.lower() for s in character.get("skills", [])]:
        modifier += 2
        
    roll = random.randint(1, 20)
    total = roll + modifier
    
    return {
        "skill": skill,
        "roll": roll,
        "modifier": modifier,
        "total": total,
        "success": total >= dc,
        "dc": dc
    }

def calculate_dr(equipment: List[Dict[str, Any]]) -> int:
    """
    Calculate damage reduction from equipped items.
    
    Args:
        equipment: List of equipped items
        
    Returns:
        Total damage reduction value
    """
    total_dr = 0
    for item in equipment:
        total_dr += item.get("dr", 0)
    return total_dr

__all__ = [
    'RACES', 'CLASSES', 'BALANCE_CONSTANTS',
    'generate_character_stats', 'generate_character_skills',
    'validate_character_data', 'validate_character_stats',
    'calculate_level', 'calculate_ability_modifier',
    'calculate_hit_points', 'calculate_mana_points',
    'calculate_proficiency_bonus', 'calculate_saving_throw',
    'calculate_skill_bonus', 'roll_dice',
    'has_spellcasting', 'apply_level_up_benefits',
    'calculate_xp_for_level', 'generate_random_name',
    'parse_coords', 'perform_skill_check', 'calculate_dr'
] 