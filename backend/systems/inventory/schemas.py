"""
Pydantic schemas for inventory data validation and serialization.

This module defines the schemas used for validating API requests and 
responses related to inventory operations.
"""

from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime
from enum import Enum

class ItemCategoryEnum(str, Enum):
    """Enum for item categories in API schemas"""
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    QUEST = "quest"
    MISC = "misc"

class ItemBase(BaseModel):
    """Base schema for Item data"""
    name: str = Field(..., description="Name of the item")
    description: Optional[str] = Field(None, description="Description of the item")
    weight: float = Field(0.0, description="Weight of the item in pounds", ge=0)
    value: float = Field(0.0, description="Value of the item in gold pieces", ge=0)
    category: ItemCategoryEnum = Field(ItemCategoryEnum.MISC, description="Category of the item")
    is_stackable: bool = Field(True, description="Whether the item can stack in inventory")
    tags: List[str] = Field(default_factory=list, description="Tags for filtering and categorization")
    image_url: Optional[str] = Field(None, description="URL to item image")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "Longsword",
                "description": "A versatile one-handed slashing weapon",
                "weight": 3.0,
                "value": 15.0,
                "category": "weapon",
                "is_stackable": False,
                "tags": ["metal", "weapon", "martial", "sword"],
                "image_url": "/assets/items/longsword.png",
                "properties": {
                    "damage": "1d8",
                    "damage_type": "slashing",
                    "requires_attunement": False,
                    "durability": 100
                }
            }
        }

class ItemCreate(ItemBase):
    """Schema for creating a new item"""
    pass

class Item(ItemBase):
    """Schema for item responses"""
    id: int = Field(..., description="Unique identifier for the item")
    created_at: datetime = Field(..., description="When the item was created")
    updated_at: Optional[datetime] = Field(None, description="When the item was last updated")

class InventoryItemBase(BaseModel):
    """Base schema for inventory item data"""
    item_id: int = Field(..., description="Item ID")
    quantity: int = Field(1, description="Quantity of the item", gt=0)
    is_equipped: bool = Field(False, description="Whether the item is equipped")
    custom_name: Optional[str] = Field(None, description="Custom name for this specific item instance")
    condition: Optional[float] = Field(None, description="Condition of the item (0-100%)")
    position: Optional[Dict[str, int]] = Field(None, description="Position in the inventory grid")
    
    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

class InventoryItemCreate(InventoryItemBase):
    """Schema for creating a new inventory item"""
    inventory_id: int = Field(..., description="ID of the inventory this item belongs to")

class InventoryItem(InventoryItemBase):
    """Schema for inventory item responses"""
    id: int = Field(..., description="Unique identifier")
    inventory_id: int = Field(..., description="ID of the inventory this item belongs to")
    item: Item = Field(..., description="The full item data")
    
    class Config:
        orm_mode = True

class InventoryBase(BaseModel):
    """Base schema for inventory data"""
    name: str = Field(..., description="Name of the inventory")
    description: Optional[str] = Field(None, description="Description of the inventory")
    inventory_type: str = Field("generic", description="Type of inventory (character, container, shop)")
    owner_id: Optional[int] = Field(None, description="Owner ID (character, NPC, etc)")
    capacity: Optional[int] = Field(None, description="Maximum number of item slots")
    weight_limit: Optional[float] = Field(None, description="Maximum weight capacity in pounds")
    is_public: bool = Field(False, description="Whether the inventory is publicly viewable")

class InventoryCreate(InventoryBase):
    """Schema for creating a new inventory"""
    pass

class Inventory(InventoryBase):
    """Schema for inventory responses"""
    id: int = Field(..., description="Unique identifier")
    items: List[InventoryItem] = Field(default_factory=list, description="Items in the inventory")
    created_at: datetime = Field(..., description="When the inventory was created")
    updated_at: Optional[datetime] = Field(None, description="When the inventory was last updated")
    total_weight: float = Field(0.0, description="Total weight of all items")
    total_value: float = Field(0.0, description="Total value of all items")
    
    @root_validator
    def calculate_totals(cls, values):
        """Calculate derived fields like total weight and value"""
        items = values.get('items', [])
        
        total_weight = sum(item.quantity * item.item.weight for item in items)
        total_value = sum(item.quantity * item.item.value for item in items)
        
        values['total_weight'] = round(total_weight, 2)
        values['total_value'] = round(total_value, 2)
        
        return values
    
    class Config:
        orm_mode = True

class InventoryTransferRequest(BaseModel):
    """Schema for inventory transfer requests"""
    source_inventory_id: int = Field(..., description="Source inventory ID")
    target_inventory_id: int = Field(..., description="Target inventory ID")
    item_id: int = Field(..., description="Item ID to transfer")
    quantity: int = Field(1, description="Quantity to transfer", gt=0)
    
    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

class ValidationResponse(BaseModel):
    """Schema for validation responses"""
    valid: bool = Field(..., description="Whether the validation passed")
    error_message: Optional[str] = Field(None, description="Error message if validation failed")
    details: Optional[Dict[str, Any]] = Field(None, description="Detailed validation information")

class InventoryFilterParams(BaseModel):
    """Schema for inventory filtering parameters"""
    owner_id: Optional[int] = Field(None, description="Filter by owner ID")
    inventory_type: Optional[str] = Field(None, description="Filter by inventory type")
    is_public: Optional[bool] = Field(None, description="Filter by public status")
    contains_item_id: Optional[int] = Field(None, description="Filter inventories containing specific item")
    contains_item_category: Optional[str] = Field(None, description="Filter inventories containing items of category")
    min_capacity: Optional[int] = Field(None, description="Filter by minimum capacity")
    has_space: Optional[bool] = Field(None, description="Filter by having available space")
    
    class Config:
        extra = "ignore"

class PaginatedInventoryResponse(BaseModel):
    """Schema for paginated inventory listings"""
    items: List[Inventory] = Field(..., description="List of inventories")
    total: int = Field(..., description="Total number of inventories matching filter")
    page: int = Field(1, description="Current page number")
    size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
    
    @validator('pages')
    def calculate_pages(cls, v, values):
        """Ensure pages is calculated correctly"""
        if 'total' in values and 'size' in values and values['size'] > 0:
            return (values['total'] + values['size'] - 1) // values['size']
        return v 