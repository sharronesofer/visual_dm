"""
Character Utilities
-----------------
Utility functions for character manipulation, calculation, and validation.
"""

from backend.systems.character.utils.character_utils import (
    RACES, CLASSES, BALANCE_CONSTANTS,
    generate_character_stats, generate_character_skills,
    validate_character_data, validate_character_stats,
    calculate_level, calculate_ability_modifier,
    calculate_hit_points, calculate_mana_points,
    calculate_proficiency_bonus, calculate_saving_throw,
    calculate_skill_bonus, roll_dice,
    has_spellcasting, apply_level_up_benefits,
    calculate_xp_for_level, generate_random_name
)

from backend.systems.character.utils.visual_utils import (
    RandomCharacterGenerator, serialize_character, deserialize_character,
    load_preset, save_preset, SERIALIZATION_VERSION
)

__all__ = [
    # Character utils
    'RACES', 'CLASSES', 'BALANCE_CONSTANTS',
    'generate_character_stats', 'generate_character_skills',
    'validate_character_data', 'validate_character_stats',
    'calculate_level', 'calculate_ability_modifier',
    'calculate_hit_points', 'calculate_mana_points',
    'calculate_proficiency_bonus', 'calculate_saving_throw',
    'calculate_skill_bonus', 'roll_dice',
    'has_spellcasting', 'apply_level_up_benefits',
    'calculate_xp_for_level', 'generate_random_name',
    
    # Visual utils
    'RandomCharacterGenerator', 'serialize_character', 'deserialize_character',
    'load_preset', 'save_preset', 'SERIALIZATION_VERSION'
]
