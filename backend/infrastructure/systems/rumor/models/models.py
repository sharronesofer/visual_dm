"""
Rumor System Infrastructure Models

This module defines the infrastructure data models for the rumor system
according to the Development Bible standards and business logic requirements.

This module contains database entities and Pydantic models for the rumor system.
Includes performance optimizations with proper indexing.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Float, JSON, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.infrastructure.database import Base, UUIDMixin, TimestampMixin
from backend.infrastructure.shared.models import SharedBaseModel

Base = declarative_base()

class RumorBaseModel(SharedBaseModel):
    """Base model for rumor system with common fields"""
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)

class RumorEntity(Base):
    """
    Database entity for rumors with sophisticated variant/spread tracking
    
    Updated to match the business logic with variants and complex spread tracking.
    """
    __tablename__ = "rumors"

    # Primary key
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Core rumor data - updated to match business model
    original_content = Column(Text, nullable=False)  # Changed from 'content' to match business model
    originator_id = Column(String(100), nullable=False, index=True)
    
    # Categorization and severity
    categories = Column(JSON, nullable=False, default=list)
    severity = Column(String(20), nullable=False, default="minor")
    
    # Core metrics
    truth_value = Column(Float, nullable=False, default=0.5)
    
    # Metadata
    properties = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Timestamps - indexed for time-based queries
    created_at = Column(DateTime(timezone=True), nullable=False, 
                       default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True, 
                       onupdate=func.now())

    # Relationships to variants and spread records
    variants = relationship("RumorVariantEntity", back_populates="rumor", cascade="all, delete-orphan")
    spread_records = relationship("RumorSpreadEntity", back_populates="rumor", cascade="all, delete-orphan")

    # Composite indexes for common query patterns
    __table_args__ = (
        # Index for filtering by originator
        Index('idx_rumor_originator', 'originator_id'),
        
        # Index for time-based queries
        Index('idx_rumor_created', 'created_at'),
        
        # Index for severity analysis
        Index('idx_rumor_severity', 'severity'),
        
        # Index for active rumors by creation time (most common query)
        Index('idx_rumor_active_created', 'is_active', 'created_at'),
    )

    def __repr__(self):
        return f"<RumorEntity(id={self.id}, originator={self.originator_id}, severity={self.severity})>"

    @property
    def spread_count(self) -> int:
        """Get the number of entities that know this rumor"""
        return len(self.spread_records) if self.spread_records else 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary matching business logic"""
        return {
            "id": str(self.id),
            "original_content": self.original_content,
            "originator_id": self.originator_id,
            "categories": self.categories or [],
            "severity": self.severity,
            "truth_value": self.truth_value,
            "properties": self.properties or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "spread_count": self.spread_count,
            "variants": [v.to_dict() for v in (self.variants or [])],
            "spread_records": [s.to_dict() for s in (self.spread_records or [])]
        }

class RumorVariantEntity(Base):
    """
    Database entity for rumor variants (mutations)
    """
    __tablename__ = "rumor_variants"

    # Primary key
    id = Column(String(36), primary_key=True)  # UUID as string
    
    # Foreign key to parent rumor
    rumor_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey('rumors.id'), nullable=False, index=True)
    
    # Variant content and metadata
    content = Column(Text, nullable=False)
    parent_variant_id = Column(String(36), nullable=True, index=True)  # References another variant
    entity_id = Column(String(100), nullable=False, index=True)  # Who created this variant
    mutation_metadata = Column(JSON, nullable=False, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    # Relationships
    rumor = relationship("RumorEntity", back_populates="variants")

    # Indexes
    __table_args__ = (
        Index('idx_variant_rumor_created', 'rumor_id', 'created_at'),
        Index('idx_variant_entity', 'entity_id'),
        Index('idx_variant_parent', 'parent_variant_id'),
    )

    def __repr__(self):
        return f"<RumorVariantEntity(id={self.id}, rumor_id={self.rumor_id}, entity_id={self.entity_id})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": self.id,
            "rumor_id": str(self.rumor_id),
            "content": self.content,
            "parent_variant_id": self.parent_variant_id,
            "entity_id": self.entity_id,
            "mutation_metadata": self.mutation_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class RumorSpreadEntity(Base):
    """
    Database entity for tracking rumor spread to entities
    """
    __tablename__ = "rumor_spread"

    # Primary key
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Foreign key to parent rumor
    rumor_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey('rumors.id'), nullable=False, index=True)
    
    # Spread tracking data
    entity_id = Column(String(100), nullable=False, index=True)
    variant_id = Column(String(36), nullable=False, index=True)  # Which variant they heard
    heard_from_entity_id = Column(String(100), nullable=True, index=True)  # Source of the rumor
    believability = Column(Float, nullable=False, default=0.5)
    
    # Timestamps
    heard_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

    # Relationships
    rumor = relationship("RumorEntity", back_populates="spread_records")

    # Unique constraint to prevent duplicate entity entries for same rumor
    __table_args__ = (
        Index('idx_spread_rumor_entity', 'rumor_id', 'entity_id'),
        Index('idx_spread_entity', 'entity_id'),
        Index('idx_spread_variant', 'variant_id'),
        Index('idx_spread_source', 'heard_from_entity_id'),
        Index('idx_spread_believability', 'believability'),
    )

    def __repr__(self):
        return f"<RumorSpreadEntity(rumor_id={self.rumor_id}, entity_id={self.entity_id}, believability={self.believability})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": str(self.id),
            "rumor_id": str(self.rumor_id),
            "entity_id": self.entity_id,
            "variant_id": self.variant_id,
            "heard_from_entity_id": self.heard_from_entity_id,
            "believability": self.believability,
            "heard_at": self.heard_at.isoformat() if self.heard_at else None
        }

# Request/Response Models - Updated to match new structure
class CreateRumorRequest(BaseModel):
    """Request model for creating a rumor"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    content: str = Field(..., min_length=10, max_length=500, description="Rumor content")
    originator_id: str = Field(..., min_length=1, max_length=100, description="ID of the originator")
    categories: Optional[List[str]] = Field(default_factory=list, description="Rumor categories")
    severity: str = Field(default="minor", description="Severity level")
    truth_value: float = Field(default=0.5, ge=0.0, le=1.0, description="Truth value")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional properties")

class UpdateRumorRequest(BaseModel):
    """Request model for updating a rumor"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    original_content: Optional[str] = Field(None, min_length=10, max_length=500)
    categories: Optional[List[str]] = None
    severity: Optional[str] = None
    truth_value: Optional[float] = Field(None, ge=0.0, le=1.0)
    properties: Optional[Dict[str, Any]] = None

class RumorVariantResponse(BaseModel):
    """Response model for rumor variant data"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    content: str
    parent_variant_id: Optional[str] = None
    entity_id: str
    mutation_metadata: Dict[str, Any]
    created_at: datetime

class RumorSpreadResponse(BaseModel):
    """Response model for rumor spread data"""
    model_config = ConfigDict(from_attributes=True)
    
    entity_id: str
    variant_id: str
    heard_from_entity_id: Optional[str] = None
    believability: float
    heard_at: datetime

class RumorResponse(BaseModel):
    """Response model for rumor data - Updated for new structure"""
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    id: str
    original_content: str
    originator_id: str
    categories: List[str]
    severity: str
    truth_value: float
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None
    spread_count: int
    variants: List[RumorVariantResponse] = Field(default_factory=list)
    spread_records: List[RumorSpreadResponse] = Field(default_factory=list)

    @classmethod
    def from_orm(cls, entity: RumorEntity) -> "RumorResponse":
        """Create response from database entity"""
        return cls(
            id=str(entity.id),
            original_content=entity.original_content,
            originator_id=entity.originator_id,
            categories=entity.categories or [],
            severity=entity.severity,
            truth_value=entity.truth_value,
            properties=entity.properties or {},
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            spread_count=entity.spread_count,
            variants=[
                RumorVariantResponse(
                    id=v.id,
                    content=v.content,
                    parent_variant_id=v.parent_variant_id,
                    entity_id=v.entity_id,
                    mutation_metadata=v.mutation_metadata or {},
                    created_at=v.created_at
                ) for v in (entity.variants or [])
            ],
            spread_records=[
                RumorSpreadResponse(
                    entity_id=s.entity_id,
                    variant_id=s.variant_id,
                    heard_from_entity_id=s.heard_from_entity_id,
                    believability=s.believability,
                    heard_at=s.heard_at
                ) for s in (entity.spread_records or [])
            ]
        )

class RumorListResponse(BaseModel):
    """Response model for paginated rumor lists"""
    items: List[RumorResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool

# Spread-specific request models
class SpreadRumorRequest(BaseModel):
    """Request model for spreading a rumor"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    from_entity_id: str = Field(..., min_length=1, description="Entity spreading the rumor")
    to_entity_id: str = Field(..., min_length=1, description="Entity receiving the rumor")
    variant_id: Optional[str] = Field(None, description="Specific variant to spread")
    believability_modifier: float = Field(default=0.0, ge=-1.0, le=1.0, description="Adjustment to believability")
    allow_mutation: bool = Field(default=True, description="Whether to allow mutation during spread")
    social_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Social context factors")
    receiver_personality: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Receiver personality traits")

class MutateRumorRequest(BaseModel):
    """Request model for creating a rumor mutation"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    entity_id: str = Field(..., min_length=1, description="Entity creating the mutation")
    parent_variant_id: Optional[str] = Field(None, description="Parent variant being mutated")
    new_content: Optional[str] = Field(None, min_length=10, max_length=500, description="Specific mutated content")
    mutation_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Mutation metadata")
