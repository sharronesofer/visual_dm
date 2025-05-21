"""
Utility functions for inventory operations.

This module provides utility functions for inventory operations,
such as calculating stats, transferring items, and handling inventory recovery.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import logging
from datetime import datetime

from backend.core.database import db
from backend.systems.inventory.models import Item, Inventory, InventoryItem
from backend.systems.inventory.repository import InventoryItemRepository
from backend.systems.inventory.events import (
    emit_transfer_started, 
    emit_transfer_completed, 
    emit_transfer_failed,
    emit_weight_limit_exceeded
)

# Configure logger
logger = logging.getLogger(__name__)

def calculate_inventory_stats(inventory: Inventory) -> Dict[str, Any]:
    """
    Calculate statistics for an inventory.
    
    Args:
        inventory: Inventory to calculate stats for
        
    Returns:
        Dictionary with inventory statistics
    """
    if not inventory:
        return {
            "total_items": 0,
            "unique_items": 0,
            "total_weight": 0,
            "total_value": 0,
            "used_capacity_pct": 0,
            "used_weight_pct": 0
        }
        
    # Calculate stats
    total_items = sum(item.quantity for item in inventory.items)
    unique_items = len(inventory.items)
    total_weight = sum(item.item.weight * item.quantity for item in inventory.items)
    total_value = sum(item.item.value * item.quantity for item in inventory.items)
    
    # Calculate capacity usage
    capacity_pct = 0
    if inventory.capacity is not None and inventory.capacity > 0:
        capacity_pct = min(100, round((total_items / inventory.capacity) * 100, 1))
        
    # Calculate weight usage
    weight_pct = 0
    if inventory.weight_limit is not None and inventory.weight_limit > 0:
        weight_pct = min(100, round((total_weight / inventory.weight_limit) * 100, 1))
        
    return {
        "total_items": total_items,
        "unique_items": unique_items,
        "total_weight": total_weight,
        "total_value": total_value,
        "used_capacity_pct": capacity_pct,
        "used_weight_pct": weight_pct
    }

def transfer_item_between_inventories(
    from_inventory_id: int,
    to_inventory_id: int,
    inventory_item_id: int,
    quantity: int,
    session=None
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Transfer items between inventories with atomic transaction and validation.
    
    Args:
        from_inventory_id: Source inventory ID
        to_inventory_id: Destination inventory ID
        inventory_item_id: Inventory item ID to transfer
        quantity: Quantity to transfer
        session: Database session to use
        
    Returns:
        Tuple of (success, error_message, transfer_data)
    """
    if session is None:
        session = db.session
        
    try:
        # Get inventories
        source_inventory = session.query(Inventory).filter_by(id=from_inventory_id).first()
        target_inventory = session.query(Inventory).filter_by(id=to_inventory_id).first()
        
        if not source_inventory:
            return False, f"Source inventory {from_inventory_id} not found", None
            
        if not target_inventory:
            return False, f"Target inventory {to_inventory_id} not found", None
            
        # Get inventory item to transfer
        inv_item = session.query(InventoryItem).filter_by(
            id=inventory_item_id, 
            inventory_id=from_inventory_id
        ).first()
        
        if not inv_item:
            return False, f"Item {inventory_item_id} not found in inventory {from_inventory_id}", None
            
        # Check quantity
        if quantity > inv_item.quantity:
            return False, f"Cannot transfer {quantity} items when only {inv_item.quantity} are available", None
            
        # Get item details
        item_id = inv_item.item_id
        item = inv_item.item
        
        # Calculate weight to be transferred
        transfer_weight = item.weight * quantity
        
        # Check target inventory weight limit
        if target_inventory.weight_limit is not None:
            current_target_weight = sum(i.item.weight * i.quantity for i in target_inventory.items)
            if current_target_weight + transfer_weight > target_inventory.weight_limit:
                # Emit weight limit exceeded event
                emit_weight_limit_exceeded(
                    to_inventory_id,
                    current_target_weight,
                    target_inventory.weight_limit,
                    current_target_weight + transfer_weight - target_inventory.weight_limit
                )
                
                return False, f"Transfer would exceed target inventory weight limit of {target_inventory.weight_limit}", {
                    "current_weight": current_target_weight,
                    "transfer_weight": transfer_weight,
                    "weight_limit": target_inventory.weight_limit,
                    "excess": current_target_weight + transfer_weight - target_inventory.weight_limit
                }
                
        # Check target inventory capacity limit
        if target_inventory.capacity is not None:
            # Check if item already exists in target inventory
            existing_target_item = session.query(InventoryItem).filter_by(
                inventory_id=to_inventory_id,
                item_id=item_id
            ).first()
            
            if not existing_target_item and target_inventory.items.count() >= target_inventory.capacity:
                return False, f"Target inventory has reached its capacity limit of {target_inventory.capacity} items", {
                    "current_items": target_inventory.items.count(),
                    "capacity": target_inventory.capacity
                }
                
        # Emit pre-transfer event
        emit_transfer_started(
            from_inventory_id, 
            to_inventory_id, 
            item_id, 
            quantity, 
            transfer_weight
        )
        
        # Add to destination inventory
        add_result = InventoryItemRepository.add_item_to_inventory(
            to_inventory_id,
            item_id,
            quantity,
            is_equipped=False,
            session=session
        )
        
        if not add_result[0]:
            # Emit transfer failed event
            emit_transfer_failed(
                from_inventory_id,
                to_inventory_id,
                item_id,
                quantity,
                add_result[1] or "Unknown error"
            )
            
            return False, add_result[1], None
            
        # Get or create the target inventory item ID for the transfer data
        target_inventory_item = session.query(InventoryItem).filter_by(
            inventory_id=to_inventory_id,
            item_id=item_id
        ).first()
        
        target_inventory_item_id = target_inventory_item.id if target_inventory_item else None
            
        # Remove from source inventory or update quantity
        if quantity == inv_item.quantity:
            # Remove entire item
            session.delete(inv_item)
            remaining_quantity = 0
        else:
            # Update quantity
            inv_item.quantity -= quantity
            inv_item.updated_at = datetime.utcnow()
            remaining_quantity = inv_item.quantity
            
        # Commit changes
        session.commit()
        
        # Create transfer data for event emission and response
        transfer_data = {
            "from_inventory_id": from_inventory_id,
            "to_inventory_id": to_inventory_id,
            "item_id": item_id,
            "inventory_item_id": inventory_item_id,
            "to_inventory_item_id": target_inventory_item_id,
            "quantity": quantity,
            "remaining_quantity": remaining_quantity,
            "item_name": item.name,
            "item_weight": item.weight,
            "total_weight_transferred": transfer_weight,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Emit post-transfer event for analytics, SFX, and UI integration
        emit_transfer_completed(transfer_data)
        
        return True, None, transfer_data
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error transferring item: {str(e)}")
        
        # Emit transfer failed event on exception
        if 'item_id' in locals() and 'quantity' in locals():
            emit_transfer_failed(
                from_inventory_id,
                to_inventory_id,
                item_id,
                quantity,
                str(e)
            )
            
        return False, f"Error: {str(e)}", None

class RecoveryManager:
    """
    Manager for handling inventory recovery operations.
    
    This class provides methods for backing up and restoring
    inventory data to recover from errors or crashes.
    """
    
    @staticmethod
    def backup_inventory(inventory_id: int) -> Dict[str, Any]:
        """
        Create a backup of an inventory's state.
        
        Args:
            inventory_id: ID of the inventory to backup
            
        Returns:
            Dictionary with backup data
        """
        inventory = db.session.query(Inventory).filter_by(id=inventory_id).first()
        if not inventory:
            return {"success": False, "error": f"Inventory {inventory_id} not found"}
            
        # Create backup data
        backup_data = {
            "inventory_id": inventory_id,
            "timestamp": datetime.utcnow().isoformat(),
            "inventory": {
                "name": inventory.name,
                "description": inventory.description,
                "inventory_type": inventory.inventory_type,
                "owner_id": inventory.owner_id,
                "capacity": inventory.capacity,
                "weight_limit": inventory.weight_limit,
                "is_public": inventory.is_public
            },
            "items": []
        }
        
        # Backup items
        for inv_item in inventory.items:
            item = inv_item.item
            backup_data["items"].append({
                "inventory_item_id": inv_item.id,
                "item_id": item.id,
                "quantity": inv_item.quantity,
                "is_equipped": inv_item.is_equipped,
                "custom_name": inv_item.custom_name,
                "position": inv_item.position,
                "item_data": {
                    "name": item.name,
                    "description": item.description,
                    "category": str(item.category),
                    "weight": item.weight,
                    "value": item.value,
                    "properties": item.properties
                }
            })
            
        return {
            "success": True,
            "backup_data": backup_data
        }
        
    @staticmethod
    def restore_inventory(backup_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restore an inventory from backup data.
        
        Args:
            backup_data: Backup data from backup_inventory
            
        Returns:
            Dictionary with restore results
        """
        if not backup_data or not isinstance(backup_data, dict):
            return {"success": False, "error": "Invalid backup data"}
            
        inventory_id = backup_data.get("inventory_id")
        if not inventory_id:
            return {"success": False, "error": "Backup data missing inventory_id"}
            
        try:
            # Get inventory
            inventory = db.session.query(Inventory).filter_by(id=inventory_id).first()
            if not inventory:
                return {"success": False, "error": f"Inventory {inventory_id} not found"}
                
            # Begin transaction
            with db.session.begin():
                # Update inventory properties
                inventory_data = backup_data.get("inventory", {})
                for key, value in inventory_data.items():
                    if hasattr(inventory, key):
                        setattr(inventory, key, value)
                
                # Remove all existing items
                db.session.query(InventoryItem).filter_by(inventory_id=inventory_id).delete()
                
                # Restore items
                restored_items = []
                items_data = backup_data.get("items", [])
                
                for item_data in items_data:
                    item_id = item_data.get("item_id")
                    if not item_id:
                        continue
                        
                    # Check if item exists
                    item = db.session.query(Item).filter_by(id=item_id).first()
                    if not item:
                        # Create stub item from backup if original not found
                        original_item = item_data.get("item_data", {})
                        item = Item(
                            id=item_id,
                            name=original_item.get("name", "Recovered Item"),
                            description=original_item.get("description", ""),
                            category=original_item.get("category", "MISC"),
                            weight=original_item.get("weight", 0),
                            value=original_item.get("value", 0),
                            properties=original_item.get("properties", {})
                        )
                        db.session.add(item)
                        
                    # Create inventory item
                    inv_item = InventoryItem(
                        inventory_id=inventory_id,
                        item_id=item_id,
                        quantity=item_data.get("quantity", 1),
                        is_equipped=item_data.get("is_equipped", False),
                        custom_name=item_data.get("custom_name"),
                        position=item_data.get("position")
                    )
                    db.session.add(inv_item)
                    restored_items.append(item_id)
                    
            return {
                "success": True,
                "message": f"Restored inventory {inventory_id} with {len(restored_items)} items",
                "inventory_id": inventory_id,
                "restored_items": len(restored_items)
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error restoring inventory: {str(e)}")
            return {"success": False, "error": f"Error: {str(e)}"}

def get_inventory_weight(inventory_id: int, session=None) -> float:
    """
    Calculate the total weight of all items in an inventory.
    
    Args:
        inventory_id: Inventory ID to calculate weight for
        session: Database session to use
        
    Returns:
        Total weight of all items in inventory
    """
    if session is None:
        session = db.session
    
    try:
        # Get all inventory items
        inventory_items = session.query(InventoryItem).filter_by(inventory_id=inventory_id).all()
        
        # Calculate total weight
        total_weight = 0.0
        for inv_item in inventory_items:
            item_weight = inv_item.item.weight * inv_item.quantity
            total_weight += item_weight
            
        return total_weight
    except Exception as e:
        logger.error(f"Error calculating inventory weight: {str(e)}")
        return 0.0

def validate_weight_limit(inventory_id: int, additional_weight: float = 0.0, session=None) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Validate if adding weight to an inventory would exceed its weight limit.
    
    Args:
        inventory_id: Inventory ID to validate
        additional_weight: Additional weight to add in validation
        session: Database session to use
        
    Returns:
        Tuple of (is_valid, details). If is_valid is False, details contains weight information.
    """
    if session is None:
        session = db.session
    
    try:
        # Get inventory
        inventory = session.query(Inventory).filter_by(id=inventory_id).first()
        
        if not inventory:
            return False, {"error": f"Inventory {inventory_id} not found"}
            
        # Check if inventory has a weight limit
        if inventory.weight_limit is None:
            return True, None
            
        # Get current weight
        current_weight = get_inventory_weight(inventory_id, session)
        
        # Check if adding weight would exceed limit
        if current_weight + additional_weight > inventory.weight_limit:
            excess = current_weight + additional_weight - inventory.weight_limit
            
            # Emit weight limit exceeded event
            emit_weight_limit_exceeded(
                inventory_id,
                current_weight,
                inventory.weight_limit,
                excess
            )
            
            return False, {
                "current_weight": current_weight,
                "additional_weight": additional_weight,
                "weight_limit": inventory.weight_limit,
                "excess": excess
            }
            
        return True, None
    except Exception as e:
        logger.error(f"Error validating weight limit: {str(e)}")
        return False, {"error": str(e)}

def validate_inventory_capacity(inventory_id: int, additional_items: int = 1, session=None) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Validate if adding items to an inventory would exceed its capacity.
    
    Args:
        inventory_id: Inventory ID to validate
        additional_items: Number of additional unique items to add
        session: Database session to use
        
    Returns:
        Tuple of (is_valid, details). If is_valid is False, details contains capacity information.
    """
    if session is None:
        session = db.session
    
    try:
        # Get inventory
        inventory = session.query(Inventory).filter_by(id=inventory_id).first()
        
        if not inventory:
            return False, {"error": f"Inventory {inventory_id} not found"}
            
        # Check if inventory has a capacity limit
        if inventory.capacity is None:
            return True, None
            
        # Get current item count
        current_count = session.query(InventoryItem).filter_by(inventory_id=inventory_id).count()
        
        # Check if adding items would exceed capacity
        if current_count + additional_items > inventory.capacity:
            return False, {
                "current_count": current_count,
                "additional_items": additional_items,
                "capacity": inventory.capacity,
                "excess": current_count + additional_items - inventory.capacity
            }
            
        return True, None
    except Exception as e:
        logger.error(f"Error validating inventory capacity: {str(e)}")
        return False, {"error": str(e)}

def optimize_inventory_stacks(inventory_id: int, session=None) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """
    Optimize inventory by combining stackable items of the same type.
    
    Args:
        inventory_id: Inventory ID to optimize
        session: Database session to use
        
    Returns:
        Tuple of (success, error_message, results)
    """
    if session is None:
        session = db.session
    
    try:
        # Get inventory
        inventory = session.query(Inventory).filter_by(id=inventory_id).first()
        
        if not inventory:
            return False, f"Inventory {inventory_id} not found", {}
        
        # Track results
        combined_stacks = 0
        removed_stacks = 0
        affected_items = []
        
        # Group items by item_id
        item_groups = {}
        for inv_item in inventory.items:
            # Skip non-stackable items
            if not inv_item.item.is_stackable:
                continue
                
            # Skip equipped items
            if inv_item.is_equipped:
                continue
                
            if inv_item.item_id not in item_groups:
                item_groups[inv_item.item_id] = []
                
            item_groups[inv_item.item_id].append(inv_item)
        
        # Process each item group with multiple stacks
        for item_id, stacks in item_groups.items():
            if len(stacks) <= 1:
                continue
                
            # Sort stacks by quantity (largest first)
            stacks.sort(key=lambda x: x.quantity, reverse=True)
            
            # Take the first stack as the target
            target_stack = stacks[0]
            
            # Combine all other stacks into the target
            with session.begin_nested():
                for source_stack in stacks[1:]:
                    # Add quantity to target
                    target_stack.quantity += source_stack.quantity
                    
                    # Track data for the affected stack
                    affected_items.append({
                        "item_id": item_id,
                        "source_id": source_stack.id,
                        "target_id": target_stack.id,
                        "quantity": source_stack.quantity
                    })
                    
                    # Remove source stack
                    session.delete(source_stack)
                    removed_stacks += 1
                    combined_stacks += 1
                    
                # Update target timestamp
                target_stack.updated_at = datetime.utcnow()
        
        # Commit changes
        session.commit()
        
        return True, None, {
            "combined_stacks": combined_stacks,
            "removed_stacks": removed_stacks,
            "affected_items": affected_items
        }
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error optimizing inventory stacks: {str(e)}")
        return False, f"Error: {str(e)}", {}

def combine_item_stacks(
    inventory_id: int,
    source_stack_id: int,
    target_stack_id: int,
    quantity: Optional[int] = None,
    session=None
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Combine two item stacks in an inventory.
    
    Args:
        inventory_id: ID of the inventory
        source_stack_id: ID of the source stack (will be reduced or removed)
        target_stack_id: ID of the target stack (will receive items)
        quantity: Optional quantity to move (all if None)
        session: Database session to use
        
    Returns:
        Tuple of (success, error_message, result)
    """
    if session is None:
        session = db.session
        
    try:
        # Get inventory items
        source = session.query(InventoryItem).filter_by(
            id=source_stack_id, 
            inventory_id=inventory_id
        ).first()
        
        target = session.query(InventoryItem).filter_by(
            id=target_stack_id, 
            inventory_id=inventory_id
        ).first()
        
        if not source:
            return False, f"Source item {source_stack_id} not found in inventory {inventory_id}", None
            
        if not target:
            return False, f"Target item {target_stack_id} not found in inventory {inventory_id}", None
            
        # Validate items are the same type
        if source.item_id != target.item_id:
            return False, "Cannot combine different item types", None
            
        # Determine transfer quantity
        transfer_qty = quantity if quantity is not None else source.quantity
        
        if transfer_qty <= 0:
            return False, "Transfer quantity must be positive", None
            
        if transfer_qty > source.quantity:
            return False, f"Not enough items in source stack (requested: {transfer_qty}, available: {source.quantity})", None
            
        # Begin transaction
        with session.begin_nested():
            # Update source stack
            if transfer_qty == source.quantity:
                # Delete source if all items transferred
                session.delete(source)
            else:
                # Reduce source quantity
                source.quantity -= transfer_qty
                source.updated_at = datetime.utcnow()
                
            # Update target stack
            target.quantity += transfer_qty
            target.updated_at = datetime.utcnow()
            
            # Create result data
            result = {
                "inventory_id": inventory_id,
                "source_stack_id": source_stack_id,
                "target_stack_id": target_stack_id,
                "quantity_transferred": transfer_qty,
                "source_remaining": source.quantity - transfer_qty if transfer_qty < source.quantity else 0,
                "target_new_quantity": target.quantity,
                "item_id": source.item_id,
                "source_removed": transfer_qty == source.quantity
            }
            
        # Commit transaction
        session.commit()
        
        # Emit stack combined event
        from backend.systems.inventory.events import InventoryEventType, emit_event
        emit_event(InventoryEventType.ITEM_UPDATED, {
            "inventory_id": inventory_id,
            "event": "stack_combined",
            "source_stack_id": source_stack_id,
            "target_stack_id": target_stack_id,
            "quantity": transfer_qty,
            "source_removed": result["source_removed"]
        })
        
        return True, None, result
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error combining stacks: {str(e)}")
        return False, f"Error: {str(e)}", None

def split_item_stack(
    inventory_id: int,
    stack_id: int,
    quantity: int,
    session=None
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Split an item stack into two separate stacks.
    
    Args:
        inventory_id: ID of the inventory
        stack_id: ID of the stack to split
        quantity: Quantity to move to the new stack
        session: Database session to use
        
    Returns:
        Tuple of (success, error_message, result)
    """
    if session is None:
        session = db.session
        
    try:
        # Get inventory item
        stack = session.query(InventoryItem).filter_by(
            id=stack_id, 
            inventory_id=inventory_id
        ).first()
        
        if not stack:
            return False, f"Item {stack_id} not found in inventory {inventory_id}", None
            
        # Validate quantity
        if quantity <= 0:
            return False, "Split quantity must be positive", None
            
        if quantity >= stack.quantity:
            return False, f"Split quantity must be less than stack size ({stack.quantity})", None
            
        # Get item details
        item = stack.item
        
        # Validate item is stackable
        if not getattr(item, "is_stackable", True):  # Default to True if property doesn't exist
            return False, "Cannot split non-stackable items", None
            
        # Check inventory capacity
        capacity_valid, capacity_details = validate_inventory_capacity(
            inventory_id, 
            additional_items=1,  # New stack counts as a new item slot
            session=session
        )
        
        if not capacity_valid:
            return False, "Cannot split stack: inventory capacity limit reached", capacity_details
            
        # Begin transaction
        with session.begin_nested():
            # Create new stack with split quantity
            new_stack = InventoryItem(
                inventory_id=inventory_id,
                item_id=item.id,
                quantity=quantity,
                is_equipped=False,
                position=stack.position, # Use same position for now
                custom_name=stack.custom_name
            )
            session.add(new_stack)
            
            # Reduce quantity from original stack
            stack.quantity -= quantity
            stack.updated_at = datetime.utcnow()
            
            # Flush to get new stack ID
            session.flush()
            
            # Create result data
            result = {
                "inventory_id": inventory_id,
                "original_stack_id": stack_id,
                "new_stack_id": new_stack.id,
                "item_id": item.id,
                "split_quantity": quantity,
                "original_remaining": stack.quantity,
                "position": new_stack.position
            }
            
        # Commit transaction
        session.commit()
        
        # Emit stack split event
        from backend.systems.inventory.events import InventoryEventType, emit_event
        emit_event(InventoryEventType.ITEM_UPDATED, {
            "inventory_id": inventory_id,
            "event": "stack_split",
            "original_stack_id": stack_id,
            "new_stack_id": new_stack.id,
            "quantity": quantity,
            "item_id": item.id
        })
        
        return True, None, result
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error splitting stack: {str(e)}")
        return False, f"Error: {str(e)}", None

def filter_inventory_items(
    inventory_id: int,
    filters: Dict[str, Any],
    session=None
) -> Tuple[bool, Optional[str], List[Dict[str, Any]]]:
    """
    Filter inventory items by various criteria.
    
    Args:
        inventory_id: Inventory ID to filter items from
        filters: Dictionary of filter criteria, which may include:
            - name: String to search in item names (case-insensitive partial match)
            - description: String to search in item descriptions
            - category: Category or list of categories to match
            - min_weight: Minimum weight
            - max_weight: Maximum weight
            - min_value: Minimum value
            - max_value: Maximum value
            - is_equipped: Boolean to filter equipped/unequipped items
            - properties: Dictionary of property key-values to match
            - sort_by: Field to sort by (name, weight, value, category)
            - sort_dir: Sort direction (asc or desc)
        session: Database session to use
        
    Returns:
        Tuple of (success, error_message, filtered_items)
    """
    if session is None:
        session = db.session
        
    try:
        # Get inventory
        inventory = session.query(Inventory).filter_by(id=inventory_id).first()
        
        if not inventory:
            return False, f"Inventory {inventory_id} not found", []
            
        # Start with base query
        query = session.query(InventoryItem).filter_by(inventory_id=inventory_id).join(Item)
        
        # Apply filters
        if 'name' in filters and filters['name']:
            query = query.filter(Item.name.ilike(f"%{filters['name']}%"))
            
        if 'description' in filters and filters['description']:
            query = query.filter(Item.description.ilike(f"%{filters['description']}%"))
            
        if 'category' in filters and filters['category']:
            categories = filters['category']
            if isinstance(categories, list):
                query = query.filter(Item.category.in_(categories))
            else:
                query = query.filter(Item.category == categories)
                
        if 'min_weight' in filters and filters['min_weight'] is not None:
            query = query.filter(Item.weight >= filters['min_weight'])
            
        if 'max_weight' in filters and filters['max_weight'] is not None:
            query = query.filter(Item.weight <= filters['max_weight'])
            
        if 'min_value' in filters and filters['min_value'] is not None:
            query = query.filter(Item.value >= filters['min_value'])
            
        if 'max_value' in filters and filters['max_value'] is not None:
            query = query.filter(Item.value <= filters['max_value'])
            
        if 'is_equipped' in filters and filters['is_equipped'] is not None:
            query = query.filter(InventoryItem.is_equipped == filters['is_equipped'])
            
        # Apply sorting
        sort_by = filters.get('sort_by', 'name')
        sort_dir = filters.get('sort_dir', 'asc')
        
        if sort_by == 'name':
            order_by = Item.name.asc() if sort_dir == 'asc' else Item.name.desc()
        elif sort_by == 'weight':
            order_by = Item.weight.asc() if sort_dir == 'asc' else Item.weight.desc()
        elif sort_by == 'value':
            order_by = Item.value.asc() if sort_dir == 'asc' else Item.value.desc()
        elif sort_by == 'category':
            order_by = Item.category.asc() if sort_dir == 'asc' else Item.category.desc()
        elif sort_by == 'quantity':
            order_by = InventoryItem.quantity.asc() if sort_dir == 'asc' else InventoryItem.quantity.desc()
        else:
            order_by = Item.name.asc()  # Default sort
            
        query = query.order_by(order_by)
        
        # Execute query and process results
        items = query.all()
        result_items = []
        
        # Post-process for property filters (can't easily do these in SQL)
        property_filters = filters.get('properties', {})
        
        for inv_item in items:
            # Skip if property filters don't match
            if property_filters:
                item_props = inv_item.item.properties or {}
                match = True
                
                for key, value in property_filters.items():
                    if key not in item_props or item_props[key] != value:
                        match = False
                        break
                        
                if not match:
                    continue
                    
            # Add matched item to results
            result_items.append({
                'id': inv_item.id,
                'inventory_id': inv_item.inventory_id,
                'item_id': inv_item.item_id,
                'quantity': inv_item.quantity,
                'is_equipped': inv_item.is_equipped,
                'position': inv_item.position,
                'custom_name': inv_item.custom_name,
                'item': {
                    'id': inv_item.item.id,
                    'name': inv_item.item.name,
                    'description': inv_item.item.description,
                    'category': inv_item.item.category,
                    'weight': inv_item.item.weight,
                    'value': inv_item.item.value,
                    'properties': inv_item.item.properties
                }
            })
            
        return True, None, result_items
        
    except Exception as e:
        logger.error(f"Error filtering inventory items: {str(e)}")
        return False, f"Error: {str(e)}", [] 