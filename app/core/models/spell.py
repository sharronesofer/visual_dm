"""
Consolidated Spell and SpellEffect models.
Provides a single authoritative definition for spells and their effects in the game.
"""

from typing import Dict, Any, List, Optional, Union
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Float, Boolean, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel
import enum

class SpellType(enum.Enum):
    OFFENSIVE = "offensive"
    DEFENSIVE = "defensive"
    UTILITY = "utility"
    HEALING = "healing"

class Spell(BaseModel):
    """
    Model for spells in the game.
    Fields:
        id (int): Primary key.
        name (str): Spell name.
        description (str): Spell description.
        spell_type (SpellType): Type of spell.
        mana_cost (float): Mana cost to cast the spell.
        cooldown (float): Cooldown in seconds.
        effects (dict): Effects of the spell.
        requirements (dict): Requirements to learn/cast the spell.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        owner_id (int): Foreign key to character owner.
        owner (Character): Related character.
    """
    __tablename__ = 'spells'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, doc="Primary key.")
    name: Mapped[str] = mapped_column(String(100), nullable=False, doc="Spell name.")
    description: Mapped[Optional[str]] = mapped_column(Text, doc="Spell description.")
    spell_type: Mapped[SpellType] = mapped_column(Enum(SpellType), default=SpellType.UTILITY, doc="Type of spell.")
    mana_cost: Mapped[float] = mapped_column(Float, default=0.0, doc="Mana cost to cast the spell.")
    cooldown: Mapped[float] = mapped_column(Float, default=0.0, doc="Cooldown in seconds.")
    effects: Mapped[dict] = mapped_column(JSON, default=dict, doc="Effects of the spell.")
    requirements: Mapped[dict] = mapped_column(JSON, default=dict, doc="Requirements to learn/cast the spell.")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, doc="Creation timestamp.")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, doc="Last update timestamp.")

    owner_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('characters.id'), doc="Foreign key to character owner.")
    owner: Mapped[Optional['Character']] = relationship('Character', back_populates='spells')

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the spell to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "spell_type": self.spell_type.value if self.spell_type else None,
            "mana_cost": self.mana_cost,
            "cooldown": self.cooldown,
            "effects": self.effects,
            "requirements": self.requirements,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "owner_id": self.owner_id
        }

    def get_effects(self) -> List['SpellEffect']:
        """Get all effects associated with this spell."""
        return self.effects.get('effects', [])

    def get_requirements(self) -> Dict:
        """Get any requirements for casting this spell."""
        return self.requirements.get('requirements', {})

class SpellEffect(db.Model):
    """Model for spell effects in the game."""
    __tablename__ = 'spell_effects'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    spell_id = Column(Integer, ForeignKey('spells.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    type = Column(String(50), nullable=False)  # damage, healing, status, etc.
    duration = Column(String(50))
    magnitude = Column(Float, default=0.0)
    properties = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    spell = relationship('Spell', back_populates='effects')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.properties = kwargs.get('properties', {})

    def to_dict(self) -> Dict:
        """Convert spell effect to dictionary representation."""
        return {
            'id': self.id,
            'spell_id': self.spell_id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'duration': self.duration,
            'magnitude': self.magnitude,
            'properties': self.properties,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def apply(self, target: 'Character') -> Dict:
        """Apply this effect to a target."""
        result = {
            'success': True,
            'effect': self.name,
            'magnitude': self.magnitude,
            'duration': self.duration
        }

        if self.type == 'damage':
            target.take_damage(self.magnitude)
        elif self.type == 'healing':
            target.heal(self.magnitude)
        elif self.type == 'status':
            target.add_status_effect(self.name, self.duration)

        return result

    def get_modifiers(self) -> Dict:
        """Get any modifiers this effect applies."""
        return self.properties.get('modifiers', {})

    def get_conditions(self) -> List[str]:
        """Get any conditions this effect applies."""
        return self.properties.get('conditions', []) 