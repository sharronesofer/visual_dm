"""
Combat-related utilities and calculations.
"""

from .combat_calculations import (
    calculate_damage,
    calculate_attack_bonus,
    calculate_attack_roll,
    apply_damage,
    resolve_turn
)

__all__ = [
    'calculate_damage',
    'calculate_attack_bonus',
    'calculate_attack_roll',
    'apply_damage',
    'resolve_turn'
]
