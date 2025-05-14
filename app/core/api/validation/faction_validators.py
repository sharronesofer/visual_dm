"""Validation models for Faction-related API requests."""

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

class FactionType(str, Enum):
    """Valid faction type values."""
    GUILD = "guild"
    KINGDOM = "kingdom"
    CLAN = "clan"
    CULT = "cult"
    ORGANIZATION = "organization"
    TRIBE = "tribe"
    ALLIANCE = "alliance"
    EMPIRE = "empire"
    MERCHANT = "merchant"
    CRIMINAL = "criminal"
    RELIGIOUS = "religious"
    MILITARY = "military"
    OTHER = "other"

class FactionStatus(str, Enum):
    """Valid faction status values."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    HIDDEN = "hidden"
    DESTROYED = "destroyed"
    DISBANDED = "disbanded"

class FactionAlignment(str, Enum):
    """Valid faction alignment values."""
    LAWFUL_GOOD = "lawful_good"
    NEUTRAL_GOOD = "neutral_good"
    CHAOTIC_GOOD = "chaotic_good"
    LAWFUL_NEUTRAL = "lawful_neutral"
    TRUE_NEUTRAL = "true_neutral"
    CHAOTIC_NEUTRAL = "chaotic_neutral"
    LAWFUL_EVIL = "lawful_evil"
    NEUTRAL_EVIL = "neutral_evil"
    CHAOTIC_EVIL = "chaotic_evil"

class RelationshipType(str, Enum):
    """Valid faction relationship type values."""
    ALLIED = "allied"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    UNFRIENDLY = "unfriendly"
    HOSTILE = "hostile"
    AT_WAR = "at_war"

class FactionRelationship(BaseModel):
    """Model for faction relationships."""
    
    target_faction_id: str = Field(..., min_length=1, max_length=100)
    relationship_type: RelationshipType
    influence_level: int = Field(..., ge=-100, le=100)
    metadata: Optional[Dict] = Field(default_factory=dict)
    
    @validator('target_faction_id')
    def validate_target_faction_id(cls, v):
        """Validate target faction ID."""
        result = validate_id(v)
        if not result.is_valid:
            raise ValueError(f"Invalid target faction ID: {result.errors[0]['error']}")
        return v
    
    @validator('metadata')
    def validate_metadata_dict(cls, v):
        """Validate metadata if provided."""
        if v:
            result = validate_metadata(v)
            if not result.is_valid:
                raise ValueError(result.errors[0]['error'])
        return v

class FactionCreateRequest(BaseModel):
    """Validation model for faction creation requests."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    type: FactionType
    status: FactionStatus = Field(default=FactionStatus.ACTIVE)
    alignment: FactionAlignment
    leader_id: Optional[str] = Field(None, min_length=1, max_length=100)
    headquarters_id: Optional[str] = Field(None, min_length=1, max_length=100)
    parent_faction_id: Optional[str] = Field(None, min_length=1, max_length=100)
    relationships: Optional[List[FactionRelationship]] = Field(default_factory=list)
    influence_radius: Optional[int] = Field(None, ge=0)  # in game world units
    member_count: Optional[int] = Field(None, ge=0)
    wealth_rating: Optional[int] = Field(None, ge=0, le=100)
    military_strength: Optional[int] = Field(None, ge=0, le=100)
    tags: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict] = Field(default_factory=dict)
    
    @validator('leader_id', 'headquarters_id', 'parent_faction_id')
    def validate_entity_ids(cls, v, field):
        """Validate entity IDs if provided."""
        if v is not None:
            result = validate_id(v)
            if not result.is_valid:
                raise ValueError(f"Invalid {field.name}: {result.errors[0]['error']}")
        return v
    
    @validator('relationships')
    def validate_relationships(cls, v):
        """Validate relationships if provided."""
        if v:
            seen_factions = set()
            for rel in v:
                if rel.target_faction_id in seen_factions:
                    raise ValueError(f"Duplicate relationship with faction {rel.target_faction_id}")
                seen_factions.add(rel.target_faction_id)
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

class FactionUpdateRequest(BaseModel):
    """Validation model for faction update requests."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    type: Optional[FactionType] = None
    status: Optional[FactionStatus] = None
    alignment: Optional[FactionAlignment] = None
    leader_id: Optional[str] = None
    headquarters_id: Optional[str] = None
    parent_faction_id: Optional[str] = None
    relationships: Optional[List[FactionRelationship]] = None
    influence_radius: Optional[int] = Field(None, ge=0)
    member_count: Optional[int] = Field(None, ge=0)
    wealth_rating: Optional[int] = Field(None, ge=0, le=100)
    military_strength: Optional[int] = Field(None, ge=0, le=100)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None
    
    @validator('leader_id', 'headquarters_id', 'parent_faction_id')
    def validate_entity_ids(cls, v, field):
        """Validate entity IDs if provided."""
        if v is not None:
            result = validate_id(v)
            if not result.is_valid:
                raise ValueError(f"Invalid {field.name}: {result.errors[0]['error']}")
        return v
    
    @validator('relationships')
    def validate_relationships(cls, v):
        """Validate relationships if provided."""
        if v is not None:
            seen_factions = set()
            for rel in v:
                if rel.target_faction_id in seen_factions:
                    raise ValueError(f"Duplicate relationship with faction {rel.target_faction_id}")
                seen_factions.add(rel.target_faction_id)
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

class FactionQueryParams(BaseModel, PaginationValidationMixin, SortValidationMixin, FilterValidationMixin):
    """Validation model for faction query parameters."""
    
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    sort_by: str = Field('name')
    order: str = Field('asc')
    filters: Optional[Dict] = None
    type: Optional[FactionType] = None
    status: Optional[FactionStatus] = None
    alignment: Optional[FactionAlignment] = None
    leader_id: Optional[str] = None
    headquarters_id: Optional[str] = None
    parent_faction_id: Optional[str] = None
    min_influence_radius: Optional[int] = Field(None, ge=0)
    min_member_count: Optional[int] = Field(None, ge=0)
    min_wealth_rating: Optional[int] = Field(None, ge=0, le=100)
    min_military_strength: Optional[int] = Field(None, ge=0, le=100)
    tags: Optional[List[str]] = None
    
    valid_sort_fields = ['name', 'type', 'status', 'alignment', 'influence_radius', 'member_count', 'wealth_rating', 'military_strength', 'created_at', 'updated_at']
    valid_filters = {
        'type': FactionType,
        'status': FactionStatus,
        'alignment': FactionAlignment,
        'leader_id': str,
        'headquarters_id': str,
        'parent_faction_id': str,
        'min_influence_radius': int,
        'min_member_count': int,
        'min_wealth_rating': int,
        'min_military_strength': int,
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

class FactionRelationshipUpdateRequest(BaseModel):
    """Validation model for faction relationship update requests."""
    
    target_faction_id: str = Field(..., min_length=1, max_length=100)
    relationship_type: RelationshipType
    influence_level: int = Field(..., ge=-100, le=100)
    bidirectional: bool = Field(default=True)
    metadata: Optional[Dict] = None
    
    @validator('target_faction_id')
    def validate_target_faction_id(cls, v):
        """Validate target faction ID."""
        result = validate_id(v)
        if not result.is_valid:
            raise ValueError(f"Invalid target faction ID: {result.errors[0]['error']}")
        return v
    
    @validator('metadata')
    def validate_metadata_dict(cls, v):
        """Validate metadata if provided."""
        if v is not None:
            result = validate_metadata(v)
            if not result.is_valid:
                raise ValueError(result.errors[0]['error'])
        return v 