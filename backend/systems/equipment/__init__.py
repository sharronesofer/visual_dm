"""
Equipment package initialization.
This package provides functionality for managing equipment in the game,
building on top of the Inventory system.
"""

from .models import Equipment
from .inventory_utils import (
    load_equipment_rules,
    calculate_carry_capacity,
    can_equip_item,
    get_equipment_stats,
    get_item_details
)
from .shop_utils import (
    restock_shop_inventory,
    get_shop_inventory
)
from .service import EquipmentService
from .router import router as equipment_router

__all__ = [
    # Models
    'Equipment',
    
    # Utility functions
    'load_equipment_rules',
    'calculate_carry_capacity',
    'can_equip_item',
    'get_equipment_stats',
    'get_item_details',
    'restock_shop_inventory',
    'get_shop_inventory',
    
    # Service and router
    'EquipmentService',
    'equipment_router'
] 