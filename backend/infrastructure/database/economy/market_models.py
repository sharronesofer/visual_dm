"""
Market SQLAlchemy Models - Infrastructure Layer

This module contains the SQLAlchemy table definitions for markets.
Business logic models remain in backend/systems/economy/models/market.py
"""

from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship

from backend.infrastructure.database import Base


class Market(Base):
    """
    SQLAlchemy ORM model for markets.
    
    This model represents regional markets and is used for database persistence.
    """
    __tablename__ = 'markets'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)
    market_type = Column(String(50), default='general')
    price_modifiers = Column(JSON, default=dict)
    supply_demand = Column(JSON, default=dict)
    trading_volume = Column(JSON, default=dict)
    tax_rate = Column(Float, default=0.05)  # Default 5% tax rate
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional metadata
    # Renamed from 'metadata' to avoid SQLAlchemy reserved attribute conflict
    market_metadata = Column(JSON, default=dict)

    # Relationships
    region = relationship('Region', back_populates='markets')
    futures = relationship("CommodityFuture", back_populates="market")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "region_id": self.region_id,
            "market_type": self.market_type,
            "price_modifiers": self.price_modifiers or {},
            "supply_demand": self.supply_demand or {},
            "trading_volume": self.trading_volume or {},
            "tax_rate": self.tax_rate,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "market_metadata": self.market_metadata or {}
        }
        
    def get_price_modifier(self, resource_id: str) -> float:
        """Get price modifier for a resource."""
        if not self.price_modifiers:
            return 1.0
        return self.price_modifiers.get(str(resource_id), 1.0)
    
    def set_price_modifier(self, resource_id: str, modifier: float) -> None:
        """Set price modifier for a resource."""
        if not self.price_modifiers:
            self.price_modifiers = {}
        self.price_modifiers[str(resource_id)] = modifier
        
    def update_supply_demand(self, resource_id: str, supply: float, demand: float) -> None:
        """Update supply and demand for a resource."""
        if not self.supply_demand:
            self.supply_demand = {}
        resource_id = str(resource_id)
        if resource_id not in self.supply_demand:
            self.supply_demand[resource_id] = {}
        self.supply_demand[resource_id]['supply'] = supply
        self.supply_demand[resource_id]['demand'] = demand
        
        # Auto-adjust price modifier based on supply and demand
        if supply > 0 and demand > 0:
            ratio = demand / supply
            self.set_price_modifier(resource_id, max(0.1, min(10.0, ratio)))
        
    def record_trade(self, resource_id: str, volume: float) -> None:
        """Record a trade for a resource."""
        if not self.trading_volume:
            self.trading_volume = {}
        resource_id = str(resource_id)
        if resource_id not in self.trading_volume:
            self.trading_volume[resource_id] = 0.0
        self.trading_volume[resource_id] += volume 