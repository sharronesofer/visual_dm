"""
Commodity Future SQLAlchemy Models - Infrastructure Layer

This module contains the SQLAlchemy table definitions for commodity futures.
Business logic models remain in backend/systems/economy/models/commodity_future.py
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from backend.infrastructure.database import Base


class CommodityFuture(Base):
    """ORM model for commodity futures contracts."""
    
    __tablename__ = "commodity_futures"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    resource_id = Column(String, ForeignKey("resources.id"), nullable=False, index=True)
    market_id = Column(String, ForeignKey("markets.id"), nullable=False, index=True)
    seller_id = Column(String, nullable=False, index=True)
    buyer_id = Column(String, nullable=True, index=True)
    quantity = Column(Float, nullable=False)
    strike_price = Column(Float, nullable=False)
    expiration_date = Column(DateTime, nullable=False, index=True)
    settlement_date = Column(DateTime, nullable=True)
    is_settled = Column(Boolean, default=False)
    premium = Column(Float, default=0.0)
    contract_type = Column(String, default="future")
    status = Column(String, default="open", index=True)
    terms = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resource = relationship("Resource", back_populates="futures")
    market = relationship("Market", back_populates="futures")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "resource_id": self.resource_id,
            "market_id": self.market_id,
            "seller_id": self.seller_id,
            "buyer_id": self.buyer_id,
            "quantity": self.quantity,
            "strike_price": self.strike_price,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "settlement_date": self.settlement_date.isoformat() if self.settlement_date else None,
            "is_settled": self.is_settled,
            "premium": self.premium,
            "contract_type": self.contract_type,
            "status": self.status,
            "terms": self.terms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 