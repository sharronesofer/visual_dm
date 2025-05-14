"""
Database models for inventory management.
"""

from app.core.database import db
from datetime import datetime

class Item(db.Model):
    """Model representing an item that can be stored in inventories."""
    __tablename__ = 'items'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    item_type = db.Column(db.String(50), nullable=False)
    rarity = db.Column(db.String(50), default='common')
    value = db.Column(db.Integer, default=0)
    weight = db.Column(db.Float, default=0.0)
    properties = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert the item to a dictionary."""
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
    """Model representing an inventory that can hold items."""
    __tablename__ = 'inventories'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, nullable=False)
    owner_type = db.Column(db.String(50), nullable=False)  # 'character', 'npc', 'container', etc.
    capacity = db.Column(db.Integer)  # Maximum number of items, null means unlimited
    weight_limit = db.Column(db.Float)  # Maximum weight, null means unlimited
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('InventoryItem', back_populates='inventory', lazy='dynamic')

    def to_dict(self):
        """Convert the inventory to a dictionary."""
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'owner_type': self.owner_type,
            'capacity': self.capacity,
            'weight_limit': self.weight_limit,
            'items': [item.to_dict() for item in self.items]
        }

class InventoryItem(db.Model):
    """Model representing an item in an inventory with quantity and position."""
    __tablename__ = 'inventory_items'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventories.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    position = db.Column(db.JSON)  # For grid-based inventories
    is_equipped = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    inventory = db.relationship('Inventory', back_populates='items')
    item = db.relationship('Item')

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