"""
Inventory System Protocols

This module defines protocols (interfaces) for the inventory system
to avoid circular import dependencies between business and infrastructure layers.
"""

from typing import Optional, List, Dict, Any, Tuple, Protocol
from uuid import UUID

from backend.systems.inventory.models import (
    InventoryModel,
    InventoryType,
    InventoryStatus,
    EncumbranceLevel
)


# Repository Protocol
class InventoryRepositoryInterface(Protocol):
    """Repository interface for inventory data access"""
    
    async def create(self, data: Dict[str, Any]) -> InventoryModel:
        """Create a new inventory"""
        ...
    
    async def get_by_id(self, inventory_id: UUID) -> Optional[InventoryModel]:
        """Get inventory by ID"""
        ...
    
    async def get_by_name(self, name: str) -> Optional[InventoryModel]:
        """Get inventory by name"""
        ...
    
    async def get_by_name_and_owner(self, name: str, owner_id: UUID) -> Optional[InventoryModel]:
        """Get inventory by name for specific owner"""
        ...
    
    async def update(self, inventory_id: UUID, data: Dict[str, Any]) -> Optional[InventoryModel]:
        """Update existing inventory"""
        ...
    
    async def delete(self, inventory_id: UUID) -> bool:
        """Delete inventory"""
        ...
    
    async def list(self, page: int = 1, size: int = 50, status: Optional[str] = None, search: Optional[str] = None) -> Tuple[List[InventoryModel], int]:
        """List inventories with pagination"""
        ...
    
    async def list_by_owner(self, owner_id: UUID, page: int = 1, size: int = 50) -> Tuple[List[InventoryModel], int]:
        """List inventories by owner"""
        ...
    
    async def list_by_player(self, player_id: UUID, page: int = 1, size: int = 50) -> Tuple[List[InventoryModel], int]:
        """List inventories by player"""
        ...
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get inventory statistics"""
        ...


# Configuration Service Protocol
class InventoryConfigurationService(Protocol):
    """Configuration service for inventory system"""
    
    def get_inventory_type_config(self, inventory_type: InventoryType) -> Dict[str, Any]:
        """Get configuration for inventory type"""
        ...
    
    def get_status_transitions(self) -> Dict[str, List[str]]:
        """Get allowed status transitions"""
        ...
    
    def can_transition_status(self, from_status: InventoryStatus, to_status: InventoryStatus) -> bool:
        """Check if status transition is allowed"""
        ...
    
    def calculate_movement_mp_multiplier(self, encumbrance_level: EncumbranceLevel) -> float:
        """Calculate movement MP multiplier for encumbrance level"""
        ...


# Character/Player Service Protocol (for integration)
class CharacterServiceInterface(Protocol):
    """Interface for character service integration"""
    
    async def get_character_strength(self, character_id: UUID) -> int:
        """Get character strength attribute"""
        ...
    
    async def get_character_player_id(self, character_id: UUID) -> Optional[UUID]:
        """Get player ID for character"""
        ... 