"""
Rules utilities for game calculations.
Contains functions for damage reduction, stats, and other game mechanics.
"""

def calculate_dr(level: int = 1, constitution: int = 10, armor_bonus: int = 0) -> int:
    """
    Calculate damage reduction (DR) for a character/NPC.
    
    Args:
        level: Character level
        constitution: Constitution score
        armor_bonus: Bonus from armor/equipment
        
    Returns:
        Calculated DR value
    """
    # Basic DR calculation based on level and constitution
    base_dr = max(0, (level - 1) // 2)  # DR increases every 2 levels
    constitution_bonus = max(0, (constitution - 10) // 2)  # Constitution modifier
    
    total_dr = base_dr + constitution_bonus + armor_bonus
    return max(0, total_dr)


def calculate_ac(base_ac: int = 10, dex_modifier: int = 0, armor_bonus: int = 0) -> int:
    """
    Calculate armor class.
    
    Args:
        base_ac: Base armor class (usually 10)
        dex_modifier: Dexterity modifier
        armor_bonus: Bonus from armor
        
    Returns:
        Total armor class
    """
    return base_ac + dex_modifier + armor_bonus


def calculate_modifier(ability_score: int) -> int:
    """
    Calculate ability modifier from ability score.
    
    Args:
        ability_score: The ability score (3-20+ range)
        
    Returns:
        Ability modifier
    """
    return (ability_score - 10) // 2


def calculate_hp(level: int, constitution: int, hit_die: int = 8) -> int:
    """
    Calculate hit points.
    
    Args:
        level: Character level
        constitution: Constitution score
        hit_die: Hit die size (d6=6, d8=8, etc.)
        
    Returns:
        Total hit points
    """
    con_modifier = calculate_modifier(constitution)
    base_hp = hit_die  # Max HP at first level
    
    # Add average HP for subsequent levels
    if level > 1:
        avg_hp_per_level = (hit_die // 2) + 1
        base_hp += (level - 1) * avg_hp_per_level
    
    # Add constitution bonus
    total_hp = base_hp + (con_modifier * level)
    
    return max(1, total_hp)  # Minimum 1 HP 