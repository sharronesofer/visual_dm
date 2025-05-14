"""
Status effect model for tracking effects on characters.
"""

from typing import Dict, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Enum, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum
from app.core.db_base import Base

class EffectType(enum.Enum):
    """Status effect type enumeration."""
    BUFF = "buff"
    DEBUFF = "debuff"
    CONDITION = "condition"
    DISEASE = "disease"
    POISON = "poison"
    CURSE = "curse"
    BLESSING = "blessing"

class StatusEffect(Base):
    """Status effect model representing an effect on a character."""
    __tablename__ = 'status_effects'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))
    type: Mapped[EffectType] = mapped_column(Enum(EffectType))
    target_id: Mapped[int] = mapped_column(ForeignKey('characters.id'))
    caster_id: Mapped[Optional[int]] = mapped_column(ForeignKey('characters.id'), nullable=True)
    duration: Mapped[int] = mapped_column(default=0)  # in rounds
    remaining_duration: Mapped[int] = mapped_column(default=0)
    potency: Mapped[float] = mapped_column(Float, default=1.0)
    effects: Mapped[Dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(nullable=True)
    character_id: Mapped[int] = mapped_column(ForeignKey('characters.id'))

    # Relationships
    target = relationship('Character', foreign_keys=[target_id], back_populates='status_effects')
    caster = relationship('Character', foreign_keys=[caster_id])
    character = relationship('Character', foreign_keys=[character_id])

    def __repr__(self) -> str:
        """String representation of the status effect."""
        return f"<StatusEffect {self.name} on character {self.target_id}>"

    def to_dict(self) -> Dict:
        """Convert status effect to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type.value,
            'target_id': self.target_id,
            'caster_id': self.caster_id,
            'character_id': self.character_id,
            'duration': self.duration,
            'remaining_duration': self.remaining_duration,
            'potency': self.potency,
            'effects': self.effects,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        } 