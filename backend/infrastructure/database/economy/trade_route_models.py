"""
Trade Route SQLAlchemy Models - Infrastructure Layer

This module contains the SQLAlchemy table definitions for trade routes.
Business logic models remain in backend/systems/economy/models/trade_route.py
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship

from backend.infrastructure.database import Base


class TradeRoute(Base):
    """
    SQLAlchemy ORM model for trade routes.
    
    This model represents trade routes between regions and is used for database persistence.
    """
    __tablename__ = 'trade_routes'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    origin_region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)
    destination_region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)
    resource_id = Column(Integer, ForeignKey('resources.id'), nullable=True)  # Primary resource
    resource_ids = Column(JSON, default=list)  # List of all resources traded
    volume = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)
    status = Column(String(20), default='active')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_trade_time = Column(DateTime, nullable=True)
    
    # Additional data
    # Renamed from 'metadata' to avoid SQLAlchemy reserved attribute conflict
    route_metadata = Column(JSON, default=dict)

    # Relationships
    origin_region = relationship('Region', foreign_keys=[origin_region_id])
    destination_region = relationship('Region', foreign_keys=[destination_region_id])
    primary_resource = relationship('Resource', foreign_keys=[resource_id])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "origin_region_id": self.origin_region_id,
            "destination_region_id": self.destination_region_id,
            "resource_id": self.resource_id,
            "resource_ids": self.resource_ids or [],
            "volume": self.volume,
            "profit": self.profit,
            "status": self.status,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "last_trade_time": self.last_trade_time.isoformat() if self.last_trade_time else None,
            "route_metadata": self.route_metadata or {}
        } 