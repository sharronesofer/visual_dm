"""
Magic model definitions.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Integer, String, JSON, DateTime, ForeignKey, Text, Float, Boolean, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel
import enum

class MagicType(enum.Enum):
    ELEMENTAL = "elemental"
    ARCANE = "arcane"
    DIVINE = "divine"
    DARK = "dark"
    LIGHT = "light"

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