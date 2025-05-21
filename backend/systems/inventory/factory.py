"""
Factory module for creating inventory objects.

This module provides factory methods for creating different types of inventories.
"""

from typing import Dict, Any, Optional
import logging

from backend.systems.inventory.models import Inventory
from backend.systems.inventory.repository import InventoryRepository

# Configure logger
logger = logging.getLogger(__name__)

class InventoryFactory:
    """
    Factory class for creating different types of inventories.
    
    This centralizes the creation logic for different inventory types,
    ensuring consistent configuration and properties.
    """
    
    @staticmethod
    def create_character_inventory(character_id: int, name: Optional[str] = None) -> Inventory:
        """
        Create a new inventory for a character.
        
        Args:
            character_id: Character ID
            name: Optional inventory name (defaults to "Character Inventory")
            
        Returns:
            Created inventory
        """
        inventory_data = {
            "name": name or f"Character Inventory",
            "description": f"Main inventory for character #{character_id}",
            "inventory_type": "character",
            "owner_id": character_id,
            "capacity": 50,  # Default capacity
            "weight_limit": 150.0,  # Default weight limit in pounds
            "is_public": False
        }
        
        return InventoryRepository.create_inventory(inventory_data)
    
    @staticmethod
    def create_container_inventory(
        name: str,
        description: Optional[str] = None,
        capacity: Optional[int] = None,
        weight_limit: Optional[float] = None,
        owner_id: Optional[int] = None
    ) -> Inventory:
        """
        Create a new container inventory (chest, backpack, etc).
        
        Args:
            name: Container name
            description: Optional description
            capacity: Optional item capacity
            weight_limit: Optional weight limit
            owner_id: Optional owner ID
            
        Returns:
            Created inventory
        """
        inventory_data = {
            "name": name,
            "description": description or f"{name} container",
            "inventory_type": "container",
            "capacity": capacity,
            "weight_limit": weight_limit,
            "owner_id": owner_id,
            "is_public": False
        }
        
        return InventoryRepository.create_inventory(inventory_data)
    
    @staticmethod
    def create_shop_inventory(
        name: str,
        owner_id: int,
        description: Optional[str] = None,
        is_public: bool = True
    ) -> Inventory:
        """
        Create a new shop inventory.
        
        Args:
            name: Shop name
            owner_id: Shop owner ID
            description: Optional description
            is_public: Whether the shop inventory is public
            
        Returns:
            Created inventory
        """
        inventory_data = {
            "name": name,
            "description": description or f"{name} shop inventory",
            "inventory_type": "shop",
            "owner_id": owner_id,
            "capacity": None,  # Shops don't have capacity limits
            "weight_limit": None,  # Shops don't have weight limits
            "is_public": is_public
        }
        
        return InventoryRepository.create_inventory(inventory_data) 