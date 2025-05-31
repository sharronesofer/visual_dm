from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.infrastructure.models import BaseModel

class MarketItem(BaseModel):
    """Represents an item available in the market."""
    __tablename__ = 'market_items'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)  # ResourceType or ProductType
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    offers = relationship('TradeOffer', back_populates='item')
    price_history = relationship('PriceHistory', back_populates='item')

    def __repr__(self):
        return f"<MarketItem {self.name} ({self.type})>"

class TradeOffer(BaseModel):
    """Represents a trade offer in the market."""
    __tablename__ = 'trade_offers'
    __table_args__ = (
        Index('ix_trade_offer_item_id', 'item_id'),
        Index('ix_trade_offer_seller_id', 'seller_id'),
    )

    id = Column(Integer, primary_key=True)
    seller_id = Column(String(64), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey('market_items.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    minimum_quantity = Column(Float)
    negotiable = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    item = relationship('MarketItem', back_populates='offers')
    transactions = relationship('Transaction', back_populates='offer')

    def __repr__(self):
        return f"<TradeOffer {self.id} for item {self.item_id} by {self.seller_id}>"

class Transaction(BaseModel):
    """Represents a completed trade transaction."""
    __tablename__ = 'transactions'
    __table_args__ = (
        Index('ix_transaction_offer_id', 'offer_id'),
        Index('ix_transaction_buyer_id', 'buyer_id'),
        Index('ix_transaction_seller_id', 'seller_id'),
    )

    id = Column(Integer, primary_key=True)
    offer_id = Column(Integer, ForeignKey('trade_offers.id'), nullable=False)
    buyer_id = Column(String(64), nullable=False, index=True)
    seller_id = Column(String(64), nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    market_id = Column(String(64), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    offer = relationship('TradeOffer', back_populates='transactions')

    def __repr__(self):
        return f"<Transaction {self.id} offer {self.offer_id} buyer {self.buyer_id}>"

class PriceHistory(BaseModel):
    """Tracks historical price data for market items."""
    __tablename__ = 'price_history'
    __table_args__ = (
        Index('ix_price_history_item_id', 'item_id'),
        Index('ix_price_history_last_update', 'last_update'),
    )

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('market_items.id'), nullable=False)
    average_price = Column(Float, nullable=False)
    min_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    trend = Column(Float, default=0.0)
    last_update = Column(DateTime, default=datetime.utcnow)

    item = relationship('MarketItem', back_populates='price_history')

    def __repr__(self):
        return f"<PriceHistory {self.id} item {self.item_id} @ {self.last_update}>" 