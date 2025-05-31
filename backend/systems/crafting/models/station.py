"""
CraftingStation Model

Defines the structure and behavior of crafting stations.
"""
from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, Boolean, JSON, Float
from sqlalchemy.orm import relationship

from backend.infrastructure.database import BaseModel

class CraftingStation(BaseModel):
    """
    Represents a crafting station in the game.
    
    A station provides the necessary equipment and environment for crafting
    specific types of items. Stations can have levels, special capabilities,
    and requirements for their use.
    """
    
    __tablename__ = "crafting_stations"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Station identification
    name = Column(String, nullable=False, index=True)
    description = Column(String, default="")
    station_type = Column(String, nullable=False, index=True)  # smithy, alchemy, etc.
    
    # Station properties
    level = Column(Integer, default=1, index=True)
    capacity = Column(Integer, default=1)  # How many can use simultaneously
    efficiency_bonus = Column(Float, default=1.0)  # Speed multiplier
    quality_bonus = Column(Float, default=0.0)  # Quality improvement chance
    
    # Station state
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)  # Can others use it
    
    # Location and ownership
    location_id = Column(String, nullable=True, index=True)
    owner_id = Column(String, nullable=True, index=True)
    
    # Advanced features
    upgrade_level = Column(Integer, default=0)
    allowed_categories = Column(JSON, default=list)  # What can be crafted
    required_materials = Column(JSON, default=dict)  # Materials to build/upgrade
    special_abilities = Column(JSON, default=list)  # Special crafting abilities
    maintenance_cost = Column(JSON, default=dict)  # Upkeep requirements
    
    # Additional data
    station_metadata = Column(JSON, default=dict)

    def can_craft_recipe(self, recipe) -> bool:
        """
        Check if this station can be used to craft a specific recipe.
        
        Args:
            recipe: The recipe to check compatibility with
            
        Returns:
            bool: True if the station can craft this recipe
        """
        if not self.is_active:
            return False
            
        # Check if station is required and matches
        if hasattr(recipe, 'station_required'):
            if recipe.station_required and recipe.station_required != self.station_type:
                return False
                
        # Check if station level is sufficient
        if hasattr(recipe, 'station_level'):
            if recipe.station_level > self.level:
                return False
                
        return True
        
    def get_efficiency_multiplier(self) -> float:
        """
        Get the efficiency multiplier for crafting speed.
        
        Returns:
            float: Multiplier for crafting time (higher = faster)
        """
        base_efficiency = self.efficiency_bonus
        level_bonus = 1.0 + (self.level - 1) * 0.1  # 10% per level
        upgrade_bonus = 1.0 + self.upgrade_level * 0.05  # 5% per upgrade
        
        return base_efficiency * level_bonus * upgrade_bonus
        
    def get_quality_bonus(self) -> float:
        """
        Get the quality bonus provided by this station.
        
        Returns:
            float: Quality bonus (added to quality calculation)
        """
        base_quality = self.quality_bonus
        level_bonus = self.level * 0.01  # 1% per level
        upgrade_bonus = self.upgrade_level * 0.005  # 0.5% per upgrade
        
        return base_quality + level_bonus + upgrade_bonus
        
    def is_available(self, character_id: Optional[str] = None) -> bool:
        """
        Check if the station is available for use.
        
        Args:
            character_id: Optional ID of the character wanting to use the station
            
        Returns:
            bool: True if the station is available
        """
        if not self.is_active:
            return False
            
        # Check if it's public or owned by the character
        if not self.is_public and self.owner_id != character_id:
            return False
            
        # TODO: Check current usage vs capacity when reservation system is implemented
        return True
        
    def upgrade(self, upgrade_type: str = "level") -> Dict[str, Any]:
        """
        Upgrade the station.
        
        Args:
            upgrade_type: Type of upgrade (level, efficiency, quality, capacity)
            
        Returns:
            Dictionary with upgrade results
        """
        if upgrade_type == "level":
            old_level = self.level
            self.level += 1
            return {
                "success": True,
                "upgrade_type": "level",
                "old_value": old_level,
                "new_value": self.level
            }
        elif upgrade_type == "upgrade_level":
            old_upgrade = self.upgrade_level
            self.upgrade_level += 1
            return {
                "success": True,
                "upgrade_type": "upgrade_level",
                "old_value": old_upgrade,
                "new_value": self.upgrade_level
            }
        else:
            return {
                "success": False,
                "error": f"Unknown upgrade type: {upgrade_type}"
            }
            
    def get_allowed_categories(self) -> List[str]:
        """
        Get the list of item categories that can be crafted at this station.
        
        Returns:
            List of allowed crafting categories
        """
        if self.allowed_categories:
            return self.allowed_categories
            
        # Default categories based on station type
        default_categories = {
            "smithy": ["weapons", "armor", "tools"],
            "alchemy": ["potions", "elixirs", "reagents"],
            "workshop": ["tools", "equipment", "misc"],
            "kitchen": ["food", "beverages"],
            "enchanting": ["enchantments", "scrolls", "magical_items"],
            "tannery": ["leather", "armor"],
            "forge": ["weapons", "armor", "tools", "jewelry"]
        }
        
        return default_categories.get(self.station_type, ["misc"])
        
    def get_build_requirements(self) -> Dict[str, Any]:
        """
        Get the materials and requirements needed to build this station.
        
        Returns:
            Dictionary containing build requirements
        """
        return self.required_materials or {}
        
    def calculate_maintenance_cost(self) -> Dict[str, int]:
        """
        Calculate the maintenance cost for this station.
        
        Returns:
            Dictionary of item_id -> quantity needed for maintenance
        """
        base_cost = self.maintenance_cost or {}
        
        # Scale cost by level and upgrade level
        level_multiplier = 1.0 + (self.level - 1) * 0.1
        upgrade_multiplier = 1.0 + self.upgrade_level * 0.05
        
        scaled_cost = {}
        for item_id, quantity in base_cost.items():
            scaled_quantity = int(quantity * level_multiplier * upgrade_multiplier)
            scaled_cost[item_id] = max(1, scaled_quantity)  # Minimum 1
            
        return scaled_cost 