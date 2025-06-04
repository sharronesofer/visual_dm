"""
Diplomacy System Models

This module defines the Pydantic data models for the diplomacy system according to
the Development Bible standards. SQLAlchemy database models are in db_models/
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict

from backend.infrastructure.shared.models import SharedBaseModel

class DiplomacyBaseModel(SharedBaseModel):
    """Base model for diplomacy system with common fields"""
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)

class DiplomacyModel(DiplomacyBaseModel):
    """Primary model for diplomacy system"""
    
    name: str = Field(..., description="Name of the diplomacy")
    description: Optional[str] = Field(None, description="Description of the diplomacy")
    status: str = Field(default="active", description="Status of the diplomacy")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

# Request/Response Models
class CreateDiplomacyRequest(BaseModel):
    """Request model for creating diplomacy"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

class UpdateDiplomacyRequest(BaseModel):
    """Request model for updating diplomacy"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    properties: Optional[Dict[str, Any]] = None

class DiplomacyResponse(BaseModel):
    """Response model for diplomacy"""
    
    id: UUID
    name: str
    description: Optional[str]
    status: str
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class DiplomacyListResponse(BaseModel):
    """Response model for diplomacy lists"""
    
    items: List[DiplomacyResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool
