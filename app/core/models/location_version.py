"""
Location version control model for tracking location changes and history.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Boolean, Index, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel

class LocationVersion(BaseModel):
    """Model for tracking location versions and changes."""
    __tablename__ = 'location_versions'
    __table_args__ = (
        Index('ix_location_versions_location_id', 'location_id'),
        Index('ix_location_versions_version_number', 'version_number'),
        UniqueConstraint('location_id', 'version_number', name='uq_location_versions'),
        {'extend_existing': True}
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey('locations.id'), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(50))
    coordinates: Mapped[dict] = mapped_column(JSON, default=lambda: {'x': 0, 'y': 0, 'z': 0})
    size: Mapped[dict] = mapped_column(JSON, default=lambda: {'width': 100, 'height': 100, 'levels': 1})
    level: Mapped[Optional[int]] = mapped_column(Integer)
    difficulty: Mapped[Optional[str]] = mapped_column(String(50))
    resources: Mapped[dict] = mapped_column(JSON, default=dict)
    npcs: Mapped[dict] = mapped_column(JSON, default=dict)
    quests: Mapped[dict] = mapped_column(JSON, default=dict)
    points_of_interest: Mapped[dict] = mapped_column(JSON, default=dict)
    features: Mapped[dict] = mapped_column(JSON, default=lambda: {
        'terrain': 'plain',
        'climate': 'temperate',
        'landmarks': [],
        'resources': [],
        'hazards': []
    })
    objects: Mapped[dict] = mapped_column(JSON, default=lambda: {
        'items': [],
        'containers': [],
        'interactables': []
    })
    state: Mapped[dict] = mapped_column(JSON, default=lambda: {
        'current_weather': None,
        'active_events': [],
        'conditions': [],
        'visitors': [],
        'last_updated': datetime.utcnow().isoformat()
    })
    change_type: Mapped[str] = mapped_column(String(50), nullable=False)  # creation, modification, deletion
    change_reason: Mapped[str] = mapped_column(Text)
    changed_by: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    location = relationship('Location', back_populates='versions', foreign_keys=[location_id])
    change_logs = relationship('LocationChangeLog', back_populates='version')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert version to dictionary representation."""
        return {
            'id': self.id,
            'location_id': self.location_id,
            'version_number': self.version_number,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'coordinates': self.coordinates,
            'size': self.size,
            'level': self.level,
            'difficulty': self.difficulty,
            'resources': self.resources,
            'npcs': self.npcs,
            'quests': self.quests,
            'points_of_interest': self.points_of_interest,
            'features': self.features,
            'objects': self.objects,
            'state': self.state,
            'change_type': self.change_type,
            'change_reason': self.change_reason,
            'changed_by': self.changed_by,
            'created_at': self.created_at.isoformat()
        }

class LocationChangeLog(BaseModel):
    """Model for tracking detailed changes to locations."""
    __tablename__ = 'location_change_logs'
    __table_args__ = (
        Index('ix_location_change_logs_location_id', 'location_id'),
        Index('ix_location_change_logs_version_id', 'version_id'),
        {'extend_existing': True}
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey('locations.id'), nullable=False)
    version_id: Mapped[int] = mapped_column(Integer, ForeignKey('location_versions.id'), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(JSON)
    new_value: Mapped[Optional[str]] = mapped_column(JSON)
    change_type: Mapped[str] = mapped_column(String(50), nullable=False)  # add, modify, delete
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    location = relationship('Location', back_populates='change_logs')
    version = relationship('LocationVersion', back_populates='change_logs')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert change log to dictionary representation."""
        return {
            'id': self.id,
            'location_id': self.location_id,
            'version_id': self.version_id,
            'field_name': self.field_name,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'change_type': self.change_type,
            'created_at': self.created_at.isoformat()
        } 