"""
Inventory model definitions.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, JSON, Boolean, ForeignKey, Text, Enum
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel
import enum

class ItemCategory(enum.Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    QUEST = "quest"
    MISC = "misc"

class Item(db.Model):
    """Item model for game items."""
    __tablename__ = 'items'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500))
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)
    rarity: Mapped[str] = mapped_column(String(20), default='common')
    value: Mapped[int] = mapped_column(Integer, default=0)
    weight: Mapped[float] = mapped_column(Float, default=0.0)
    properties: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert item to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'item_type': self.item_type,
            'rarity': self.rarity,
            'value': self.value,
            'weight': self.weight,
            'properties': self.properties
        }

class Inventory(db.Model):
    """Inventory model for storing items."""
    __tablename__ = 'inventories'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(Integer, nullable=False)
    owner_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'character', 'npc', 'container'
    capacity: Mapped[int] = mapped_column(Integer, default=100)
    weight_limit: Mapped[float] = mapped_column(Float, default=100.0)
    items: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert inventory to dictionary."""
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'owner_type': self.owner_type,
            'capacity': self.capacity,
            'weight_limit': self.weight_limit,
            'items': self.items
        }

    def add_item(self, item: dict) -> bool:
        """Add item to inventory."""
        if len(self.items.get('items', [])) >= self.capacity:
            return False
            
        total_weight = sum(item.get('weight', 0) for item in self.items.get('items', []))
        if total_weight + item.get('weight', 0) > self.weight_limit:
            return False
            
        if 'items' not in self.items:
            self.items['items'] = []
        self.items['items'].append(item)
        self.updated_at = datetime.utcnow()
        return True

    def remove_item(self, item_id: int) -> bool:
        """Remove item from inventory."""
        if 'items' not in self.items:
            return False
            
        for i, item in enumerate(self.items['items']):
            if item.get('id') == item_id:
                self.items['items'].pop(i)
                self.updated_at = datetime.utcnow()
                return True
        return False

class EquipmentSlot(db.Model):
    """Equipment slot model for character equipment."""
    __tablename__ = 'equipment_slots'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    character_id: Mapped[int] = mapped_column(Integer, nullable=False)
    slot_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'head', 'body', 'weapon', etc.
    item_id: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert equipment slot to dictionary."""
        return {
            'id': self.id,
            'character_id': self.character_id,
            'slot_type': self.slot_type,
            'item_id': self.item_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Equipment(db.Model):
    """Equipment model for character equipment."""
    __tablename__ = 'equipment'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey('characters.id'), nullable=False)
    slot: Mapped[str] = mapped_column(String(50), nullable=False)  # head, body, weapon, etc.
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey('items.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert equipment to dictionary."""
        return {
            'id': self.id,
            'character_id': self.character_id,
            'slot': self.slot,
            'item_id': self.item_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 