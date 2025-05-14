"""Validation models for NPC-related API requests."""

from typing import Dict, List, Optional
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

class NPCAlignment(str, Enum):
    """Valid NPC alignment values."""
    LAWFUL_GOOD = "lawful_good"
    NEUTRAL_GOOD = "neutral_good"
    CHAOTIC_GOOD = "chaotic_good"
    LAWFUL_NEUTRAL = "lawful_neutral"
    TRUE_NEUTRAL = "true_neutral"
    CHAOTIC_NEUTRAL = "chaotic_neutral"
    LAWFUL_EVIL = "lawful_evil"
    NEUTRAL_EVIL = "neutral_evil"
    CHAOTIC_EVIL = "chaotic_evil"

class NPCStatus(str, Enum):
    """Valid NPC status values."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEAD = "dead"
    MISSING = "missing"

class NPCCreateRequest(BaseModel):
    """Validation model for NPC creation requests."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    location_id: str = Field(..., min_length=1, max_length=100)
    faction_ids: Optional[List[str]] = Field(default=None)
    alignment: NPCAlignment
    status: NPCStatus = Field(default=NPCStatus.ACTIVE)
    level: Optional[int] = Field(default=1, ge=1, le=20)
    tags: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict] = Field(default_factory=dict)
    
    @validator('faction_ids')
    def validate_faction_ids(cls, v):
        """Validate faction IDs if provided."""
        if v is not None:
            for faction_id in v:
                result = validate_id(faction_id)
                if not result.is_valid:
                    raise ValueError(f"Invalid faction ID: {result.errors[0]['error']}")
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

class NPCUpdateRequest(BaseModel):
    """Validation model for NPC update requests."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    location_id: Optional[str] = Field(None, min_length=1, max_length=100)
    faction_ids: Optional[List[str]] = None
    alignment: Optional[NPCAlignment] = None
    status: Optional[NPCStatus] = None
    level: Optional[int] = Field(None, ge=1, le=20)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None
    
    @validator('faction_ids')
    def validate_faction_ids(cls, v):
        """Validate faction IDs if provided."""
        if v is not None:
            for faction_id in v:
                result = validate_id(faction_id)
                if not result.is_valid:
                    raise ValueError(f"Invalid faction ID: {result.errors[0]['error']}")
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

class NPCQueryParams(BaseModel, PaginationValidationMixin, SortValidationMixin, FilterValidationMixin):
    """Validation model for NPC query parameters."""
    
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    sort_by: str = Field('name')
    order: str = Field('asc')
    filters: Optional[Dict] = None
    location_id: Optional[str] = None
    faction_id: Optional[str] = None
    alignment: Optional[NPCAlignment] = None
    status: Optional[NPCStatus] = None
    min_level: Optional[int] = Field(None, ge=1, le=20)
    max_level: Optional[int] = Field(None, ge=1, le=20)
    tags: Optional[List[str]] = None
    
    valid_sort_fields = ['name', 'alignment', 'status', 'level', 'created_at', 'updated_at']
    valid_filters = {
        'location_id': str,
        'faction_id': str,
        'alignment': NPCAlignment,
        'status': NPCStatus,
        'level': int,
        'tags': list
    }
    
    @validator('min_level', 'max_level')
    def validate_level_range(cls, v, values, field):
        """Validate level range if both min and max are provided."""
        if v is not None:
            min_level = values.get('min_level')
            max_level = values.get('max_level')
            if min_level is not None and max_level is not None and min_level > max_level:
                raise ValueError("min_level cannot be greater than max_level")
        return v
    
    @validator('tags')
    def validate_tags_list(cls, v):
        """Validate tags if provided."""
        if v is not None:
            result = validate_tags(v)
            if not result.is_valid:
                raise ValueError(result.errors[0]['error'])
        return v

class NPCInventoryUpdateRequest(BaseModel):
    """Validation model for NPC inventory update requests."""
    
    item_id: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., ge=0)
    operation: str = Field(..., regex='^(add|remove)$')
    
    @validator('item_id')
    def validate_item_id(cls, v):
        """Validate item ID."""
        result = validate_id(v)
        if not result.is_valid:
            raise ValueError(result.errors[0]['error'])
        return v 