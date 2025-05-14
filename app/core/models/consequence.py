"""
Consequence model for tracking punitive actions applied to players.
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import db
from app.core.models.base import BaseModel
from app.core.enums import InfractionSeverity, ConsequenceType

class Consequence(BaseModel):
    """Model for consequences applied to players."""
    __tablename__ = 'consequences'
    __table_args__ = {'extend_existing': True}

    # Foreign Keys
    player_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    infraction_id = Column(Integer, ForeignKey('infractions.id'), nullable=True)

    # Consequence details
    type = Column(String(50), nullable=False)
    severity = Column(SQLEnum(InfractionSeverity), nullable=False)
    active = Column(Boolean, default=True)
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    details = Column(Text, nullable=True)

    # Relationships
    player = relationship('User', foreign_keys=[player_id])
    character = relationship('Character', foreign_keys=[character_id])
    infraction = relationship('Infraction', foreign_keys=[infraction_id])

    def __repr__(self):
        return f'<Consequence {self.id} type={self.type} severity={self.severity} player={self.player_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'character_id': self.character_id,
            'infraction_id': self.infraction_id,
            'type': self.type,
            'severity': self.severity.value if self.severity else None,
            'active': self.active,
            'issued_at': self.issued_at.isoformat() if self.issued_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'details': self.details,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 