"""
Consolidated Spell and SpellEffect models.
Provides a single authoritative definition for spells and their effects in the game.
"""

from typing import Dict, Any, List, Optional, Union
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel

class Spell(BaseModel):
    """Model for spells in the game."""
    __tablename__ = 'spells'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    school = Column(String(50), nullable=False)  # evocation, necromancy, etc.
    level = Column(Integer, default=0)
    casting_time = Column(String(50))
    range = Column(String(50))
    components = Column(JSON, default=dict)  # verbal, somatic, material
    duration = Column(String(50))
    concentration = Column(Boolean, default=False)
    ritual = Column(Boolean, default=False)
    properties = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    effects = relationship('SpellEffect', back_populates='spell')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.components = kwargs.get('components', {})
        self.properties = kwargs.get('properties', {})

    def to_dict(self) -> Dict:
        """Convert spell to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'school': self.school,
            'level': self.level,
            'casting_time': self.casting_time,
            'range': self.range,
            'components': self.components,
            'duration': self.duration,
            'concentration': self.concentration,
            'ritual': self.ritual,
            'properties': self.properties,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def get_effects(self) -> List['SpellEffect']:
        """Get all effects associated with this spell."""
        return self.effects

    def get_requirements(self) -> Dict:
        """Get any requirements for casting this spell."""
        return self.properties.get('requirements', {})

class SpellEffect(db.Model):
    """Model for spell effects in the game."""
    __tablename__ = 'spell_effects'

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