"""
Trade route business model for economy system.
SQLAlchemy models have been moved to backend/infrastructure/database/economy/trade_route_models.py
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid


@dataclass
class TradeRouteData:
    """
    Data model for a trade route between regions.
    
    Trade routes represent the flow of goods and resources between regions,
    and can affect the economies of both regions.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    origin_region_id: str = ""
    destination_region_id: str = ""
    resource_ids: List[str] = field(default_factory=list)
    volume: float = 0.0
    profit: float = 0.0
    status: str = "active"  # active, disrupted, closed
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def dict(self):
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "origin_region_id": self.origin_region_id,
            "destination_region_id": self.destination_region_id, 
            "resource_ids": self.resource_ids,
            "volume": self.volume,
            "profit": self.profit,
            "status": self.status,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "metadata": self.metadata
        } 