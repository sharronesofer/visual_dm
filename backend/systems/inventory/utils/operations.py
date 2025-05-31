"""
Specialized operations for inventory system.

This module provides specialized operation classes for different aspects of inventory
management, such as equipment, item manipulation, and transfers.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
import logging
from datetime import datetime

from backend.infrastructure.database import db
from backend.systems.inventory.models import Item, Inventory, InventoryItem
from backend.systems.inventory.repositories import (
    ItemRepository, InventoryRepository, InventoryItemRepository
)
from backend.systems.inventory.validator import InventoryValidator, ValidationResult
from backend.systems.inventory.utils import transfer_item_between_inventories, validate_grid_position

# Configure logger
logger = logging.getLogger(__name__)

class EquipmentOperations:
    """
    Operations for equipping and unequipping items.
    """
    
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
        try:
            # Get inventory and item
            inventory = InventoryRepository.get_inventory(inventory_id)
            if not inventory:
                return False, "Inventory not found"
                
            inventory_item = InventoryItemRepository.get_inventory_item(inventory_id, item_id)
            if not inventory_item:
                return False, "Item not found in inventory"
                
            # Get item details
            item = inventory_item.item
                
            # Check if already equipped
            if inventory_item.is_equipped:
                return True, None  # Already equipped
                
            # Validate equipment (example: character can only equip one helmet at a time)
            validation = InventoryValidator.validate_equip_item(inventory, item)
            if not validation.valid:
                return False, validation.error_message or "Cannot equip this item"
                
            # Update inventory item
            InventoryItemRepository.update_inventory_item(
                inventory_id, 
                item_id, 
                {"is_equipped": True}
            )
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error equipping item {item_id} in inventory {inventory_id}: {str(e)}")
            return False, f"Error: {str(e)}"
    
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
        try:
            # Get inventory item
            inventory_item = InventoryItemRepository.get_inventory_item(inventory_id, item_id)
            if not inventory_item:
                return False, "Item not found in inventory"
                
            # Check if already unequipped
            if not inventory_item.is_equipped:
                return True, None  # Already unequipped
                
            # Update inventory item
            InventoryItemRepository.update_inventory_item(
                inventory_id, 
                item_id, 
                {"is_equipped": False}
            )
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error unequipping item {item_id} in inventory {inventory_id}: {str(e)}")
            return False, f"Error: {str(e)}"
            
class ItemOperations:
    """
    Operations for managing items within an inventory.
    """
    
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
        try:
            # Get inventory item
            inventory_item = InventoryItemRepository.get_inventory_item(inventory_id, item_id)
            if not inventory_item:
                return False, "Item not found in inventory"
                
            # Import grid validation utilities
            from backend.systems.inventory.utils import validate_grid_position
            
            # Get item size from properties if available
            item = inventory_item.item
            item_size = None
            if item.properties and isinstance(item.properties, dict):
                width = item.properties.get('width', 1)
                height = item.properties.get('height', 1)
                item_size = {"width": width, "height": height}
            
            # Validate position is available
            is_valid, error_message = validate_grid_position(
                inventory_id, 
                position, 
                item_size
            )
            
            if not is_valid:
                return False, f"Invalid position: {error_message}"
                
            # Update inventory item position
            InventoryItemRepository.update_inventory_item(
                inventory_id, 
                item_id, 
                {"position": position}
            )
            
            # Emit position change event
            from backend.systems.inventory.events import emit_event, InventoryEventType
            emit_event(InventoryEventType.ITEM_UPDATED, {
                "inventory_id": inventory_id,
                "inventory_item_id": item_id,
                "changes": {"position": position}
            })
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error moving item {item_id} in inventory {inventory_id}: {str(e)}")
            return False, f"Error: {str(e)}"

    @staticmethod
    def calculate_inventory_stats(inventory_id: int) -> Dict[str, Any]:
        """
        Calculate statistics for an inventory.
        
        Args:
            inventory_id: Inventory ID
            
        Returns:
            Dictionary of inventory statistics
        """
        try:
            inventory = InventoryRepository.get_inventory(inventory_id)
            if not inventory:
                return {"error": "Inventory not found"}
                
            items = inventory.items
            
            # Calculate stats
            stats = {
                "total_items": len(items),
                "total_weight": sum(item.quantity * item.item.weight for item in items),
                "total_value": sum(item.quantity * item.item.value for item in items),
                "equipped_items": sum(1 for item in items if item.is_equipped),
                "categories": {},
                "weight_capacity_used": 0,
                "slot_capacity_used": 0
            }
            
            # Calculate category breakdown
            for item in items:
                category = item.item.category.name if hasattr(item.item.category, 'name') else str(item.item.category)
                if category not in stats["categories"]:
                    stats["categories"][category] = 0
                stats["categories"][category] += item.quantity
                
            # Calculate capacity percentages
            if inventory.weight_limit:
                stats["weight_capacity_used"] = min(
                    100, 
                    round((stats["total_weight"] / inventory.weight_limit) * 100, 1)
                )
                
            if inventory.capacity:
                stats["slot_capacity_used"] = min(
                    100,
                    round((stats["total_items"] / inventory.capacity) * 100, 1)
                )
                
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating inventory stats for {inventory_id}: {str(e)}")
            return {"error": str(e)}
            
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
        result = {
            "success_count": 0,
            "error_count": 0,
            "errors": []
        }
        
        try:
            inventory = InventoryRepository.get_inventory(inventory_id)
            if not inventory:
                result["errors"].append({"message": "Inventory not found"})
                result["error_count"] = len(items_data)
                return result
                
            # Start transaction
            with db.session.begin():
                for item_data in items_data:
                    item_id = item_data.get("item_id")
                    quantity = item_data.get("quantity", 1)
                    
                    if not item_id:
                        result["errors"].append({
                            "item_data": item_data,
                            "message": "Missing item_id"
                        })
                        result["error_count"] += 1
                        continue
                        
                    # Get item
                    item = ItemRepository.get_item(item_id)
                    if not item:
                        result["errors"].append({
                            "item_id": item_id,
                            "message": "Item not found"
                        })
                        result["error_count"] += 1
                        continue
                        
                    # Validate
                    validator = InventoryValidator()
                    validation = validator.validate_add_item(inventory, item, quantity)
                    if not validation.valid:
                        result["errors"].append({
                            "item_id": item_id,
                            "message": validation.error_message or "Validation failed"
                        })
                        result["error_count"] += 1
                        continue
                        
                    # Add item
                    try:
                        InventoryItemRepository.add_item_to_inventory(
                            inventory_id,
                            item_id,
                            quantity,
                            False,
                            session=db.session
                        )
                        result["success_count"] += 1
                    except Exception as e:
                        result["errors"].append({
                            "item_id": item_id,
                            "message": str(e)
                        })
                        result["error_count"] += 1
                        
            return result
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in bulk_add_items: {str(e)}")
            result["errors"].append({"message": f"Transaction error: {str(e)}"})
            result["error_count"] = len(items_data) - result["success_count"]
            return result
            
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
        try:
            # Get inventory item
            inventory_item = InventoryItemRepository.get_inventory_item(inventory_id, item_id)
            if not inventory_item:
                return False, "Item not found in inventory", None
                
            # Validate quantity
            if inventory_item.quantity <= quantity:
                return False, "Cannot split: not enough items in stack", None
                
            # Get item
            item = inventory_item.item
            if not item.is_stackable:
                return False, "Item is not stackable", None
                
            # Create new inventory item with split quantity
            with db.session.begin():
                # Reduce quantity from original stack
                InventoryItemRepository.update_inventory_item(
                    inventory_id,
                    item_id,
                    {"quantity": inventory_item.quantity - quantity}
                )
                
                # Create new stack with split quantity
                new_item = InventoryItemRepository.add_item_to_inventory(
                    inventory_id,
                    item_id,
                    quantity,
                    is_equipped=False,
                    session=db.session
                )
                
            return True, None, new_item
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error splitting item {item_id} in inventory {inventory_id}: {str(e)}")
            return False, f"Error: {str(e)}", None
            
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
        try:
            # Get inventory items
            source_item = InventoryItemRepository.get_inventory_item(inventory_id, source_item_id)
            target_item = InventoryItemRepository.get_inventory_item(inventory_id, target_item_id)
            
            if not source_item:
                return False, "Source item not found in inventory"
                
            if not target_item:
                return False, "Target item not found in inventory"
                
            # Validate items are the same type
            if source_item.item_id != target_item.item_id:
                return False, "Cannot merge different item types"
                
            # Validate item is stackable
            if not source_item.item.is_stackable:
                return False, "Item is not stackable"
                
            # Merge stacks
            with db.session.begin():
                # Update target with combined quantity
                InventoryItemRepository.update_inventory_item(
                    inventory_id,
                    target_item_id,
                    {"quantity": target_item.quantity + source_item.quantity}
                )
                
                # Remove source
                InventoryItemRepository.remove_item_from_inventory(
                    inventory_id,
                    source_item_id,
                    source_item.quantity,
                    session=db.session
                )
                
            return True, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error merging items in inventory {inventory_id}: {str(e)}")
            return False, f"Error: {str(e)}"
            
    @staticmethod
    def swap_items(
        inventory_id: int,
        item_id1: int,
        item_id2: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Swap positions of two items in the same inventory.
        
        Args:
            inventory_id: Inventory ID
            item_id1: First item ID
            item_id2: Second item ID
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Get inventory items
            item1 = db.session.query(InventoryItem).filter_by(
                inventory_id=inventory_id,
                id=item_id1
            ).first()
            
            item2 = db.session.query(InventoryItem).filter_by(
                inventory_id=inventory_id,
                id=item_id2
            ).first()
            
            if not item1:
                return False, f"Item {item_id1} not found in inventory {inventory_id}"
                
            if not item2:
                return False, f"Item {item_id2} not found in inventory {inventory_id}"
                
            # Swap positions
            with db.session.begin():
                temp_position = item1.position
                item1.position = item2.position
                item2.position = temp_position
                
                # Update timestamps
                now = datetime.utcnow()
                item1.updated_at = now
                item2.updated_at = now
                
                # Emit event for item updates
                from backend.systems.inventory.events import InventoryEventType, emit_event
                
                emit_event(InventoryEventType.ITEM_UPDATED, {
                    "inventory_id": inventory_id,
                    "inventory_item_id": item_id1,
                    "changes": {"position": item1.position}
                })
                
                emit_event(InventoryEventType.ITEM_UPDATED, {
                    "inventory_id": inventory_id,
                    "inventory_item_id": item_id2,
                    "changes": {"position": item2.position}
                })
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error swapping items in inventory {inventory_id}: {str(e)}")
            return False, f"Error: {str(e)}"
            
class TransferOperations:
    """
    Operations for transferring items between inventories.
    """
    
    @staticmethod
    def transfer_items(
        from_inventory_id: int,
        to_inventory_id: int,
        inventory_item_id: int,
        quantity: int
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Transfer items between inventories.
        
        Args:
            from_inventory_id: Source inventory ID
            to_inventory_id: Destination inventory ID
            inventory_item_id: Inventory item ID to transfer
            quantity: Quantity to transfer
            
        Returns:
            Tuple of (success, error_message, data)
        """
        # Use the enhanced transfer function from utils
        return transfer_item_between_inventories(
            from_inventory_id,
            to_inventory_id,
            inventory_item_id,
            quantity
        )

    @staticmethod
    def transfer_item_between_inventories(
        from_inventory_id: int,
        to_inventory_id: int,
        inventory_item_id: int,
        quantity: int,
        session=None
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Transfer items between inventories.
        
        Args:
            from_inventory_id: Source inventory ID
            to_inventory_id: Destination inventory ID
            inventory_item_id: Inventory item ID to transfer
            quantity: Quantity to transfer
            
        Returns:
            Tuple of (success, error_message, data)
        """
        # Start a database session
        session = session or db.session
        
        # Get inventory items
        source_item = session.query(InventoryItem).filter_by(
            id=inventory_item_id, 
            inventory_id=from_inventory_id
        ).first()
        
        if not source_item:
            return False, f"Item {inventory_item_id} not found in inventory {from_inventory_id}", None
            
        # Get target inventory
        target_inventory = session.query(Inventory).filter_by(id=to_inventory_id).first()
        
        if not target_inventory:
            return False, f"Target inventory {to_inventory_id} not found", None
            
        # Validate quantity
        if source_item.quantity < quantity:
            return False, f"Not enough items in inventory {from_inventory_id}", None
            
        # Validate target inventory capacity
        if target_inventory.capacity is not None and len(target_inventory.items) >= target_inventory.capacity:
            return False, f"Target inventory {to_inventory_id} is full", None
            
        # Validate target inventory weight
        if target_inventory.weight_limit is not None and sum(i.item.weight * i.quantity for i in target_inventory.items) + source_item.item.weight * quantity > target_inventory.weight_limit:
            return False, f"Target inventory {to_inventory_id} weight limit exceeded", None
            
        # Transfer items
        with session.begin():
            # Update source inventory
            source_item.quantity -= quantity
            
            # Add to target inventory
            new_item = InventoryItemRepository.add_item_to_inventory(
                to_inventory_id,
                source_item.item_id,
                quantity,
                source_item.is_equipped,
                session=session
            )
            
            # Prepare result data
            data = {
                "from_inventory_id": from_inventory_id,
                "to_inventory_id": to_inventory_id,
                "inventory_item_id": inventory_item_id,
                "quantity": quantity,
                "total_weight_transferred": source_item.item.weight * quantity,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return True, None, data
            
    @staticmethod
    def bulk_transfer_items(
        from_inventory_id: int,
        to_inventory_id: int,
        items_data: List[Dict[str, Any]]
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Transfer multiple items between inventories in a single transaction.
        
        Args:
            from_inventory_id: Source inventory ID
            to_inventory_id: Destination inventory ID
            items_data: List of items to transfer, each containing:
                - inventory_item_id: ID of the inventory item
                - quantity: Quantity to transfer
            
        Returns:
            Tuple of (success, error_message, data)
        """
        # Start a database session
        session = db.session
        
        # Track successful transfers
        successful_transfers = []
        failed_transfers = []
        total_weight_transferred = 0
        
        try:
            # Get inventories
            source_inventory = session.query(Inventory).filter_by(id=from_inventory_id).first()
            target_inventory = session.query(Inventory).filter_by(id=to_inventory_id).first()
            
            if not source_inventory:
                return False, f"Source inventory {from_inventory_id} not found", None
            
            if not target_inventory:
                return False, f"Target inventory {to_inventory_id} not found", None
            
            # Pre-validate to avoid partial transfers when they would exceed limits
            if target_inventory.weight_limit is not None:
                current_target_weight = sum(i.item.weight * i.quantity for i in target_inventory.items)
                transfer_weight_total = 0
                
                # Calculate total weight to be transferred
                for item_data in items_data:
                    inventory_item_id = item_data.get('inventory_item_id')
                    quantity = item_data.get('quantity', 1)
                    
                    # Get inventory item
                    inv_item = session.query(InventoryItem).filter_by(
                        id=inventory_item_id, 
                        inventory_id=from_inventory_id
                    ).first()
                    
                    if not inv_item:
                        return False, f"Item {inventory_item_id} not found in inventory {from_inventory_id}", None
                        
                    # Add weight of this item to total
                    transfer_weight_total += inv_item.item.weight * quantity
                
                # Check if total transfer would exceed weight limit
                if current_target_weight + transfer_weight_total > target_inventory.weight_limit:
                    # Emit weight limit exceeded event
                    from backend.systems.inventory.events import emit_weight_limit_exceeded
                    emit_weight_limit_exceeded(
                        to_inventory_id,
                        current_target_weight,
                        target_inventory.weight_limit,
                        current_target_weight + transfer_weight_total - target_inventory.weight_limit
                    )
                    
                    return False, f"Bulk transfer would exceed target inventory weight limit of {target_inventory.weight_limit}", {
                        "current_weight": current_target_weight,
                        "transfer_weight_total": transfer_weight_total,
                        "weight_limit": target_inventory.weight_limit,
                        "excess": current_target_weight + transfer_weight_total - target_inventory.weight_limit
                    }
                    
            # Pre-validate capacity limit
            if target_inventory.capacity is not None:
                # Get count of unique new items (those not already in target inventory)
                current_target_item_ids = set(item.item_id for item in target_inventory.items)
                new_items_count = 0
                
                for item_data in items_data:
                    inventory_item_id = item_data.get('inventory_item_id')
                    inv_item = session.query(InventoryItem).filter_by(
                        id=inventory_item_id, 
                        inventory_id=from_inventory_id
                    ).first()
                    
                    if inv_item and inv_item.item_id not in current_target_item_ids:
                        new_items_count += 1
                        current_target_item_ids.add(inv_item.item_id)  # Don't count duplicates
                
                # Check if adding these items would exceed capacity
                if len(current_target_item_ids) > target_inventory.capacity:
                    return False, f"Bulk transfer would exceed target inventory capacity of {target_inventory.capacity} unique items", {
                        "current_items": target_inventory.items.count(),
                        "new_items": new_items_count,
                        "capacity": target_inventory.capacity
                    }
                    
            # Emit bulk transfer started event
            from backend.systems.inventory.events import emit_bulk_transfer_started
            emit_bulk_transfer_started(
                from_inventory_id,
                to_inventory_id,
                len(items_data)
            )
                    
            # Process each transfer
            for item_data in items_data:
                inventory_item_id = item_data.get('inventory_item_id')
                quantity = item_data.get('quantity', 1)
                
                # Transfer single item
                success, message, data = TransferOperations.transfer_item_between_inventories(
                    from_inventory_id,
                    to_inventory_id,
                    inventory_item_id,
                    quantity,
                    session=session
                )
                
                if success:
                    successful_transfers.append(data)
                    total_weight_transferred += data.get('total_weight_transferred', 0)
                else:
                    failed_transfers.append({
                        "inventory_item_id": inventory_item_id,
                        "quantity": quantity,
                        "error": message
                    })
                    
                    # If any transfer fails, rollback the entire transaction
                    session.rollback()
                    
                    # Emit bulk transfer failed event
                    from backend.systems.inventory.events import emit_bulk_transfer_failed
                    emit_bulk_transfer_failed(
                        from_inventory_id,
                        to_inventory_id,
                        len(items_data),
                        len(successful_transfers),
                        len(failed_transfers),
                        message
                    )
                    
                    return False, f"Failed to transfer item {inventory_item_id}: {message}", {
                        "successful": successful_transfers,
                        "failed": failed_transfers
                    }
            
            # Commit the transaction
            session.commit()
            
            # Prepare result data
            result_data = {
                "from_inventory_id": from_inventory_id,
                "to_inventory_id": to_inventory_id,
                "items_transferred": len(successful_transfers),
                "total_weight_transferred": total_weight_transferred,
                "transfers": successful_transfers,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Emit bulk transfer completed event
            from backend.systems.inventory.events import emit_bulk_transfer_completed
            emit_bulk_transfer_completed(result_data)
            
            return True, None, result_data
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error in bulk transfer: {str(e)}")
            
            # Emit bulk transfer failed event
            from backend.systems.inventory.events import emit_bulk_transfer_failed
            emit_bulk_transfer_failed(
                from_inventory_id,
                to_inventory_id,
                len(items_data),
                len(successful_transfers),
                len(failed_transfers),
                str(e)
            )
            
            return False, f"Error: {str(e)}", {
                "successful": successful_transfers,
                "failed": failed_transfers
            } 