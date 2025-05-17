"""
Inventory item model for game items.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Integer, String, JSON, DateTime, ForeignKey, Text, Float, Boolean, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel

class InventoryItem(BaseModel):
    """
    Model for game items in inventory.
    Fields:
        id (int): Primary key.
        name (str): Item name.
        description (str): Item description.
        item_type (str): Type of item (weapon, armor, consumable, etc.).
        rarity (str): Rarity of the item (common, rare, epic, legendary).
        value (int): Gold value.
        weight (float): Weight in kg.
        stack_size (int): Current stack size.
        max_stack (int): Maximum stack size.
        properties (dict): Item properties (damage, defense, effects, etc.).
        requirements (dict): Requirements (level, stats, etc.).
        is_equippable (bool): Whether the item can be equipped.
        is_consumable (bool): Whether the item can be consumed.
        is_quest_item (bool): Whether the item is a quest item.
        owner_id (int): Foreign key to character owner.
        owner (Character): Related character.
        item_id (int): Foreign key to item definition.
        item (Item): Related item definition.
    """
    __tablename__ = 'inventory_items'
    __table_args__ = (
        Index('ix_inventory_items_type', 'item_type'),
        Index('ix_inventory_items_rarity', 'rarity'),
        Index('ix_inventory_items_owner_id', 'owner_id'),
        {'extend_existing': True}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, doc="Primary key.")
    name: Mapped[str] = mapped_column(String(100), nullable=False, doc="Item name.")
    description: Mapped[Optional[str]] = mapped_column(Text, doc="Item description.")
    item_type: Mapped[Optional[str]] = mapped_column(String(50), doc="Type of item (weapon, armor, consumable, etc.).")
    rarity: Mapped[Optional[str]] = mapped_column(String(20), doc="Rarity of the item (common, rare, epic, legendary).")
    value: Mapped[Optional[int]] = mapped_column(Integer, doc="Gold value.")
    weight: Mapped[Optional[float]] = mapped_column(Float, doc="Weight in kg.")
    stack_size: Mapped[int] = mapped_column(Integer, default=1, doc="Current stack size.")
    max_stack: Mapped[int] = mapped_column(Integer, default=1, doc="Maximum stack size.")
    properties: Mapped[dict] = mapped_column(JSON, default=dict, doc="Item properties (damage, defense, effects, etc.).")
    requirements: Mapped[dict] = mapped_column(JSON, default=dict, doc="Requirements (level, stats, etc.).")
    is_equippable: Mapped[bool] = mapped_column(Boolean, default=False, doc="Whether the item can be equipped.")
    is_consumable: Mapped[bool] = mapped_column(Boolean, default=False, doc="Whether the item can be consumed.")
    is_quest_item: Mapped[bool] = mapped_column(Boolean, default=False, doc="Whether the item is a quest item.")

    owner_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('characters.id'), doc="Foreign key to character owner.")
    owner: Mapped[Optional['Character']] = relationship('Character', back_populates='inventory_items')
    item_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('items.id'), doc="Foreign key to item definition.")
    item: Mapped[Optional['Item']] = relationship('app.core.models.item.Item', back_populates='inventory_items')

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