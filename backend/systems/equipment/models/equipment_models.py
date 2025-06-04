"""
Equipment SQLAlchemy models for Visual DM.

This module defines the database models for equipment instances while
equipment templates remain in JSON configuration files.

Hybrid Pattern:
- Templates (JSON): Static definitions of equipment types, enchantments, quality tiers
- Instances (Database): Individual equipment owned by characters with unique state
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import uuid4
from enum import Enum

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

Base = declarative_base()

class EquipmentSlot(Enum):
    """
    Equipment slot types according to Development Bible standard
    """
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    CHEST = "chest"
    PANTS = "pants"
    BOOTS = "boots"
    GLOVES = "gloves"
    HAT = "hat"
    RING_1 = "ring_1"
    RING_2 = "ring_2"
    AMULET = "amulet"
    EARRING_1 = "earring_1"
    EARRING_2 = "earring_2"

class EquipmentInstance(Base):
    """
    Individual equipment instance owned by a character.
    
    References a template_id from JSON configuration for base properties,
    but maintains its own unique state (durability, enchantments, etc.)
    """
    __tablename__ = "equipment_instances"
    
    # Primary identification
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    template_id = Column(String, nullable=False, index=True)  # References JSON template
    
    # Ownership and location
    owner_id = Column(String, ForeignKey("characters.id"), index=True)
    is_equipped = Column(Boolean, default=False)
    equipment_slot = Column(String)  # main_hand, off_hand, chest, etc.
    location = Column(String, default="inventory")  # inventory, equipped, storage, etc.
    
    # Instance-specific state
    durability = Column(Float, default=100.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_repaired = Column(DateTime)
    
    # Customization
    custom_name = Column(String)  # Player-given name like "Bob's Lucky Sword"
    custom_description = Column(Text)  # Player notes
    
    # Calculated values (cached for performance)
    current_value = Column(Integer)  # Based on template + condition + enchantments
    identification_level = Column(Integer, default=0)  # How much player knows about item
    
    # Relationships
    applied_enchantments = relationship("AppliedEnchantment", back_populates="equipment", 
                                       cascade="all, delete-orphan")
    maintenance_history = relationship("MaintenanceRecord", back_populates="equipment",
                                     cascade="all, delete-orphan")
    
    # JSON field for flexible additional data
    custom_metadata = Column(JSON, default=dict)  # For custom properties, quest flags, etc.
    
    @validates('durability')
    def validate_durability(self, key, durability):
        """Ensure durability stays within valid range."""
        return max(0.0, min(100.0, durability))
    
    @validates('identification_level')
    def validate_identification_level(self, key, level):
        """Ensure identification level is non-negative."""
        return max(0, level)
    
    def get_durability_status(self) -> str:
        """Get human-readable durability status."""
        if self.durability >= 90:
            return "excellent"
        elif self.durability >= 75:
            return "good"
        elif self.durability >= 50:
            return "worn"
        elif self.durability >= 25:
            return "damaged"
        elif self.durability > 0:
            return "very_damaged"
        else:
            return "broken"
    
    def is_functional(self) -> bool:
        """Check if equipment provides any benefits."""
        return self.durability > 0.0
    
    def __repr__(self):
        name = self.custom_name or f"Equipment({self.template_id})"
        return f"<EquipmentInstance(id='{self.id}', name='{name}', durability={self.durability:.1f})>"


class AppliedEnchantment(Base):
    """
    Enchantment applied to a specific equipment instance.
    
    References enchantment_id from JSON configuration for base properties,
    but tracks instance-specific power level and application details.
    """
    __tablename__ = "applied_enchantments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    equipment_instance_id = Column(String, ForeignKey("equipment_instances.id"), nullable=False)
    enchantment_id = Column(String, nullable=False, index=True)  # References JSON definition
    
    # Instance-specific enchantment state
    power_level = Column(Integer, default=100)  # 1-100% of full power
    applied_at = Column(DateTime, default=datetime.utcnow)
    applied_by = Column(String)  # Character ID who applied the enchantment
    mastery_level = Column(Integer, default=1)  # Enchanter's mastery when applied
    
    # Enchantment condition
    stability = Column(Float, default=100.0)  # Can degrade over time or from use
    last_triggered = Column(DateTime)  # Last time enchantment effect activated
    
    # Relationships
    equipment = relationship("EquipmentInstance", back_populates="applied_enchantments")
    
    @validates('power_level')
    def validate_power_level(self, key, power):
        """Ensure power level stays within valid range."""
        return max(1, min(100, power))
    
    @validates('stability')
    def validate_stability(self, key, stability):
        """Ensure stability stays within valid range."""
        return max(0.0, min(100.0, stability))
    
    def is_active(self) -> bool:
        """Check if enchantment is still functional."""
        return self.stability > 0.0 and self.power_level > 0
    
    def __repr__(self):
        return f"<AppliedEnchantment(enchantment='{self.enchantment_id}', power={self.power_level}%)>"


class MaintenanceRecord(Base):
    """
    History of repairs and maintenance performed on equipment.
    
    Tracks equipment lifecycle for durability calculations and value assessment.
    """
    __tablename__ = "maintenance_records"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    equipment_instance_id = Column(String, ForeignKey("equipment_instances.id"), nullable=False)
    
    # Maintenance details
    action_type = Column(String, nullable=False)  # repair, enchant, upgrade, clean, etc.
    performed_at = Column(DateTime, default=datetime.utcnow)
    performed_by = Column(String)  # Character or NPC ID
    
    # Before/after state
    durability_before = Column(Float)
    durability_after = Column(Float)
    
    # Cost and materials
    gold_cost = Column(Integer, default=0)
    materials_used = Column(JSON, default=list)  # List of material IDs and quantities
    
    # Success/failure
    success = Column(Boolean, default=True)
    notes = Column(Text)  # Reason for failure, special outcomes, etc.
    
    # Relationships
    equipment = relationship("EquipmentInstance", back_populates="maintenance_history")
    
    def durability_change(self) -> float:
        """Calculate the durability change from this maintenance."""
        if self.durability_before is None or self.durability_after is None:
            return 0.0
        return self.durability_after - self.durability_before
    
    def __repr__(self):
        return f"<MaintenanceRecord(action='{self.action_type}', success={self.success})>"


class EquipmentSet(Base):
    """
    Dynamic equipment sets discovered through AI semantic analysis.
    
    Unlike templates, these are discovered relationships between equipment instances
    based on thematic similarity and player equipment choices.
    """
    __tablename__ = "equipment_sets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # AI-generated thematic data
    thematic_tags = Column(JSON, default=list)  # ["fire", "dragon", "magical"]
    discovered_at = Column(DateTime, default=datetime.utcnow)
    
    # Set bonus configuration (could also reference JSON templates)
    set_bonuses = Column(JSON, default=dict)  # {2: {...}, 4: {...}, 6: {...}}
    
    # Activation tracking
    active_for_characters = Column(JSON, default=list)  # Character IDs with active set
    
    def __repr__(self):
        return f"<EquipmentSet(name='{self.name}', tags={len(self.thematic_tags)})>"


class CharacterEquipmentProfile(Base):
    """
    Character-specific equipment preferences and statistics.
    
    Tracks equipment usage patterns for AI-driven recommendations.
    """
    __tablename__ = "character_equipment_profiles"
    
    character_id = Column(String, primary_key=True)  # One profile per character
    
    # Equipment preferences learned from usage
    preferred_weapon_types = Column(JSON, default=list)
    preferred_armor_types = Column(JSON, default=list)
    preferred_enchantment_schools = Column(JSON, default=list)
    
    # Usage statistics
    total_equipment_owned = Column(Integer, default=0)
    total_enchantments_applied = Column(Integer, default=0)
    total_repairs_performed = Column(Integer, default=0)
    
    # Economic data
    total_gold_spent_equipment = Column(Integer, default=0)
    average_equipment_value = Column(Float, default=0.0)
    
    # Behavioral patterns
    repair_frequency = Column(Float, default=0.0)  # Repairs per week
    upgrade_frequency = Column(Float, default=0.0)  # New equipment per week
    
    # Profile metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def update_statistics(self, equipment_instances: List[EquipmentInstance]):
        """Update profile statistics based on current equipment."""
        self.total_equipment_owned = len(equipment_instances)
        if equipment_instances:
            self.average_equipment_value = sum(
                eq.current_value or 0 for eq in equipment_instances
            ) / len(equipment_instances)
        self.last_updated = datetime.utcnow()
    
    def __repr__(self):
        return f"<CharacterEquipmentProfile(character='{self.character_id}', items={self.total_equipment_owned})>" 