"""
Loot history and analytics models for tracking item generation and distribution.

This module provides classes for tracking the history and analytics of loot generation
and distribution throughout the game.
"""

from datetime import datetime
from typing import Dict, Any
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from .base import LootBase # Correct
# from .item import BaseItem # For explicit relationship/type hint
# from .location import Location # For explicit relationship/type hint
import enum
from sqlalchemy.dialects.postgresql import UUID

class LootSourceType(str, enum.Enum):
    """Enumeration of loot source types."""
    CONTAINER = "container"
    SHOP = "shop"
    QUEST = "quest"
    ENEMY = "enemy"
    EVENT = "event"
    CRAFTING = "crafting"
    ADMIN = "admin"

class MetricType(str, enum.Enum):
    """Enumeration of loot analytics metric types."""
    ITEM_GENERATION = "item_generation"
    ITEM_ACQUISITION = "item_acquisition"
    GOLD_GENERATION = "gold_generation"
    GOLD_SINK = "gold_sink"
    RARITY_DISTRIBUTION = "rarity_distribution"
    LOCATION_DISTRIBUTION = "location_distribution"
    PLAYER_WEALTH = "player_wealth"

class LootHistory(LootBase):
    """Model for tracking loot generation and acquisition."""
    __tablename__ = 'loot_history'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    source_type = Column(Enum(LootSourceType), nullable=False)
    source_id = Column(String(50))  # ID of the container/shop/enemy/etc
    item_id = Column(Integer, ForeignKey('loot_items.id'), nullable=False)
    quantity = Column(Integer, default=1)
    player_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))  # Null for generation events
    character_id = Column(Integer, ForeignKey('characters.id'))  # Null for generation events
    location_id = Column(Integer, ForeignKey('loot_locations.id'))
    danger_level = Column(Integer)
    player_level = Column(Integer)
    value = Column(Integer)  # Value at time of event
    context = Column(JSON, default=dict)  # Additional event-specific data
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    item = relationship('BaseItem', back_populates='loot_history_entries')
    location = relationship('Location', backref='loot_history_entries')

    def to_dict(self) -> Dict[str, Any]:
        """Convert loot history entry to dictionary representation."""
        return {
            'id': self.id,
            'source_type': self.source_type.value,
            'source_id': self.source_id,
            'item_id': self.item_id,
            'quantity': self.quantity,
            'player_id': self.player_id,
            'character_id': self.character_id,
            'location_id': self.location_id,
            'danger_level': self.danger_level,
            'player_level': self.player_level,
            'value': self.value,
            'context': self.context,
            'created_at': self.created_at.isoformat()
        }

class LootAnalytics(LootBase):
    """Model for aggregated loot metrics and analytics."""
    __tablename__ = 'loot_analytics'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    metric_type = Column(Enum(MetricType), nullable=False)
    time_bucket = Column(DateTime, nullable=False)  # Start of the aggregation period
    location_id = Column(Integer, ForeignKey('loot_locations.id'))
    danger_level = Column(Integer)
    player_level_range = Column(String(20))  # e.g., "1-5", "6-10", etc.
    metric_value = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=False)  # Number of events aggregated
    context = Column(JSON, default=dict)  # Additional metric-specific data
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    location = relationship('Location', backref='loot_analytics_entries')

    def to_dict(self) -> Dict[str, Any]:
        """Convert analytics entry to dictionary representation."""
        return {
            'id': self.id,
            'metric_type': self.metric_type.value,
            'time_bucket': self.time_bucket.isoformat(),
            'location_id': self.location_id,
            'danger_level': self.danger_level,
            'player_level_range': self.player_level_range,
            'metric_value': self.metric_value,
            'sample_size': self.sample_size,
            'context': self.context,
            'created_at': self.created_at.isoformat()
        } 