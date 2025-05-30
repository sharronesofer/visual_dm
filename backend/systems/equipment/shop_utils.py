"""
Shop utility functions for managing shop inventory and restocking.
This module provides equipment-specific shop functionality that works with
the canonical Inventory system.
"""

from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Import canonical inventory and database modules
try:
    from backend.core.database import db
    from backend.systems.inventory.models import Inventory, InventoryItem
    from backend.systems.poi.models import PointOfInterest
    from backend.core.utils.logging_utils import log_performance
    from backend.core.utils.error_utils import retry_on_db_error
    HAS_INVENTORY_SYSTEM = True
except ImportError:
    HAS_INVENTORY_SYSTEM = False
    logger.warning("Canonical inventory system not available. Shop functions will be limited.")
    
    # Define stub decorators for compatibility
    def log_performance(func):
        return func
    def retry_on_db_error(func):
        return func

@log_performance
@retry_on_db_error
def restock_shop_inventory(shop_id: int) -> Dict[str, Any]:
    """
    Restock a shop's inventory with new items using the canonical Inventory/InventoryItem system.
    
    Args:
        shop_id: The ID of the shop to restock
        
    Returns:
        Dict with status of restocking operation
    
    Note:
        This operation requires the canonical inventory system to be available.
    """
    if not HAS_INVENTORY_SYSTEM:
        return {
            "success": False,
            "message": "Cannot restock shop: Inventory system not available"
        }
    
    try:
        shop = PointOfInterest.query.filter_by(id=shop_id, type='shop').first()
        if not shop:
            return {
                "success": False,
                "message": f"Shop with ID {shop_id} not found"
            }
        
        # Clear existing inventory
        InventoryItem.query.filter_by(
            inventory_id=shop_id
        ).delete()
        
        # Generate new inventory based on shop type and level
        shop_level = shop.properties.get('level', 1)
        shop_specialties = shop.properties.get('specialty_types', ['weapon', 'armor'])
        inventory_size = shop.properties.get('inventory_size', 20)
        
        # Get items based on shop type, level, and specialties
        items = _generate_shop_items(shop_level, shop_specialties, inventory_size)
        
        # Add items to shop inventory
        for item in items:
            instance = InventoryItem(
                inventory_id=shop_id,
                item_id=item.id,
                quantity=1,
                condition=100,
                properties=item.properties
            )
            db.session.add(instance)
        
        db.session.commit()
        
        return {
            "success": True,
            "message": f"Shop inventory restocked with {len(items)} items",
            "shop_id": shop_id,
            "items_added": len(items)
        }
    except Exception as e:
        logger.error(f"Error restocking shop inventory: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

def _generate_shop_items(level: int, specialties: List[str], count: int) -> List:
    """
    Generate a list of items for a shop based on level and specialties.
    
    Args:
        level: Shop level, affecting item quality and rarity
        specialties: Shop specialties, determining item types
        count: Number of items to generate
        
    Returns:
        List of item objects to stock in the shop
    """
    # This would normally call an item generation service
    # For now, return an empty list as a placeholder
    return []

def get_shop_inventory(shop_id: int) -> Optional[Dict[str, Any]]:
    """
    Get the inventory of a shop.
    
    Args:
        shop_id: ID of the shop
        
    Returns:
        Dictionary containing shop inventory information, or error response if shop not found
    """
    if not HAS_INVENTORY_SYSTEM:
        return {
            "success": False,
            "message": "Cannot get shop inventory: Inventory system not available"
        }
    
    try:    
        shop = PointOfInterest.query.filter_by(id=shop_id, type='shop').first()
        if not shop:
            return {
                "success": False,
                "message": f"Shop with ID {shop_id} not found"
            }
            
        inventory = Inventory.query.filter_by(id=shop_id).first()
        if not inventory:
            return {
                "success": False,
                "message": f"Inventory for shop {shop_id} not found"
            }
            
        items = InventoryItem.query.filter_by(inventory_id=shop_id).all()
        
        return {
            "success": True,
            "shop_id": shop_id,
            "name": shop.name,
            "level": shop.properties.get('level', 1),
            "specialties": shop.properties.get('specialty_types', []),
            "items": [item.to_dict() for item in items]
        }
    except Exception as e:
        logger.error(f"Error getting shop inventory: {e}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        } 