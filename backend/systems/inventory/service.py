"""
Service layer for inventory operations.

This module contains business logic for inventory operations, sitting
between the API layer and data access layer.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
import logging
from datetime import datetime
import json
from pathlib import Path

from backend.core.database import db
from backend.systems.inventory.models import Item, Inventory, InventoryItem
from backend.systems.inventory.repository import (
    ItemRepository, InventoryRepository, InventoryItemRepository
)
from backend.systems.inventory.validator import InventoryValidator, ValidationResult
from backend.systems.inventory.utils import RecoveryManager, transfer_item_between_inventories
from backend.systems.inventory.factory import InventoryFactory
from backend.systems.inventory.operations import EquipmentOperations, ItemOperations, TransferOperations
from backend.systems.inventory.export import InventoryExporter

# Configure logger
logger = logging.getLogger(__name__)

class InventoryService:
    """
    Service for inventory system business logic.
    
    This service centralizes operations that involve multiple repositories
    or complex business rules. It delegates specialized operations to focused
    subcomponents.
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
        return InventoryFactory.create_character_inventory(character_id, name)
    
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
        return InventoryFactory.create_container_inventory(
            name, description, capacity, weight_limit, owner_id
        )
    
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
        return InventoryFactory.create_shop_inventory(
            name, owner_id, description, is_public
        )
    
    @staticmethod
    def equip_item(inventory_id: int, item_id: int) -> Tuple[bool, Optional[str]]:
        """
        Equip an item from inventory.
        
        Args:
            inventory_id: Inventory ID
            item_id: Item ID to equip
            
        Returns:
            Tuple of (success, error_message)
        """
        return EquipmentOperations.equip_item(inventory_id, item_id)
    
    @staticmethod
    def unequip_item(inventory_id: int, item_id: int) -> Tuple[bool, Optional[str]]:
        """
        Unequip an item from inventory.
        
        Args:
            inventory_id: Inventory ID
            item_id: Item ID to unequip
            
        Returns:
            Tuple of (success, error_message)
        """
        return EquipmentOperations.unequip_item(inventory_id, item_id)
    
    @staticmethod
    def move_item_to_position(
        inventory_id: int,
        item_id: int,
        position: Dict[str, int]
    ) -> Tuple[bool, Optional[str]]:
        """
        Move an inventory item to a specific position.
        
        Args:
            inventory_id: Inventory ID
            item_id: Item ID to move
            position: Position data (e.g., {"x": 1, "y": 2})
            
        Returns:
            Tuple of (success, error_message)
        """
        return ItemOperations.move_item_to_position(inventory_id, item_id, position)
    
    @staticmethod
    def calculate_inventory_stats(inventory_id: int) -> Dict[str, Any]:
        """
        Calculate statistics for an inventory.
        
        Args:
            inventory_id: Inventory ID
            
        Returns:
            Dictionary of inventory statistics
        """
        return ItemOperations.calculate_inventory_stats(inventory_id)
    
    @staticmethod
    def bulk_add_items(inventory_id: int, items_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add multiple items to an inventory in bulk.
        
        Args:
            inventory_id: Inventory ID
            items_data: List of item data dictionaries, each with "item_id" and "quantity"
            
        Returns:
            Dictionary with results of operation
        """
        return ItemOperations.bulk_add_items(inventory_id, items_data)
    
    @staticmethod
    def split_item_stack(
        inventory_id: int,
        item_id: int,
        quantity: int
    ) -> Tuple[bool, Optional[str], Optional[InventoryItem]]:
        """
        Split an item stack into two stacks.
        
        Args:
            inventory_id: Inventory ID
            item_id: Item ID to split
            quantity: Quantity to split off
            
        Returns:
            Tuple of (success, error_message, new_inventory_item)
        """
        return ItemOperations.split_item_stack(inventory_id, item_id, quantity)
    
    @staticmethod
    def merge_item_stacks(
        inventory_id: int,
        source_item_id: int,
        target_item_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Merge two item stacks into one.
        
        Args:
            inventory_id: Inventory ID
            source_item_id: Source item ID to merge from
            target_item_id: Target item ID to merge into
            
        Returns:
            Tuple of (success, error_message)
        """
        return ItemOperations.merge_item_stacks(
            inventory_id, source_item_id, target_item_id
        )
    
    @staticmethod
    def export_inventory_to_json(inventory_id: int) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Export inventory data to JSON format.
        
        Args:
            inventory_id: Inventory ID
            
        Returns:
            Tuple of (success, error_message, data)
        """
        return InventoryExporter.export_to_json(inventory_id)
    
    @staticmethod
    def import_inventory_from_json(data: Dict[str, Any], owner_id: Optional[int] = None) -> Tuple[bool, Optional[str], Optional[Inventory]]:
        """
        Import inventory data from JSON format.
        
        Args:
            data: JSON inventory data
            owner_id: Optional new owner ID
            
        Returns:
            Tuple of (success, error_message, imported_inventory)
        """
        return InventoryExporter.import_from_json(data, owner_id)
    
    @staticmethod
    def repair_inventory_data(inventory_id: int) -> Dict[str, Any]:
        """
        Repair inventory data inconsistencies.
        
        Args:
            inventory_id: Inventory ID
            
        Returns:
            Dictionary with repair results
        """
        return RecoveryManager.repair_inventory(inventory_id) 