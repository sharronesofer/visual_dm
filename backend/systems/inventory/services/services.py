"""
Inventory System Business Services

This module provides business logic services for the inventory system
according to the Development Bible standards and game requirements.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime
import json
import os

# Business Models
from backend.systems.inventory.models import (
    InventoryModel,
    CreateInventoryRequest,
    UpdateInventoryRequest,
    InventoryResponse,
    InventoryListResponse,
    InventoryCapacityInfo,
    ItemTransferRequest,
    ItemTransferResponse,
    InventoryFilterOptions,
    InventoryStatistics,
    InventoryType,
    InventoryStatus,
    EncumbranceLevel
)

# Import protocols from separate module to avoid circular imports
from backend.systems.inventory.protocols import (
    InventoryRepositoryInterface,
    InventoryConfigurationService,
    CharacterServiceInterface
)


class DefaultInventoryConfigurationService:
    """Default implementation of inventory configuration using infrastructure loader"""
    
    def __init__(self):
        # Use the infrastructure configuration loader
        from backend.infrastructure.utils.inventory.config_loader import ConfigurableInventoryService
        self._config_service = ConfigurableInventoryService()
    
    def get_inventory_type_config(self, inventory_type: InventoryType) -> Dict[str, Any]:
        """Get configuration for inventory type"""
        return self._config_service.get_inventory_type_config(inventory_type)
    
    def get_status_transitions(self) -> Dict[str, List[str]]:
        """Get allowed status transitions"""
        return self._config_service.get_status_transitions()
    
    def can_transition_status(self, from_status: InventoryStatus, to_status: InventoryStatus) -> bool:
        """Check if status transition is allowed"""
        return self._config_service.can_transition_status(from_status, to_status)
    
    def calculate_movement_mp_multiplier(self, encumbrance_level: EncumbranceLevel) -> float:
        """Calculate movement MP multiplier for encumbrance level"""
        return self._config_service.calculate_movement_mp_multiplier(encumbrance_level)


class InventoryCapacityService:
    """Service for managing inventory capacity and weight calculations"""
    
    def __init__(self, character_service: Optional[CharacterServiceInterface] = None):
        self.character_service = character_service
        # Use infrastructure configuration
        from backend.infrastructure.utils.inventory.config_loader import ConfigurableInventoryService
        self._config_service = ConfigurableInventoryService()
    
    async def calculate_max_weight_for_character(self, character_id: UUID) -> float:
        """Calculate max weight capacity based on character strength"""
        if not self.character_service:
            return 100.0  # Default fallback
        
        strength = await self.character_service.get_character_strength(character_id)
        # Use configuration for calculation
        return self._config_service.calculate_max_weight_from_strength(strength)
    
    def calculate_encumbrance_impact(self, encumbrance_level: EncumbranceLevel) -> Dict[str, Any]:
        """Calculate the impact of encumbrance on character"""
        return self._config_service.get_encumbrance_effects(encumbrance_level)


class InventoryBusinessService:
    """Core business service for inventory operations"""
    
    def __init__(
        self,
        repository: InventoryRepositoryInterface,
        config_service: InventoryConfigurationService,
        capacity_service: InventoryCapacityService,
        character_service: Optional[CharacterServiceInterface] = None
    ):
        self.repository = repository
        self.config_service = config_service
        self.capacity_service = capacity_service
        self.character_service = character_service
    
    async def create_inventory(self, request: CreateInventoryRequest) -> InventoryResponse:
        """Create a new inventory with business validation"""
        # Business rule: Check for duplicate names
        if request.owner_id:
            # Check for duplicate names per player/owner
            existing = await self._check_duplicate_name_for_owner(request.name, request.owner_id)
            if existing:
                raise ValueError(f"Inventory with name '{request.name}' already exists for this owner")
        else:
            # No owner specified, check globally
            existing = await self.repository.get_by_name(request.name)
            if existing:
                raise ValueError(f"Inventory with name '{request.name}' already exists")
        
        # Get type-specific configuration
        type_config = self.config_service.get_inventory_type_config(request.inventory_type)
        
        # Set defaults from configuration
        max_capacity = request.max_capacity or type_config.get("default_capacity", 50)
        max_weight = request.max_weight or type_config.get("default_weight_limit", 100.0)
        
        # For character inventories, calculate weight based on strength
        if request.inventory_type == InventoryType.CHARACTER and request.owner_id:
            if self.character_service:
                calculated_weight = await self.capacity_service.calculate_max_weight_for_character(request.owner_id)
                max_weight = calculated_weight
        
        # Get player ID if not provided
        player_id = request.player_id
        if not player_id and request.owner_id and self.character_service:
            player_id = await self.character_service.get_character_player_id(request.owner_id)
        
        # Create inventory model
        inventory_data = {
            "name": request.name,
            "description": request.description,
            "inventory_type": request.inventory_type.value,
            "status": InventoryStatus.ACTIVE.value,
            "properties": request.properties,
            "owner_id": request.owner_id,
            "player_id": player_id,
            "max_capacity": max_capacity,
            "max_weight": max_weight,
            "current_item_count": 0,
            "current_weight": 0.0,
            "allows_trading": type_config.get("allows_trading", True),
            "allows_sorting": type_config.get("allows_sorting", True),
            "allows_filtering": type_config.get("allows_filtering", True),
            "default_sort": type_config.get("default_sort", "name"),
            "available_filters": type_config.get("available_filters", [])
        }
        
        inventory = await self.repository.create(inventory_data)
        return InventoryResponse.from_model(inventory)
    
    async def get_inventory_by_id(self, inventory_id: UUID) -> Optional[InventoryResponse]:
        """Get inventory by ID"""
        inventory = await self.repository.get_by_id(inventory_id)
        if not inventory:
            return None
        return InventoryResponse.from_model(inventory)
    
    async def update_inventory(self, inventory_id: UUID, request: UpdateInventoryRequest) -> InventoryResponse:
        """Update inventory with business validation"""
        # Business rule: Inventory must exist
        inventory = await self.repository.get_by_id(inventory_id)
        if not inventory:
            raise ValueError(f"Inventory {inventory_id} not found")
        
        update_data = {}
        
        # Update basic fields
        if request.name is not None:
            # Check for duplicate names
            if request.name != inventory.name and inventory.owner_id:
                existing = await self._check_duplicate_name_for_owner(request.name, inventory.owner_id)
                if existing and existing.id != inventory_id:
                    raise ValueError(f"Inventory with name '{request.name}' already exists for this owner")
            update_data["name"] = request.name
        
        if request.description is not None:
            update_data["description"] = request.description
        
        if request.properties is not None:
            update_data["properties"] = request.properties
        
        # Handle status transitions
        if request.status is not None:
            current_status = InventoryStatus(inventory.status)
            new_status = request.status
            
            if not self.config_service.can_transition_status(current_status, new_status):
                raise ValueError(f"Cannot transition from {current_status.value} to {new_status.value}")
            
            update_data["status"] = new_status.value
        
        # Update capacity fields
        if request.max_capacity is not None:
            # Business rule: Cannot reduce capacity below current item count
            if request.max_capacity < inventory.current_item_count:
                raise ValueError(f"Cannot reduce capacity below current item count ({inventory.current_item_count})")
            update_data["max_capacity"] = request.max_capacity
        
        if request.max_weight is not None:
            # Business rule: Cannot reduce weight limit below current weight (with overload threshold)
            overload_threshold = 1.25  # Default, should come from config
            try:
                # Try to get from configuration
                rules = self.config_service.get_inventory_type_config(inventory.inventory_type)
                capacity_config = rules.get("capacity_management", {})
                overload_threshold = capacity_config.get("overload_threshold", 1.25)
            except Exception:
                pass  # Use default if config unavailable
            
            if request.max_weight < (inventory.current_weight / overload_threshold):
                raise ValueError(f"Cannot reduce weight limit below current weight with overload allowance")
            update_data["max_weight"] = request.max_weight
        
        update_data["updated_at"] = datetime.utcnow()
        
        updated_inventory = await self.repository.update(inventory_id, update_data)
        if not updated_inventory:
            raise ValueError(f"Failed to update inventory {inventory_id}")
        
        return InventoryResponse.from_model(updated_inventory)
    
    async def delete_inventory(self, inventory_id: UUID) -> bool:
        """Delete inventory with business validation"""
        # Business rule: Inventory must exist
        inventory = await self.repository.get_by_id(inventory_id)
        if not inventory:
            raise ValueError(f"Inventory {inventory_id} not found")
        
        # Business rule: Can only delete active inventories
        if inventory.status != InventoryStatus.ACTIVE.value:
            raise ValueError(f"Cannot delete inventory in {inventory.status} status")
        
        # Business rule: Cannot delete if it contains items
        if inventory.current_item_count > 0:
            raise ValueError(f"Cannot delete inventory containing {inventory.current_item_count} items")
        
        return await self.repository.delete(inventory_id)
    
    async def list_inventories(
        self,
        page: int = 1,
        size: int = 50,
        filters: Optional[InventoryFilterOptions] = None
    ) -> InventoryListResponse:
        """List inventories with business filtering"""
        # For now, use basic repository listing
        # TODO: Implement advanced filtering in repository
        status_filter = None
        search_filter = None
        
        if filters:
            if filters.status and len(filters.status) == 1:
                status_filter = filters.status[0].value
            if filters.search:
                search_filter = filters.search
        
        inventories, total = await self.repository.list(page, size, status_filter, search_filter)
        
        # Convert to responses
        responses = [InventoryResponse.from_model(inv) for inv in inventories]
        
        # Calculate summary statistics
        total_active = sum(1 for inv in inventories if inv.status == InventoryStatus.ACTIVE.value)
        total_by_type = {}
        total_by_status = {}
        
        for inv in inventories:
            # Count by type
            inv_type = inv.inventory_type
            total_by_type[inv_type] = total_by_type.get(inv_type, 0) + 1
            
            # Count by status
            total_by_status[inv.status] = total_by_status.get(inv.status, 0) + 1
        
        return InventoryListResponse(
            items=responses,
            total=total,
            page=page,
            size=size,
            has_next=(page * size) < total,
            has_prev=page > 1,
            total_active=total_active,
            total_by_type=total_by_type,
            total_by_status=total_by_status
        )
    
    async def get_inventory_capacity_info(self, inventory_id: UUID) -> InventoryCapacityInfo:
        """Get detailed capacity information for inventory"""
        inventory = await self.repository.get_by_id(inventory_id)
        if not inventory:
            raise ValueError(f"Inventory {inventory_id} not found")
        
        encumbrance_level = inventory.get_encumbrance_level()
        movement_mp_multiplier = self.config_service.calculate_movement_mp_multiplier(encumbrance_level)
        
        return InventoryCapacityInfo(
            inventory_id=inventory.id,
            current_item_count=inventory.current_item_count,
            max_capacity=inventory.max_capacity,
            current_weight=inventory.current_weight,
            max_weight=inventory.max_weight,
            capacity_percentage=inventory.get_capacity_percentage(),
            weight_percentage=inventory.get_weight_percentage(),
            encumbrance_level=encumbrance_level,
            movement_mp_multiplier=movement_mp_multiplier,
            is_near_capacity=inventory.get_capacity_percentage() > 80.0,
            is_over_weight=inventory.max_weight is not None and inventory.current_weight > inventory.max_weight,
            can_add_items=inventory.can_add_item()
        )
    
    async def validate_item_addition(
        self,
        inventory_id: UUID,
        item_weight: float,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """Validate if item can be added to inventory"""
        inventory = await self.repository.get_by_id(inventory_id)
        if not inventory:
            raise ValueError(f"Inventory {inventory_id} not found")
        
        # Check if inventory allows operations
        if inventory.status != InventoryStatus.ACTIVE.value:
            return {
                "can_add": False,
                "reason": f"Inventory is {inventory.status}",
                "blocking": True
            }
        
        # Check capacity
        can_add = inventory.can_add_item(item_weight, quantity)
        new_count = inventory.current_item_count + quantity
        new_weight = inventory.current_weight + (item_weight * quantity)
        
        result = {
            "can_add": can_add,
            "current_count": inventory.current_item_count,
            "new_count": new_count,
            "current_weight": inventory.current_weight,
            "new_weight": new_weight,
            "max_capacity": inventory.max_capacity,
            "max_weight": inventory.max_weight
        }
        
        if not can_add:
            if new_count > inventory.max_capacity:
                result["reason"] = f"Would exceed capacity ({new_count}/{inventory.max_capacity})"
            elif inventory.max_weight and new_weight > inventory.max_weight * 1.25:
                result["reason"] = f"Would exceed weight limit ({new_weight:.1f}/{inventory.max_weight:.1f})"
            result["blocking"] = True
        else:
            # Check for warnings
            warnings = []
            if new_count / inventory.max_capacity > 0.8:
                warnings.append("Approaching capacity limit")
            
            if inventory.max_weight and new_weight / inventory.max_weight > 0.8:
                warnings.append("Approaching weight limit")
            
            result["warnings"] = warnings
        
        return result
    
    async def get_inventory_statistics(self) -> InventoryStatistics:
        """Get comprehensive inventory statistics"""
        stats_data = await self.repository.get_statistics()
        
        # The repository should provide these statistics
        # For now, provide basic structure
        return InventoryStatistics(
            total_inventories=stats_data.get("total", 0),
            by_type=stats_data.get("by_type", {}),
            by_status=stats_data.get("by_status", {}),
            by_encumbrance=stats_data.get("by_encumbrance", {}),
            average_capacity_usage=stats_data.get("avg_capacity_usage", 0.0),
            average_weight_usage=stats_data.get("avg_weight_usage", 0.0),
            total_items_stored=stats_data.get("total_items", 0),
            total_weight_stored=stats_data.get("total_weight", 0.0),
            total_players_with_inventories=stats_data.get("total_players", 0),
            average_inventories_per_player=stats_data.get("avg_inventories_per_player", 0.0)
        )
    
    async def _check_duplicate_name_for_owner(self, name: str, owner_id: UUID) -> Optional[InventoryModel]:
        """Check for duplicate inventory names for the same owner"""
        return await self.repository.get_by_name_and_owner(name, owner_id)


# Facade Service for Compatibility
class InventoryService:
    """Facade service that provides the expected interface for existing tests and routers"""
    
    def __init__(self, repository: InventoryRepositoryInterface):
        self.repository = repository
        # Create business service directly to avoid recursion
        config_service = DefaultInventoryConfigurationService()
        capacity_service = InventoryCapacityService()
        self.business_service = InventoryBusinessService(
            repository=repository,
            config_service=config_service,
            capacity_service=capacity_service,
            character_service=None
        )
    
    async def create_inventory(self, request: CreateInventoryRequest) -> InventoryResponse:
        """Create new inventory"""
        return await self.business_service.create_inventory(request)
    
    async def get_inventory_by_id(self, inventory_id: UUID) -> Optional[InventoryResponse]:
        """Get inventory by ID"""
        return await self.business_service.get_inventory_by_id(inventory_id)
    
    async def update_inventory(self, inventory_id: UUID, request: UpdateInventoryRequest) -> InventoryResponse:
        """Update inventory"""
        return await self.business_service.update_inventory(inventory_id, request)
    
    async def delete_inventory(self, inventory_id: UUID) -> bool:
        """Delete inventory"""
        return await self.business_service.delete_inventory(inventory_id)
    
    async def list_inventories(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[InventoryResponse], int]:
        """List inventories (simplified interface for compatibility)"""
        filters = None
        if status or search:
            filters = InventoryFilterOptions()
            if status:
                filters.status = [InventoryStatus(status)]
            if search:
                filters.search = search
        
        result = await self.business_service.list_inventories(page, size, filters)
        return result.items, result.total
    
    async def get_inventory_statistics(self) -> Dict[str, Any]:
        """Get inventory statistics"""
        stats = await self.business_service.get_inventory_statistics()
        return {
            "total": stats.total_inventories,
            "by_type": stats.by_type,
            "by_status": stats.by_status
        }


# Service Factory Functions
def create_inventory_service(
    repository: InventoryRepositoryInterface,
    config_service: Optional[InventoryConfigurationService] = None,
    character_service: Optional[CharacterServiceInterface] = None
) -> InventoryService:
    """Factory function to create inventory facade service"""
    # Business rule: Repository is required
    if repository is None:
        raise ValueError("Repository cannot be None")
    
    # Return the facade service
    return InventoryService(repository)


def create_inventory_business_service(
    repository: InventoryRepositoryInterface,
    config_service: Optional[InventoryConfigurationService] = None,
    character_service: Optional[CharacterServiceInterface] = None
) -> InventoryBusinessService:
    """Factory function to create inventory business service directly"""
    # Business rule: Repository is required
    if repository is None:
        raise ValueError("Repository cannot be None")
    
    if config_service is None:
        config_service = DefaultInventoryConfigurationService()
    
    capacity_service = InventoryCapacityService(character_service)
    
    return InventoryBusinessService(
        repository=repository,
        config_service=config_service,
        capacity_service=capacity_service,
        character_service=character_service
    )
