"""
Base item model for the loot system.
"""

from datetime import datetime
from typing import Dict, Any
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
try:
    from app.loot.models.base import LootBase
except ImportError:
    from .base import LootBase
from sqlalchemy.ext.declarative import declared_attr
import enum

class ItemType(str, enum.Enum):
    """Enumeration of item types."""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    QUEST = "quest"
    TREASURE = "treasure"
    KEY = "key"

class RarityTier(str, enum.Enum):
    """Enumeration of rarity tiers with their probabilities."""
    COMMON = "common"      # 60%
    UNCOMMON = "uncommon"  # 25%
    RARE = "rare"         # 10%
    EPIC = "epic"         # 4%
    LEGENDARY = "legendary" # 1%

class BaseItem(LootBase):
    """Base model for all lootable items."""
    __tablename__ = 'loot_items'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    item_type = Column(Enum(ItemType), nullable=False)
    rarity = Column(Enum(RarityTier), default=RarityTier.COMMON)
    weight = Column(Float, default=0.0)
    value = Column(Integer, default=0)
    base_stats = Column(JSON, default=dict)  # Core item statistics
    thematic_tags = Column(JSON, default=list)  # List of thematic categories
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    container_contents = relationship('ContainerContent', back_populates='item')
    shop_inventory_entries = relationship('ShopInventory', back_populates='item')
    loot_history_entries = relationship('LootHistory', back_populates='item')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_stats = kwargs.get('base_stats', {})
        self.thematic_tags = kwargs.get('thematic_tags', [])

    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'item_type': self.item_type.value,
            'rarity': self.rarity.value,
            'weight': self.weight,
            'value': self.value,
            'base_stats': self.base_stats,
            'thematic_tags': self.thematic_tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 