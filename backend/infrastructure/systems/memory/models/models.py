"""
Memory System Models

This module defines the data models for the memory system according to
the Development Bible standards and business logic requirements.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB

from sqlalchemy.orm import relationship
from backend.infrastructure.database import Base, UUIDMixin, TimestampMixin
from backend.infrastructure.shared.models import SharedBaseModel

class MemoryBaseModel(SharedBaseModel):
    """Base model for memory system with common fields"""
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)

class MemoryModel(MemoryBaseModel):
    """Primary model for memory system aligned with business logic"""
    
    npc_id: str = Field(..., description="Entity ID that owns this memory")
    content: str = Field(..., description="The actual memory content")
    memory_type: str = Field(default="regular", description="Type: core or regular")
    summary: Optional[str] = Field(None, description="Short summary of the memory")
    categories: List[str] = Field(default_factory=list, description="Memory categories")
    importance: float = Field(default=0.5, description="Importance score (0.0-1.0)")
    relevance: Optional[float] = Field(None, description="Current relevance score")
    is_core: bool = Field(default=False, description="Whether this is a core memory")
    context_ids: Optional[List[str]] = Field(default_factory=list, description="Related memory IDs")
    access_count: int = Field(default=0, description="Number of times accessed")
    last_accessed: Optional[datetime] = Field(None, description="Last access timestamp")

class MemoryEntity(Base):
    """SQLAlchemy entity for memory system aligned with business logic"""
    
    __tablename__ = f"memory_entities"
    __table_args__ = {'extend_existing': True}
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    npc_id = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    memory_type = Column(String(50), default="regular")
    summary = Column(Text)
    categories = Column(JSONB, default=list)
    importance = Column(Float, default=0.5)
    relevance = Column(Float, nullable=True)
    is_core = Column(Boolean, default=False)
    context_ids = Column(JSONB, default=list)
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    metadata = Column(JSONB, default=dict)

    def __repr__(self):
        return f"<MemoryEntity(id={self.id}, npc_id={self.npc_id}, content={self.content[:50]}...)>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": str(self.id),
            "npc_id": self.npc_id,
            "content": self.content,
            "memory_type": self.memory_type,
            "summary": self.summary,
            "categories": self.categories or [],
            "importance": self.importance,
            "relevance": self.relevance,
            "is_core": self.is_core,
            "context_ids": self.context_ids or [],
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "metadata": self.metadata or {}
        }

# Request/Response Models
class CreateMemoryRequest(BaseModel):
    """Request model for creating memory"""
    
    npc_id: str = Field(..., description="Entity ID that will own this memory")
    content: str = Field(..., min_length=1, description="Memory content")
    memory_type: str = Field(default="regular", description="Type: core or regular")
    summary: Optional[str] = Field(None, description="Short summary")
    categories: Optional[List[str]] = Field(default_factory=list, description="Memory categories")
    importance: Optional[float] = Field(default=0.5, ge=0.0, le=1.0, description="Importance score")
    is_core: bool = Field(default=False, description="Whether this is a core memory")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class UpdateMemoryRequest(BaseModel):
    """Request model for updating memory"""
    
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = Field(None)
    memory_type: Optional[str] = Field(None)
    categories: Optional[List[str]] = None
    importance: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_core: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class MemoryResponse(BaseModel):
    """Response model for memory"""
    
    id: UUID
    npc_id: str
    content: str
    memory_type: str
    summary: Optional[str]
    categories: List[str]
    importance: float
    relevance: Optional[float]
    is_core: bool
    context_ids: List[str]
    access_count: int
    last_accessed: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    metadata: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)

class MemoryListResponse(BaseModel):
    """Response model for memory lists"""
    
    items: List[MemoryResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool
