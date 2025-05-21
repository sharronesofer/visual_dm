"""
Commodity Future - Data models for resource futures contracts.

This module defines models for futures contracts, which allow buying/selling
resources at a predetermined price on a future date.
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from sqlalchemy import Column, String, Float, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


@dataclass
class CommodityFutureData:
    """
    Data model for a commodity future contract.
    
    Futures contracts allow buying/selling resources at a 
    predetermined price on a future date.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    resource_id: str = ""
    market_id: str = ""
    seller_id: str = ""  # Entity offering the contract
    buyer_id: str = ""   # Entity purchasing the contract (empty if available)
    quantity: float = 0.0
    strike_price: float = 0.0
    expiration_date: datetime = field(default_factory=lambda: datetime.utcnow())
    settlement_date: Optional[datetime] = None
    is_settled: bool = False
    premium: float = 0.0  # Cost to purchase the contract
    contract_type: str = "future"  # future, option, forward
    status: str = "open"  # open, matched, expired, settled, cancelled
    terms: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.utcnow())
    updated_at: datetime = field(default_factory=lambda: datetime.utcnow())


class CommodityFuture(Base):
    """ORM model for commodity futures contracts."""
    
    __tablename__ = "commodity_futures"
    
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
    
    @classmethod
    def from_data(cls, data: CommodityFutureData) -> 'CommodityFuture':
        """Create CommodityFuture from CommodityFutureData."""
        return cls(
            id=data.id,
            resource_id=data.resource_id,
            market_id=data.market_id,
            seller_id=data.seller_id,
            buyer_id=data.buyer_id,
            quantity=data.quantity,
            strike_price=data.strike_price,
            expiration_date=data.expiration_date,
            settlement_date=data.settlement_date,
            is_settled=data.is_settled,
            premium=data.premium,
            contract_type=data.contract_type,
            status=data.status,
            terms=data.terms,
            created_at=data.created_at,
            updated_at=data.updated_at
        ) 