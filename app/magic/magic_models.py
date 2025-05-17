"""
Magic model definitions.
"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, JSON, DateTime, Boolean, Float
from datetime import datetime
from app.core.database import db

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