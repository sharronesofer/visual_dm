"""
World event model for managing time-based events in the game world.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import db

class WorldEvent(db.Model):
    """Model for world events."""
    
    __tablename__ = 'world_events'
    
    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default='active')
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime)
    data = Column(JSON, nullable=False, default=dict)
    
    # Foreign keys
    world_state_id = Column(Integer, ForeignKey('world_states.id'), nullable=False)
    
    # Relationships
    world_state = relationship('WorldState', back_populates='events')
    
    def __init__(self, type: str, status: str = 'active', end_time: datetime = None, data: dict = None):
        """Initialize a world event."""
        self.type = type
        self.status = status
        self.end_time = end_time
        self.data = data or {}
        
    def __repr__(self):
        """String representation."""
        return f'<WorldEvent {self.id}: {self.type} ({self.status})>'
        
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'type': self.type,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'data': self.data
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'WorldEvent':
        """Create from dictionary."""
        return cls(
            type=data['type'],
            status=data.get('status', 'active'),
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            data=data.get('data', {})
        )
        
    def is_expired(self) -> bool:
        """Check if the event has expired."""
        return self.end_time and datetime.utcnow() >= self.end_time
        
    def is_active(self) -> bool:
        """Check if the event is active."""
        return self.status == 'active' and not self.is_expired()
        
    def complete(self) -> None:
        """Mark the event as completed."""
        self.status = 'completed'
        
    def cancel(self) -> None:
        """Cancel the event."""
        self.status = 'cancelled'
        
    def extend(self, duration) -> None:
        """Extend the event duration."""
        if self.end_time:
            self.end_time += duration
            
    def update_data(self, new_data: dict) -> None:
        """Update event data."""
        self.data.update(new_data)
        
    def get_duration(self):
        """Get event duration."""
        if not self.end_time:
            return None
        return self.end_time - self.start_time
        
    def get_remaining_time(self):
        """Get remaining time."""
        if not self.end_time:
            return None
        return max(datetime.timedelta(0), self.end_time - datetime.utcnow())
        
    def get_completion_percentage(self):
        """Get completion percentage."""
        if not self.end_time:
            return None
            
        total_duration = self.get_duration()
        if not total_duration:
            return None
            
        elapsed = datetime.utcnow() - self.start_time
        return min(100, max(0, (elapsed.total_seconds() / total_duration.total_seconds()) * 100))
        
    def get_affected_entities(self):
        """Get affected entities."""
        affected = {
            'factions': [],
            'regions': [],
            'npcs': []
        }
        
        if self.type == 'war_declaration':
            affected['factions'].extend([
                self.data.get('aggressor_id'),
                self.data.get('defender_id')
            ])
        elif self.type == 'trade_agreement':
            affected['regions'].extend([
                self.data.get('region1_id'),
                self.data.get('region2_id')
            ])
        elif self.type == 'diplomatic_crisis':
            affected['factions'].extend([
                self.data.get('faction1_id'),
                self.data.get('faction2_id')
            ])
        elif self.type == 'global_festival':
            affected['regions'].extend(self.data.get('participating_regions', []))
        elif self.type == 'natural_calamity':
            affected['regions'].extend(self.data.get('affected_regions', []))
        elif self.type == 'technological_discovery':
            affected['factions'].append(self.data.get('discoverer_faction_id'))
        elif self.type == 'religious_movement':
            affected['regions'].extend(self.data.get('affected_regions', []))
            
        return {k: [v for v in vs if v is not None] for k, vs in affected.items()} 