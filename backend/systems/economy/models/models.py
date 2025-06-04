"""
Economy System Business Models

This module defines the business data models for the economy system.
SQLAlchemy models have been moved to backend/infrastructure/database/economy/models.py
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict

from backend.infrastructure.shared.models import SharedBaseModel

class EconomyBaseModel(SharedBaseModel):
    """Base model for economy system with common fields"""
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)

class EconomyModel(EconomyBaseModel):
    """Primary model for economy system"""
    
    name: str = Field(..., description="Name of the economy")
    description: Optional[str] = Field(None, description="Description of the economy")
    status: str = Field(default="active", description="Status of the economy")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

# Request/Response Models
class CreateEconomyRequest(BaseModel):
    """Request model for creating economy"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

class UpdateEconomyRequest(BaseModel):
    """Request model for updating economy"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    properties: Optional[Dict[str, Any]] = None

class EconomyResponse(BaseModel):
    """Response model for economy"""
    
    id: UUID
    name: str
    description: Optional[str]
    status: str
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class EconomyListResponse(BaseModel):
    """Response model for economy lists"""
    
    items: List[EconomyResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool
