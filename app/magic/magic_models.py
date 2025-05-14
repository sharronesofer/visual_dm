"""
Magic model definitions.
"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, JSON, DateTime, Boolean, Float
from datetime import datetime
from app.core.database import db

class Spell(db.Model):
    """Spell model for storing spell definitions."""
    __tablename__ = 'spells'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    school: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'evocation', 'necromancy'
    casting_time: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., '1 action', '1 minute'
    range: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'touch', '60 feet'
    components: Mapped[dict] = mapped_column(JSON, default=dict)  # Verbal, somatic, material components
    duration: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'instantaneous', '1 hour'
    concentration: Mapped[bool] = mapped_column(Boolean, default=False)
    ritual: Mapped[bool] = mapped_column(Boolean, default=False)
    damage: Mapped[dict] = mapped_column(JSON, nullable=True)  # Damage type and dice
    effects: Mapped[dict] = mapped_column(JSON, default=dict)  # Spell effects
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert spell to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'level': self.level,
            'school': self.school,
            'casting_time': self.casting_time,
            'range': self.range,
            'components': self.components,
            'duration': self.duration,
            'concentration': self.concentration,
            'ritual': self.ritual,
            'damage': self.damage,
            'effects': self.effects,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class SpellSlot(db.Model):
    """Spell slot model for tracking available spell slots."""
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

class SpellEffect(db.Model):
    """Spell effect model for tracking active spell effects."""
    __tablename__ = 'spell_effects'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    character_id: Mapped[int] = mapped_column(Integer, nullable=False)
    spell_id: Mapped[int] = mapped_column(Integer, nullable=False)
    caster_id: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    end_time: Mapped[datetime] = mapped_column(nullable=True)
    concentration: Mapped[bool] = mapped_column(Boolean, default=False)
    effects: Mapped[dict] = mapped_column(JSON, default=dict)  # Active effects
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert spell effect to dictionary."""
        return {
            'id': self.id,
            'character_id': self.character_id,
            'spell_id': self.spell_id,
            'caster_id': self.caster_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'concentration': self.concentration,
            'effects': self.effects,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def update_effect(self, new_effects: dict) -> None:
        """Update spell effects."""
        self.effects.update(new_effects)
        self.updated_at = datetime.utcnow()

    def end_effect(self) -> None:
        """End the spell effect."""
        self.end_time = datetime.utcnow()
        self.updated_at = datetime.utcnow() 