"""Validation models for Location-related API requests."""

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

class LocationType(str, Enum):
    """Valid location type values."""
    CITY = "city"
    TOWN = "town"
    VILLAGE = "village"
    DUNGEON = "dungeon"
    WILDERNESS = "wilderness"
    BUILDING = "building"
    SHOP = "shop"
    TAVERN = "tavern"
    TEMPLE = "temple"
    CASTLE = "castle"
    RUINS = "ruins"
    OTHER = "other"

class LocationStatus(str, Enum):
    """Valid location status values."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DESTROYED = "destroyed"
    HIDDEN = "hidden"
    DISCOVERED = "discovered"

class LocationCreateRequest(BaseModel):
    """Validation model for location creation requests."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    type: LocationType
    status: LocationStatus = Field(default=LocationStatus.ACTIVE)
    parent_id: Optional[str] = Field(None, min_length=1, max_length=100)
    connected_location_ids: Optional[List[str]] = Field(default_factory=list)
    faction_ids: Optional[List[str]] = Field(default_factory=list)
    coordinates: Optional[Dict[str, float]] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict] = Field(default_factory=dict)
    
    @validator('parent_id')
    def validate_parent_id(cls, v):
        """Validate parent location ID if provided."""
        if v is not None:
            result = validate_id(v)
            if not result.is_valid:
                raise ValueError(f"Invalid parent location ID: {result.errors[0]['error']}")
        return v
    
    @validator('connected_location_ids')
    def validate_connected_location_ids(cls, v):
        """Validate connected location IDs if provided."""
        if v:
            for location_id in v:
                result = validate_id(location_id)
                if not result.is_valid:
                    raise ValueError(f"Invalid connected location ID: {result.errors[0]['error']}")
        return v
    
    @validator('faction_ids')
    def validate_faction_ids(cls, v):
        """Validate faction IDs if provided."""
        if v:
            for faction_id in v:
                result = validate_id(faction_id)
                if not result.is_valid:
                    raise ValueError(f"Invalid faction ID: {result.errors[0]['error']}")
        return v
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        """Validate coordinates if provided."""
        if v is not None:
            required_keys = {'x', 'y'}
            if not all(key in v for key in required_keys):
                raise ValueError("Coordinates must include 'x' and 'y' values")
            
            for key, value in v.items():
                if not isinstance(value, (int, float)):
                    raise ValueError(f"Coordinate {key} must be a number")
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

class LocationUpdateRequest(BaseModel):
    """Validation model for location update requests."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    type: Optional[LocationType] = None
    status: Optional[LocationStatus] = None
    parent_id: Optional[str] = None
    connected_location_ids: Optional[List[str]] = None
    faction_ids: Optional[List[str]] = None
    coordinates: Optional[Dict[str, float]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None
    
    @validator('parent_id')
    def validate_parent_id(cls, v):
        """Validate parent location ID if provided."""
        if v is not None:
            result = validate_id(v)
            if not result.is_valid:
                raise ValueError(f"Invalid parent location ID: {result.errors[0]['error']}")
        return v
    
    @validator('connected_location_ids')
    def validate_connected_location_ids(cls, v):
        """Validate connected location IDs if provided."""
        if v is not None:
            for location_id in v:
                result = validate_id(location_id)
                if not result.is_valid:
                    raise ValueError(f"Invalid connected location ID: {result.errors[0]['error']}")
        return v
    
    @validator('faction_ids')
    def validate_faction_ids(cls, v):
        """Validate faction IDs if provided."""
        if v is not None:
            for faction_id in v:
                result = validate_id(faction_id)
                if not result.is_valid:
                    raise ValueError(f"Invalid faction ID: {result.errors[0]['error']}")
        return v
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        """Validate coordinates if provided."""
        if v is not None:
            required_keys = {'x', 'y'}
            if not all(key in v for key in required_keys):
                raise ValueError("Coordinates must include 'x' and 'y' values")
            
            for key, value in v.items():
                if not isinstance(value, (int, float)):
                    raise ValueError(f"Coordinate {key} must be a number")
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

class LocationQueryParams(BaseModel, PaginationValidationMixin, SortValidationMixin, FilterValidationMixin):
    """Validation model for location query parameters."""
    
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    sort_by: str = Field('name')
    order: str = Field('asc')
    filters: Optional[Dict] = None
    type: Optional[LocationType] = None
    status: Optional[LocationStatus] = None
    parent_id: Optional[str] = None
    faction_id: Optional[str] = None
    has_coordinates: Optional[bool] = None
    tags: Optional[List[str]] = None
    
    valid_sort_fields: ClassVar = ['name', 'type', 'status', 'created_at', 'updated_at']
    valid_filters: ClassVar = {
        'type': LocationType,
        'status': LocationStatus,
        'parent_id': str,
        'faction_id': str,
        'has_coordinates': bool,
        'tags': list
    }
    
    @validator('tags')
    def validate_tags_list(cls, v):
        """Validate tags if provided."""
        if v is not None:
            result = validate_tags(v)
            if not result.is_valid:
                raise ValueError(result.errors[0]['error'])
        return v

class LocationConnectionRequest(BaseModel):
    """Validation model for location connection requests."""
    
    target_location_id: str = Field(..., min_length=1, max_length=100)
    connection_type: str = Field(..., pattern='^(add|remove)$')
    bidirectional: bool = Field(default=True)
    
    @validator('target_location_id')
    def validate_target_location_id(cls, v):
        """Validate target location ID."""
        result = validate_id(v)
        if not result.is_valid:
            raise ValueError(result.errors[0]['error'])
        return v 