"""
CraftingIngredient Model

Defines the structure and behavior of ingredients used in crafting recipes.
"""
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from backend.infrastructure.database import BaseModel, GUID

class CraftingIngredient(BaseModel):
    """
    Represents an ingredient required for a crafting recipe.
    
    An ingredient defines what item is needed, how many are required,
    and whether they are consumed in the crafting process.
    """
    
    __tablename__ = "crafting_ingredients"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to recipe
    recipe_id = Column(GUID(), ForeignKey("crafting_recipes.id"), nullable=False, index=True)
    recipe = relationship("CraftingRecipe", back_populates="ingredients")
    
    # Ingredient details
    item_id = Column(String, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    is_consumed = Column(Boolean, default=True)
    is_tool = Column(Boolean, default=False)  # Tools are not consumed
    
    # Advanced ingredient features
    substitution_groups = Column(JSON, default=dict)  # Alternative ingredients
    quality_requirement = Column(String, nullable=True)  # Minimum quality needed
    
    def check_availability(self, inventory: Any) -> bool:
        """
        Check if the required quantity of this ingredient is available in the inventory.
        
        Args:
            inventory: The inventory to check
            
        Returns:
            bool: True if the required quantity is available, False otherwise
        """
        # TODO: Implement when inventory system is available
        # This would check if inventory has sufficient quantity of item_id
        # and handle substitution groups if the primary ingredient is not available
        return True  # Placeholder
        
    def get_substitution_options(self) -> Dict[str, Any]:
        """
        Get available substitution options for this ingredient.
        
        Returns:
            Dictionary of substitution groups and their requirements
        """
        return self.substitution_groups or {}
        
    def can_substitute(self, available_item_id: str, available_quantity: int) -> bool:
        """
        Check if an available item can substitute for this ingredient.
        
        Args:
            available_item_id: ID of the available item
            available_quantity: Quantity of the available item
            
        Returns:
            bool: True if substitution is possible, False otherwise
        """
        if available_item_id == self.item_id:
            return available_quantity >= self.quantity
            
        # Check substitution groups
        for group_name, substitutions in self.substitution_groups.items():
            if available_item_id in substitutions:
                required_quantity = substitutions[available_item_id]
                return available_quantity >= required_quantity
                
        return False 