"""
Religion System Schemas

This module defines the Pydantic schemas for the religion system API endpoints.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ReligionSchema(BaseModel):
    """Base religion schema"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    description: Optional[str] = None
    religion_type: str
    tenets: List[str] = []
    holy_places: List[str] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True


class ReligionCreateSchema(BaseModel):
    """Schema for creating a new religion"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    religion_type: str = Field(...)
    tenets: List[str] = Field(default_factory=list)
    holy_places: List[str] = Field(default_factory=list)


class ReligionUpdateSchema(BaseModel):
    """Schema for updating a religion"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    religion_type: Optional[str] = None
    tenets: Optional[List[str]] = None
    holy_places: Optional[List[str]] = None


class ReligionMembershipSchema(BaseModel):
    """Religion membership schema"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    entity_id: UUID
    religion_id: UUID
    devotion_level: float = Field(ge=0.0, le=1.0)
    role: Optional[str] = None
    joined_at: datetime
    status: str = "active"


class ReligionMembershipCreateSchema(BaseModel):
    """Schema for creating religion membership"""
    
    entity_id: UUID
    religion_id: UUID
    devotion_level: float = Field(default=0.5, ge=0.0, le=1.0)
    role: Optional[str] = None
