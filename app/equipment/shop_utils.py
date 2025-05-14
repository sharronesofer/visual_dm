"""
Shop utility functions for managing shop inventory and restocking.
"""

from app.core.database import db
from app.models.equipment import Equipment, EquipmentInstance
from app.models.point_of_interest import PointOfInterest
from app.core.utils.logging_utils import log_performance
from app.core.utils.error_utils import retry_on_db_error

@log_performance
@retry_on_db_error
def restock_shop_inventory(shop_id: int) -> None:
    """
    Restock a shop's inventory with new items.
    
    Args:
        shop_id (int): The ID of the shop to restock
    """
    shop = PointOfInterest.query.filter_by(id=shop_id, type='shop').first()
    if not shop:
        return
        
    # Clear existing inventory
    EquipmentInstance.query.filter_by(
        owner_type='shop',
        owner_id=shop_id
    ).delete()
    
    # Generate new inventory based on shop type and level
    shop_level = shop.properties.get('level', 1)
    shop_specialties = shop.properties.get('specialty_types', ['weapon', 'armor'])
    inventory_size = shop.properties.get('inventory_size', 20)
    
    items = Equipment.query.filter(
        Equipment.level_requirement <= shop_level,
        Equipment.equipment_type.in_(shop_specialties)
    ).limit(inventory_size).all()
    
    # Add items to shop inventory
    for item in items:
        instance = EquipmentInstance(
            equipment_id=item.id,
            owner_type='shop',
            owner_id=shop_id,
            condition=100
        )
        db.session.add(instance)
    
    db.session.commit() 