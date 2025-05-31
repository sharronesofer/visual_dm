"""
Crafting Experience Service

This service handles crafting skill progression, experience calculation, and achievement management.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple

# Set up logging
logger = logging.getLogger(__name__)


class CraftingExperienceService:
    """
    Service for managing crafting experience, skill progression, and achievements.
    """
    
    def __init__(self):
        """Initialize the crafting experience service."""
        self.logger = logger
        # Quality multipliers for experience calculation
        self.quality_multipliers = {
            "POOR": 0.5,
            "NORMAL": 1.0,
            "GOOD": 1.2,
            "EXCELLENT": 1.5,
            "EXCEPTIONAL": 2.0,
            "MASTERWORK": 3.0,
            "LEGENDARY": 5.0
        }
        
    def calculate_crafting_experience(
        self, 
        recipe: Any, 
        result_items: List[Dict[str, Any]], 
        skills: Optional[Dict[str, int]] = None
    ) -> Tuple[Optional[str], int]:
        """
        Calculate experience gained from crafting a recipe.
        
        Args:
            recipe: The recipe that was crafted
            result_items: List of items produced with quality and quantity info
            skills: Optional character skills for bonus calculations
            
        Returns:
            Tuple of (skill_name, experience_amount)
        """
        # Check if recipe requires a skill
        skill_required = getattr(recipe, 'skill_required', None)
        if not skill_required:
            return None, 0
            
        # Get base experience from recipe
        base_experience = getattr(recipe, 'base_experience', 10)
        
        # Calculate experience based on result items
        total_experience = base_experience
        
        if result_items:
            quality_bonus = 0
            quantity_bonus = 0
            
            for item in result_items:
                # Quality bonus
                quality = item.get('quality', 'NORMAL')
                multiplier = self.quality_multipliers.get(quality, 1.0)
                quality_bonus += base_experience * (multiplier - 1.0)
                
                # Quantity bonus (small bonus for multiple items)
                quantity = item.get('quantity', 1)
                if quantity > 1:
                    quantity_bonus += base_experience * 0.1 * (quantity - 1)
                    
            total_experience += quality_bonus + quantity_bonus
            
        # Skill level bonus (if skills provided)
        if skills and skill_required in skills:
            skill_level = skills[skill_required]
            # Small bonus based on skill level
            skill_bonus = base_experience * 0.05 * skill_level
            total_experience += skill_bonus
            
        return skill_required, int(total_experience)
        
    def apply_crafting_experience(
        self, 
        character_id: str, 
        skill: str, 
        experience: int
    ) -> None:
        """
        Apply crafting experience to a character's skill.
        
        Args:
            character_id: ID of the character
            skill: Name of the skill to gain experience in
            experience: Amount of experience to gain
            
        Note:
            Currently a placeholder - would integrate with character system
        """
        # Placeholder implementation
        # In a full implementation, this would:
        # 1. Load character data
        # 2. Update skill experience
        # 3. Check for level ups
        # 4. Save character data
        # 5. Trigger achievement checks
        
        if experience > 0:
            self.logger.info(
                f"Character {character_id} gained {experience} experience in {skill}"
            )
            
    def get_skill_level(self, character_id: str, skill_type: str) -> int:
        """
        Get a character's current skill level.
        
        Args:
            character_id: ID of the character
            skill_type: Type of skill to check
            
        Returns:
            Current skill level (placeholder returns 1)
        """
        # Placeholder implementation
        return 1
        
    def gain_experience(self, character_id: str, recipe_id: str, amount: int) -> Dict[str, Any]:
        """
        Have a character gain experience from crafting a recipe.
        
        Args:
            character_id: ID of the character
            recipe_id: ID of the recipe crafted
            amount: Amount of experience gained
            
        Returns:
            Results of experience gain
        """
        # Placeholder implementation
        return {
            "character_id": character_id,
            "recipe_id": recipe_id,
            "experience_gained": amount,
            "level_up": False
        }
        
    def unlock_recipe(self, character_id: str, recipe_id: str) -> bool:
        """
        Unlock a recipe for a character.
        
        Args:
            character_id: ID of the character
            recipe_id: ID of the recipe to unlock
            
        Returns:
            True if recipe was unlocked successfully
        """
        # Placeholder implementation
        self.logger.info(f"Recipe {recipe_id} unlocked for character {character_id}")
        return True
        
    def get_unlocked_recipes(self, character_id: str) -> List[str]:
        """
        Get all recipes unlocked by a character.
        
        Args:
            character_id: ID of the character
            
        Returns:
            List of unlocked recipe IDs
        """
        # Placeholder implementation
        return []
        
    def calculate_success_chance(self, character_id: str, recipe_id: str) -> float:
        """
        Calculate the success chance for a character crafting a recipe.
        
        Args:
            character_id: ID of the character
            recipe_id: ID of the recipe
            
        Returns:
            Success chance as a float between 0.0 and 1.0
        """
        # Placeholder implementation - base 75% chance
        return 0.75 