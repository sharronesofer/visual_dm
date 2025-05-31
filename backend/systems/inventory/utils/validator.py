"""
Validator module for inventory operations.

This module provides validation logic for inventory operations,
ensuring data integrity and business rule compliance.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
import logging
from dataclasses import dataclass

from backend.systems.inventory.models import Item, Inventory, InventoryItem
from backend.systems.inventory.repositories import ItemRepository, InventoryRepository

# Configure logger
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Data class representing a validation result."""
    is_valid: bool
    error_message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    
    @property
    def is_error(self) -> bool:
        """Return True if validation failed."""
        return not self.is_valid
        
    @classmethod
    def success(cls, data: Optional[Dict[str, Any]] = None) -> 'ValidationResult':
        """Create a successful validation result."""
        return cls(is_valid=True, data=data)
        
    @classmethod
    def error(cls, message: str, data: Optional[Dict[str, Any]] = None) -> 'ValidationResult':
        """Create a failed validation result with error message."""
        return cls(is_valid=False, error_message=message, data=data)

class InventoryValidator:
    """
    Validator class for inventory operations.
    
    Provides methods to validate various inventory operations
    like adding items, transferring items, etc.
    """
    
    @staticmethod
    def validate_inventory_exists(inventory_id: int) -> ValidationResult:
        """
        Validate that an inventory exists.
        
        Args:
            inventory_id: ID of the inventory to check
            
        Returns:
            ValidationResult indicating success or failure
        """
        inventory = InventoryRepository.get_inventory(inventory_id)
        if not inventory:
            return ValidationResult.error(f"Inventory {inventory_id} not found")
            
        return ValidationResult.success({"inventory": inventory})
        
    @staticmethod
    def validate_item_exists(item_id: int) -> ValidationResult:
        """
        Validate that an item exists.
        
        Args:
            item_id: ID of the item to check
            
        Returns:
            ValidationResult indicating success or failure
        """
        item = ItemRepository.get_item(item_id)
        if not item:
            return ValidationResult.error(f"Item {item_id} not found")
            
        return ValidationResult.success({"item": item})
        
    @staticmethod
    def validate_add_item(inventory_id: int, item_id: int, quantity: int) -> ValidationResult:
        """
        Validate adding an item to an inventory.
        
        Args:
            inventory_id: Inventory ID
            item_id: Item ID
            quantity: Quantity to add
            
        Returns:
            ValidationResult indicating success or failure
        """
        # Check inventory exists
        inventory_result = InventoryValidator.validate_inventory_exists(inventory_id)
        if inventory_result.is_error:
            return inventory_result
            
        # Check item exists
        item_result = InventoryValidator.validate_item_exists(item_id)
        if item_result.is_error:
            return item_result
            
        # Check quantity is positive
        if quantity <= 0:
            return ValidationResult.error("Quantity must be positive")
            
        inventory = inventory_result.data["inventory"]
        item = item_result.data["item"]
        
        # Check capacity limit
        current_item_count = sum([inv_item.quantity for inv_item in inventory.items])
        if inventory.capacity is not None and current_item_count + quantity > inventory.capacity:
            return ValidationResult.error(
                f"Adding {quantity} of this item would exceed inventory capacity of {inventory.capacity}"
            )
            
        # Check weight limit
        current_weight = sum([inv_item.item.weight * inv_item.quantity for inv_item in inventory.items])
        new_weight = current_weight + (item.weight * quantity)
        if inventory.weight_limit is not None and new_weight > inventory.weight_limit:
            return ValidationResult.error(
                f"Adding {quantity} of this item would exceed inventory weight limit of {inventory.weight_limit}"
            )
            
        return ValidationResult.success({
            "inventory": inventory,
            "item": item,
            "quantity": quantity
        })
        
    @staticmethod
    def validate_remove_item(inventory_id: int, inventory_item_id: int, quantity: int) -> ValidationResult:
        """
        Validate removing an item from an inventory.
        
        Args:
            inventory_id: Inventory ID
            inventory_item_id: Inventory item ID
            quantity: Quantity to remove
            
        Returns:
            ValidationResult indicating success or failure
        """
        # Check inventory exists
        inventory_result = InventoryValidator.validate_inventory_exists(inventory_id)
        if inventory_result.is_error:
            return inventory_result
            
        # Check quantity is positive
        if quantity <= 0:
            return ValidationResult.error("Quantity must be positive")
            
        inventory = inventory_result.data["inventory"]
        
        # Find the inventory item
        inventory_item = None
        for inv_item in inventory.items:
            if inv_item.id == inventory_item_id:
                inventory_item = inv_item
                break
                
        if not inventory_item:
            return ValidationResult.error(f"Item {inventory_item_id} not found in inventory {inventory_id}")
            
        # Check quantity
        if quantity > inventory_item.quantity:
            return ValidationResult.error(
                f"Cannot remove {quantity} items when only {inventory_item.quantity} are available"
            )
            
        return ValidationResult.success({
            "inventory": inventory,
            "inventory_item": inventory_item,
            "quantity": quantity
        })
        
    @staticmethod
    def validate_transfer_item(from_inventory_id: int, to_inventory_id: int, 
                            inventory_item_id: int, quantity: int) -> ValidationResult:
        """
        Validate transferring an item between inventories.
        
        Args:
            from_inventory_id: Source inventory ID
            to_inventory_id: Destination inventory ID
            inventory_item_id: Inventory item ID to transfer
            quantity: Quantity to transfer
            
        Returns:
            ValidationResult indicating success or failure
        """
        # Check removal is valid
        remove_result = InventoryValidator.validate_remove_item(
            from_inventory_id, inventory_item_id, quantity
        )
        if remove_result.is_error:
            return remove_result
            
        # Check destination inventory exists
        to_inventory_result = InventoryValidator.validate_inventory_exists(to_inventory_id)
        if to_inventory_result.is_error:
            return to_inventory_result
            
        inventory_item = remove_result.data["inventory_item"]
        item_id = inventory_item.item_id
        
        # Check addition is valid
        add_result = InventoryValidator.validate_add_item(
            to_inventory_id, item_id, quantity
        )
        if add_result.is_error:
            return add_result
            
        return ValidationResult.success({
            "from_inventory_id": from_inventory_id,
            "to_inventory_id": to_inventory_id,
            "inventory_item": inventory_item,
            "quantity": quantity
        })
        
    @staticmethod
    def validate_equip_item(inventory_id: int, inventory_item_id: int) -> ValidationResult:
        """
        Validate equipping an item.
        
        Args:
            inventory_id: Inventory ID
            inventory_item_id: Inventory item ID to equip
            
        Returns:
            ValidationResult indicating success or failure
        """
        # Check inventory exists
        inventory_result = InventoryValidator.validate_inventory_exists(inventory_id)
        if inventory_result.is_error:
            return inventory_result
            
        inventory = inventory_result.data["inventory"]
        
        # Find the inventory item
        inventory_item = None
        for inv_item in inventory.items:
            if inv_item.id == inventory_item_id:
                inventory_item = inv_item
                break
                
        if not inventory_item:
            return ValidationResult.error(f"Item {inventory_item_id} not found in inventory {inventory_id}")
            
        # Check if already equipped
        if inventory_item.is_equipped:
            return ValidationResult.error("Item is already equipped")
            
        # Add other equipment validation rules here
        # For example, checking if the item is equippable, if the character has required stats, etc.
        
        return ValidationResult.success({
            "inventory": inventory,
            "inventory_item": inventory_item
        })
        
    @staticmethod
    def validate_unequip_item(inventory_id: int, inventory_item_id: int) -> ValidationResult:
        """
        Validate unequipping an item.
        
        Args:
            inventory_id: Inventory ID
            inventory_item_id: Inventory item ID to unequip
            
        Returns:
            ValidationResult indicating success or failure
        """
        # Check inventory exists
        inventory_result = InventoryValidator.validate_inventory_exists(inventory_id)
        if inventory_result.is_error:
            return inventory_result
            
        inventory = inventory_result.data["inventory"]
        
        # Find the inventory item
        inventory_item = None
        for inv_item in inventory.items:
            if inv_item.id == inventory_item_id:
                inventory_item = inv_item
                break
                
        if not inventory_item:
            return ValidationResult.error(f"Item {inventory_item_id} not found in inventory {inventory_id}")
            
        # Check if already unequipped
        if not inventory_item.is_equipped:
            return ValidationResult.error("Item is not equipped")
            
        return ValidationResult.success({
            "inventory": inventory,
            "inventory_item": inventory_item
        }) 