"""
Infraction model for tracking player misconduct and punitive actions.
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import db
from app.core.models.base import BaseModel
from app.core.enums import InfractionType, InfractionSeverity
from sqlalchemy.dialects.postgresql import UUID

class Infraction(BaseModel):
    """Model for player infractions."""
    __tablename__ = 'infractions'
    __table_args__ = {'extend_existing': True}

    # Foreign Keys
    player_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    target_npc_id = Column(Integer, ForeignKey('npcs.id'), nullable=True)

    # Infraction details
    type = Column(SQLEnum(InfractionType), nullable=False)
    severity = Column(SQLEnum(InfractionSeverity), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    location = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    resolved = Column(Boolean, default=False)

    # Relationships
    player = relationship('User', foreign_keys=[player_id])
    character = relationship('Character', foreign_keys=[character_id])
    target_npc = relationship('NPC', foreign_keys=[target_npc_id])

    def __repr__(self):
        return f'<Infraction {self.id} type={self.type} severity={self.severity} player={self.player_id} character={self.character_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'character_id': self.character_id,
            'target_npc_id': self.target_npc_id,
            'type': self.type.value if self.type else None,
            'severity': self.severity.value if self.severity else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'location': self.location,
            'details': self.details,
            'resolved': self.resolved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 