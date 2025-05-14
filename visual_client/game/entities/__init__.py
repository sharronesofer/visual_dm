"""
Character-related utilities and calculations.
"""

from .character_calculations import (
    calculate_ability_modifier,
    calculate_proficiency_bonus,
    calculate_hit_points,
    roll_dice,
    should_abandon
)

__all__ = [
    'calculate_ability_modifier',
    'calculate_proficiency_bonus',
    'calculate_hit_points',
    'roll_dice',
    'should_abandon'
]
