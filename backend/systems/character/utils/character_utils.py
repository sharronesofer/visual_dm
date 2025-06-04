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

# Import the canonical rules system
from backend.systems.rules.rules import (
    balance_constants,
    calculate_ability_modifier,
    calculate_proficiency_bonus,
    calculate_hp_for_level,
    calculate_mana_points as rules_calculate_mana_points,
    get_starting_equipment
)

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

# Use balance constants from rules system (deprecated local constants)
# These are maintained for backward compatibility but will delegate to rules system
BALANCE_CONSTANTS = balance_constants

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

def generate_character_attributes() -> Dict[str, int]:
    """Generate random character attributes using balance constants."""
    min_score = balance_constants['min_stat']
    max_score = balance_constants['max_stat']
    return {
        'strength': random.randint(min_score, max_score),
        'dexterity': random.randint(min_score, max_score),
        'constitution': random.randint(min_score, max_score),
        'intelligence': random.randint(min_score, max_score),
        'wisdom': random.randint(min_score, max_score),
        'charisma': random.randint(min_score, max_score),
        'hit_points': balance_constants.get('base_hp', 10),
        'mana_points': balance_constants.get('base_mana_points', 8),
        'skill_points': balance_constants.get('starting_skill_points', 4)
    }

def generate_character_skills() -> Dict[str, bool]:
    """Generate random character skills."""
    all_skills = list(SKILL_TO_ABILITY.keys())
    skill_count = random.randint(3, 6)  # Random number of proficient skills
    selected_skills = random.sample(all_skills, skill_count)
    
    return {skill: skill in selected_skills for skill in all_skills}

def validate_character_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate complete character data.
    
    Args:
        data: Dictionary containing complete character data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    required_fields = ['name', 'race']
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate race
    if data['race'].lower() not in [race.lower() for race in RACES]:
        return False, f"Invalid race: {data['race']}. Must be one of {RACES}"
    
    # Validate attributes if present
    if 'attributes' in data:
        valid, error = validate_character_attributes(data['attributes'])
        if not valid:
            return False, error
    
    return True, None

def validate_character_attributes(attributes: Dict[str, int]) -> Tuple[bool, Optional[str]]:
    """
    Validate character attributes.
    
    Args:
        attributes: Dictionary containing character attributes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    basic_attributes = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
    min_score = balance_constants['min_stat']
    max_score = balance_constants['max_stat']
    
    for attribute in basic_attributes:
        if attribute in attributes:
            if not isinstance(attributes[attribute], int):
                return False, f"{attribute} must be an integer"
            if attributes[attribute] < min_score or attributes[attribute] > max_score:
                return False, f"{attribute} must be between {min_score} and {max_score}"
    
    return True, None

def calculate_level(xp: int) -> int:
    """Calculate character level from experience points using XP thresholds from rules system."""
    if xp < 0:
        return balance_constants['starting_level']
    
    # Use XP thresholds from rules system
    xp_thresholds = balance_constants['xp_thresholds']
    
    for level, threshold in enumerate(xp_thresholds):
        if xp < threshold:
            return max(1, level)  # Return previous level (1-indexed)
    
    # If XP exceeds all thresholds, return max level
    return balance_constants['max_level']

def calculate_xp_for_level(level: int) -> int:
    """Calculate the experience points required for a given level."""
    if level <= 1:
        return 0
    
    # Use XP thresholds from rules system
    xp_thresholds = balance_constants['xp_thresholds']
    
    if level <= len(xp_thresholds):
        return xp_thresholds[level - 1]
    
    # For levels beyond the table, use the last threshold
    return xp_thresholds[-1]

def calculate_hit_points(level: int, constitution_modifier: int) -> int:
    """
    Calculate hit points using the CANONICAL rules system calculation.
    
    Args:
        level: Character level
        constitution_modifier: Constitution modifier (NOT raw score)
        
    Returns:
        Total hit points
    """
    # Use the canonical calculation from rules system
    return calculate_hp_for_level(level, constitution_modifier)

def calculate_mana_points(level: int, intelligence_modifier: int) -> int:
    """
    Calculate mana points using the CANONICAL rules system calculation.
    
    Args:
        level: Character level
        intelligence_modifier: Intelligence modifier (NOT raw score)
        
    Returns:
        Total mana points
    """
    # Use the canonical calculation from rules system
    return rules_calculate_mana_points(level, intelligence_modifier)

def calculate_skill_modifier(character_attributes: Dict[str, int], skill: str, is_proficient: bool = False) -> int:
    """
    Calculate skill modifier for a character.
    
    Args:
        character_attributes: Dictionary containing character attributes
        skill: Name of the skill
        is_proficient: Whether the character is proficient in the skill
        
    Returns:
        Skill modifier
    """
    # Get the associated ability for this skill
    ability = SKILL_TO_ABILITY.get(skill)
    if not ability:
        return 0
    
    # Get ability score and calculate modifier using canonical function
    ability_score = character_attributes.get(ability.lower(), 10)
    ability_modifier = calculate_ability_modifier(ability_score)
    
    # Add proficiency bonus if proficient
    proficiency_bonus = 0
    if is_proficient:
        level = character_attributes.get('level', 1)
        proficiency_bonus = calculate_proficiency_bonus(level)
    
    return ability_modifier + proficiency_bonus

def get_character_creation_summary(character_data: Dict[str, Any]) -> str:
    """
    Generate a summary of character creation choices for ability-based system.
    
    Args:
        character_data: Dictionary containing character data
        
    Returns:
        Formatted summary string
    """
    name = character_data.get('name', 'Unknown')
    race = character_data.get('race', 'Unknown')
    level = character_data.get('level', 1)
    
    summary = f"Character: {name}\n"
    summary += f"Race: {race.title()}\n"
    summary += f"Level: {level}\n"
    summary += f"System: Ability-based progression\n"
    
    # Add stats if available
    if 'attributes' in character_data:
        summary += "\nAttributes:\n"
        for stat, value in character_data['attributes'].items():
            summary += f"  {stat.upper()}: {value}\n"
    
    return summary

def apply_racial_modifiers(attributes: Dict[str, int], race: str) -> Dict[str, int]:
    """
    Apply racial modifiers to character attributes using rules system data.
    
    Args:
        attributes: Dictionary containing base character attributes
        race: Character race
        
    Returns:
        Modified attributes dictionary
    """
    modified_attributes = attributes.copy()
    
    # Get racial bonuses from rules system
    racial_bonuses = balance_constants.get('racial_bonuses', {})
    race_bonuses = racial_bonuses.get(race.lower(), {})
    
    # Apply racial bonuses
    for bonus_type, bonus_value in race_bonuses.items():
        if bonus_type == "all_stats":
            for attribute in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
                if attribute in modified_attributes:
                    modified_attributes[attribute] += bonus_value
        else:
            if bonus_type in modified_attributes:
                modified_attributes[bonus_type] += bonus_value
    
    return modified_attributes

def get_available_skills() -> List[str]:
    """Get the list of all available skills (no class restrictions in ability-based system)."""
    return list(SKILL_TO_ABILITY.keys())

__all__ = [
    'generate_character_attributes',
    'generate_character_skills', 
    'validate_character_data',
    'validate_character_attributes',
    'calculate_level',
    'calculate_xp_for_level',
    'calculate_ability_modifier',
    'calculate_hit_points',
    'calculate_mana_points',
    'calculate_skill_modifier',
    'get_character_creation_summary',
    'apply_racial_modifiers',
    'get_available_skills',
    'RACES',
    'BALANCE_CONSTANTS',
    'SKILL_TO_ABILITY'
] 