"""
Exporter module for inventory system.

This module provides functions for exporting inventory data to JSON
and importing it back into the system.
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime

from backend.infrastructure.database import db
from backend.systems.inventory.models import Item, Inventory, InventoryItem
from backend.systems.inventory.repositories import (
    ItemRepository, InventoryRepository, InventoryItemRepository
)
from backend.systems.inventory.service import InventoryService

# Configure logger
logger = logging.getLogger(__name__)

class InventoryExporter:
    """
    Functions for exporting and importing inventory data.
    """
    
    @staticmethod
    def export_to_json(inventory_id: int) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Export inventory data to JSON format.
        
        Args:
            inventory_id: Inventory ID
            
        Returns:
            Tuple of (success, error_message, data)
        """
        try:
            inventory = InventoryRepository.get_inventory(inventory_id)
            if not inventory:
                return False, "Inventory not found", None
                
            # Create serializable representation
            items_data = []
            for inv_item in inventory.items:
                item = inv_item.item
                items_data.append({
                    "id": inv_item.id,
                    "item_id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "category": str(item.category),
                    "weight": item.weight,
                    "value": item.value,
                    "quantity": inv_item.quantity,
                    "is_equipped": inv_item.is_equipped,
                    "custom_name": inv_item.custom_name,
                    "position": inv_item.position,
                    "properties": item.properties
                })
                
            export_data = {
                "inventory": {
                    "id": inventory.id,
                    "name": inventory.name,
                    "description": inventory.description,
                    "inventory_type": inventory.inventory_type,
                    "owner_id": inventory.owner_id,
                    "capacity": inventory.capacity,
                    "weight_limit": inventory.weight_limit,
                    "is_public": inventory.is_public,
                    "created_at": inventory.created_at.isoformat() if inventory.created_at else None,
                    "updated_at": inventory.updated_at.isoformat() if inventory.updated_at else None
                },
                "items": items_data,
                "stats": InventoryService.calculate_inventory_stats(inventory_id),
                "export_timestamp": datetime.utcnow().isoformat()
            }
            
            return True, None, export_data
            
        except Exception as e:
            logger.error(f"Error exporting inventory {inventory_id}: {str(e)}")
            return False, f"Error: {str(e)}", None
    
    @staticmethod
    def import_from_json(data: Dict[str, Any], owner_id: Optional[int] = None) -> Tuple[bool, Optional[str], Optional[Inventory]]:
        """
        Import inventory data from JSON format.
        
        Args:
            data: JSON inventory data
            owner_id: Optional new owner ID
            
        Returns:
            Tuple of (success, error_message, imported_inventory)
        """
        try:
            inventory_data = data.get("inventory", {})
            items_data = data.get("items", [])
            
            # Remove ID and timestamps to create a new inventory
            if "id" in inventory_data:
                del inventory_data["id"]
            if "created_at" in inventory_data:
                del inventory_data["created_at"]
            if "updated_at" in inventory_data:
                del inventory_data["updated_at"]
                
            # Override owner if specified
            if owner_id is not None:
                inventory_data["owner_id"] = owner_id
                
            # Create inventory
            with db.session.begin():
                inventory = InventoryRepository.create_inventory(inventory_data)
                
                # Add items
                for item_data in items_data:
                    item_id = item_data.get("item_id")
                    if not item_id:
                        logger.warning(f"Skipping item without item_id during import")
                        continue
                    
                    # Check if item exists
                    item = ItemRepository.get_item(item_id)
                    if not item:
                        logger.warning(f"Skipping non-existent item {item_id} during import")
                        continue
                        
                    # Add to inventory
                    InventoryItemRepository.add_item_to_inventory(
                        inventory.id,
                        item_id,
                        item_data.get("quantity", 1),
                        item_data.get("is_equipped", False),
                        session=db.session
                    )
                    
            return True, None, inventory
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error importing inventory: {str(e)}")
            return False, f"Error: {str(e)}", None 