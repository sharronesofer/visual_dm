"""
Spell model definitions.
"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, JSON, DateTime, Boolean, Float, ForeignKey
from datetime import datetime
from app.core.database import db

class SpellSchool(db.Model):
    """Spell school model for categorizing spells."""
    __tablename__ = 'spell_schools'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(500))
    color: Mapped[str] = mapped_column(String(20), default='#FFFFFF')
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert spell school to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Spellbook(db.Model):
    """Spellbook model for storing known spells."""
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
            'spells': self.spells
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
            
        for i, spell in enumerate(self.spells['spells']):
            if spell.get('id') == spell_id:
                self.spells['spells'].pop(i)
                self.updated_at = datetime.utcnow()
                return True
        return False

class SpellComponent(db.Model):
    """Spell component model for spell requirements."""
    __tablename__ = 'spell_components'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    spell_id: Mapped[int] = mapped_column(Integer, nullable=False)
    component_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'verbal', 'somatic', 'material'
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    material_cost: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert spell component to dictionary."""
        return {
            'id': self.id,
            'spell_id': self.spell_id,
            'component_type': self.component_type,
            'description': self.description,
            'material_cost': self.material_cost,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class SpellEffect(db.Model):
    """Spell effect model for tracking active spell effects."""
    __tablename__ = 'spell_effects'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    spell_id: Mapped[int] = mapped_column(Integer, ForeignKey('spells.id'), nullable=False)
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