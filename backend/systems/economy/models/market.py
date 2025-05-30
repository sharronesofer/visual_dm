"""
Market model for economy system.
New model to manage pricing and market dynamics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from app.core.db_base import Base


@dataclass
class MarketData:
    """
    Data model for a regional market.
    
    Markets represent the buying and selling of goods in a region,
    with dynamic pricing based on supply and demand.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    region_id: str = ""
    market_type: str = "general"  # general, specialized, black_market
    price_modifiers: Dict[str, float] = field(default_factory=dict)  # resource_id -> modifier
    supply_demand: Dict[str, Dict[str, float]] = field(default_factory=dict)  # resource_id -> {supply, demand}
    trading_volume: Dict[str, float] = field(default_factory=dict)  # resource_id -> volume
    tax_rate: float = 0.05  # Default 5% tax rate
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def dict(self):
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "region_id": self.region_id,
            "market_type": self.market_type,
            "price_modifiers": self.price_modifiers,
            "supply_demand": self.supply_demand,
            "trading_volume": self.trading_volume,
            "tax_rate": self.tax_rate,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "metadata": self.metadata
        }
    
    def get_price_modifier(self, resource_id: str) -> float:
        """Get price modifier for a resource."""
        return self.price_modifiers.get(resource_id, 1.0)
    
    def set_price_modifier(self, resource_id: str, modifier: float) -> None:
        """Set price modifier for a resource."""
        self.price_modifiers[resource_id] = modifier
        
    def update_supply_demand(self, resource_id: str, supply: float, demand: float) -> None:
        """Update supply and demand for a resource."""
        if resource_id not in self.supply_demand:
            self.supply_demand[resource_id] = {}
        self.supply_demand[resource_id]['supply'] = supply
        self.supply_demand[resource_id]['demand'] = demand
        
        # Auto-adjust price modifier based on supply and demand
        if supply > 0 and demand > 0:
            ratio = demand / supply
            self.price_modifiers[resource_id] = max(0.1, min(10.0, ratio))
        
    def record_trade(self, resource_id: str, volume: float) -> None:
        """Record a trade for a resource."""
        if resource_id not in self.trading_volume:
            self.trading_volume[resource_id] = 0.0
        self.trading_volume[resource_id] += volume


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
    metadata = Column(JSON, default=dict)

    # Relationships
    region = relationship('Region', back_populates='markets')
    futures = relationship("CommodityFuture", back_populates="market")
    
    def to_data_model(self) -> MarketData:
        """Convert ORM model to data model."""
        return MarketData(
            id=str(self.id),
            name=self.name or f"Market {self.id}",
            region_id=str(self.region_id),
            market_type=self.market_type,
            price_modifiers=self.price_modifiers or {},
            supply_demand=self.supply_demand or {},
            trading_volume=self.trading_volume or {},
            tax_rate=self.tax_rate,
            created_at=self.created_at,
            updated_at=self.updated_at,
            metadata=self.metadata or {}
        )
    
    @classmethod
    def from_data_model(cls, data_model: MarketData) -> 'Market':
        """Create ORM model from data model."""
        return cls(
            name=data_model.name,
            region_id=int(data_model.region_id) if data_model.region_id else None,
            market_type=data_model.market_type,
            price_modifiers=data_model.price_modifiers,
            supply_demand=data_model.supply_demand,
            trading_volume=data_model.trading_volume,
            tax_rate=data_model.tax_rate,
            created_at=data_model.created_at,
            updated_at=data_model.updated_at,
            metadata=data_model.metadata
        )
        
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