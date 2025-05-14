"""
Inventory item model for game items.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Float, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel

class InventoryItem(BaseModel):
    """Model for game items."""
    __tablename__ = 'inventory_items'
    __table_args__ = (
        Index('ix_inventory_items_type', 'item_type'),
        Index('ix_inventory_items_rarity', 'rarity'),
        Index('ix_inventory_items_owner_id', 'owner_id'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    item_type = Column(String(50))  # weapon, armor, consumable, etc.
    rarity = Column(String(20))  # common, rare, epic, legendary
    value = Column(Integer)  # gold value
    weight = Column(Float)  # in kg
    stack_size = Column(Integer, default=1)
    max_stack = Column(Integer, default=1)
    properties = Column(JSON, default=dict)  # damage, defense, effects, etc.
    requirements = Column(JSON, default=dict)  # level, stats, etc.
    is_equippable = Column(Boolean, default=False)
    is_consumable = Column(Boolean, default=False)
    is_quest_item = Column(Boolean, default=False)
    
    # Foreign Keys
    owner_id = Column(Integer, ForeignKey('characters.id'))
    owner = relationship('Character', back_populates='inventory_items')
    item_id = Column(Integer, ForeignKey('items.id'))
    item = relationship('app.core.models.item.Item', back_populates='inventory_items')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'item_type': self.item_type,
            'rarity': self.rarity,
            'value': self.value,
            'weight': self.weight,
            'stack_size': self.stack_size,
            'max_stack': self.max_stack,
            'properties': self.properties,
            'requirements': self.requirements,
            'is_equippable': self.is_equippable,
            'is_consumable': self.is_consumable,
            'is_quest_item': self.is_quest_item,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Inventory:
    """Helper class for managing character inventories."""
    def __init__(self, capacity: float = 100.0):
        self.capacity = capacity
        self.items = []
        self.current_weight = 0.0

    def add_item(self, item: Dict) -> bool:
        """Add an item to the inventory."""
        if self.current_weight + item.get('weight', 0) <= self.capacity:
            self.items.append(item)
            self.current_weight += item.get('weight', 0)
            return True
        return False

    def remove_item(self, item_id: str) -> bool:
        """Remove an item from the inventory."""
        for item in self.items:
            if item.get('id') == item_id:
                self.items.remove(item)
                self.current_weight -= item.get('weight', 0)
                return True
        return False

    def find_item(self, item_id: str) -> Optional[Dict]:
        """Find an item in the inventory."""
        for item in self.items:
            if item.get('id') == item_id:
                return item
        return None

    def get_equipped_items(self) -> list[Dict]:
        """Get all equipped items."""
        return [item for item in self.items if item.get('equipped', False)]

    def get_items_by_type(self, item_type: str) -> list[Dict]:
        """Get all items of a specific type."""
        return [item for item in self.items if item.get('item_type') == item_type]

    def clear(self) -> None:
        """Clear the inventory."""
        self.items = []
        self.current_weight = 0.0 