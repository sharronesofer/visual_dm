"""
Database models for inventory management.

This module defines the core models for the inventory system: Item, Inventory, and InventoryItem.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, JSON, Boolean, ForeignKey, Text, Enum
from datetime import datetime
import enum

from backend.core.database import db

class ItemCategory(enum.Enum):
    """Enum for categorizing items in the inventory system."""
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    QUEST = "quest"
    MISC = "misc"

class Item(db.Model):
    """
    Model for items that can be stored in inventories.
    """
    __tablename__ = "items"
    
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(100), nullable=False)
    description = mapped_column(Text, nullable=True)
    category = mapped_column(String(50), nullable=False, default="MISC")
    weight = mapped_column(Float, nullable=False, default=0)
    value = mapped_column(Integer, nullable=False, default=0)
    properties = mapped_column(JSON, nullable=True)
    
    # Stackable item properties
    is_stackable = mapped_column(Boolean, default=True)
    max_stack_size = mapped_column(Integer, nullable=True)  # None means unlimited
    
    # Weight validation properties
    apply_weight_when_equipped = mapped_column(Boolean, default=True)
    
    # Equipment properties
    can_be_equipped = mapped_column(Boolean, default=False)
    equipment_slot = mapped_column(String(50), nullable=True)

    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    inventory_items = relationship("InventoryItem", back_populates="item", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert item to a dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'weight': self.weight,
            'value': self.value,
            'properties': self.properties,
            'is_stackable': self.is_stackable,
            'max_stack_size': self.max_stack_size,
            'can_be_equipped': self.can_be_equipped,
            'equipment_slot': self.equipment_slot,
            'apply_weight_when_equipped': self.apply_weight_when_equipped,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Inventory(db.Model):
    """Model representing an inventory that can hold items."""
    __tablename__ = 'inventories'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(Integer, nullable=False)
    owner_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'character', 'npc', 'container', etc.
    capacity: Mapped[int] = mapped_column(Integer)  # Maximum number of items, null means unlimited
    weight_limit: Mapped[float] = mapped_column(Float)  # Maximum weight, null means unlimited
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship('InventoryItem', back_populates='inventory', lazy='dynamic')

    def to_dict(self, include_items=False, include_stats=False):
        """Convert inventory to a dictionary for API responses
        
        Args:
            include_items: Whether to include items in the result
            include_stats: Whether to include calculated stats like current weight
            
        Returns:
            Dictionary representation of the inventory
        """
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'inventory_type': self.owner_type,
            'capacity': self.capacity,
            'weight_limit': self.weight_limit,
            'count_equipped_weight': self.count_equipped_weight,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_stats:
            current_weight = self.calculate_total_weight()
            result.update({
                'current_weight': current_weight,
                'remaining_weight': (self.weight_limit - current_weight) if self.weight_limit else None,
                'item_count': len(self.items),
                'remaining_capacity': (self.capacity - len(self.items)) if self.capacity else None
            })
            
        if include_items:
            result['items'] = [item.to_dict() for item in self.items]
            
        return result

    def add_item(self, item: Item, quantity: int = 1) -> bool:
        """
        Add an item to the inventory.
        
        Args:
            item: Item to add
            quantity: Number of items to add
            
        Returns:
            True if add was successful, False otherwise
        """
        # Check capacity constraint
        if self.capacity is not None and self.items.count() >= self.capacity:
            return False
            
        # Check weight constraint
        if self.weight_limit is not None:
            current_weight = sum(item_entry.item.weight * item_entry.quantity for item_entry in self.items)
            if current_weight + (item.weight * quantity) > self.weight_limit:
                return False
                
        # Look for existing inventory item to stack with
        inv_item = self.items.filter_by(item_id=item.id).first()
        
        if inv_item:
            inv_item.quantity += quantity
        else:
            inv_item = InventoryItem(
                inventory=self,
                item=item,
                quantity=quantity
            )
            db.session.add(inv_item)
            
        self.updated_at = datetime.utcnow()
        return True

    def remove_item(self, item_id: int, quantity: int = 1) -> bool:
        """
        Remove an item from the inventory.
        
        Args:
            item_id: ID of the item to remove
            quantity: Number of items to remove
            
        Returns:
            True if removal was successful, False otherwise
        """
        inv_item = self.items.filter_by(item_id=item_id).first()
        
        if not inv_item:
            return False
            
        if inv_item.quantity <= quantity:
            db.session.delete(inv_item)
        else:
            inv_item.quantity -= quantity
            
        self.updated_at = datetime.utcnow()
        return True

    def calculate_total_weight(self) -> float:
        """
        Calculate the total weight of all items in the inventory.
        
        Returns:
            Total weight
        """
        if self.count_equipped_weight:
            # Count all items
            return sum(item.item.weight * item.quantity for item in self.items)
        else:
            # Only count unequipped items
            return sum(
                item.item.weight * item.quantity 
                for item in self.items 
                if not item.is_equipped or item.item.apply_weight_when_equipped
            )
    
    def has_space_for_item(self, item_id: int, quantity: int = 1) -> bool:
        """
        Check if inventory has space for a new item.
        
        Args:
            item_id: ID of the item to add
            quantity: Quantity to add
            
        Returns:
            True if inventory has space, False otherwise
        """
        # Check capacity constraint
        if self.capacity is not None:
            # Check if item already exists in inventory
            existing_item = next((i for i in self.items if i.item_id == item_id), None)
            
            if not existing_item and len(self.items) >= self.capacity:
                return False
                
        # Check weight constraint
        if self.weight_limit is not None:
            # Need to get the item weight
            for inv_item in self.items:
                if inv_item.item_id == item_id:
                    new_weight = self.calculate_total_weight() + (inv_item.item.weight * quantity)
                    return new_weight <= self.weight_limit
                    
        return True

class InventoryItem(db.Model):
    """Model representing an item in an inventory with quantity and position."""
    __tablename__ = 'inventory_items'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inventory_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('inventories.id'), nullable=False)
    item_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('items.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    position: Mapped[dict] = mapped_column(JSON)  # For grid-based inventories
    is_equipped: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    inventory = relationship('Inventory', back_populates='items')
    item = relationship('Item')

    def to_dict(self):
        """Convert the inventory item to a dictionary."""
        return {
            'id': self.id,
            'inventory_id': self.inventory_id,
            'item': self.item.to_dict(),
            'quantity': self.quantity,
            'position': self.position,
            'is_equipped': self.is_equipped
        } 