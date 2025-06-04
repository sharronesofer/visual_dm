"""
Economy System SQLAlchemy Models - Infrastructure Layer

This module contains the SQLAlchemy table definitions for the economy system.
Business logic models remain in backend/systems/economy/models/
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB
from sqlalchemy.orm import relationship

from backend.infrastructure.database import Base


class Resource(Base):
    """SQLAlchemy model for resources in the economy system"""
    
    __tablename__ = "resources"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    name = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    region_id = Column(Integer, nullable=False, index=True)
    amount = Column(Float, default=0.0)
    base_value = Column(Float, default=0.0)
    rarity = Column(String(20), default='common', index=True)
    description = Column(String(500), default='')
    is_tradeable = Column(Boolean, default=True, index=True)
    is_consumable = Column(Boolean, default=False)
    weight = Column(Float, default=0.0)
    volume = Column(Float, default=0.0)
    durability = Column(Float, default=100.0)
    quality = Column(String(20), default='standard')
    minimum_viable_amount = Column(Float, default=0.0)
    maximum_capacity = Column(Float, nullable=True)
    production_rate = Column(Float, default=0.0)
    consumption_rate = Column(Float, default=0.0)
    seasonal_modifier = Column(Float, default=1.0)
    resource_metadata = Column(JSONB, default=dict)
    tags = Column(JSONB, default=list)
    properties = Column(JSONB, default=dict)
    
    # Relationships
    futures = relationship("CommodityFuture", back_populates="resource")
    trade_routes = relationship("TradeRoute", back_populates="primary_resource")
    
    def __repr__(self):
        return f"<Resource(id={self.id}, name={self.name}, type={self.resource_type})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "resource_type": self.resource_type,
            "region_id": self.region_id,
            "amount": self.amount,
            "base_value": self.base_value,
            "rarity": self.rarity,
            "description": self.description,
            "is_tradeable": self.is_tradeable,
            "is_consumable": self.is_consumable,
            "weight": self.weight,
            "volume": self.volume,
            "durability": self.durability,
            "quality": self.quality,
            "minimum_viable_amount": self.minimum_viable_amount,
            "maximum_capacity": self.maximum_capacity,
            "production_rate": self.production_rate,
            "consumption_rate": self.consumption_rate,
            "seasonal_modifier": self.seasonal_modifier,
            "resource_metadata": self.resource_metadata or {},
            "tags": self.tags or [],
            "properties": self.properties or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class EconomyEntity(Base):
    """SQLAlchemy entity for economy system"""
    
    __tablename__ = f"economy_entities"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(50), default="active", index=True)
    properties = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)

    def __repr__(self):
        return f"<EconomyEntity(id={self.id}, name={self.name})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "properties": self.properties or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        } 