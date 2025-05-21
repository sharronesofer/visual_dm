"""
CraftingIngredient Model

Defines the structure and behavior of ingredients used in crafting recipes.
"""
from typing import Optional
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

# Import the base model/db setup when available
# from backend.database import Base


class CraftingIngredient:
    """
    Represents an ingredient required for a crafting recipe.
    
    An ingredient defines what item is needed, how many are required,
    and whether they are consumed in the crafting process.
    """
    
    # These fields will be properly implemented when the database models are set up
    # id = Column(Integer, primary_key=True)
    # recipe_id = Column(Integer, ForeignKey("crafting_recipe.id"))
    # recipe = relationship("CraftingRecipe", back_populates="ingredients")
    # item_id = Column(String, nullable=False)
    # quantity = Column(Integer, nullable=False, default=1)
    # is_consumed = Column(Boolean, default=True)
    # is_tool = Column(Boolean, default=False)

    def __init__(
        self, 
        item_id: str, 
        quantity: int = 1,
        is_consumed: bool = True,
        is_tool: bool = False,
        recipe_id: Optional[int] = None
    ):
        """Initialize a crafting ingredient."""
        self.item_id = item_id
        self.quantity = quantity
        self.is_consumed = is_consumed
        self.is_tool = is_tool
        self.recipe_id = recipe_id

    def check_availability(self, inventory: any) -> bool:
        """
        Check if the required quantity of this ingredient is available in the inventory.
        
        Args:
            inventory: The inventory to check
            
        Returns:
            bool: True if the required quantity is available, False otherwise
        """
        # Will be implemented when the inventory system is available
        return False 