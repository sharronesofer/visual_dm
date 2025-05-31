"""
Character system - Relationship models.

This module provides the canonical relationship models for the character system,
supporting all inter-entity relationships as specified in Development_Bible.md.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from backend.infrastructure.database import Base
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from uuid import UUID


class RelationshipType(Enum):
    """Enumeration of relationship types supported by the character system."""
    FACTION = "faction"
    QUEST = "quest"
    CHARACTER = "character"
    SPATIAL = "spatial"
    AUTH = "auth"
    CUSTOM = "custom"


class RelationshipStanding(Enum):
    """Enumeration of relationship standing levels."""
    HATED = "hated"
    HOSTILE = "hostile"
    DISLIKED = "disliked"
    UNFRIENDLY = "unfriendly"
    NEUTRAL = "neutral"
    LIKED = "liked"
    FRIENDLY = "friendly"
    HONORED = "honored"


class Relationship(Base):
    """
    Relationship model representing relationships between entities.
    
    This is the canonical implementation for all inter-entity relationships
    as specified in Development_Bible.md. Supports faction relationships,
    quest progress tracking, character-to-character relationships, spatial
    relationships, authentication relationships, and custom relationship types.
    """
    
    __tablename__ = 'relationships'
    __table_args__ = (
        Index('ix_relationship_source_type', 'source_id', 'type'),
        Index('ix_relationship_target_type', 'target_id', 'type'),
        Index('ix_relationship_source_target', 'source_id', 'target_id'),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(255), nullable=False, index=True)
    target_id = Column(String(255), nullable=False, index=True)
    type = Column(SQLEnum(RelationshipType), nullable=False, default=RelationshipType.CUSTOM)
    standing = Column(SQLEnum(RelationshipStanding), nullable=True, default=RelationshipStanding.NEUTRAL)
    data = Column(JSON, default=dict)  # Relationship-specific data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Relationship {self.source_id} -> {self.target_id} ({self.type.value})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert relationship to dictionary representation."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type.value if self.type else None,
            "standing": self.standing.value if self.standing else None,
            "data": self.data or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Relationship":
        """Create relationship from dictionary representation."""
        relationship = cls()
        relationship.source_id = data.get("source_id")
        relationship.target_id = data.get("target_id")
        
        # Handle type conversion
        if "type" in data:
            if isinstance(data["type"], str):
                relationship.type = RelationshipType(data["type"])
            else:
                relationship.type = data["type"]
        
        # Handle standing conversion
        if "standing" in data:
            if isinstance(data["standing"], str):
                relationship.standing = RelationshipStanding(data["standing"])
            else:
                relationship.standing = data["standing"]
        
        relationship.data = data.get("data", {})
        return relationship
    
    def update_data(self, new_data: Dict[str, Any]) -> None:
        """Update relationship data, merging with existing data."""
        if self.data is None:
            self.data = {}
        self.data.update(new_data)
        self.updated_at = datetime.utcnow()
    
    def get_data_value(self, key: str, default: Any = None) -> Any:
        """Get a specific value from relationship data."""
        if self.data is None:
            return default
        return self.data.get(key, default)
    
    def set_data_value(self, key: str, value: Any) -> None:
        """Set a specific value in relationship data."""
        if self.data is None:
            self.data = {}
        self.data[key] = value
        self.updated_at = datetime.utcnow()
