"""
Shop utility functions for managing shop inventory and restocking.
All inventory operations should use the canonical Inventory/InventoryItem models and services.
Legacy direct field logic has been removed.
"""

# # # # from app.core.database import db
from app.models.inventory import Inventory, InventoryItem
from app.models.point_of_interest import PointOfInterest
from app.core.utils.logging_utils import log_performance
from app.core.utils.error_utils import retry_on_db_error

@log_performance
@retry_on_db_error
def restock_shop_inventory(shop_id: int) -> None:
    """
    Restock a shop's inventory with new items using the canonical Inventory/InventoryItem system.
    Args:
        shop_id (int): The ID of the shop to restock
    """
    shop = PointOfInterest.query.filter_by(id=shop_id, type='shop').first()
    if not shop:
        return
    
    # Clear existing inventory
    InventoryItem.query.filter_by(
        inventory_id=shop_id
    ).delete()
    
    # Generate new inventory based on shop type and level
    shop_level = shop.properties.get('level', 1)
    shop_specialties = shop.properties.get('specialty_types', ['weapon', 'armor'])
    inventory_size = shop.properties.get('inventory_size', 20)
    
    # This assumes a function exists to get items by type/level; replace as needed
    items = []  # Replace with canonical item selection logic
    
    # Add items to shop inventory
    for item in items:
        instance = InventoryItem(
            inventory_id=shop_id,
            item_id=item.id,
            quantity=1,
            condition=100
        )
        db.session.add(instance)
    
    db.session.commit() 
