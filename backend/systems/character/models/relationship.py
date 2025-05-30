"""
Relationship Model
-----------------
Canonical implementation of the relationship system as described in the Development Bible.
Represents all inter-entity relationships in the game.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from uuid import UUID
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum, auto

# Assuming Base is defined elsewhere
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class RelationshipType(str, Enum):
    """Enumeration of supported relationship types."""
    FACTION = "faction"
    QUEST = "quest"
    SPATIAL = "spatial"
    AUTH = "auth"
    CHARACTER = "character"
    ITEM = "item"
    POI = "poi"
    CUSTOM = "custom"

class Relationship(Base):
    """
    Canonical relationship model for all inter-entity relationships.
    
    Key features:
    - Represents all relationships between entities (characters, factions, quests, etc.)
    - Stores type-specific data in a JSON field
    - Supports querying by source, target, and type
    """
    __tablename__ = 'relationships'
    
    id = Column(Integer, primary_key=True)
    source_id = Column(String(36), nullable=False, index=True)  # UUID of source entity
    target_id = Column(String(36), nullable=False, index=True)  # UUID of target entity
    type = Column(String(30), nullable=False, index=True)       # RelationshipType
    data = Column(JSON, nullable=False, default=dict)           # Type-specific payload
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Index for efficient lookup by source+type and target+type
    __table_args__ = (
        Index('idx_source_type', 'source_id', 'type'),
        Index('idx_target_type', 'target_id', 'type'),
    )
    
    def __repr__(self):
        """String representation of relationship."""
        return f"<Relationship {self.source_id} -> {self.target_id} ({self.type})>"
    
    @classmethod
    def create_faction_relationship(cls, source_id: Union[str, UUID], 
                                  faction_id: Union[str, UUID], 
                                  reputation: int = 0, 
                                  standing: str = "neutral") -> 'Relationship':
        """Create a faction relationship with faction-specific data."""
        return cls(
            source_id=str(source_id),
            target_id=str(faction_id),
            type=RelationshipType.FACTION,
            data={
                "reputation": reputation,
                "standing": standing
            }
        )
    
    @classmethod
    def create_quest_relationship(cls, source_id: Union[str, UUID], 
                                quest_id: Union[str, UUID], 
                                status: str = "active", 
                                progress: float = 0.0) -> 'Relationship':
        """Create a quest relationship with quest-specific data."""
        return cls(
            source_id=str(source_id),
            target_id=str(quest_id),
            type=RelationshipType.QUEST,
            data={
                "status": status,
                "progress": progress
            }
        )
    
    @classmethod
    def create_spatial_relationship(cls, source_id: Union[str, UUID], 
                                  location_id: Union[str, UUID], 
                                  distance: float = 0.0) -> 'Relationship':
        """Create a spatial relationship with location-specific data."""
        return cls(
            source_id=str(source_id),
            target_id=str(location_id),
            type=RelationshipType.SPATIAL,
            data={
                "distance": distance,
                "location_id": str(location_id)
            }
        )
    
    @classmethod
    def create_auth_relationship(cls, source_id: Union[str, UUID], 
                               user_id: Union[str, UUID], 
                               permissions: List[str] = None, 
                               owner: bool = False) -> 'Relationship':
        """Create an authentication relationship with permission data."""
        return cls(
            source_id=str(source_id),
            target_id=str(user_id),
            type=RelationshipType.AUTH,
            data={
                "permissions": permissions or [],
                "owner": owner
            }
        )
    
    @classmethod
    def create_character_relationship(cls, source_id: Union[str, UUID], 
                                    target_id: Union[str, UUID], 
                                    relationship_level: int = 0,
                                    relationship_type: str = "neutral") -> 'Relationship':
        """Create a character-to-character relationship."""
        return cls(
            source_id=str(source_id),
            target_id=str(target_id),
            type=RelationshipType.CHARACTER,
            data={
                "level": relationship_level,
                "type": relationship_type
            }
        )
    
    def get_reputation(self) -> int:
        """Get reputation value for faction relationships."""
        if self.type != RelationshipType.FACTION:
            raise ValueError(f"Cannot get reputation from non-faction relationship of type {self.type}")
        return self.data.get("reputation", 0)
    
    def get_standing(self) -> str:
        """Get standing status for faction relationships."""
        if self.type != RelationshipType.FACTION:
            raise ValueError(f"Cannot get standing from non-faction relationship of type {self.type}")
        return self.data.get("standing", "neutral")
    
    def get_quest_status(self) -> str:
        """Get status for quest relationships."""
        if self.type != RelationshipType.QUEST:
            raise ValueError(f"Cannot get quest status from non-quest relationship of type {self.type}")
        return self.data.get("status", "inactive")
    
    def get_quest_progress(self) -> float:
        """Get progress for quest relationships."""
        if self.type != RelationshipType.QUEST:
            raise ValueError(f"Cannot get quest progress from non-quest relationship of type {self.type}")
        return self.data.get("progress", 0.0)
    
    def get_distance(self) -> float:
        """Get distance for spatial relationships."""
        if self.type != RelationshipType.SPATIAL:
            raise ValueError(f"Cannot get distance from non-spatial relationship of type {self.type}")
        return self.data.get("distance", 0.0)
    
    def get_permissions(self) -> List[str]:
        """Get permissions for auth relationships."""
        if self.type != RelationshipType.AUTH:
            raise ValueError(f"Cannot get permissions from non-auth relationship of type {self.type}")
        return self.data.get("permissions", [])
    
    def is_owner(self) -> bool:
        """Check if auth relationship has owner status."""
        if self.type != RelationshipType.AUTH:
            raise ValueError(f"Cannot check ownership from non-auth relationship of type {self.type}")
        return self.data.get("owner", False)
    
    def update_data(self, new_data: Dict[str, Any]) -> None:
        """Update relationship data with new values."""
        if not isinstance(new_data, dict):
            raise ValueError("new_data must be a dictionary")
        self.data.update(new_data)
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert relationship to dictionary for serialization."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type,
            "data": self.data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """Create relationship instance from dictionary."""
        relationship = cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            type=data["type"],
            data=data["data"]
        )
        if data.get("id"):
            relationship.id = data["id"]
        if data.get("created_at"):
            relationship.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            relationship.updated_at = datetime.fromisoformat(data["updated_at"])
        return relationship 