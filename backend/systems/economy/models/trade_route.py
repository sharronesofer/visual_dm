"""
Trade route model for economy system.
Consolidated and improved from the original trade_route.py.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from app.core.db_base import Base


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
    metadata = Column(JSON, default=dict)

    # Relationships
    origin_region = relationship('Region', foreign_keys=[origin_region_id])
    destination_region = relationship('Region', foreign_keys=[destination_region_id])
    primary_resource = relationship('Resource', foreign_keys=[resource_id])
    
    def to_data_model(self) -> TradeRouteData:
        """Convert ORM model to data model."""
        resource_ids = self.resource_ids or []
        if self.resource_id and str(self.resource_id) not in resource_ids:
            resource_ids.append(str(self.resource_id))
            
        return TradeRouteData(
            id=str(self.id),
            name=self.name or f"Trade route {self.id}",
            origin_region_id=str(self.origin_region_id),
            destination_region_id=str(self.destination_region_id),
            resource_ids=resource_ids,
            volume=self.volume,
            profit=self.profit,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.last_updated,
            metadata=self.metadata or {}
        )
    
    @classmethod
    def from_data_model(cls, data_model: TradeRouteData) -> 'TradeRoute':
        """Create ORM model from data model."""
        # Extract primary resource ID (first in the list)
        primary_resource_id = None
        if data_model.resource_ids:
            try:
                primary_resource_id = int(data_model.resource_ids[0])
            except (ValueError, IndexError):
                pass
        
        return cls(
            name=data_model.name,
            origin_region_id=int(data_model.origin_region_id) if data_model.origin_region_id else None,
            destination_region_id=int(data_model.destination_region_id) if data_model.destination_region_id else None,
            resource_id=primary_resource_id,
            resource_ids=data_model.resource_ids,
            volume=data_model.volume,
            profit=data_model.profit,
            status=data_model.status,
            created_at=data_model.created_at,
            last_updated=data_model.updated_at,
            metadata=data_model.metadata
        ) 