"""
Magic system models.

This module contains all models related to the magic system, including
spells, magic abilities, schools, and related components.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Integer, String, JSON, DateTime, ForeignKey, Text, Float, Boolean, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel
import enum

# ================ Magic Enums ================

class MagicType(enum.Enum):
    """Types of magic abilities."""
    ELEMENTAL = "elemental"
    ARCANE = "arcane"
    DIVINE = "divine"
    DARK = "dark"
    LIGHT = "light"

class MagicSchool(enum.Enum):
    """Schools of magic for spells."""
    FIRE = "fire"
    WATER = "water"
    EARTH = "earth"
    AIR = "air"
    ARCANE = "arcane"
    DIVINE = "divine"

class ComponentType(enum.Enum):
    """Types of spell components."""
    VERBAL = "verbal"
    SOMATIC = "somatic"
    MATERIAL = "material"

class EffectType(enum.Enum):
    """Types of spell effects."""
    DAMAGE = "damage"
    HEALING = "healing"
    BUFF = "buff"
    DEBUFF = "debuff"
    CONTROL = "control"
    UTILITY = "utility"

# ================ Magic Models ================

class MagicModel(BaseModel):
    """
    Model for magic abilities in the game.
    
    Fields:
        id (int): Primary key.
        name (str): Magic ability name.
        description (str): Description of the ability.
        magic_type (MagicType): Type of magic.
        power (float): Power of the ability.
        cost (float): Cost to use the ability.
        effects (dict): Effects of the ability.
        requirements (dict): Requirements to use the ability.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        owner_id (int): Foreign key to character owner.
        owner (Character): Related character.
    """
    __tablename__ = 'magic_abilities'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, doc="Primary key.")
    name: Mapped[str] = mapped_column(String(100), nullable=False, doc="Magic ability name.")
    description: Mapped[Optional[str]] = mapped_column(Text, doc="Description of the ability.")
    magic_type: Mapped[MagicType] = mapped_column(Enum(MagicType), default=MagicType.ARCANE, doc="Type of magic.")
    power: Mapped[float] = mapped_column(Float, default=0.0, doc="Power of the ability.")
    cost: Mapped[float] = mapped_column(Float, default=0.0, doc="Cost to use the ability.")
    effects: Mapped[dict] = mapped_column(JSON, default=dict, doc="Effects of the ability.")
    requirements: Mapped[dict] = mapped_column(JSON, default=dict, doc="Requirements to use the ability.")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, doc="Creation timestamp.")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, doc="Last update timestamp.")

    owner_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('characters.id'), doc="Foreign key to character owner.")
    owner: Mapped[Optional['Character']] = relationship('Character', back_populates='magic_abilities')

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the magic ability to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "magic_type": self.magic_type.value if self.magic_type else None,
            "power": self.power,
            "cost": self.cost,
            "effects": self.effects,
            "requirements": self.requirements,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "owner_id": self.owner_id
        }

class SpellModel(BaseModel):
    """
    Model for magic spells in the game.
    
    Fields:
        id (int): Primary key.
        name (str): Spell name.
        description (str): Spell description.
        school (MagicSchool): School of magic.
        mana_cost (float): Mana cost to cast the spell.
        power (float): Power of the spell.
        effects (dict): Effects of the spell.
        requirements (dict): Requirements to learn/cast the spell.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        owner_id (int): Foreign key to character owner.
        owner (Character): Related character.
    """
    __tablename__ = 'magic_spells'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, doc="Primary key.")
    name: Mapped[str] = mapped_column(String(100), nullable=False, doc="Spell name.")
    description: Mapped[Optional[str]] = mapped_column(Text, doc="Spell description.")
    school: Mapped[MagicSchool] = mapped_column(Enum(MagicSchool), default=MagicSchool.ARCANE, doc="School of magic.")
    mana_cost: Mapped[float] = mapped_column(Float, default=0.0, doc="Mana cost to cast the spell.")
    power: Mapped[float] = mapped_column(Float, default=0.0, doc="Power of the spell.")
    effects: Mapped[dict] = mapped_column(JSON, default=dict, doc="Effects of the spell.")
    requirements: Mapped[dict] = mapped_column(JSON, default=dict, doc="Requirements to learn/cast the spell.")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, doc="Creation timestamp.")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, doc="Last update timestamp.")

    owner_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('characters.id'), doc="Foreign key to character owner.")
    owner: Mapped[Optional['Character']] = relationship('Character', back_populates='magic_spells')

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the magic spell to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "school": self.school.value if self.school else None,
            "mana_cost": self.mana_cost,
            "power": self.power,
            "effects": self.effects,
            "requirements": self.requirements,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "owner_id": self.owner_id
        }

# ================ Spell Management Models ================

class SpellSlot(db.Model):
    """
    Spell slot model for tracking available spell slots.
    
    Used to track a character's spell casting resources.
    """
    __tablename__ = 'spell_slots'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    character_id: Mapped[int] = mapped_column(Integer, nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[int] = mapped_column(Integer, nullable=False)
    used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert spell slot to dictionary."""
        return {
            'id': self.id,
            'character_id': self.character_id,
            'level': self.level,
            'total': self.total,
            'used': self.used,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def use_slot(self) -> bool:
        """Use a spell slot if available."""
        if self.used < self.total:
            self.used += 1
            self.updated_at = datetime.utcnow()
            return True
        return False

    def restore_slot(self) -> bool:
        """Restore a used spell slot."""
        if self.used > 0:
            self.used -= 1
            self.updated_at = datetime.utcnow()
            return True
        return False

class Spellbook(db.Model):
    """
    Spellbook model for storing known spells.
    
    Represents a collection of spells known by a character or NPC.
    """
    __tablename__ = 'spellbooks'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(Integer, nullable=False)
    owner_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'character', 'npc'
    spells: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert spellbook to dictionary."""
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'owner_type': self.owner_type,
            'spells': self.spells,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def add_spell(self, spell: dict) -> bool:
        """Add spell to spellbook."""
        if 'spells' not in self.spells:
            self.spells['spells'] = []
            
        # Check if spell already exists
        if any(s.get('id') == spell.get('id') for s in self.spells.get('spells', [])):
            return False
            
        self.spells['spells'].append(spell)
        self.updated_at = datetime.utcnow()
        return True

    def remove_spell(self, spell_id: int) -> bool:
        """Remove spell from spellbook."""
        if 'spells' not in self.spells:
            return False
            
        initial_length = len(self.spells['spells'])
        self.spells['spells'] = [s for s in self.spells['spells'] if s.get('id') != spell_id]
        
        if len(self.spells['spells']) < initial_length:
            self.updated_at = datetime.utcnow()
            return True
        return False

class SpellComponent(db.Model):
    """
    Spell component model for spell requirements.
    
    Represents the physical, verbal, or material components needed for spells.
    """
    __tablename__ = 'spell_components'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    spell_id: Mapped[int] = mapped_column(Integer, nullable=False)
    component_type: Mapped[ComponentType] = mapped_column(Enum(ComponentType), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    material_cost: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert spell component to dictionary."""
        return {
            'id': self.id,
            'spell_id': self.spell_id,
            'component_type': self.component_type.value if self.component_type else None,
            'description': self.description,
            'material_cost': self.material_cost,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class SpellEffect(db.Model):
    """
    Spell effect model for tracking active spell effects.
    
    Represents the ongoing effects of a spell on a target.
    """
    __tablename__ = 'spell_effects'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    spell_id: Mapped[int] = mapped_column(Integer, ForeignKey('magic_spells.id'), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)  # character, npc, etc.
    duration: Mapped[int] = mapped_column(Integer, nullable=False)  # in rounds
    remaining_duration: Mapped[int] = mapped_column(Integer, nullable=False)
    effects: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert spell effect to dictionary."""
        return {
            'id': self.id,
            'spell_id': self.spell_id,
            'target_id': self.target_id,
            'target_type': self.target_type,
            'duration': self.duration,
            'remaining_duration': self.remaining_duration,
            'effects': self.effects,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 