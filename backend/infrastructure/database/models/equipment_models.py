"""
Equipment Database Models

SQLAlchemy models for the equipment system persistence layer.
Maps business domain models to database tables.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Import Base from the database infrastructure
try:
    from backend.infrastructure.shared.database.base import Base, BaseModel, UUIDMixin, TimestampMixin
except ImportError:
    # Fallback if shared doesn't exist
    from backend.infrastructure.database import Base
    from sqlalchemy.orm import declarative_base
    
    if Base is None:
        Base = declarative_base()
    
    class BaseModel(Base):
        """Base model with common fields."""
        __abstract__ = True
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# Association table for equipment magical effects (many-to-many)
equipment_effects_association = Table(
    'equipment_magical_effects',
    Base.metadata,
    Column('equipment_id', UUID(as_uuid=True), ForeignKey('equipment_instances.id'), primary_key=True),
    Column('effect_id', UUID(as_uuid=True), ForeignKey('magical_effects.id'), primary_key=True),
    Column('power_level', Integer, default=50),
    Column('applied_at', DateTime(timezone=True), server_default=func.now())
)


class EquipmentTemplate(BaseModel):
    """Equipment template/base type database model"""
    __tablename__ = 'equipment_templates'
    
    # Template identification
    template_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Equipment categorization
    item_type = Column(String(50), nullable=False, index=True)  # weapon, armor, accessory, tool
    quality_tier = Column(String(20), nullable=False, default='basic')  # basic, military, mastercraft
    rarity = Column(String(20), default='common')  # common, rare, epic, legendary
    
    # Base properties
    base_value = Column(Integer, nullable=False, default=100)
    weight = Column(Float, default=1.0)
    durability_multiplier = Column(Float, default=1.0)
    
    # Base stats as JSON
    base_stats = Column(JSONB, default=lambda: {})
    
    # Equipment slots this can be equipped to
    equipment_slots = Column(JSONB, default=lambda: [])  # ["main_hand", "off_hand", etc.]
    
    # Abilities and properties
    abilities = Column(JSONB, default=lambda: [])
    compatible_enchantments = Column(JSONB, default=lambda: [])
    thematic_tags = Column(JSONB, default=lambda: [])
    restrictions = Column(JSONB, default=lambda: {})
    
    # Visual and lore
    material = Column(String(100))
    visual_description = Column(Text)
    lore_text = Column(Text)
    
    # Crafting information
    crafting_requirements = Column(JSONB)
    
    def __repr__(self):
        return f"<EquipmentTemplate(template_id='{self.template_id}', name='{self.name}')>"


class EquipmentInstance(BaseModel):
    """Individual equipment instance database model"""
    __tablename__ = 'equipment_instances'
    
    # Template reference
    template_id = Column(String(100), ForeignKey('equipment_templates.template_id'), nullable=False)
    template = relationship("EquipmentTemplate", backref="instances")
    
    # Ownership
    owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Character UUID
    
    # Instance-specific properties
    quality_tier = Column(String(20), nullable=False, default='basic')
    custom_name = Column(String(200))
    
    # Condition tracking
    durability = Column(Float, nullable=False, default=100.0)
    max_durability = Column(Float, nullable=False, default=100.0)
    
    # Equipment state
    is_equipped = Column(Boolean, default=False)
    equipped_slot = Column(String(50))  # main_hand, off_hand, chest, etc.
    
    # Usage tracking
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True))
    total_usage_hours = Column(Float, default=0.0)
    
    # Instance-specific stats (modifications from base)
    stat_modifiers = Column(JSONB, default=lambda: {})
    
    # Magical effects relationship
    magical_effects = relationship(
        "MagicalEffect",
        secondary=equipment_effects_association,
        back_populates="equipment_instances"
    )
    
    def __repr__(self):
        return f"<EquipmentInstance(id='{self.id}', template='{self.template_id}', owner='{self.owner_id}')>"


class MagicalEffect(BaseModel):
    """Magical effect database model"""
    __tablename__ = 'magical_effects'
    
    # Effect identification
    effect_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Effect categorization
    effect_type = Column(String(50), nullable=False)  # stat_bonus, damage_bonus, resistance, etc.
    school = Column(String(50))  # enchantment, evocation, etc.
    rarity = Column(String(20), default='common')
    
    # Effect properties
    base_power = Column(Integer, default=50)
    scaling_type = Column(String(20), default='linear')
    
    # Effect parameters as JSON
    parameters = Column(JSONB, default=lambda: {})
    
    # Requirements and restrictions
    min_quality_tier = Column(String(20), default='basic')
    compatible_item_types = Column(JSONB, default=lambda: [])
    
    # Equipment instances that have this effect
    equipment_instances = relationship(
        "EquipmentInstance",
        secondary=equipment_effects_association,
        back_populates="magical_effects"
    )
    
    def __repr__(self):
        return f"<MagicalEffect(effect_id='{self.effect_id}', name='{self.name}')>"


class CharacterEquipmentSlot(BaseModel):
    """Character equipment slot assignments"""
    __tablename__ = 'character_equipment_slots'
    
    # Character identification
    character_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Slot information
    slot_name = Column(String(50), nullable=False)  # main_hand, off_hand, chest, etc.
    
    # Equipped item
    equipment_id = Column(UUID(as_uuid=True), ForeignKey('equipment_instances.id'), nullable=True)
    equipment = relationship("EquipmentInstance", backref="equipped_slot_assignments")
    
    # Timestamp tracking
    equipped_at = Column(DateTime(timezone=True))
    
    # Unique constraint: one character can only have one item per slot
    __table_args__ = (
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<CharacterEquipmentSlot(character='{self.character_id}', slot='{self.slot_name}')>"


class EquipmentMaintenanceRecord(BaseModel):
    """Equipment maintenance and durability history"""
    __tablename__ = 'equipment_maintenance_records'
    
    # Equipment reference
    equipment_id = Column(UUID(as_uuid=True), ForeignKey('equipment_instances.id'), nullable=False)
    equipment = relationship("EquipmentInstance", backref="maintenance_records")
    
    # Maintenance event
    event_type = Column(String(50), nullable=False)  # repair, degradation, usage, etc.
    event_description = Column(Text)
    
    # Durability changes
    durability_before = Column(Float, nullable=False)
    durability_after = Column(Float, nullable=False)
    durability_change = Column(Float, nullable=False)
    
    # Event context
    cause = Column(String(100))  # combat, usage, environment, repair, etc.
    location = Column(String(200))
    event_data = Column(JSONB, default=lambda: {})
    
    # Cost information (for repairs)
    cost_paid = Column(Integer, default=0)
    materials_used = Column(JSONB, default=lambda: [])
    
    def __repr__(self):
        return f"<EquipmentMaintenanceRecord(equipment='{self.equipment_id}', type='{self.event_type}')>"


class QualityTier(BaseModel):
    """Quality tier definitions"""
    __tablename__ = 'quality_tiers'
    
    # Tier identification
    tier_name = Column(String(20), unique=True, nullable=False, primary_key=True)
    display_name = Column(String(50), nullable=False)
    description = Column(Text)
    
    # Durability properties
    durability_weeks = Column(Integer, nullable=False, default=1)  # weeks of daily use
    degradation_rate = Column(Float, default=1.0)
    
    # Value and enchantment properties
    value_multiplier = Column(Float, default=1.0)
    enchantment_capacity = Column(Integer, default=5)
    max_enchantment_power = Column(Integer, default=75)
    
    # Visual properties
    color_code = Column(String(10))  # hex color for UI
    rarity_weight = Column(Float, default=1.0)
    
    def __repr__(self):
        return f"<QualityTier(tier='{self.tier_name}', weeks='{self.durability_weeks}')>"


# Indexes for performance
from sqlalchemy import Index

# Equipment instances indexes
Index('ix_equipment_instances_owner_equipped', 
      EquipmentInstance.owner_id, EquipmentInstance.is_equipped)
Index('ix_equipment_instances_template_quality', 
      EquipmentInstance.template_id, EquipmentInstance.quality_tier)

# Character equipment slots indexes  
Index('ix_character_equipment_slots_character_slot', 
      CharacterEquipmentSlot.character_id, CharacterEquipmentSlot.slot_name, unique=True)

# Maintenance records indexes
Index('ix_equipment_maintenance_created', 
      EquipmentMaintenanceRecord.equipment_id, EquipmentMaintenanceRecord.created_at) 