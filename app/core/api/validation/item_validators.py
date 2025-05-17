"""Validation models for Item-related API requests."""

from typing import Dict, List, Optional, ClassVar
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime

from .base_validators import (
    PaginationValidationMixin,
    SortValidationMixin,
    FilterValidationMixin,
    DateRangeValidationMixin,
    validate_id,
    validate_name,
    validate_description,
    validate_tags,
    validate_metadata
)

class ItemType(str, Enum):
    """Valid item type values."""
    WEAPON = "weapon"
    ARMOR = "armor"
    POTION = "potion"
    SCROLL = "scroll"
    TOOL = "tool"
    TREASURE = "treasure"
    QUEST_ITEM = "quest_item"
    MISC = "misc"

class ItemRarity(str, Enum):
    """Valid item rarity values."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"

class ItemStatus(str, Enum):
    """Valid item status values."""
    AVAILABLE = "available"
    IN_USE = "in_use"
    BROKEN = "broken"
    LOST = "lost"
    DESTROYED = "destroyed"

class ItemCreateRequest(BaseModel):
    """Validation model for item creation requests."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    type: ItemType
    rarity: ItemRarity = Field(default=ItemRarity.COMMON)
    status: ItemStatus = Field(default=ItemStatus.AVAILABLE)
    location_id: Optional[str] = Field(None, min_length=1, max_length=100)
    owner_id: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: int = Field(default=1, ge=0)
    value: Optional[float] = Field(None, ge=0)
    weight: Optional[float] = Field(None, ge=0)
    tags: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict] = Field(default_factory=dict)
    
    @validator('location_id')
    def validate_location_id(cls, v):
        """Validate location ID if provided."""
        if v is not None:
            result = validate_id(v)
            if not result.is_valid:
                raise ValueError(f"Invalid location ID: {result.errors[0]['error']}")
        return v
    
    @validator('owner_id')
    def validate_owner_id(cls, v):
        """Validate owner ID if provided."""
        if v is not None:
            result = validate_id(v)
            if not result.is_valid:
                raise ValueError(f"Invalid owner ID: {result.errors[0]['error']}")
        return v
    
    @validator('tags')
    def validate_tags_list(cls, v):
        """Validate tags if provided."""
        if v:
            result = validate_tags(v)
            if not result.is_valid:
                raise ValueError(result.errors[0]['error'])
        return v
    
    @validator('metadata')
    def validate_metadata_dict(cls, v):
        """Validate metadata if provided."""
        if v:
            result = validate_metadata(v)
            if not result.is_valid:
                raise ValueError(result.errors[0]['error'])
        return v

class ItemUpdateRequest(BaseModel):
    """Validation model for item update requests."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    type: Optional[ItemType] = None
    rarity: Optional[ItemRarity] = None
    status: Optional[ItemStatus] = None
    location_id: Optional[str] = None
    owner_id: Optional[str] = None
    quantity: Optional[int] = Field(None, ge=0)
    value: Optional[float] = Field(None, ge=0)
    weight: Optional[float] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None
    
    @validator('location_id')
    def validate_location_id(cls, v):
        """Validate location ID if provided."""
        if v is not None:
            result = validate_id(v)
            if not result.is_valid:
                raise ValueError(f"Invalid location ID: {result.errors[0]['error']}")
        return v
    
    @validator('owner_id')
    def validate_owner_id(cls, v):
        """Validate owner ID if provided."""
        if v is not None:
            result = validate_id(v)
            if not result.is_valid:
                raise ValueError(f"Invalid owner ID: {result.errors[0]['error']}")
        return v
    
    @validator('tags')
    def validate_tags_list(cls, v):
        """Validate tags if provided."""
        if v is not None:
            result = validate_tags(v)
            if not result.is_valid:
                raise ValueError(result.errors[0]['error'])
        return v
    
    @validator('metadata')
    def validate_metadata_dict(cls, v):
        """Validate metadata if provided."""
        if v is not None:
            result = validate_metadata(v)
            if not result.is_valid:
                raise ValueError(result.errors[0]['error'])
        return v

class ItemQueryParams(BaseModel, PaginationValidationMixin, SortValidationMixin, FilterValidationMixin):
    """Validation model for item query parameters."""
    
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    sort_by: str = Field('name')
    order: str = Field('asc')
    filters: Optional[Dict] = None
    type: Optional[ItemType] = None
    rarity: Optional[ItemRarity] = None
    status: Optional[ItemStatus] = None
    location_id: Optional[str] = None
    owner_id: Optional[str] = None
    min_value: Optional[float] = Field(None, ge=0)
    max_value: Optional[float] = Field(None, ge=0)
    min_weight: Optional[float] = Field(None, ge=0)
    max_weight: Optional[float] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    
    valid_sort_fields: ClassVar = ['name', 'type', 'rarity', 'status', 'value', 'weight', 'quantity', 'created_at', 'updated_at']
    valid_filters: ClassVar = {
        'type': ItemType,
        'rarity': ItemRarity,
        'status': ItemStatus,
        'location_id': str,
        'owner_id': str,
        'value': float,
        'weight': float,
        'quantity': int,
        'tags': list
    }
    
    @validator('min_value', 'max_value')
    def validate_value_range(cls, v):
        """Validate value range if both min and max are provided."""
        if v is not None:
            min_value = cls.model_fields['min_value'].default
            max_value = cls.model_fields['max_value'].default
            if min_value is not None and max_value is not None and min_value > max_value:
                raise ValueError("min_value cannot be greater than max_value")
        return v
    
    @validator('min_weight', 'max_weight')
    def validate_weight_range(cls, v):
        """Validate weight range if both min and max are provided."""
        if v is not None:
            min_weight = cls.model_fields['min_weight'].default
            max_weight = cls.model_fields['max_weight'].default
            if min_weight is not None and max_weight is not None and min_weight > max_weight:
                raise ValueError("min_weight cannot be greater than max_weight")
        return v
    
    @validator('tags')
    def validate_tags_list(cls, v):
        """Validate tags if provided."""
        if v is not None:
            result = validate_tags(v)
            if not result.is_valid:
                raise ValueError(result.errors[0]['error'])
        return v

class ItemTransferRequest(BaseModel):
    """Validation model for item transfer requests."""
    
    quantity: int = Field(..., ge=1)
    from_id: str = Field(..., min_length=1, max_length=100)
    to_id: str = Field(..., min_length=1, max_length=100)
    
    @validator('from_id', 'to_id')
    def validate_entity_ids(cls, v):
        """Validate entity IDs."""
        result = validate_id(v)
        if not result.is_valid:
            raise ValueError(result.errors[0]['error'])
        return v
    
    @validator('to_id')
    def validate_different_entities(cls, v, values):
        """Ensure from_id and to_id are different."""
        if 'from_id' in values and v == values['from_id']:
            raise ValueError("Source and destination must be different") 