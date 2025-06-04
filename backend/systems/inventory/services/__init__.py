"""Business services for inventory system"""

from .services import (
    InventoryService, 
    InventoryBusinessService,
    DefaultInventoryConfigurationService,
    InventoryCapacityService,
    create_inventory_service
)

from backend.systems.inventory.protocols import (
    InventoryRepositoryInterface,
    InventoryConfigurationService,
    CharacterServiceInterface
)

__all__ = [
    # Service classes
    "InventoryService",
    "InventoryBusinessService", 
    "DefaultInventoryConfigurationService",
    "InventoryCapacityService",
    "create_inventory_service",
    
    # Protocol interfaces
    "InventoryRepositoryInterface",
    "InventoryConfigurationService",
    "CharacterServiceInterface"
]
