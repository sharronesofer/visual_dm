"""
Inventory System Business Models

This module provides business domain models for the inventory system
according to the Development Bible standards and game requirements.
"""

from typing import Optional, List, Dict, Any, Union
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator


class InventoryType(str, Enum):
    """Inventory type enumeration from inventory_types.json"""
    CHARACTER = "character"
    CONTAINER = "container" 
    SHOP = "shop"
    BANK = "bank"
    QUEST = "quest"


class InventoryStatus(str, Enum):
    """Inventory status enumeration from inventory_statuses.json"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ARCHIVED = "archived"
    CORRUPTED = "corrupted"


class EncumbranceLevel(str, Enum):
    """Encumbrance levels for weight-based capacity"""
    NORMAL = "normal"
    HEAVY = "heavy"
    ENCUMBERED = "encumbered"
    OVERLOADED = "overloaded"


class InventoryBaseModel(BaseModel):
    """Base model with common fields for all inventory models"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None
        }


class InventoryModel(InventoryBaseModel):
    """Core inventory business model"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    inventory_type: InventoryType = InventoryType.CHARACTER
    status: InventoryStatus = InventoryStatus.ACTIVE
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    # Ownership
    owner_id: Optional[UUID] = None  # Character ID who owns this inventory
    player_id: Optional[UUID] = None  # Player ID (derived from character)
    
    # Capacity Management (weight-based) - limits from inventory_rules.json capacity_management.limits
    max_capacity: int = Field(default=50, ge=1, le=1000)
    max_weight: Optional[float] = Field(default=100.0, ge=0.0)
    current_item_count: int = Field(default=0, ge=0)
    current_weight: float = Field(default=0.0, ge=0.0)
    
    # Type-specific configurations loaded from JSON
    allows_trading: bool = True
    allows_sorting: bool = True  
    allows_filtering: bool = True
    default_sort: str = "name"
    available_filters: List[str] = Field(default_factory=list)

    @validator('current_item_count')
    def validate_item_count(cls, v, values):
        if v < 0:
            raise ValueError("Item count cannot be negative")
        max_capacity = values.get('max_capacity', 50)
        if v > max_capacity:
            raise ValueError(f"Current item count {v} exceeds max capacity {max_capacity}")
        return v

    @validator('current_weight')
    def validate_current_weight(cls, v, values):
        if v < 0.0:
            raise ValueError("Current weight cannot be negative")
        max_weight = values.get('max_weight')
        # Using 1.25 threshold (25% overload) from inventory_rules.json capacity_management.overload_threshold
        if max_weight is not None and v > max_weight * 1.25:
            raise ValueError(f"Current weight {v} far exceeds max weight {max_weight}")
        return v

    def get_encumbrance_level(self) -> EncumbranceLevel:
        """Calculate encumbrance level based on current weight
        
        Note: This method uses hardcoded thresholds for now. 
        For production use, this should be called through a service 
        that has access to the configuration loader.
        """
        if self.max_weight is None:
            return EncumbranceLevel.NORMAL
        
        ratio = self.current_weight / self.max_weight
        
        # TODO: Load these from configuration service
        # For now using defaults that match inventory_rules.json
        if ratio <= 0.75:  # normal threshold from config
            return EncumbranceLevel.NORMAL
        elif ratio <= 1.0:  # heavy threshold from config
            return EncumbranceLevel.HEAVY
        elif ratio <= 1.25:  # encumbered threshold from config
            return EncumbranceLevel.ENCUMBERED
        else:
            return EncumbranceLevel.OVERLOADED

    def get_capacity_percentage(self) -> float:
        """Get capacity usage as percentage"""
        if self.max_capacity == 0:
            return 100.0
        return (self.current_item_count / self.max_capacity) * 100.0

    def get_weight_percentage(self) -> float:
        """Get weight usage as percentage"""
        if self.max_weight is None or self.max_weight == 0:
            return 0.0
        return (self.current_weight / self.max_weight) * 100.0

    def can_add_item(self, item_weight: float = 0.0, quantity: int = 1) -> bool:
        """Check if item can be added without exceeding limits"""
        new_count = self.current_item_count + quantity
        new_weight = self.current_weight + (item_weight * quantity)
        
        if new_count > self.max_capacity:
            return False
        
        if self.max_weight is not None and new_weight > self.max_weight * 1.25:
            return False
            
        return True


class CreateInventoryRequest(BaseModel):
    """Request model for creating new inventory"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    inventory_type: InventoryType = InventoryType.CHARACTER
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    # Ownership (required for most inventory types)
    owner_id: Optional[UUID] = None
    player_id: Optional[UUID] = None
    
    # Capacity overrides (optional, will use type defaults)
    max_capacity: Optional[int] = Field(None, ge=1, le=1000)
    max_weight: Optional[float] = Field(None, ge=0.0)

    @validator('owner_id')
    def validate_ownership(cls, v, values):
        inventory_type = values.get('inventory_type')
        if inventory_type in [InventoryType.CHARACTER, InventoryType.QUEST] and v is None:
            raise ValueError(f"owner_id is required for {inventory_type} inventory")
        return v


class UpdateInventoryRequest(BaseModel):
    """Request model for updating inventory"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[InventoryStatus] = None
    properties: Optional[Dict[str, Any]] = None
    
    # Capacity management updates
    max_capacity: Optional[int] = Field(None, ge=1, le=1000)
    max_weight: Optional[float] = Field(None, ge=0.0)


class InventoryResponse(InventoryBaseModel):
    """Response model for inventory data"""
    name: str
    description: Optional[str]
    inventory_type: InventoryType
    status: InventoryStatus
    properties: Dict[str, Any]
    
    # Ownership
    owner_id: Optional[UUID]
    player_id: Optional[UUID]
    
    # Capacity information
    max_capacity: int
    max_weight: Optional[float]
    current_item_count: int
    current_weight: float
    
    # Calculated fields
    encumbrance_level: EncumbranceLevel
    capacity_percentage: float
    weight_percentage: float
    
    # Type-specific settings
    allows_trading: bool
    allows_sorting: bool
    allows_filtering: bool
    default_sort: str
    available_filters: List[str]

    @classmethod
    def from_model(cls, inventory: InventoryModel) -> "InventoryResponse":
        """Create response from inventory model"""
        return cls(
            id=inventory.id,
            created_at=inventory.created_at,
            updated_at=inventory.updated_at,
            is_active=inventory.is_active,
            metadata=inventory.metadata,
            name=inventory.name,
            description=inventory.description,
            inventory_type=inventory.inventory_type,
            status=inventory.status,
            properties=inventory.properties,
            owner_id=inventory.owner_id,
            player_id=inventory.player_id,
            max_capacity=inventory.max_capacity,
            max_weight=inventory.max_weight,
            current_item_count=inventory.current_item_count,
            current_weight=inventory.current_weight,
            encumbrance_level=inventory.get_encumbrance_level(),
            capacity_percentage=inventory.get_capacity_percentage(),
            weight_percentage=inventory.get_weight_percentage(),
            allows_trading=inventory.allows_trading,
            allows_sorting=inventory.allows_sorting,
            allows_filtering=inventory.allows_filtering,
            default_sort=inventory.default_sort,
            available_filters=inventory.available_filters
        )


class InventoryListResponse(BaseModel):
    """Response model for paginated inventory lists"""
    items: List[InventoryResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool
    
    # Summary statistics
    total_active: int = 0
    total_by_type: Dict[str, int] = Field(default_factory=dict)
    total_by_status: Dict[str, int] = Field(default_factory=dict)


class InventoryCapacityInfo(BaseModel):
    """Detailed capacity information for an inventory"""
    inventory_id: UUID
    current_item_count: int
    max_capacity: int
    current_weight: float
    max_weight: Optional[float]
    
    # Calculated values
    capacity_percentage: float
    weight_percentage: float
    encumbrance_level: EncumbranceLevel
    movement_mp_multiplier: float
    
    # Warnings
    is_near_capacity: bool = False
    is_over_weight: bool = False
    can_add_items: bool = True


class ItemTransferRequest(BaseModel):
    """Request model for transferring items between inventories"""
    from_inventory_id: UUID
    to_inventory_id: UUID
    item_id: UUID
    quantity: int = Field(default=1, ge=1)
    
    # Optional overrides
    ignore_capacity_limits: bool = False
    force_transfer: bool = False  # Admin only


class ItemTransferResponse(BaseModel):
    """Response model for item transfer operations"""
    success: bool
    transfer_id: UUID = Field(default_factory=uuid4)
    from_inventory_id: UUID
    to_inventory_id: UUID
    item_id: UUID
    quantity_transferred: int
    
    # Updated capacity info
    from_inventory_capacity: InventoryCapacityInfo
    to_inventory_capacity: InventoryCapacityInfo
    
    # Transfer details
    transfer_timestamp: datetime = Field(default_factory=datetime.utcnow)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class InventoryFilterOptions(BaseModel):
    """Available filter options for inventory queries"""
    status: Optional[List[InventoryStatus]] = None
    inventory_type: Optional[List[InventoryType]] = None
    owner_id: Optional[UUID] = None
    player_id: Optional[UUID] = None
    has_capacity: Optional[bool] = None  # Has available capacity
    is_overweight: Optional[bool] = None
    encumbrance_level: Optional[List[EncumbranceLevel]] = None
    search: Optional[str] = None  # Search in name/description


class InventoryStatistics(BaseModel):
    """Statistics about inventories in the system"""
    total_inventories: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    by_encumbrance: Dict[str, int]
    
    # Capacity statistics
    average_capacity_usage: float
    average_weight_usage: float
    total_items_stored: int
    total_weight_stored: float
    
    # Player statistics
    total_players_with_inventories: int
    average_inventories_per_player: float
