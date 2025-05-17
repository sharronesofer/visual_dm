import random
import re
from typing import Tuple, List, Dict, Optional, Any, Union

# Regex pattern for dice notation (e.g., "2d6+3")
DICE_PATTERN = re.compile(r'(?P<count>\d+)d(?P<sides>\d+)(?P<modifier>[+-]\d+)?')


def roll_die(sides: int) -> int:
    """Roll a single die with the specified number of sides

    Args:
        sides: Number of sides on the die

    Returns:
        The result of the roll (1 to sides)
    """
    if sides < 1:
        raise ValueError(f"Invalid number of sides: {sides}")
    
    return random.randint(1, sides)


def roll_dice(count: int, sides: int) -> List[int]:
    """Roll multiple dice with the specified number of sides

    Args:
        count: Number of dice to roll
        sides: Number of sides on each die

    Returns:
        List of individual die results
    """
    if count < 1:
        raise ValueError(f"Invalid number of dice: {count}")
    
    return [roll_die(sides) for _ in range(count)]


def parse_dice_notation(notation: str) -> Tuple[int, int, int]:
    """Parse dice notation string (e.g., "2d6+3")

    Args:
        notation: Dice notation string in the format XdY+Z where:
                 X = number of dice
                 Y = number of sides
                 Z = optional modifier (can be positive or negative)

    Returns:
        Tuple of (count, sides, modifier)
    """
    match = DICE_PATTERN.match(notation)
    if not match:
        raise ValueError(f"Invalid dice notation: {notation}")
    
    count = int(match.group('count'))
    sides = int(match.group('sides'))
    modifier_str = match.group('modifier')
    modifier = int(modifier_str) if modifier_str else 0
    
    return count, sides, modifier


def roll_dice_notation(notation: str, advantage: bool = False, disadvantage: bool = False) -> Dict[str, Any]:
    """Roll dice based on dice notation

    Args:
        notation: Dice notation string (e.g., "2d6+3")
        advantage: Roll twice and take the higher result
        disadvantage: Roll twice and take the lower result

    Returns:
        Dictionary with the following keys:
        - total: Total result including modifiers
        - rolls: List of individual die results
        - details: Dictionary with details of the roll
    """
    count, sides, modifier = parse_dice_notation(notation)
    
    if advantage and disadvantage:
        # They cancel each other out
        advantage = disadvantage = False
    
    # Roll the dice
    if advantage or disadvantage:
        # Roll twice for advantage/disadvantage
        rolls1 = roll_dice(count, sides)
        rolls2 = roll_dice(count, sides)
        
        total1 = sum(rolls1) + modifier
        total2 = sum(rolls2) + modifier
        
        if advantage:
            # Take the higher result
            if total1 >= total2:
                rolls = rolls1
                total = total1
                unused = rolls2
            else:
                rolls = rolls2
                total = total2
                unused = rolls1
        else:  # disadvantage
            # Take the lower result
            if total1 <= total2:
                rolls = rolls1
                total = total1
                unused = rolls2
            else:
                rolls = rolls2
                total = total2
                unused = rolls1
                
        return {
            "total": total,
            "rolls": rolls,
            "details": {
                "count": count,
                "sides": sides,
                "modifier": modifier,
                "advantage": advantage,
                "disadvantage": disadvantage,
                "unused_rolls": unused,
                "unused_total": sum(unused) + modifier
            }
        }
    else:
        # Normal roll
        rolls = roll_dice(count, sides)
        total = sum(rolls) + modifier
        
        return {
            "total": total,
            "rolls": rolls,
            "details": {
                "count": count,
                "sides": sides,
                "modifier": modifier
            }
        }


def roll_with_advantage(notation: str) -> Dict[str, Any]:
    """Convenience function for rolling with advantage"""
    return roll_dice_notation(notation, advantage=True)


def roll_with_disadvantage(notation: str) -> Dict[str, Any]:
    """Convenience function for rolling with disadvantage"""
    return roll_dice_notation(notation, disadvantage=True)


def d20(modifier: int = 0, advantage: bool = False, disadvantage: bool = False) -> Dict[str, Any]:
    """Convenience function for rolling a d20"""
    notation = f"1d20{'+' + str(modifier) if modifier > 0 else str(modifier) if modifier < 0 else ''}"
    return roll_dice_notation(notation, advantage, disadvantage)


def calculate_critical_damage(notation: str) -> Dict[str, Any]:
    """Calculate critical hit damage (typically double dice rolls but not modifiers)

    Args:
        notation: Dice notation string (e.g., "2d6+3")

    Returns:
        Dictionary with the following keys:
        - total: Total result including modifiers
        - rolls: List of individual die results
        - details: Dictionary with details of the roll
    """
    count, sides, modifier = parse_dice_notation(notation)
    
    # For critical hits, roll double the number of dice
    rolls = roll_dice(count * 2, sides)
    total = sum(rolls) + modifier
    
    return {
        "total": total,
        "rolls": rolls,
        "details": {
            "count": count * 2,  # Double the dice
            "sides": sides,
            "modifier": modifier,
            "is_critical": True
        }
    } 