"""
Social interaction models for tracking character relationships and interactions.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Float, Table, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel

# Association table for character relationships
character_relationships = Table(
    'character_relationships',
    BaseModel.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('related_character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('relationship_type', String(50)),
    Column('strength', Float, default=0.0),
    Index('ix_character_relationships_composite', 'character_id', 'related_character_id'),
    Index('ix_relationships_type', 'relationship_type'),
    extend_existing=True
)

class SocialInteraction(BaseModel):
    """Model for tracking social interactions between characters."""
    __tablename__ = 'social_interactions'
    __table_args__ = (
        Index('ix_social_interactions_initiator', 'initiator_id'),
        Index('ix_social_interactions_target', 'target_id'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True)
    interaction_type = Column(String(50))  # conversation, trade, combat, etc.
    description = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    outcome = Column(JSON, default=dict)
    
    # Foreign Keys
    initiator_id = Column(Integer, ForeignKey('characters.id'))
    target_id = Column(Integer, ForeignKey('characters.id'))
    
    # Relationships
    initiator = relationship('Character', foreign_keys=[initiator_id], back_populates='initiated_interactions')
    target = relationship('Character', foreign_keys=[target_id], back_populates='received_interactions')
    
    def __repr__(self):
        return f'<SocialInteraction {self.interaction_type}>'

class CharacterRelationship(BaseModel):
    """Model for tracking relationships between characters."""
    __tablename__ = 'character_relationship_details'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    relationship_type = Column(String(50))  # friend, enemy, ally, etc.
    strength = Column(Float, default=0.0)  # -1.0 to 1.0
    history = Column(JSON, default=dict)
    
    # Foreign Keys
    character_id = Column(Integer, ForeignKey('characters.id'))
    related_character_id = Column(Integer, ForeignKey('characters.id'))
    
    # Relationships
    character = relationship('Character', foreign_keys=[character_id], back_populates='relationships')
    related_character = relationship('Character', foreign_keys=[related_character_id], back_populates='related_to')
    
    def __repr__(self):
        return f'<CharacterRelationship {self.relationship_type}>' 