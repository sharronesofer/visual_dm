from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Text
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from enum import Enum as PyEnum

from app.extensions import db

class ItemCategory(db.Model):
    __tablename__ = 'item_categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text)
    types = relationship('ItemType', backref='category', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ItemCategory {self.name}>'

class ItemType(db.Model):
    __tablename__ = 'item_types'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey('item_categories.id'), nullable=False)
    templates = relationship('BaseItemTemplate', backref='type', cascade='all, delete-orphan')
    items = relationship('Item', backref='type')

    def __repr__(self):
        return f'<ItemType {self.name}>'

class BaseItemTemplate(db.Model):
    __tablename__ = 'base_item_templates'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    type_id = Column(Integer, ForeignKey('item_types.id'), nullable=False)
    base_stats = Column(JSON, nullable=False, default={})
    description = Column(Text)
    items = relationship('Item', backref='base_template')

    def __repr__(self):
        return f'<BaseItemTemplate {self.name}>'

class Item(db.Model):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    type_id = Column(Integer, ForeignKey('item_types.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('item_categories.id'), nullable=False)
    base_template_id = Column(Integer, ForeignKey('base_item_templates.id'))
    base_stats = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    durability = Column(Integer, default=100)
    max_durability = Column(Integer, default=100)
    usage_count = Column(Integer, default=0)
    enhancement_level = Column(Integer, default=0)

    category = relationship('ItemCategory', backref=backref('items', lazy='dynamic'))

    def __repr__(self):
        return f'<Item {self.name}>'

class PropertyDefinition(db.Model):
    __tablename__ = 'property_definitions'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text)
    data_type = Column(String(32), nullable=False)
    default_value = Column(String(128))
    allowed_values = Column(JSON, default=list)
    formula = Column(Text)
    properties = relationship('ItemProperty', backref='property_definition', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<PropertyDefinition {self.name}>'

class ItemProperty(db.Model):
    __tablename__ = 'item_properties'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    property_id = Column(Integer, ForeignKey('property_definitions.id'), nullable=False)
    value = Column(String(128))  # Store as string, convert as needed
    is_active = Column(Integer, default=1)  # 1 = True, 0 = False
    condition = Column(Text)  # Optional: JSON or expression for conditional activation

    item = relationship('Item', backref=backref('properties', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<ItemProperty item_id={self.item_id} property_id={self.property_id}>'

class Rarity(PyEnum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class EnchantmentType(db.Model):
    __tablename__ = 'enchantment_types'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text)
    allowed_effects = Column(JSON, default=list)
    enchantments = relationship('ItemEnchantment', backref='enchantment_type')

    def __repr__(self):
        return f'<EnchantmentType {self.name}>'

class MagicalEffect(db.Model):
    __tablename__ = 'magical_effects'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text)
    effect_type = Column(String(64))
    magnitude_range = Column(JSON, default=list)  # [min, max]
    scaling_formula = Column(Text)
    enchantments = relationship('ItemEnchantment', backref='magical_effect')

    def __repr__(self):
        return f'<MagicalEffect {self.name}>'

class ItemEnchantment(db.Model):
    __tablename__ = 'item_enchantments'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    enchantment_type_id = Column(Integer, ForeignKey('enchantment_types.id'), nullable=False)
    effect_id = Column(Integer, ForeignKey('magical_effects.id'), nullable=False)
    magnitude = Column(Integer)
    rarity = Column(String(16), nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow)

    item = relationship('Item', backref=backref('enchantments', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<ItemEnchantment item_id={self.item_id} effect_id={self.effect_id} rarity={self.rarity}>'

class ItemHistory(db.Model):
    __tablename__ = 'item_histories'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    owner_id = Column(Integer, nullable=True)
    event_type = Column(String(64), nullable=False)
    event_data = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)
    enhancement_event_type = Column(String(32))
    materials_used = Column(JSON, default=list)

    item = relationship('Item', backref=backref('history', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<ItemHistory item_id={self.item_id} event_type={self.event_type}>'

class ItemEvent(db.Model):
    __tablename__ = 'item_events'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    event_type = Column(String(64), nullable=False)
    description = Column(Text)
    occurred_at = Column(DateTime, default=datetime.utcnow)

    item = relationship('Item', backref=backref('events', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<ItemEvent item_id={self.item_id} event_type={self.event_type}>'

class EnhancementMaterial(db.Model):
    __tablename__ = 'enhancement_materials'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text)
    effect = Column(Text)
    rarity = Column(String(16), nullable=False)

    def __repr__(self):
        return f'<EnhancementMaterial {self.name}>' 