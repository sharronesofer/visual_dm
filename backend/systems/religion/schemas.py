"""
API schemas for the religion system.

These schemas are used for API input/output validation and serialization.
They define the contract for religion-related API operations.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

from .models import ReligionType


class ReligionBaseSchema(BaseModel):
    """Base schema for religion data."""
    name: str
    description: str
    type: ReligionType
    tags: List[str] = Field(default_factory=list)
    tenets: List[str] = Field(default_factory=list)
    holy_places: List[str] = Field(default_factory=list)
    sacred_texts: List[str] = Field(default_factory=list)
    region_ids: List[str] = Field(default_factory=list)
    faction_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ReligionCreateSchema(ReligionBaseSchema):
    """Schema for creating a new religion."""
    pass


class ReligionUpdateSchema(BaseModel):
    """Schema for updating an existing religion."""
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[ReligionType] = None
    tags: Optional[List[str]] = None
    tenets: Optional[List[str]] = None
    holy_places: Optional[List[str]] = None
    sacred_texts: Optional[List[str]] = None
    region_ids: Optional[List[str]] = None
    faction_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ReligionSchema(ReligionBaseSchema):
    """Schema for religion responses."""
    id: str
    created_at: datetime
    updated_at: datetime
    type_string: str = ""
    
    class Config:
        orm_mode = True


class ReligionMembershipBaseSchema(BaseModel):
    """Base schema for religion membership data."""
    entity_id: str
    religion_id: str
    devotion_level: int = 0
    status: str = "member"
    role: Optional[str] = None
    is_public: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ReligionMembershipCreateSchema(ReligionMembershipBaseSchema):
    """Schema for creating a new religion membership."""
    pass


class ReligionMembershipUpdateSchema(BaseModel):
    """Schema for updating an existing religion membership."""
    devotion_level: Optional[int] = None
    status: Optional[str] = None
    role: Optional[str] = None
    is_public: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class ReligionMembershipSchema(ReligionMembershipBaseSchema):
    """Schema for religion membership responses."""
    id: str
    joined_date: datetime
    religion_name: Optional[str] = None
    
    class Config:
        orm_mode = True 