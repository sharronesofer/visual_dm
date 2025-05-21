"""
CraftingResult Model

Defines the structure and behavior of crafting results.
"""
from typing import Optional
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship

# Import the base model/db setup when available
# from backend.database import Base


class CraftingResult:
    """
    Represents a potential result from a crafting recipe.
    
    A result defines what item is produced, how many are created,
    and the probability of getting this result.
    """
    
    # These fields will be properly implemented when the database models are set up
    # id = Column(Integer, primary_key=True)
    # recipe_id = Column(Integer, ForeignKey("crafting_recipe.id"))
    # recipe = relationship("CraftingRecipe", back_populates="results")
    # item_id = Column(String, nullable=False)
    # quantity = Column(Integer, nullable=False, default=1)
    # probability = Column(Float, default=1.0)  # 0.0 to 1.0

    def __init__(
        self, 
        item_id: str, 
        quantity: int = 1,
        probability: float = 1.0,
        recipe_id: Optional[int] = None
    ):
        """Initialize a crafting result."""
        self.item_id = item_id
        self.quantity = quantity
        self.probability = max(0.0, min(1.0, probability))  # Clamp between 0 and 1
        self.recipe_id = recipe_id

    def get_item_details(self) -> dict:
        """
        Get the details of the result item.
        
        Returns:
            dict: Item details including id, name, description, etc.
        """
        # Will be implemented when the item system is available
        return {"id": self.item_id, "quantity": self.quantity} 