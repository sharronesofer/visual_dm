"""
Dice Rolling Service Infrastructure Implementation

This module provides the infrastructure implementation for dice rolling and randomization,
used by the combat system for attack rolls, damage, and other random mechanics.
"""

import random
import re
from typing import List, Tuple


class DiceRollingServiceImpl:
    """
    Infrastructure implementation of the DiceRollingService protocol.
    
    Provides dice rolling functionality with support for standard
    D&D-style dice expressions and custom randomization.
    """
    
    def __init__(self, seed: int = None):
        """Initialize with optional random seed for testing."""
        if seed is not None:
            random.seed(seed)
    
    def roll_d20(self) -> int:
        """Roll a single d20."""
        return random.randint(1, 20)
    
    def roll_dice(self, count: int, sides: int) -> List[int]:
        """Roll multiple dice of the same type."""
        if count <= 0 or sides <= 0:
            raise ValueError("Count and sides must be positive")
        
        return [random.randint(1, sides) for _ in range(count)]
    
    def roll_damage(self, damage_expr: str) -> int:
        """
        Roll damage from a dice expression like '2d6+3', '1d8', '4d4-1', etc.
        
        Args:
            damage_expr: Dice expression string
            
        Returns:
            Total damage rolled
            
        Raises:
            ValueError: If the expression is invalid
        """
        if not damage_expr:
            return 0
        
        # Remove spaces and convert to lowercase
        expr = damage_expr.strip().lower()
        
        # Handle simple integer values
        if expr.isdigit():
            return int(expr)
        
        # Parse dice expression using regex
        # Matches patterns like: 2d6, 1d8+3, 3d4-1, d20 (implying 1d20)
        dice_pattern = r'^(\d*)d(\d+)([+-]\d+)?$'
        match = re.match(dice_pattern, expr)
        
        if not match:
            raise ValueError(f"Invalid dice expression: {damage_expr}")
        
        count_str, sides_str, modifier_str = match.groups()
        
        # Parse count (default to 1 if not specified)
        count = int(count_str) if count_str else 1
        sides = int(sides_str)
        modifier = int(modifier_str) if modifier_str else 0
        
        if count <= 0 or sides <= 0:
            raise ValueError(f"Invalid dice parameters: {count}d{sides}")
        
        # Roll dice and sum
        rolls = self.roll_dice(count, sides)
        total = sum(rolls) + modifier
        
        return max(0, total)  # Minimum 0 damage
    
    def roll_with_advantage(self) -> int:
        """Roll d20 with advantage (roll twice, take higher)."""
        roll1 = self.roll_d20()
        roll2 = self.roll_d20()
        return max(roll1, roll2)
    
    def roll_with_disadvantage(self) -> int:
        """Roll d20 with disadvantage (roll twice, take lower)."""
        roll1 = self.roll_d20()
        roll2 = self.roll_d20()
        return min(roll1, roll2)
    
    def roll_stat(self, method: str = "4d6_drop_lowest") -> int:
        """
        Roll a stat using various methods.
        
        Args:
            method: Rolling method ('4d6_drop_lowest', '3d6', 'point_buy')
            
        Returns:
            Stat value
        """
        if method == "4d6_drop_lowest":
            rolls = self.roll_dice(4, 6)
            rolls.sort(reverse=True)
            return sum(rolls[:3])  # Take highest 3
        elif method == "3d6":
            return sum(self.roll_dice(3, 6))
        elif method == "point_buy":
            # Return a balanced point-buy equivalent
            return random.choice([8, 10, 12, 13, 14, 15])
        else:
            raise ValueError(f"Unknown stat rolling method: {method}")
    
    def roll_initiative(self, dex_modifier: int = 0) -> int:
        """Roll initiative with dexterity modifier."""
        return self.roll_d20() + dex_modifier
    
    def roll_hit_dice(self, hit_die_type: int, constitution_modifier: int = 0) -> int:
        """Roll hit dice for healing."""
        roll = random.randint(1, hit_die_type)
        return max(1, roll + constitution_modifier)  # Minimum 1 HP
    
    def roll_saving_throw(self, bonus: int = 0, advantage: bool = False, disadvantage: bool = False) -> int:
        """Roll a saving throw with optional advantage/disadvantage."""
        if advantage and disadvantage:
            # Advantage and disadvantage cancel out
            roll = self.roll_d20()
        elif advantage:
            roll = self.roll_with_advantage()
        elif disadvantage:
            roll = self.roll_with_disadvantage()
        else:
            roll = self.roll_d20()
        
        return roll + bonus
    
    def roll_attack(self, attack_bonus: int = 0, advantage: bool = False, disadvantage: bool = False) -> Tuple[int, bool]:
        """
        Roll an attack with optional advantage/disadvantage.
        
        Returns:
            Tuple of (total_roll, is_critical_hit)
        """
        base_roll = self.roll_d20()
        
        if advantage and disadvantage:
            # Advantage and disadvantage cancel out
            final_roll = base_roll
        elif advantage:
            second_roll = self.roll_d20()
            base_roll = max(base_roll, second_roll)
            final_roll = base_roll
        elif disadvantage:
            second_roll = self.roll_d20()
            base_roll = min(base_roll, second_roll)
            final_roll = base_roll
        else:
            final_roll = base_roll
        
        total = final_roll + attack_bonus
        is_critical = base_roll == 20
        
        return total, is_critical
    
    def roll_critical_damage(self, damage_expr: str) -> int:
        """Roll critical damage (double dice, not modifiers)."""
        if not damage_expr:
            return 0
        
        expr = damage_expr.strip().lower()
        
        # Parse dice expression
        dice_pattern = r'^(\d*)d(\d+)([+-]\d+)?$'
        match = re.match(dice_pattern, expr)
        
        if not match:
            # If not a dice expression, just double the value
            try:
                return int(expr) * 2
            except ValueError:
                raise ValueError(f"Invalid damage expression: {damage_expr}")
        
        count_str, sides_str, modifier_str = match.groups()
        
        count = int(count_str) if count_str else 1
        sides = int(sides_str)
        modifier = int(modifier_str) if modifier_str else 0
        
        # Roll double the dice for critical, but don't double the modifier
        normal_rolls = self.roll_dice(count, sides)
        critical_rolls = self.roll_dice(count, sides)
        
        total = sum(normal_rolls) + sum(critical_rolls) + modifier
        return max(0, total)
    
    def roll_percentile(self) -> int:
        """Roll percentile dice (1-100)."""
        return random.randint(1, 100)
    
    def roll_custom(self, min_val: int, max_val: int) -> int:
        """Roll a custom range."""
        return random.randint(min_val, max_val)


def create_dice_service(seed: int = None) -> DiceRollingServiceImpl:
    """Factory function to create dice rolling service."""
    return DiceRollingServiceImpl(seed)


__all__ = ["DiceRollingServiceImpl", "create_dice_service"] 