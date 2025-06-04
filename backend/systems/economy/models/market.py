"""
Market business model for economy system.
SQLAlchemy models have been moved to backend/infrastructure/database/economy/market_models.py
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid


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