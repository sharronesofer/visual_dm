"""
Shop and inventory models for the loot system.
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Text, Enum, Boolean, Interval
from sqlalchemy.orm import relationship
from loot_models.base import LootBase
import enum

class ShopType(str, enum.Enum):
    """Enumeration of shop types."""
    GENERAL = "general"
    BLACKSMITH = "blacksmith"
    ALCHEMIST = "alchemist"
    MAGIC = "magic"
    JEWELER = "jeweler"
    EXOTIC = "exotic"
    WANDERING = "wandering"

class Shop(LootBase):
    """Model for shops that sell items."""
    __tablename__ = 'loot_shops'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    shop_type = Column(Enum(ShopType), nullable=False)
    location_id = Column(Integer, ForeignKey('loot_locations.id'), nullable=False)
    description = Column(Text)
    refresh_interval = Column(Interval, default=timedelta(days=1))  # How often inventory refreshes
    base_markup = Column(Float, default=1.5)  # Multiplier for item base prices
    reputation_requirement = Column(Integer, default=0)  # Minimum reputation needed to shop
    last_refresh = Column(DateTime, default=datetime.utcnow)
    next_refresh = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    location = relationship('Location', back_populates='shops')
    inventory = relationship('ShopInventory', back_populates='shop', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.next_refresh = self.last_refresh + self.refresh_interval

    def to_dict(self) -> Dict[str, Any]:
        """Convert shop to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'shop_type': self.shop_type.value,
            'location_id': self.location_id,
            'description': self.description,
            'refresh_interval': str(self.refresh_interval),
            'base_markup': self.base_markup,
            'reputation_requirement': self.reputation_requirement,
            'last_refresh': self.last_refresh.isoformat(),
            'next_refresh': self.next_refresh.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ShopInventory(LootBase):
    """Model for items available in shops."""
    __tablename__ = 'loot_shop_inventory'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey('loot_shops.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('loot_items.id'), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Integer, nullable=False)  # Actual selling price
    is_special = Column(Boolean, default=False)  # Special/limited time items
    restock_quantity = Column(Integer)  # How many to restock to on refresh
    min_quantity = Column(Integer, default=0)  # Minimum stock to maintain
    max_quantity = Column(Integer)  # Maximum stock allowed
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # When item should be removed from shop
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    shop = relationship('Shop', back_populates='inventory')
    item = relationship('BaseItem', back_populates='shop_inventory_entries')

    def to_dict(self) -> Dict[str, Any]:
        """Convert shop inventory entry to dictionary representation."""
        return {
            'id': self.id,
            'shop_id': self.shop_id,
            'item_id': self.item_id,
            'quantity': self.quantity,
            'price': self.price,
            'is_special': self.is_special,
            'restock_quantity': self.restock_quantity,
            'min_quantity': self.min_quantity,
            'max_quantity': self.max_quantity,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'updated_at': self.updated_at.isoformat()
        } 
