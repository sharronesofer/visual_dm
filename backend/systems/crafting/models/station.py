"""
CraftingStation Model

Defines the structure and behavior of crafting stations.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.orm import relationship

# Import the base model/db setup when available
# from backend.database import Base


class CraftingStation:
    """
    Represents a crafting station in the game.
    
    A crafting station is a location or object where certain recipes can be crafted.
    Examples include forge, alchemy table, cooking fire, etc.
    """
    
    # These fields will be properly implemented when the database models are set up
    # id = Column(Integer, primary_key=True)
    # name = Column(String, nullable=False)
    # description = Column(String)
    # location_id = Column(String, nullable=True)  # If tied to a specific location
    # is_portable = Column(Boolean, default=False)
    # skill_bonuses = Column(JSON, default=dict)  # e.g., {"blacksmithing": 5}
    # compatible_recipes = Column(JSON, default=list)  # List of recipe types it supports
    # is_enabled = Column(Boolean, default=True)
    # metadata = Column(JSON, default=dict)

    def __init__(
        self,
        name: str,
        description: str = "",
        location_id: Optional[str] = None,
        is_portable: bool = False,
        skill_bonuses: Optional[Dict[str, int]] = None,
        compatible_recipes: Optional[List[str]] = None,
        is_enabled: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a crafting station."""
        self.name = name
        self.description = description
        self.location_id = location_id
        self.is_portable = is_portable
        self.skill_bonuses = skill_bonuses or {}
        self.compatible_recipes = compatible_recipes or []
        self.is_enabled = is_enabled
        self.metadata = metadata or {}

    def can_craft_recipe(self, recipe: any) -> bool:
        """
        Check if a recipe can be crafted at this station.
        
        Args:
            recipe: The recipe to check
            
        Returns:
            bool: True if the recipe can be crafted at this station, False otherwise
        """
        # Will be implemented when the recipe system is available
        if not hasattr(recipe, 'station_required'):
            return False
            
        if not recipe.station_required:
            # If no station is required, it can be crafted anywhere
            return True
            
        # Check if the station is compatible with the recipe
        return recipe.station_required == self.name or recipe.station_required in self.compatible_recipes

    def get_skill_bonus(self, skill_name: str) -> int:
        """
        Get the bonus this station provides for a specific skill.
        
        Args:
            skill_name: The name of the skill
            
        Returns:
            int: The bonus value (0 if no bonus)
        """
        return self.skill_bonuses.get(skill_name, 0) 