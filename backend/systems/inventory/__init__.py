"""
Inventory System - Business Logic Only

This module contains only the business logic for the inventory system.
Infrastructure components have been moved to backend.infrastructure.

For infrastructure components, import from:
- backend.infrastructure.systems.inventory.models (database entities)
- backend.infrastructure.systems.inventory.repositories (data access)
- backend.infrastructure.config_loaders.inventory_config (configuration loading)
- backend.infrastructure.systems.inventory.routers (API routes)
- backend.infrastructure.systems.inventory.schemas (API schemas)
- backend.infrastructure.systems.inventory.events (event handling)
"""

# Business Logic Exports
from .models import (
    InventoryBaseModel,
    InventoryModel,
    CreateInventoryRequest,
    UpdateInventoryRequest,
    InventoryResponse,
    InventoryListResponse
)
from .services import (
    InventoryService, 
    InventoryRepositoryInterface,
    create_inventory_service
)
from .utils import InventoryConfigLoader, get_config_loader, reload_config

__all__ = [
    # Business Models
    "InventoryBaseModel",
    "InventoryModel",
    "CreateInventoryRequest",
    "UpdateInventoryRequest", 
    "InventoryResponse",
    "InventoryListResponse",
    
    # Business Services & Interfaces
    "InventoryService",
    "InventoryRepositoryInterface",
    "create_inventory_service",
    
    # Configuration Management (proxied from infrastructure)
    "InventoryConfigLoader",
    "get_config_loader",
    "reload_config"
]
