"""
Commodity Future - Business data models for resource futures contracts.

This module defines business data models for futures contracts, which allow buying/selling
resources at a predetermined price on a future date.
SQLAlchemy models have been moved to backend/infrastructure/database/economy/commodity_future_models.py
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field


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