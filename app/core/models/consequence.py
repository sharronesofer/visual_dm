"""
Consequence model for tracking punitive actions applied to players.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum, JSON, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import db
from app.core.models.base import BaseModel
from app.core.enums import InfractionSeverity
from sqlalchemy.dialects.postgresql import UUID
import enum

class ConsequenceType(enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class Consequence(BaseModel):
    """
    Model for consequences in the game.
    Fields:
        id (int): Primary key.
        description (str): Description of the consequence.
        consequence_type (ConsequenceType): Type of consequence.
        impact (dict): Impact details.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        related_event_id (int): Foreign key to related event.
        related_event (Event): Related event.
    """
    __tablename__ = 'consequences'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, doc="Primary key.")
    description: Mapped[Optional[str]] = mapped_column(Text, doc="Description of the consequence.")
    consequence_type: Mapped[ConsequenceType] = mapped_column(SQLEnum(ConsequenceType), default=ConsequenceType.NEUTRAL, doc="Type of consequence.")
    impact: Mapped[dict] = mapped_column(JSON, default=dict, doc="Impact details.")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, doc="Creation timestamp.")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, doc="Last update timestamp.")

    related_event_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('events.id'), doc="Foreign key to related event.")
    related_event: Mapped[Optional['Event']] = relationship('Event', back_populates='consequences')

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the consequence to a dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "consequence_type": self.consequence_type.value if self.consequence_type else None,
            "impact": self.impact,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "related_event_id": self.related_event_id
        }

    def __repr__(self):
        return f'<Consequence {self.id} type={self.consequence_type}>'

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'consequence_type': self.consequence_type.value if self.consequence_type else None,
            'impact': self.impact,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'related_event_id': self.related_event_id
        } 