"""
Notification module for inventory events.

This module provides a notification system for inventory-related events,
such as item additions, removals, and transfers.
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

from backend.systems.inventory.models import Inventory, Item, InventoryItem

# Configure logger
logger = logging.getLogger(__name__)

class InventoryNotifier:
    """
    Class for handling inventory event notifications.
    
    This class allows subscribing to inventory events and sending notifications
    when those events occur.
    """
    
    # Dictionary to store event subscribers
    _subscribers = {
        "item_added": [],
        "item_removed": [],
        "item_transferred": [],
        "item_equipped": [],
        "item_unequipped": [],
        "inventory_created": [],
        "inventory_deleted": []
    }
    
    @classmethod
    def subscribe(cls, event_type: str, callback):
        """
        Subscribe to an inventory event.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
        """
        if event_type not in cls._subscribers:
            logger.warning(f"Tried to subscribe to unknown event type: {event_type}")
            return False
            
        cls._subscribers[event_type].append(callback)
        return True
        
    @classmethod
    def unsubscribe(cls, event_type: str, callback):
        """
        Unsubscribe from an inventory event.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Function to remove from subscribers
        """
        if event_type not in cls._subscribers:
            return False
            
        if callback in cls._subscribers[event_type]:
            cls._subscribers[event_type].remove(callback)
            return True
            
        return False
        
    @classmethod
    def notify_item_added(cls, inventory_id: int, item_id: int, quantity: int, inventory_item_id: int):
        """
        Notify subscribers that an item was added to an inventory.
        
        Args:
            inventory_id: ID of the inventory
            item_id: ID of the item added
            quantity: Quantity added
            inventory_item_id: ID of the inventory item created
        """
        event_data = {
            "inventory_id": inventory_id,
            "item_id": item_id,
            "quantity": quantity,
            "inventory_item_id": inventory_item_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        cls._notify("item_added", event_data)
        
    @classmethod
    def notify_item_removed(cls, inventory_id: int, item_id: int, quantity: int, inventory_item_id: int):
        """
        Notify subscribers that an item was removed from an inventory.
        
        Args:
            inventory_id: ID of the inventory
            item_id: ID of the item removed
            quantity: Quantity removed
            inventory_item_id: ID of the inventory item
        """
        event_data = {
            "inventory_id": inventory_id,
            "item_id": item_id,
            "quantity": quantity,
            "inventory_item_id": inventory_item_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        cls._notify("item_removed", event_data)
        
    @classmethod
    def notify_item_transferred(cls, from_inventory_id: int, to_inventory_id: int, 
                           item_id: int, quantity: int, from_inventory_item_id: int, 
                           to_inventory_item_id: Optional[int]):
        """
        Notify subscribers that an item was transferred between inventories.
        
        Args:
            from_inventory_id: Source inventory ID
            to_inventory_id: Destination inventory ID
            item_id: ID of the transferred item
            quantity: Quantity transferred
            from_inventory_item_id: ID of the source inventory item
            to_inventory_item_id: ID of the destination inventory item (may be None)
        """
        event_data = {
            "from_inventory_id": from_inventory_id,
            "to_inventory_id": to_inventory_id,
            "item_id": item_id,
            "quantity": quantity,
            "from_inventory_item_id": from_inventory_item_id,
            "to_inventory_item_id": to_inventory_item_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        cls._notify("item_transferred", event_data)
        
    @classmethod
    def notify_item_equipped(cls, inventory_id: int, inventory_item_id: int, item_id: int):
        """
        Notify subscribers that an item was equipped.
        
        Args:
            inventory_id: ID of the inventory
            inventory_item_id: ID of the inventory item
            item_id: ID of the equipped item
        """
        event_data = {
            "inventory_id": inventory_id,
            "inventory_item_id": inventory_item_id,
            "item_id": item_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        cls._notify("item_equipped", event_data)
        
    @classmethod
    def notify_item_unequipped(cls, inventory_id: int, inventory_item_id: int, item_id: int):
        """
        Notify subscribers that an item was unequipped.
        
        Args:
            inventory_id: ID of the inventory
            inventory_item_id: ID of the inventory item
            item_id: ID of the unequipped item
        """
        event_data = {
            "inventory_id": inventory_id,
            "inventory_item_id": inventory_item_id,
            "item_id": item_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        cls._notify("item_unequipped", event_data)
        
    @classmethod
    def notify_inventory_created(cls, inventory_id: int, inventory_type: str, owner_id: Optional[int]):
        """
        Notify subscribers that a new inventory was created.
        
        Args:
            inventory_id: ID of the created inventory
            inventory_type: Type of inventory created
            owner_id: ID of the owner (if any)
        """
        event_data = {
            "inventory_id": inventory_id,
            "inventory_type": inventory_type,
            "owner_id": owner_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        cls._notify("inventory_created", event_data)
        
    @classmethod
    def notify_inventory_deleted(cls, inventory_id: int, inventory_type: str, owner_id: Optional[int]):
        """
        Notify subscribers that an inventory was deleted.
        
        Args:
            inventory_id: ID of the deleted inventory
            inventory_type: Type of inventory deleted
            owner_id: ID of the owner (if any)
        """
        event_data = {
            "inventory_id": inventory_id,
            "inventory_type": inventory_type,
            "owner_id": owner_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        cls._notify("inventory_deleted", event_data)
        
    @classmethod
    def _notify(cls, event_type: str, event_data: Dict[str, Any]):
        """
        Internal method to notify all subscribers of an event.
        
        Args:
            event_type: Type of event
            event_data: Event data to pass to subscribers
        """
        if event_type not in cls._subscribers:
            logger.error(f"Unknown event type: {event_type}")
            return
            
        for callback in cls._subscribers[event_type]:
            try:
                callback(event_data)
            except Exception as e:
                logger.error(f"Error in subscriber callback for {event_type}: {str(e)}") 