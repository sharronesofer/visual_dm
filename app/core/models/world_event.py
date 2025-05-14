"""
World event model for tracking game events.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel

class WorldEvent(BaseModel):
    """Model for tracking world events."""
    __tablename__ = 'world_events'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    event_type = Column(String(50))
    status = Column(String(50), default='active')
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    data = Column(JSON, default=dict)
    affected_regions = Column(JSON, default=list)  # List of region IDs
    consequences = Column(JSON, default=dict)      # Dict describing effects on world state
    
    # Foreign Keys
    world_state_id = Column(Integer, ForeignKey('world_states.id'))
    region_id = Column(Integer, ForeignKey('regions.id'))
    
    # Relationships
    world_state = relationship('WorldState', back_populates='events')
    region = relationship('Region', back_populates='events')
    
    def __repr__(self):
        return f'<WorldEvent {self.title}>'

    def resolve(self, world):
        """Apply event consequences to the world state."""
        # Example: apply resource changes, trigger faction relation changes, etc.
        for region_id, changes in self.consequences.get('regions', {}).items():
            region = next((r for r in world.regions if r.id == region_id), None)
            if region and 'resources' in changes:
                for res, delta in changes['resources'].items():
                    if res in region.resources:
                        region.resources[res] += delta
        # Additional consequence logic as needed
        self.status = 'resolved'

    @classmethod
    def get_active_events(cls, session):
        return session.query(cls).filter_by(status='active').all()

    @classmethod
    def get_historical_events(cls, session):
        return session.query(cls).filter(cls.status != 'active').all() 