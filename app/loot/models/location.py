"""
Location and container models for the loot system.
"""

from datetime import datetime
from typing import Dict, Any
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import relationship
try:
    from app.loot.models.base import LootBase
except ImportError:
    from .base import LootBase
import enum

class LocationType(str, enum.Enum):
    """Enumeration of location types."""
    DUNGEON = "dungeon"
    CITY = "city"
    WILDERNESS = "wilderness"
    CAVE = "cave"
    RUINS = "ruins"
    SETTLEMENT = "settlement"
    SPECIAL = "special"

class ContainerType(str, enum.Enum):
    """Enumeration of container types."""
    CHEST = "chest"
    CORPSE = "corpse"
    CRATE = "crate"
    BARREL = "barrel"
    CACHE = "cache"
    LOCKBOX = "lockbox"
    SAFE = "safe"

class Location(LootBase):
    """Model for locations that can contain loot."""
    __tablename__ = 'loot_locations'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    location_type = Column(Enum(LocationType), nullable=False)
    description = Column(Text)
    danger_level = Column(Integer, default=1)  # 1-20 scale
    base_loot_multiplier = Column(Float, default=1.0)
    thematic_tags = Column(JSON, default=list)  # For themed loot generation
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    containers = relationship('Container', back_populates='location')
    shops = relationship('Shop', back_populates='location')

    def to_dict(self) -> Dict[str, Any]:
        """Convert location to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'location_type': self.location_type.value,
            'description': self.description,
            'danger_level': self.danger_level,
            'base_loot_multiplier': self.base_loot_multiplier,
            'thematic_tags': self.thematic_tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Container(LootBase):
    """Model for loot containers."""
    __tablename__ = 'loot_containers'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    container_type = Column(Enum(ContainerType), nullable=False)
    location_id = Column(Integer, ForeignKey('loot_locations.id'), nullable=False)
    name = Column(String(100))  # Optional custom name
    description = Column(Text)
    danger_level = Column(Integer)  # Inherited from location if not specified
    is_locked = Column(Boolean, default=False)
    is_trapped = Column(Boolean, default=False)
    is_opened = Column(Boolean, default=False)
    respawn_time = Column(Integer)  # Time in minutes until container refreshes, null for no respawn
    created_at = Column(DateTime, default=datetime.utcnow)
    opened_at = Column(DateTime)
    expires_at = Column(DateTime)  # When container and contents should be removed
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    location = relationship('Location', back_populates='containers')
    contents = relationship('ContainerContent', back_populates='container', cascade='all, delete-orphan')

    def to_dict(self) -> Dict[str, Any]:
        """Convert container to dictionary representation."""
        return {
            'id': self.id,
            'container_type': self.container_type.value,
            'location_id': self.location_id,
            'name': self.name,
            'description': self.description,
            'danger_level': self.danger_level,
            'is_locked': self.is_locked,
            'is_trapped': self.is_trapped,
            'is_opened': self.is_opened,
            'respawn_time': self.respawn_time,
            'created_at': self.created_at.isoformat(),
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'updated_at': self.updated_at.isoformat()
        }

class ContainerContent(LootBase):
    """Model for items in containers."""
    __tablename__ = 'loot_container_contents'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    container_id = Column(Integer, ForeignKey('loot_containers.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('loot_items.id'), nullable=False)
    quantity = Column(Integer, default=1)
    is_claimed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    claimed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    container = relationship('Container', back_populates='contents')
    item = relationship('BaseItem', back_populates='container_contents')

    def to_dict(self) -> Dict[str, Any]:
        """Convert container content to dictionary representation."""
        return {
            'id': self.id,
            'container_id': self.container_id,
            'item_id': self.item_id,
            'quantity': self.quantity,
            'is_claimed': self.is_claimed,
            'created_at': self.created_at.isoformat(),
            'claimed_at': self.claimed_at.isoformat() if self.claimed_at else None,
            'updated_at': self.updated_at.isoformat()
        } 