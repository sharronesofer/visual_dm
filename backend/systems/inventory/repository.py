"""
Repository module for inventory operations.

This module provides data access layer functionality for inventory operations,
including CRUD operations for items and inventories.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
import logging
from datetime import datetime

from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

from backend.core.database import db
from backend.systems.inventory.models import Item, Inventory, InventoryItem
from backend.systems.inventory.utils import validate_weight_limit, validate_inventory_capacity

# Configure logger
logger = logging.getLogger(__name__)

class ItemRepository:
    """
    Repository for item operations.
    """
    
    @staticmethod
    def get_items(limit: int = 100, offset: int = 0) -> List[Item]:
        """
        Get a list of items.
        
        Args:
            limit: Maximum number of items to return
            offset: Offset for pagination
            
        Returns:
            List of items
        """
        try:
            return db.session.query(Item).order_by(Item.name).limit(limit).offset(offset).all()
        except Exception as e:
            logger.error(f"Error getting items: {str(e)}")
            return []
    
    @staticmethod
    def get_item(item_id: int) -> Optional[Item]:
        """
        Get an item by ID.
        
        Args:
            item_id: ID of the item
            
        Returns:
            Item object or None if not found
        """
        try:
            return db.session.query(Item).filter(Item.id == item_id).first()
        except Exception as e:
            logger.error(f"Error getting item {item_id}: {str(e)}")
            return None
    
    @staticmethod
    def create_item(item_data: Dict[str, Any], session=None) -> Tuple[bool, Optional[str], Optional[Item]]:
        """
        Create a new item.
        
        Args:
            item_data: Dictionary with item data
            session: Optional database session
            
        Returns:
            Tuple of (success, error_message, item)
        """
        if session is None:
            session = db.session
            
        try:
            item = Item(
                name=item_data.get('name', 'Unnamed Item'),
                description=item_data.get('description', ''),
                category=item_data.get('category', 'MISC'),
                value=item_data.get('value', 0),
                weight=item_data.get('weight', 0),
                properties=item_data.get('properties', {})
            )
            
            session.add(item)
            session.flush()
            
            return True, None, item
        except Exception as e:
            logger.error(f"Error creating item: {str(e)}")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def update_item(item_id: int, item_data: Dict[str, Any], session=None) -> Tuple[bool, Optional[str], Optional[Item]]:
        """
        Update an existing item.
        
        Args:
            item_id: ID of the item to update
            item_data: Dictionary with updated item data
            session: Optional database session
            
        Returns:
            Tuple of (success, error_message, updated_item)
        """
        if session is None:
            session = db.session
            
        try:
            item = session.query(Item).filter(Item.id == item_id).first()
            if not item:
                return False, f"Item {item_id} not found", None
                
            # Update item attributes
            for key, value in item_data.items():
                if hasattr(item, key):
                    setattr(item, key, value)
                    
            session.flush()
            return True, None, item
        except Exception as e:
            logger.error(f"Error updating item {item_id}: {str(e)}")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def delete_item(item_id: int, session=None) -> Tuple[bool, Optional[str]]:
        """
        Delete an item.
        
        Args:
            item_id: ID of the item to delete
            session: Optional database session
            
        Returns:
            Tuple of (success, error_message)
        """
        if session is None:
            session = db.session
            
        try:
            item = session.query(Item).filter(Item.id == item_id).first()
            if not item:
                return False, f"Item {item_id} not found"
                
            # Check if item is used in any inventories
            inventory_items = session.query(InventoryItem).filter(InventoryItem.item_id == item_id).all()
            if inventory_items:
                return False, f"Cannot delete item {item_id} because it is used in {len(inventory_items)} inventories"
                
            session.delete(item)
            session.flush()
            return True, None
        except Exception as e:
            logger.error(f"Error deleting item {item_id}: {str(e)}")
            return False, f"Error: {str(e)}"

class InventoryRepository:
    """
    Repository for inventory operations.
    """
    
    @staticmethod
    def get_inventories(limit: int = 100, offset: int = 0) -> List[Inventory]:
        """
        Get a list of inventories.
        
        Args:
            limit: Maximum number of inventories to return
            offset: Offset for pagination
            
        Returns:
            List of inventories
        """
        try:
            return db.session.query(Inventory).limit(limit).offset(offset).all()
        except Exception as e:
            logger.error(f"Error getting inventories: {str(e)}")
            return []
    
    @staticmethod
    def get_inventory(inventory_id: int, include_items: bool = True) -> Optional[Inventory]:
        """
        Get an inventory by ID.
        
        Args:
            inventory_id: ID of the inventory
            include_items: Whether to include items in the query
            
        Returns:
            Inventory object or None if not found
        """
        try:
            query = db.session.query(Inventory).filter(Inventory.id == inventory_id)
            
            if include_items:
                query = query.options(joinedload(Inventory.items).joinedload(InventoryItem.item))
                
            return query.first()
        except Exception as e:
            logger.error(f"Error getting inventory {inventory_id}: {str(e)}")
            return None
    
    @staticmethod
    def get_inventory_by_owner(owner_id: int, inventory_type: Optional[str] = None) -> List[Inventory]:
        """
        Get inventories by owner ID.
        
        Args:
            owner_id: ID of the owner
            inventory_type: Optional inventory type to filter by
            
        Returns:
            List of inventories
        """
        try:
            query = db.session.query(Inventory).filter(Inventory.owner_id == owner_id)
            
            if inventory_type:
                query = query.filter(Inventory.inventory_type == inventory_type)
                
            return query.all()
        except Exception as e:
            logger.error(f"Error getting inventories for owner {owner_id}: {str(e)}")
            return []
    
    @staticmethod
    def create_inventory(inventory_data: Dict[str, Any], session=None) -> Optional[Inventory]:
        """
        Create a new inventory.
        
        Args:
            inventory_data: Dictionary with inventory data
            session: Optional database session
            
        Returns:
            Created inventory or None on error
        """
        if session is None:
            session = db.session
            
        try:
            inventory = Inventory(
                name=inventory_data.get('name', 'Unnamed Inventory'),
                description=inventory_data.get('description', ''),
                inventory_type=inventory_data.get('inventory_type', 'GENERIC'),
                owner_id=inventory_data.get('owner_id'),
                capacity=inventory_data.get('capacity'),
                weight_limit=inventory_data.get('weight_limit'),
                is_public=inventory_data.get('is_public', False)
            )
            
            session.add(inventory)
            session.flush()
            
            return inventory
        except Exception as e:
            logger.error(f"Error creating inventory: {str(e)}")
            return None
    
    @staticmethod
    def update_inventory(inventory_id: int, inventory_data: Dict[str, Any], session=None) -> Tuple[bool, Optional[str], Optional[Inventory]]:
        """
        Update an existing inventory.
        
        Args:
            inventory_id: ID of the inventory to update
            inventory_data: Dictionary with updated inventory data
            session: Optional database session
            
        Returns:
            Tuple of (success, error_message, updated_inventory)
        """
        if session is None:
            session = db.session
            
        try:
            inventory = session.query(Inventory).filter(Inventory.id == inventory_id).first()
            if not inventory:
                return False, f"Inventory {inventory_id} not found", None
                
            # Update inventory attributes
            for key, value in inventory_data.items():
                if hasattr(inventory, key):
                    setattr(inventory, key, value)
                    
            inventory.updated_at = datetime.utcnow()
            session.flush()
            return True, None, inventory
        except Exception as e:
            logger.error(f"Error updating inventory {inventory_id}: {str(e)}")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def delete_inventory(inventory_id: int, session=None) -> Tuple[bool, Optional[str]]:
        """
        Delete an inventory.
        
        Args:
            inventory_id: ID of the inventory to delete
            session: Optional database session
            
        Returns:
            Tuple of (success, error_message)
        """
        if session is None:
            session = db.session
            
        try:
            inventory = session.query(Inventory).filter(Inventory.id == inventory_id).first()
            if not inventory:
                return False, f"Inventory {inventory_id} not found"
                
            # Delete inventory items first
            session.query(InventoryItem).filter(InventoryItem.inventory_id == inventory_id).delete()
            
            # Delete inventory
            session.delete(inventory)
            session.flush()
            return True, None
        except Exception as e:
            logger.error(f"Error deleting inventory {inventory_id}: {str(e)}")
            return False, f"Error: {str(e)}"

class InventoryItemRepository:
    """
    Repository for inventory item operations.
    """
    
    @staticmethod
    def get_inventory_item(inventory_item_id: int) -> Optional[InventoryItem]:
        """
        Get an inventory item by ID.
        
        Args:
            inventory_item_id: ID of the inventory item
            
        Returns:
            InventoryItem object or None if not found
        """
        try:
            return db.session.query(InventoryItem).filter(InventoryItem.id == inventory_item_id).first()
        except Exception as e:
            logger.error(f"Error getting inventory item {inventory_item_id}: {str(e)}")
            return None
    
    @staticmethod
    def get_inventory_items(inventory_id: int) -> List[InventoryItem]:
        """
        Get all items in an inventory.
        
        Args:
            inventory_id: ID of the inventory
            
        Returns:
            List of inventory items
        """
        try:
            return db.session.query(InventoryItem).filter(
                InventoryItem.inventory_id == inventory_id
            ).options(
                joinedload(InventoryItem.item)
            ).all()
        except Exception as e:
            logger.error(f"Error getting items from inventory {inventory_id}: {str(e)}")
            return []
    
    @staticmethod
    def add_item_to_inventory(
        inventory_id: int,
        item_id: int,
        quantity: int,
        is_equipped: bool = False,
        session=None
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Add an item to an inventory.
        
        Args:
            inventory_id: ID of the inventory
            item_id: ID of the item to add
            quantity: Quantity to add
            is_equipped: Whether the item is equipped
            session: Database session to use
            
        Returns:
            Tuple of (success, error_message, result_data)
        """
        if session is None:
            session = db.session
        
        try:
            # Get item for weight calculation
            item = session.query(Item).filter_by(id=item_id).first()
            if not item:
                return False, f"Item {item_id} not found", None
                
            # Check if adding weight would exceed inventory weight limit
            weight_validation = validate_weight_limit(
                inventory_id, 
                additional_weight=item.weight * quantity,
                session=session
            )
            
            if not weight_validation[0]:
                return False, f"Adding item would exceed inventory weight limit", weight_validation[1]
            
            # Check if item exists in inventory
            inventory_item = session.query(InventoryItem).filter_by(
                inventory_id=inventory_id,
                item_id=item_id
            ).first()
            
            if inventory_item:
                # Update existing item
                inventory_item.quantity += quantity
                inventory_item.updated_at = datetime.utcnow()
                if is_equipped:
                    inventory_item.is_equipped = True
                
                result_data = {
                    "inventory_id": inventory_id,
                    "item_id": item_id,
                    "quantity_added": quantity,
                    "new_quantity": inventory_item.quantity,
                    "inventory_item_id": inventory_item.id,
                    "is_equipped": inventory_item.is_equipped,
                    "operation": "updated"
                }
            else:
                # Check capacity only for new items
                capacity_validation = validate_inventory_capacity(
                    inventory_id, 
                    additional_items=1,
                    session=session
                )
                
                if not capacity_validation[0]:
                    return False, f"Adding item would exceed inventory capacity", capacity_validation[1]
                
                # Create new inventory item
                inventory_item = InventoryItem(
                    inventory_id=inventory_id,
                    item_id=item_id,
                    quantity=quantity,
                    is_equipped=is_equipped
                )
                session.add(inventory_item)
                session.flush()  # Generate ID
                
                result_data = {
                    "inventory_id": inventory_id,
                    "item_id": item_id,
                    "quantity_added": quantity,
                    "new_quantity": quantity,
                    "inventory_item_id": inventory_item.id,
                    "is_equipped": is_equipped,
                    "operation": "created"
                }
            
            # Emit item added event
            from backend.systems.inventory.events import InventoryEventType, emit_event
            emit_event(InventoryEventType.ITEM_ADDED, {
                "inventory_id": inventory_id,
                "item_id": item_id,
                "quantity": quantity,
                "is_equipped": is_equipped,
                "inventory_item_id": inventory_item.id,
                "operation": result_data["operation"]
            })
            
            return True, None, result_data
        
        except Exception as e:
            logger.error(f"Error adding item to inventory: {str(e)}")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def remove_item_from_inventory(
        inventory_id: int, 
        inventory_item_id: int, 
        quantity: int = None,
        session=None
    ) -> Tuple[bool, Optional[str]]:
        """
        Remove an item from an inventory.
        
        Args:
            inventory_id: ID of the inventory
            inventory_item_id: ID of the inventory item to remove
            quantity: Quantity to remove (all if None)
            session: Optional database session
            
        Returns:
            Tuple of (success, error_message)
        """
        if session is None:
            session = db.session
            
        try:
            # Check if inventory exists
            inventory = session.query(Inventory).filter(Inventory.id == inventory_id).first()
            if not inventory:
                return False, f"Inventory {inventory_id} not found"
                
            # Check if inventory item exists
            inventory_item = session.query(InventoryItem).filter(
                InventoryItem.id == inventory_item_id,
                InventoryItem.inventory_id == inventory_id
            ).first()
            
            if not inventory_item:
                return False, f"Item {inventory_item_id} not found in inventory {inventory_id}"
                
            # Remove quantity or all
            if quantity is None or quantity >= inventory_item.quantity:
                session.delete(inventory_item)
            else:
                inventory_item.quantity -= quantity
                inventory_item.updated_at = datetime.utcnow()
                
            # Update inventory timestamp
            inventory.updated_at = datetime.utcnow()
            session.flush()
            
            return True, None
        except Exception as e:
            logger.error(f"Error removing item {inventory_item_id} from inventory {inventory_id}: {str(e)}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def update_inventory_item(
        inventory_id: int,
        inventory_item_id: int,
        updates: Dict[str, Any],
        session=None
    ) -> Tuple[bool, Optional[str], Optional[InventoryItem]]:
        """
        Update an inventory item.
        
        Args:
            inventory_id: ID of the inventory
            inventory_item_id: ID of the inventory item to update
            updates: Dictionary with updates to apply
            session: Optional database session
            
        Returns:
            Tuple of (success, error_message, updated_inventory_item)
        """
        if session is None:
            session = db.session
            
        try:
            # Check if inventory item exists
            inventory_item = session.query(InventoryItem).filter(
                InventoryItem.id == inventory_item_id,
                InventoryItem.inventory_id == inventory_id
            ).first()
            
            if not inventory_item:
                return False, f"Item {inventory_item_id} not found in inventory {inventory_id}", None
                
            # Apply updates
            for key, value in updates.items():
                if hasattr(inventory_item, key):
                    setattr(inventory_item, key, value)
                    
            inventory_item.updated_at = datetime.utcnow()
            
            # Update inventory timestamp
            inventory = session.query(Inventory).filter(Inventory.id == inventory_id).first()
            if inventory:
                inventory.updated_at = datetime.utcnow()
                
            session.flush()
            
            return True, None, inventory_item
        except Exception as e:
            logger.error(f"Error updating item {inventory_item_id} in inventory {inventory_id}: {str(e)}")
            return False, f"Error: {str(e)}", None 