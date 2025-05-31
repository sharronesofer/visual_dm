"""
Magic System Models - D&D Compliant Implementation

This module defines comprehensive D&D magic system models including:
- Traditional magic schools (Abjuration, Conjuration, etc.)
- Spell slots and preparation mechanics
- Spellbook management
- Concentration and duration tracking
- Spell components system
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from backend.infrastructure.shared.database import Base, BaseModel as SharedBaseModel

# D&D Magic Schools Enum
class MagicSchool(str, Enum):
    """Traditional D&D Magic Schools"""
    ABJURATION = "abjuration"
    CONJURATION = "conjuration" 
    DIVINATION = "divination"
    ENCHANTMENT = "enchantment"
    EVOCATION = "evocation"
    ILLUSION = "illusion"
    NECROMANCY = "necromancy"
    TRANSMUTATION = "transmutation"

class SpellLevel(int, Enum):
    """Spell levels 0-9"""
    CANTRIP = 0
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5
    SIXTH = 6
    SEVENTH = 7
    EIGHTH = 8
    NINTH = 9

class SpellComponent(str, Enum):
    """Spell components"""
    VERBAL = "verbal"
    SOMATIC = "somatic"
    MATERIAL = "material"

class SpellDuration(str, Enum):
    """Spell duration types"""
    INSTANTANEOUS = "instantaneous"
    CONCENTRATION = "concentration"
    TIMED = "timed"
    PERMANENT = "permanent"

# SQLAlchemy Models
class Spell(Base):
    """Core spell definition"""
    __tablename__ = "spells"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    school = Column(String(50), nullable=False, index=True)
    level = Column(Integer, nullable=False, index=True)
    casting_time = Column(String(100), nullable=False)
    range = Column(String(100), nullable=False)
    components = Column(ARRAY(String), nullable=False)
    duration = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    higher_levels = Column(Text)
    material_components = Column(Text)
    ritual = Column(Boolean, default=False)
    concentration = Column(Boolean, default=False)
    damage_type = Column(String(50))
    save_type = Column(String(50))
    
    # Relationships
    component_requirements = relationship("SpellComponentRequirement", back_populates="spell")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)



class SpellPreparation(Base):
    """Daily spell preparation tracking"""
    __tablename__ = "spell_preparations"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    character_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("characters.id"), nullable=False)
    preparation_date = Column(DateTime, default=datetime.utcnow)
    preparation_data = Column(JSONB, default=dict)  # Stores prepared spell details
    created_at = Column(DateTime, default=datetime.utcnow)

class SpellComponentRequirement(Base):
    """Spell component requirements"""
    __tablename__ = "spell_component_requirements"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    spell_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("spells.id"), nullable=False)
    component_type = Column(String(50), nullable=False)  # verbal, somatic, material
    component_description = Column(Text)
    component_cost = Column(Float, default=0.0)
    consumed = Column(Boolean, default=False)
    
    # Relationships
    spell = relationship("Spell", back_populates="component_requirements")

class SpellDurationTracking(Base):
    """Enhanced spell duration tracking"""
    __tablename__ = "spell_duration_tracking"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    effect_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("active_spell_effects.id"), nullable=False)
    duration_type = Column(String(50), nullable=False)  # instantaneous, concentration, timed, permanent
    duration_value = Column(Integer)  # Duration in rounds/minutes/hours
    duration_unit = Column(String(20))  # rounds, minutes, hours, days
    remaining_duration = Column(Integer)
    
    # Relationships
    effect = relationship("ActiveSpellEffect", back_populates="duration_tracking")


class Character(Base):
    """Character model for magic system"""
    __tablename__ = "characters"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    level = Column(Integer, default=1)
    spellcasting_ability = Column(String(50))
    spell_attack_bonus = Column(Integer, default=0)
    spell_save_dc = Column(Integer, default=8)
    created_at = Column(DateTime, default=datetime.utcnow)

class Spellbook(Base):
    """Character spellbook"""
    __tablename__ = "spellbooks"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    character_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("characters.id"), nullable=False)
    name = Column(String(255), default="Spellbook")
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    known_spells = relationship("KnownSpell", back_populates="spellbook")
    prepared_spells = relationship("PreparedSpell", back_populates="spellbook")

class KnownSpell(Base):
    """Spells known by character"""
    __tablename__ = "known_spells"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    spellbook_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("spellbooks.id"), nullable=False)
    spell_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("spells.id"), nullable=False)
    learned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    spellbook = relationship("Spellbook", back_populates="known_spells")
    spell = relationship("Spell")

class PreparedSpell(Base):
    """Daily prepared spells"""
    __tablename__ = "prepared_spells"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    spellbook_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("spellbooks.id"), nullable=False)
    spell_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("spells.id"), nullable=False)
    prepared_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    spellbook = relationship("Spellbook", back_populates="prepared_spells")
    spell = relationship("Spell")

class SpellSlots(Base):
    """Character spell slots"""
    __tablename__ = "spell_slots"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    character_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("characters.id"), nullable=False)
    level = Column(Integer, nullable=False)
    total_slots = Column(Integer, nullable=False)
    used_slots = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)

class ActiveSpellEffect(Base):
    """Active spell effects with duration tracking"""
    __tablename__ = "active_spell_effects"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    character_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("characters.id"), nullable=False)
    spell_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("spells.id"), nullable=False)
    caster_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("characters.id"))
    cast_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    concentration = Column(Boolean, default=False)
    effect_data = Column(JSONB, default=dict)
    
    # Relationships
    spell = relationship("Spell")
    duration_tracking = relationship("SpellDurationTracking", back_populates="effect", uselist=False)

# Pydantic Models
class SpellResponse(BaseModel):
    """Spell response model"""
    id: UUID
    name: str
    school: str
    level: int
    casting_time: str
    range: str
    components: List[str]
    duration: str
    description: str
    higher_levels: Optional[str]
    material_components: Optional[str]
    ritual: bool
    concentration: bool
    damage_type: Optional[str]
    save_type: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)

class SpellbookResponse(BaseModel):
    """Spellbook response model"""
    id: UUID
    character_id: UUID
    name: str
    description: Optional[str]
    known_spells: List[SpellResponse]
    prepared_spells: List[SpellResponse]
    
    model_config = ConfigDict(from_attributes=True)

class SpellSlotsResponse(BaseModel):
    """Spell slots response model"""
    level: int
    total_slots: int
    used_slots: int
    remaining_slots: int
    
    @validator('remaining_slots', always=True)
    def calculate_remaining(cls, v, values):
        return values.get('total_slots', 0) - values.get('used_slots', 0)

class CastSpellRequest(BaseModel):
    """Request to cast a spell"""
    spell_id: UUID
    target_id: Optional[UUID] = None
    spell_level: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class PrepareSpellsRequest(BaseModel):
    """Request to prepare daily spells"""
    spell_ids: List[UUID]
