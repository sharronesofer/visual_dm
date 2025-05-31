"""
CraftingRecipe Model

Defines the structure and behavior of crafting recipes.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, JSON, Float
from sqlalchemy.orm import relationship

from backend.infrastructure.database import BaseModel

class CraftingRecipe(BaseModel):
    """
    Represents a crafting recipe in the game.
    
    A recipe defines the ingredients, tools, and skills needed to craft
    an item, as well as the resulting item(s) and any specific requirements.
    """
    
    __tablename__ = "crafting_recipes"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Recipe identification and basic info
    name = Column(String, nullable=False, index=True)
    description = Column(String, default="")
    
    # Skill requirements
    skill_required = Column(String, nullable=True, index=True)
    min_skill_level = Column(Integer, default=1)
    
    # Crafting mechanics
    crafting_time = Column(Integer, default=0)  # in seconds
    base_experience = Column(Integer, default=10)  # experience gained
    
    # Station requirements
    station_required = Column(String, nullable=True, index=True)
    station_level = Column(Integer, default=0)
    
    # Recipe state
    is_hidden = Column(Boolean, default=False, index=True)
    is_enabled = Column(Boolean, default=True, index=True)
    
    # Additional data
    recipe_metadata = Column(JSON, default=dict)
    discovery_methods = Column(JSON, default=list)
    
    # Relationships
    ingredients = relationship("CraftingIngredient", back_populates="recipe", cascade="all, delete-orphan")
    results = relationship("CraftingResult", back_populates="recipe", cascade="all, delete-orphan")

    def add_ingredient(self, item_id: str, quantity: int, is_consumed: bool = True, substitution_groups: Optional[Dict] = None) -> None:
        """Add an ingredient to the recipe."""
        from backend.systems.crafting.models.ingredient import CraftingIngredient
        ingredient = CraftingIngredient(
            item_id=item_id,
            quantity=quantity,
            is_consumed=is_consumed,
            substitution_groups=substitution_groups or {},
            recipe=self
        )
        self.ingredients.append(ingredient)

    def add_result(self, item_id: str, quantity: int, probability: float = 1.0) -> None:
        """Add a result item to the recipe."""
        from backend.systems.crafting.models.result import CraftingResult
        result = CraftingResult(
            item_id=item_id,
            quantity=quantity,
            probability=probability,
            recipe=self
        )
        self.results.append(result)

    def can_craft(self, inventory: Any, character_skills: Dict[str, int]) -> bool:
        """
        Check if the recipe can be crafted with the given inventory and skills.
        
        Args:
            inventory: The inventory to check for ingredients
            character_skills: Dictionary of skill names to levels
            
        Returns:
            bool: True if the recipe can be crafted, False otherwise
        """
        # Check skill requirements
        if self.skill_required:
            if self.skill_required not in character_skills:
                return False
            if character_skills[self.skill_required] < self.min_skill_level:
                return False
        
        # Check if recipe is enabled
        if not self.is_enabled:
            return False
            
        # TODO: Check ingredient availability when inventory system is integrated
        # For now, return True if skill requirements are met
        return True
        
    def get_required_ingredients(self) -> List[Dict[str, Any]]:
        """Get a list of required ingredients with details."""
        return [
            {
                "item_id": ingredient.item_id,
                "quantity": ingredient.quantity,
                "is_consumed": ingredient.is_consumed,
                "substitution_groups": ingredient.substitution_groups
            }
            for ingredient in self.ingredients
        ]
        
    def get_possible_results(self) -> List[Dict[str, Any]]:
        """Get a list of possible crafting results."""
        return [
            {
                "item_id": result.item_id,
                "quantity": result.quantity,
                "probability": result.probability
            }
            for result in self.results
        ] 