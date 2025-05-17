"""
This module handles terrain-based tactical advantages in combat.
It integrates with the hex grid system to provide combat bonuses based on terrain positioning.
"""

from typing import Dict, Any, Tuple, Optional
from app.hexmap.tactical_hex_grid import TacticalHexGrid, TacticalHexCell

def calculate_terrain_advantage(
    grid: TacticalHexGrid,
    attacker_pos: Tuple[int, int],
    defender_pos: Tuple[int, int]
) -> Dict[str, float]:
    """
    Calculate terrain-based advantages for combat between two positions.
    
    Args:
        grid: The tactical hex grid
        attacker_pos: (q, r) coordinates of attacker
        defender_pos: (q, r) coordinates of defender
        
    Returns:
        Dict containing attack and defense modifiers
    """
    attacker_cell = grid.get(*attacker_pos)
    defender_cell = grid.get(*defender_pos)
    
    if not attacker_cell or not defender_cell:
        return {'attack_mod': 0, 'defense_mod': 0}
    
    # Get base terrain bonuses
    attacker_bonus = _get_terrain_combat_bonus(attacker_cell)
    defender_bonus = _get_terrain_combat_bonus(defender_cell)
    
    # Calculate elevation advantage
    elevation_mod = _calculate_elevation_advantage(
        attacker_cell.elevation,
        defender_cell.elevation
    )
    
    # Calculate cover advantage
    cover_mod = _calculate_cover_advantage(defender_cell)
    
    # Calculate line of sight penalties
    los_penalty = _calculate_los_penalty(grid, attacker_pos, defender_pos)
    
    return {
        'attack_mod': attacker_bonus + elevation_mod - los_penalty,
        'defense_mod': defender_bonus + cover_mod
    }

def _get_terrain_combat_bonus(cell: TacticalHexCell) -> float:
    """Get the combat bonus for a specific terrain type."""
    match cell.terrainEffect:
        case 'concealment': return 0.2  # Bonus to defense
        case 'highground': return 0.3   # Bonus to attack
        case 'hardcover': return 0.4    # Major bonus to defense
        case 'impassable': return -1    # Cannot be used
        case 'exposure': return -0.2    # Penalty to defense
        case _: return 0

def _calculate_elevation_advantage(attacker_elevation: float, defender_elevation: float) -> float:
    """Calculate combat advantage based on elevation difference."""
    elevation_diff = attacker_elevation - defender_elevation
    if elevation_diff > 1:
        return 0.2  # Significant height advantage
    elif elevation_diff > 0:
        return 0.1  # Minor height advantage
    return 0

def _calculate_cover_advantage(cell: TacticalHexCell) -> float:
    """Calculate defense bonus based on cover."""
    return cell.cover * 0.5  # Convert cover percentage to defense bonus

def _calculate_los_penalty(
    grid: TacticalHexGrid,
    from_pos: Tuple[int, int],
    to_pos: Tuple[int, int]
) -> float:
    """Calculate line of sight penalties between positions."""
    # Check cells between positions for obstacles
    cells_between = grid.get_cells_between(*from_pos, *to_pos)
    total_penalty = 0
    
    for cell in cells_between:
        if cell.terrainEffect == 'concealment':
            total_penalty += 0.1
        elif cell.terrainEffect == 'hardcover':
            total_penalty += 0.2
            
    return min(total_penalty, 0.6)  # Cap maximum penalty

def apply_terrain_advantages(
    grid: TacticalHexGrid,
    attacker,
    defender,
    attack_roll: int
) -> Tuple[int, Dict[str, float]]:
    """
    Apply terrain advantages to an attack roll.
    
    Args:
        grid: The tactical hex grid
        attacker: The attacking participant
        defender: The defending participant
        attack_roll: The base attack roll
        
    Returns:
        Tuple of (modified_roll, advantage_details)
    """
    from app.core.models.combat import CombatParticipant
    # Get positions from combat state
    attacker_pos = (attacker.position_q, attacker.position_r)
    defender_pos = (defender.position_q, defender.position_r)
    
    # Calculate advantages
    advantages = calculate_terrain_advantage(grid, attacker_pos, defender_pos)
    
    # Apply modifiers to attack roll
    attack_modifier = int((advantages['attack_mod'] - advantages['defense_mod']) * 5)
    modified_roll = attack_roll + attack_modifier
    
    return modified_roll, advantages 