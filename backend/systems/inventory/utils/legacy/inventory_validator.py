"""
Validator for inventory operations in Visual DM.

This module provides validation logic for inventory operations like transfers,
weight limits, slot limits, and inventory type compatibility.
"""
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
import logging
import json
import os
from pathlib import Path

from backend.systems.inventory.models import Inventory, InventoryItem

# Configure logger
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of a validation operation with detailed information"""
    valid: bool
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class InventoryValidator:
    """
    Validator for inventory operations. Enforces business rules
    and constraints for inventory operations including weight limits,
    slot constraints, and inventory type compatibility.
    """
    
    # Cache for item and inventory type configurations
    _item_types_config: Optional[Dict[str, Any]] = None
    _inventory_types_config: Optional[Dict[str, Any]] = None
    
    @classmethod
    def _load_configuration(cls):
        """Load item and inventory type configurations from JSON file"""
        if cls._item_types_config is not None and cls._inventory_types_config is not None:
            return
            
        try:
            config_path = Path(__file__).parent.parent / "data" / "modding" / "item_types.json"
            
            if not config_path.exists():
                logger.warning(f"Item types configuration not found at {config_path}")
                cls._item_types_config = {}
                cls._inventory_types_config = {}
                return
                
            with open(config_path, "r") as f:
                config_data = json.load(f)
                
            cls._item_types_config = {item["id"]: item for item in config_data.get("item_types", [])}
            cls._inventory_types_config = {inv["id"]: inv for inv in config_data.get("inventory_types", [])}
            
            logger.info(f"Loaded {len(cls._item_types_config)} item types and "
                        f"{len(cls._inventory_types_config)} inventory types")
                        
        except Exception as e:
            logger.error(f"Error loading item type configuration: {str(e)}")
            cls._item_types_config = {}
            cls._inventory_types_config = {}
    
    @classmethod
    def get_item_type_config(cls, item_type: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific item type"""
        cls._load_configuration()
        return cls._item_types_config.get(item_type)
    
    @classmethod
    def get_inventory_type_config(cls, inventory_type: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific inventory type"""
        cls._load_configuration()
        return cls._inventory_types_config.get(inventory_type)
    
    @classmethod
    def validate_weight_limit(cls, inventory: Any, item: Any, quantity: int) -> ValidationResult:
        """
        Validate if adding an item respects the inventory's weight limit
        
        Args:
            inventory: Inventory object to validate
            item: Item to add to inventory
            quantity: Quantity of item to add
            
        Returns:
            ValidationResult with validation outcome
        """
        # Skip validation if inventory has no weight limit
        if inventory.weight_limit is None:
            return ValidationResult(valid=True)
            
        # Calculate item weight
        item_weight = item.weight * quantity
        
        # Calculate current inventory weight
        current_weight = sum(inv_item.item.weight * inv_item.quantity 
                            for inv_item in inventory.items)
        
        # Check if adding item would exceed weight limit
        new_weight = current_weight + item_weight
        
        if new_weight > inventory.weight_limit:
            excess_weight = new_weight - inventory.weight_limit
            return ValidationResult(
                valid=False,
                error_message=f"Adding {quantity}x {item.name} would exceed inventory weight limit by {excess_weight:.2f} units",
                details={
                    "current_weight": current_weight,
                    "item_weight": item_weight,
                    "new_weight": new_weight,
                    "weight_limit": inventory.weight_limit,
                    "excess_weight": excess_weight
                }
            )
            
        return ValidationResult(
            valid=True,
            details={
                "current_weight": current_weight,
                "item_weight": item_weight,
                "new_weight": new_weight,
                "weight_limit": inventory.weight_limit,
                "remaining_capacity": inventory.weight_limit - new_weight
            }
        )
    
    @classmethod
    def validate_slot_limit(cls, inventory: Any, item: Any, quantity: int) -> ValidationResult:
        """
        Validate if adding an item respects the inventory's slot limit
        
        Args:
            inventory: Inventory object to validate
            item: Item to add to inventory
            quantity: Quantity of item to add
            
        Returns:
            ValidationResult with validation outcome
        """
        # Skip validation if inventory is not slot-based
        if not inventory.is_slot_based or inventory.slot_limit is None:
            return ValidationResult(valid=True)
            
        # Get item config to check stackability
        item_type_config = cls.get_item_type_config(item.item_type)
        if item_type_config is None:
            # Fallback if config not available
            is_stackable = getattr(item, "is_stackable", False)
            stack_limit = getattr(item, "stack_limit", 1)
        else:
            is_stackable = item_type_config.get("properties", {}).get("can_be_stacked", False)
            stack_limit = item_type_config.get("properties", {}).get("default_stack_limit", 1)
            
        # For stackable items, check if existing stacks can accommodate the new quantity
        if is_stackable:
            # Find existing item stacks
            existing_stacks = [inv_item for inv_item in inventory.items if inv_item.item_id == item.id]
            
            # Calculate remaining capacity in existing stacks
            remaining_stack_capacity = sum(max(0, stack_limit - inv_item.quantity) 
                                          for inv_item in existing_stacks)
            
            # If existing stacks can hold all new items, no need for new slots
            if remaining_stack_capacity >= quantity:
                return ValidationResult(valid=True)
                
            # Calculate how many new slots needed after filling existing stacks
            remaining_quantity = quantity - remaining_stack_capacity
            new_slots_needed = (remaining_quantity + stack_limit - 1) // stack_limit
        else:
            # Non-stackable items need one slot per item
            new_slots_needed = quantity
            
        # Count current used slots
        used_slots = len(inventory.items)
        
        # Check if there are enough slots available
        if used_slots + new_slots_needed > inventory.slot_limit:
            slots_short = (used_slots + new_slots_needed) - inventory.slot_limit
            return ValidationResult(
                valid=False,
                error_message=f"Not enough slots available. Need {new_slots_needed} more slots for {quantity}x {item.name}, but only have {inventory.slot_limit - used_slots} slots available.",
                details={
                    "used_slots": used_slots,
                    "new_slots_needed": new_slots_needed,
                    "slot_limit": inventory.slot_limit,
                    "slots_short": slots_short,
                    "is_stackable": is_stackable,
                    "stack_limit": stack_limit
                }
            )
            
        return ValidationResult(
            valid=True,
            details={
                "used_slots": used_slots,
                "new_slots_needed": new_slots_needed,
                "slot_limit": inventory.slot_limit,
                "remaining_slots": inventory.slot_limit - used_slots - new_slots_needed,
                "is_stackable": is_stackable,
                "stack_limit": stack_limit
            }
        )
    
    @classmethod
    def validate_inventory_type_compatibility(cls, source_inventory: Any, target_inventory: Any, 
                                             item: Any) -> ValidationResult:
        """
        Validate if an item can be transferred between different inventory types
        
        Args:
            source_inventory: Source inventory for transfer
            target_inventory: Target inventory for transfer
            item: Item to transfer
            
        Returns:
            ValidationResult with validation outcome
        """
        # Get inventory type configurations
        target_type = getattr(target_inventory, "inventory_type", "default")
        target_config = cls.get_inventory_type_config(target_type)
        
        if target_config is None:
            # If no config, assume all transfers are valid
            return ValidationResult(valid=True)
            
        # Check if target inventory is immutable
        if target_config.get("properties", {}).get("immutable", False):
            return ValidationResult(
                valid=False,
                error_message=f"Cannot add items to an immutable inventory type: {target_type}",
                details={
                    "target_inventory_type": target_type,
                    "target_inventory_id": getattr(target_inventory, "id", None)
                }
            )
            
        # Check allowed item types
        allowed_types = target_config.get("properties", {}).get("allowed_item_types", ["all"])
        item_type = getattr(item, "item_type", "misc")
        
        # If "all" is in allowed types, any item is allowed
        if "all" in allowed_types:
            # Check for excluded types (prefixed with !)
            excluded_types = [t[1:] for t in allowed_types if t.startswith("!")]
            if item_type in excluded_types:
                return ValidationResult(
                    valid=False,
                    error_message=f"Items of type '{item_type}' are not allowed in {target_type} inventories",
                    details={
                        "item_type": item_type,
                        "target_inventory_type": target_type,
                        "allowed_types": allowed_types,
                        "excluded_types": excluded_types
                    }
                )
            return ValidationResult(valid=True)
            
        # Check if item type is in allowed types
        if item_type not in allowed_types:
            return ValidationResult(
                valid=False,
                error_message=f"Items of type '{item_type}' are not allowed in {target_type} inventories",
                details={
                    "item_type": item_type,
                    "target_inventory_type": target_type,
                    "allowed_types": allowed_types
                }
            )
            
        return ValidationResult(valid=True)
    
    @classmethod
    def validate_transfer_item(cls, source_inventory: Any, target_inventory: Any, 
                             item: Any, quantity: int) -> ValidationResult:
        """
        Validate if an item transfer is valid
        
        Args:
            source_inventory: Source inventory for transfer
            target_inventory: Target inventory for transfer
            item: Item to transfer
            quantity: Quantity to transfer
            
        Returns:
            ValidationResult with validation outcome
        """
        # Check if source has enough of the item
        source_item = next((inv_item for inv_item in source_inventory.items 
                          if inv_item.item_id == item.id), None)
                          
        if source_item is None or source_item.quantity < quantity:
            available = source_item.quantity if source_item else 0
            return ValidationResult(
                valid=False,
                error_message=f"Not enough items in source inventory. Requested: {quantity}, Available: {available}",
                details={
                    "requested_quantity": quantity,
                    "available_quantity": available,
                    "item_id": item.id,
                    "source_inventory_id": source_inventory.id
                }
            )
            
        # Validate against weight limit
        weight_result = cls.validate_weight_limit(target_inventory, item, quantity)
        if not weight_result.valid:
            return weight_result
            
        # Validate against slot limit
        slot_result = cls.validate_slot_limit(target_inventory, item, quantity)
        if not slot_result.valid:
            return slot_result
            
        # Validate inventory type compatibility
        compatibility_result = cls.validate_inventory_type_compatibility(
            source_inventory, target_inventory, item)
        if not compatibility_result.valid:
            return compatibility_result
            
        # All validations passed
        return ValidationResult(
            valid=True,
            details={
                "source_inventory_id": source_inventory.id,
                "target_inventory_id": target_inventory.id,
                "item_id": item.id,
                "quantity": quantity,
                "weight_validation": weight_result.details,
                "slot_validation": slot_result.details
            }
        )
    
    @classmethod
    def validate_inventory(cls, inventory: Any) -> Dict[str, Any]:
        """
        Validate all aspects of an inventory and provide a comprehensive validation report
        
        Args:
            inventory: Inventory to validate
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "inventory_id": inventory.id,
            "inventory_type": getattr(inventory, "inventory_type", "default"),
            "owner_id": getattr(inventory, "owner_id", None),
            "issues": [],
            "metrics": {
                "total_items": 0,
                "unique_items": 0,
                "total_weight": 0.0,
                "used_slots": 0,
                "weight_capacity_used": 0.0,
                "slot_capacity_used": 0.0
            }
        }
        
        # Calculate used weight
        total_weight = 0.0
        for inv_item in inventory.items:
            item_weight = inv_item.item.weight * inv_item.quantity
            total_weight += item_weight
            results["metrics"]["total_items"] += inv_item.quantity
            
        results["metrics"]["unique_items"] = len(inventory.items)
        results["metrics"]["total_weight"] = total_weight
        results["metrics"]["used_slots"] = len(inventory.items)
        
        # Check weight limit
        if inventory.weight_limit is not None:
            if total_weight > inventory.weight_limit:
                results["valid"] = False
                results["issues"].append({
                    "type": "weight_limit_exceeded",
                    "message": f"Inventory weight limit exceeded. Current: {total_weight:.2f}, Limit: {inventory.weight_limit:.2f}",
                    "details": {
                        "current_weight": total_weight,
                        "weight_limit": inventory.weight_limit,
                        "excess_weight": total_weight - inventory.weight_limit
                    }
                })
            results["metrics"]["weight_capacity_used"] = (
                total_weight / inventory.weight_limit if inventory.weight_limit > 0 else 0.0
            )
            
        # Check slot limit for slot-based inventories
        if inventory.is_slot_based and inventory.slot_limit is not None:
            used_slots = len(inventory.items)
            if used_slots > inventory.slot_limit:
                results["valid"] = False
                results["issues"].append({
                    "type": "slot_limit_exceeded",
                    "message": f"Inventory slot limit exceeded. Used: {used_slots}, Limit: {inventory.slot_limit}",
                    "details": {
                        "used_slots": used_slots,
                        "slot_limit": inventory.slot_limit,
                        "excess_slots": used_slots - inventory.slot_limit
                    }
                })
            results["metrics"]["slot_capacity_used"] = (
                used_slots / inventory.slot_limit if inventory.slot_limit > 0 else 0.0
            )
            
        # Check for items that shouldn't be in this inventory type
        inventory_type = getattr(inventory, "inventory_type", "default")
        inventory_config = cls.get_inventory_type_config(inventory_type)
        
        if inventory_config is not None:
            allowed_types = inventory_config.get("properties", {}).get("allowed_item_types", ["all"])
            has_all_allowed = "all" in allowed_types
            excluded_types = [t[1:] for t in allowed_types if t.startswith("!")] if has_all_allowed else []
            
            for inv_item in inventory.items:
                item_type = getattr(inv_item.item, "item_type", "misc")
                
                is_allowed = False
                if has_all_allowed:
                    is_allowed = item_type not in excluded_types
                else:
                    is_allowed = item_type in allowed_types
                    
                if not is_allowed:
                    results["valid"] = False
                    results["issues"].append({
                        "type": "invalid_item_type",
                        "message": f"Item type '{item_type}' not allowed in {inventory_type} inventory",
                        "details": {
                            "item_id": inv_item.item_id,
                            "item_type": item_type,
                            "inventory_type": inventory_type,
                            "allowed_types": allowed_types,
                            "excluded_types": excluded_types if has_all_allowed else []
                        }
                    })
                
        return results 
