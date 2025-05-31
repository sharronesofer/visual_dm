"""
Character Utility Functions
--------------------------
Comprehensive utility functions for character manipulation, validation, and calculation.
This file consolidates functionality from core/character_utils.py and other
utility files related to character operations.
"""

from typing import Dict, List, Optional, Any, Tuple, Union
import random
import math
from datetime import datetime
import os
import json

# Import exceptions
try:
    from backend.infrastructure.utils import ValidationError, NotFoundError, DatabaseError
except ImportError:
    # Fallback error classes if the main error utils are not available
    class ValidationError(Exception):
        pass
    
    class NotFoundError(Exception):
        pass
    
    class DatabaseError(Exception):
        pass

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

# Skill to ability mappings
SKILL_TO_ABILITY = {
    "acrobatics": "DEX",
    "animal_handling": "WIS",
    "arcana": "INT",
    "athletics": "STR",
    "deception": "CHA",
    "history": "INT",
    "insight": "WIS",
    "intimidation": "CHA",
    "investigation": "INT",
    "medicine": "WIS",
    "nature": "INT",
    "perception": "WIS",
    "performance": "CHA",
    "persuasion": "CHA",
    "religion": "INT",
    "sleight_of_hand": "DEX",
    "stealth": "DEX",
    "survival": "WIS",
    "pickpocket": "DEX",
    "diplomacy": "CHA"
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
    all_skills = list(SKILL_TO_ABILITY.keys())
    
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

def calculate_xp_for_level(level: int) -> int:
    """Calculate the experience points required for a given level."""
    if level <= 1:
        return 0
    return int(BALANCE_CONSTANTS['BASE_XP'] * (level - 1) ** BALANCE_CONSTANTS['XP_SCALING_FACTOR'])

def calculate_ability_modifier(score: int) -> int:
    """Calculate ability score modifier using standard D&D formula."""
    return (max(1, score) - 10) // 2

def calculate_hit_points(level: int, constitution: int, class_: Optional[str] = None) -> int:
    """Calculate character hit points using class-specific hit dice."""
    if not class_:
        class_ = BALANCE_CONSTANTS['DEFAULT_CLASS']
    
    hit_die = BALANCE_CONSTANTS['CLASS_HIT_DICE'].get(class_, BALANCE_CONSTANTS['DEFAULT_HIT_DIE'])
    con_mod = calculate_ability_modifier(constitution)
    
    # First level gets max hit die + con mod
    hp = hit_die + con_mod
    
    # Additional levels get average of hit die + con mod
    if level > 1:
        avg_hp_per_level = (hit_die // 2 + 1) + con_mod
        hp += (level - 1) * avg_hp_per_level
    
    return max(1, hp)  # Minimum 1 HP

def calculate_mana_points(level: int, spellcasting_ability: int, class_: Optional[str] = None) -> int:
    """Calculate character mana points for spellcasters."""
    if not class_ or not has_spellcasting(class_):
        return 0
    
    mana_die = BALANCE_CONSTANTS['CLASS_MANA_DICE'].get(class_, BALANCE_CONSTANTS['DEFAULT_MANA_DIE'])
    ability_mod = calculate_ability_modifier(spellcasting_ability)
    
    # First level gets max mana die + ability mod
    mp = mana_die + ability_mod
    
    # Additional levels get average of mana die + ability mod
    if level > 1:
        avg_mp_per_level = (mana_die // 2 + 1) + ability_mod
        mp += (level - 1) * avg_mp_per_level
    
    return max(0, mp)  # Minimum 0 MP

def has_spellcasting(class_: str) -> bool:
    """Check if a class has spellcasting abilities."""
    return class_ in BALANCE_CONSTANTS['CLASS_SPELLCASTING_ABILITY']

def get_spellcasting_ability(class_: str) -> Optional[str]:
    """Get the primary spellcasting ability for a class."""
    return BALANCE_CONSTANTS['CLASS_SPELLCASTING_ABILITY'].get(class_)

def calculate_skill_modifier(character_stats: Dict[str, int], skill: str, is_proficient: bool = False) -> int:
    """Calculate skill modifier for a character."""
    if skill not in SKILL_TO_ABILITY:
        return 0
    
    ability = SKILL_TO_ABILITY[skill].lower()
    ability_score = character_stats.get(ability, 10)
    ability_mod = calculate_ability_modifier(ability_score)
    
    proficiency_bonus = 0
    if is_proficient:
        # Calculate proficiency bonus based on character level
        level = character_stats.get('level', 1)
        proficiency_bonus = math.ceil(level / 4) + 1  # Standard D&D proficiency progression
    
    return ability_mod + proficiency_bonus

def get_character_creation_summary(character_data: Dict[str, Any]) -> str:
    """Generate a summary string for character creation."""
    name = character_data.get('name', 'Unknown')
    race = character_data.get('race', 'Unknown')
    class_ = character_data.get('class', 'Unknown')
    level = character_data.get('level', 1)
    
    stats = character_data.get('stats', {})
    hp = stats.get('hit_points', 0)
    mp = stats.get('mana_points', 0)
    
    summary = f"{name} - Level {level} {race.title()} {class_.title()}"
    if hp > 0:
        summary += f" (HP: {hp}"
        if mp > 0:
            summary += f", MP: {mp}"
        summary += ")"
    
    return summary

def apply_racial_modifiers(stats: Dict[str, int], race: str) -> Dict[str, int]:
    """Apply racial ability score modifiers to character stats."""
    # Standard D&D racial modifiers
    racial_modifiers = {
        'human': {'strength': 1, 'dexterity': 1, 'constitution': 1, 'intelligence': 1, 'wisdom': 1, 'charisma': 1},
        'elf': {'dexterity': 2, 'constitution': -1},
        'dwarf': {'constitution': 2, 'charisma': -1},
        'halfling': {'dexterity': 2, 'strength': -1},
        'gnome': {'intelligence': 2, 'strength': -1},
        'half-elf': {'charisma': 2},
        'half-orc': {'strength': 2, 'intelligence': -1},
        'tiefling': {'charisma': 2, 'intelligence': 1, 'wisdom': -1}
    }
    
    modifiers = racial_modifiers.get(race, {})
    modified_stats = stats.copy()
    
    for ability, modifier in modifiers.items():
        if ability in modified_stats:
            modified_stats[ability] = max(
                BALANCE_CONSTANTS['MIN_ABILITY_SCORE'],
                min(BALANCE_CONSTANTS['MAX_ABILITY_SCORE'], modified_stats[ability] + modifier)
            )
    
    return modified_stats

def get_available_skills_for_class(class_: str) -> List[str]:
    """Get the list of skills available for a given class."""
    # Standard D&D class skill lists
    class_skills = {
        'barbarian': ['animal_handling', 'athletics', 'intimidation', 'nature', 'perception', 'survival'],
        'bard': ['deception', 'history', 'investigation', 'persuasion', 'performance', 'sleight_of_hand'],
        'cleric': ['history', 'insight', 'medicine', 'persuasion', 'religion'],
        'druid': ['arcana', 'animal_handling', 'insight', 'medicine', 'nature', 'perception', 'religion', 'survival'],
        'fighter': ['acrobatics', 'animal_handling', 'athletics', 'history', 'insight', 'intimidation', 'perception', 'survival'],
        'monk': ['acrobatics', 'athletics', 'history', 'insight', 'religion', 'stealth'],
        'paladin': ['athletics', 'insight', 'intimidation', 'medicine', 'persuasion', 'religion'],
        'ranger': ['animal_handling', 'athletics', 'insight', 'investigation', 'nature', 'perception', 'stealth', 'survival'],
        'rogue': ['acrobatics', 'athletics', 'deception', 'insight', 'intimidation', 'investigation', 'perception', 'performance', 'persuasion', 'sleight_of_hand', 'stealth'],
        'sorcerer': ['arcana', 'deception', 'insight', 'intimidation', 'persuasion', 'religion'],
        'warlock': ['arcana', 'deception', 'history', 'intimidation', 'investigation', 'nature', 'religion'],
        'wizard': ['arcana', 'history', 'insight', 'investigation', 'medicine', 'religion']
    }
    
    return class_skills.get(class_, list(SKILL_TO_ABILITY.keys()))

__all__ = [
    'generate_character_stats',
    'generate_character_skills', 
    'validate_character_data',
    'validate_character_stats',
    'calculate_level',
    'calculate_xp_for_level',
    'calculate_ability_modifier',
    'calculate_hit_points',
    'calculate_mana_points',
    'has_spellcasting',
    'get_spellcasting_ability',
    'calculate_skill_modifier',
    'get_character_creation_summary',
    'apply_racial_modifiers',
    'get_available_skills_for_class',
    'RACES',
    'CLASSES',
    'BALANCE_CONSTANTS',
    'SKILL_TO_ABILITY'
] 