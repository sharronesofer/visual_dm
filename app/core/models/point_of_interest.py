"""
Point of Interest model for tracking locations and landmarks.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel

class PointOfInterest(BaseModel):
    """Model for locations and landmarks."""
    __tablename__ = 'points_of_interest'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(String(50))  # town, dungeon, landmark, etc.
    coordinates = Column(JSON)  # {x: float, y: float}
    discovered = Column(Boolean, default=False)
    importance = Column(Float, default=0.0)
    features = Column(JSON, default=dict)
    
    # Foreign Keys
    region_id = Column(Integer, ForeignKey('regions.id'))
    owner_id = Column(Integer, ForeignKey('factions.id'))
    
    # Relationships
    region = relationship('Region', back_populates='points_of_interest')
    owner = relationship('Faction', back_populates='owned_locations')
    # npcs = relationship('NPC', back_populates='location')
    # quests = relationship('app.core.models.quest.Quest', back_populates='location')

    # Evolution relationships
    states = relationship('POIState', back_populates='poi', cascade='all, delete-orphan')
    transitions = relationship('POITransition', back_populates='poi', cascade='all, delete-orphan')
    histories = relationship('POIHistory', back_populates='poi', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PointOfInterest {self.name}>' 