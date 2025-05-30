"""
Relationship Model
------------------
Defines the structure for relationships between entities (characters, factions, quests, etc.).
"""
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

# Import SQLAlchemy components when needed
# from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum as SQLAEnum
# from sqlalchemy.dialects.postgresql import UUID as PG_UUID
# from backend.core.database import Base

class RelationshipType(str, Enum):
    """Types of relationships between entities."""
    FACTION = "faction"         # Character to faction membership/reputation
    QUEST = "quest"             # Character to quest progress/status
    SPATIAL = "spatial"         # Entity to location relationships
    AUTH = "auth"               # User to character authentication/ownership
    INTERPERSONAL = "interpersonal"  # Character to character relationships
    # Add additional types as needed

class RelationshipBase(BaseModel):
    """Base model for relationship data."""
    source_id: UUID  # ID of the source entity (e.g., character)
    target_id: UUID  # ID of the target entity (e.g., faction, quest, other character)
    type: RelationshipType
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)  # Type-specific payload

class RelationshipCreate(RelationshipBase):
    """Model for creating a new relationship."""
    pass

class RelationshipUpdate(BaseModel):
    """Model for updating an existing relationship."""
    data: Optional[Dict[str, Any]] = None

class RelationshipInDB(RelationshipBase):
    """Model for a relationship as stored in the database."""
    id: UUID = Field(default_factory=uuid4)  # Primary key for the relationship itself
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True  # If using with SQLAlchemy ORM

# SQLAlchemy ORM model - commented out until needed
"""
class Relationship(Base):
    __tablename__ = "relationships"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    target_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    type = Column(SQLAEnum(RelationshipType, name="relationship_type_enum"), nullable=False, index=True)
    data = Column(JSON, nullable=True, default=lambda: {})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
""" 