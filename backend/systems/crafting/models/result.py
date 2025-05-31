"""
CraftingResult Model

Defines the structure and behavior of results produced by crafting recipes.
"""
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship

from backend.infrastructure.database import BaseModel, GUID

class CraftingResult(BaseModel):
    """
    Represents a result item produced by a crafting recipe.
    
    A result defines what item is produced, how many are created,
    and the probability of getting this result.
    """
    
    __tablename__ = "crafting_results"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to recipe
    recipe_id = Column(GUID(), ForeignKey("crafting_recipes.id"), nullable=False, index=True)
    recipe = relationship("CraftingRecipe", back_populates="results")
    
    # Result details
    item_id = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    probability = Column(Float, nullable=False, default=1.0)  # 0.0 to 1.0
    
    # Advanced result features
    quality_range = Column(JSON, default=dict)  # Min/max quality levels
    bonus_conditions = Column(JSON, default=dict)  # Conditions for bonus results
    result_metadata = Column(JSON, default=dict)  # Additional result metadata
    
    def calculate_actual_quantity(self, base_quantity: int, skill_level: int = 1, station_bonus: float = 1.0) -> int:
        """
        Calculate the actual quantity produced considering skill and station bonuses.
        
        Args:
            base_quantity: Base quantity from the recipe
            skill_level: Character's skill level
            station_bonus: Station efficiency bonus
            
        Returns:
            int: Actual quantity to produce
        """
        # Apply skill bonus (small increase based on skill level)
        skill_bonus = 1.0 + (skill_level - 1) * 0.01  # 1% per skill level above 1
        
        # Apply station bonus
        total_bonus = skill_bonus * station_bonus
        
        # Calculate final quantity
        final_quantity = int(self.quantity * total_bonus)
        
        # Ensure at least the base quantity is produced
        return max(final_quantity, self.quantity)
        
    def determine_quality(self, skill_level: int = 1, station_quality_bonus: float = 0.0) -> str:
        """
        Determine the quality of the produced item.
        
        Args:
            skill_level: Character's skill level
            station_quality_bonus: Quality bonus from the crafting station
            
        Returns:
            str: Quality level (POOR, NORMAL, GOOD, EXCELLENT, EXCEPTIONAL, MASTERWORK, LEGENDARY)
        """
        # Base quality probabilities
        quality_weights = {
            "POOR": 0.05,
            "NORMAL": 0.70,
            "GOOD": 0.20,
            "EXCELLENT": 0.04,
            "EXCEPTIONAL": 0.008,
            "MASTERWORK": 0.002,
            "LEGENDARY": 0.0001
        }
        
        # Apply skill and station bonuses to shift quality distribution
        skill_bonus = (skill_level - 1) * 0.01
        total_bonus = skill_bonus + station_quality_bonus
        
        # Shift probabilities based on bonuses
        if total_bonus > 0:
            # Reduce POOR and NORMAL, increase higher qualities
            quality_weights["POOR"] = max(0.01, quality_weights["POOR"] - total_bonus)
            quality_weights["NORMAL"] = max(0.30, quality_weights["NORMAL"] - total_bonus * 0.5)
            quality_weights["GOOD"] += total_bonus * 0.3
            quality_weights["EXCELLENT"] += total_bonus * 0.15
            quality_weights["EXCEPTIONAL"] += total_bonus * 0.04
            quality_weights["MASTERWORK"] += total_bonus * 0.01
        
        # For now, return NORMAL as default (randomization would be implemented with game's RNG)
        return "NORMAL"
        
    def meets_probability_check(self) -> bool:
        """
        Check if this result should be produced based on its probability.
        
        Returns:
            bool: True if the result should be produced
        """
        # For now, always return True if probability >= 1.0, otherwise needs RNG
        return self.probability >= 1.0
        
    def get_quality_range(self) -> Dict[str, Any]:
        """
        Get the quality range configuration for this result.
        
        Returns:
            Dictionary containing quality range information
        """
        return self.quality_range or {
            "min_quality": "POOR",
            "max_quality": "LEGENDARY",
            "base_quality": "NORMAL"
        }

    def get_item_details(self) -> dict:
        """
        Get the details of the result item.
        
        Returns:
            dict: Item details including id, name, description, etc.
        """
        # Will be implemented when the item system is available
        return {"id": self.item_id, "quantity": self.quantity} 