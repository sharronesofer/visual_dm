import random
from typing import Dict, Any, List, Optional, Tuple

def roll_dice(sides: int, count: int = 1) -> int:
    """Roll dice with given number of sides and count"""
    return sum(random.randint(1, sides) for _ in range(count))

def calculate_modifier(score: int) -> int:
    """Calculate ability modifier from score"""
    return (score - 10) // 2

def format_dice_roll(roll: int, modifier: int = 0) -> str:
    """Format a dice roll with modifier"""
    if modifier == 0:
        return str(roll)
    return f"{roll} ({roll}{modifier:+d})"

class GameCalculator:
    """Utility class for game calculations"""
    
    @staticmethod
    def calculate_xp_for_level(level: int) -> int:
        """Calculate XP required for a given level"""
        if level <= 1:
            return 0
        return (level * 1000) * (level - 1)
    
    @staticmethod
    def calculate_level_from_xp(xp: int) -> int:
        """Calculate level from XP amount"""
        level = 1
        while GameCalculator.calculate_xp_for_level(level + 1) <= xp:
            level += 1
        return level
    
    @staticmethod
    def calculate_proficiency_bonus(level: int) -> int:
        """Calculate proficiency bonus based on level"""
        return 2 + ((level - 1) // 4)
    
    @staticmethod
    def calculate_ability_check(
        ability_score: int,
        proficiency_bonus: int = 0,
        advantage: bool = False,
        disadvantage: bool = False
    ) -> Tuple[int, str]:
        """Calculate ability check result"""
        modifier = calculate_modifier(ability_score)
        total_modifier = modifier + proficiency_bonus
        
        if advantage and disadvantage:
            # They cancel each other out
            roll = roll_dice(20)
            roll_desc = "normal roll"
        elif advantage:
            roll1 = roll_dice(20)
            roll2 = roll_dice(20)
            roll = max(roll1, roll2)
            roll_desc = f"advantage ({roll1}, {roll2})"
        elif disadvantage:
            roll1 = roll_dice(20)
            roll2 = roll_dice(20)
            roll = min(roll1, roll2)
            roll_desc = f"disadvantage ({roll1}, {roll2})"
        else:
            roll = roll_dice(20)
            roll_desc = "normal roll"
        
        total = roll + total_modifier
        return total, f"{roll_desc} + {total_modifier:+d} = {total}"
    
    @staticmethod
    def calculate_damage(
        damage_dice: str,
        modifier: int = 0,
        critical: bool = False
    ) -> Tuple[int, str]:
        """Calculate damage from dice string (e.g. '2d6+3')"""
        # Parse dice string
        dice_part = damage_dice.split('+')[0].strip()
        count, sides = map(int, dice_part.split('d'))
        
        # Roll damage
        if critical:
            count *= 2
        
        rolls = [roll_dice(sides) for _ in range(count)]
        damage = sum(rolls) + modifier
        
        # Format description
        desc = f"({'+'.join(map(str, rolls))})"
        if modifier:
            desc += f"{modifier:+d}"
        
        return damage, desc 