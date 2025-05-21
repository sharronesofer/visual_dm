"""
Resource model for economy system.
Consolidated from various implementations across the codebase.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import uuid

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db_base import Base


@dataclass
class ResourceData:
    """
    Data model for a world resource like ore, crops, or magical elements.
    
    Resources can be harvested, traded, or used in crafting and other game mechanics.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    type: str = ""  # e.g., "mineral", "plant", "animal"
    rarity: str = "common"  # common, uncommon, rare, epic, legendary
    value: int = 1
    properties: Dict[str, Any] = field(default_factory=dict)
    spawn_locations: List[str] = field(default_factory=list)  # Region IDs
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def dict(self):
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "rarity": self.rarity,
            "value": self.value,
            "properties": self.properties,
            "spawn_locations": self.spawn_locations,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "metadata": self.metadata
        }


class Resource(Base):
    """
    SQLAlchemy ORM model for resources.
    
    This model represents resources that can be harvested, traded, or used in crafting.
    It is used for database persistence.
    """
    __tablename__ = 'resources'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    type = Column(String(50), nullable=False)
    rarity = Column(String(20), default="common")
    amount = Column(Float, default=0.0)
    price = Column(Float, default=1.0)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=True)
    faction_id = Column(Integer, ForeignKey('factions.id'), nullable=True)
    properties = Column(JSON, default=dict)
    last_updated = Column(String(50), default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default=dict)
    
    # Relationships
    region = relationship('Region', back_populates='resources')
    faction = relationship('Faction', back_populates='resources_rel')
    futures = relationship("CommodityFuture", back_populates="resource")
    
    def to_data_model(self) -> ResourceData:
        """Convert ORM model to data model."""
        return ResourceData(
            id=str(self.id),
            name=self.name,
            description=self.description or "",
            type=self.type,
            rarity=self.rarity,
            value=int(self.price),
            properties=self.properties or {},
            spawn_locations=[str(self.region_id)] if self.region_id else [],
            created_at=self.created_at,
            updated_at=self.updated_at,
            metadata=self.metadata or {}
        )
    
    @classmethod
    def from_data_model(cls, data_model: ResourceData) -> 'Resource':
        """Create ORM model from data model."""
        resource = cls(
            name=data_model.name,
            description=data_model.description,
            type=data_model.type,
            rarity=data_model.rarity,
            price=float(data_model.value),
            properties=data_model.properties,
            created_at=data_model.created_at,
            updated_at=data_model.updated_at,
            metadata=data_model.metadata
        )
        
        # Set region_id if spawn_locations exist
        if data_model.spawn_locations:
            try:
                resource.region_id = int(data_model.spawn_locations[0])
            except (ValueError, IndexError):
                pass
                
        return resource 