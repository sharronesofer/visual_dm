"""
Inventory management system for Visual DM.

This module provides models, schemas, and business logic for managing game inventories.
It supports item creation, inventory management, item transfers, and validation.
"""

# Import models
from backend.systems.inventory.models import Item, Inventory, InventoryItem, ItemCategory

# Import schemas
from backend.systems.inventory.schemas import (
    ItemBase, ItemCreate, Item as ItemSchema,
    InventoryBase, InventoryCreate, Inventory as InventorySchema,
    InventoryItemBase, InventoryItemCreate, InventoryItem as InventoryItemSchema,
    InventoryTransferRequest, ValidationResponse,
    InventoryFilterParams, PaginatedInventoryResponse,
    ItemCategoryEnum
)

# Import validation
from backend.systems.inventory.validator import ValidationResult, InventoryValidator

# Import repositories
from backend.systems.inventory.repository import (
    ItemRepository, InventoryRepository, InventoryItemRepository
)

# Import services
from backend.systems.inventory.service import InventoryService

# Import utilities
from backend.systems.inventory.utils import (
    calculate_total_weight, get_equipped_items, group_equipment_by_type,
    InventoryContainer, InventoryTransaction, transfer_item_between_inventories,
    RecoveryManager
)

# Import router
from backend.systems.inventory.router import router as inventory_router

__all__ = [
    # Models
    'Item', 'Inventory', 'InventoryItem', 'ItemCategory',
    
    # Schemas
    'ItemBase', 'ItemCreate', 'ItemSchema',
    'InventoryBase', 'InventoryCreate', 'InventorySchema',
    'InventoryItemBase', 'InventoryItemCreate', 'InventoryItemSchema',
    'InventoryTransferRequest', 'ValidationResponse',
    'InventoryFilterParams', 'PaginatedInventoryResponse',
    'ItemCategoryEnum',
    
    # Validation
    'ValidationResult', 'InventoryValidator',
    
    # Repositories
    'ItemRepository', 'InventoryRepository', 'InventoryItemRepository',
    
    # Services
    'InventoryService',
    
    # Utilities
    'calculate_total_weight', 'get_equipped_items', 'group_equipment_by_type',
    'InventoryContainer', 'InventoryTransaction', 'transfer_item_between_inventories',
    'RecoveryManager',
    
    # Router
    'inventory_router'
]
