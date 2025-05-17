"""
Location model for game locations.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Float, Index, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel

class Location(BaseModel):
    """
    Represents a location in the game world
    """
    __tablename__ = 'locations'
    __table_args__ = (
        Index('ix_locations_region_id', 'region_id'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(String(50))  # city, dungeon, wilderness, etc.
    is_discovered = Column(Boolean, default=False)
    is_accessible = Column(Boolean, default=True)
    coordinates = Column(JSON, default=lambda: {
        'x': 0,
        'y': 0,
        'z': 0
    })
    size = Column(JSON, default=lambda: {
        'width': 100,
        'height': 100,
        'levels': 1
    })
    level = Column(Integer)
    difficulty = Column(String(50))
    resources = Column(JSON, default=dict)
    npcs = Column(JSON, default=dict)  # List of NPC IDs
    quests = Column(JSON, default=dict)  # List of quest IDs
    points_of_interest = Column(JSON, default=dict)
    
    # Foreign Keys
    region_id = Column(Integer, ForeignKey('regions.id', use_alter=True, name='fk_location_region'))
    current_version_id = Column(Integer, ForeignKey('location_versions.id'))
    
    # Relationships
    region = relationship('Region', back_populates='locations', foreign_keys=[region_id])
    combats = relationship('Combat', back_populates='location', cascade='all, delete-orphan')
    quests = relationship('app.core.models.quest.Quest', back_populates='location')
    parent_location_id = Column(Integer, ForeignKey('locations.id'))
    parent_location = relationship("Location", remote_side="Location.id", backref="sub_locations")
    owner_faction_id = Column(Integer, ForeignKey('factions.id'))
    owner_faction = relationship('Faction')
    
    # Version control relationships
    versions = relationship('LocationVersion', back_populates='location', cascade='all, delete-orphan', 
                          foreign_keys='LocationVersion.location_id')
    current_version = relationship('LocationVersion', foreign_keys=[current_version_id])
    change_logs = relationship('LocationChangeLog', back_populates='location', cascade='all, delete-orphan')
    
    # Location Features
    features = Column(JSON, default=lambda: {
        'terrain': 'plain',
        'climate': 'temperate',
        'landmarks': [],
        'resources': [],
        'hazards': []
    })
    
    # NPCs and Objects
    objects = Column(JSON, default=lambda: {
        'items': [],
        'containers': [],
        'interactables': []
    })
    
    # Location State
    state = Column(JSON, default=lambda: {
        'current_weather': None,
        'active_events': [],
        'conditions': [],
        'visitors': [],
        'last_updated': datetime.utcnow().isoformat()
    })
    
    # Gameplay Elements
    encounters = Column(JSON, default=lambda: {
        'random': [],
        'scripted': [],
    })

    def create_version(self, change_type: str, change_reason: str, changed_by: str) -> 'LocationVersion':
        """Create a new version of this location."""
        from app.core.models.location_version import LocationVersion
        
        # Get the next version number
        next_version = 1
        if self.versions:
            next_version = max(v.version_number for v in self.versions) + 1
            
        # Create new version
        version = LocationVersion(
            location_id=self.id,
            version_number=next_version,
            name=self.name,
            description=self.description,
            type=self.type,
            coordinates=self.coordinates,
            size=self.size,
            level=self.level,
            difficulty=self.difficulty,
            resources=self.resources,
            npcs=self.npcs,
            quests=self.quests,
            points_of_interest=self.points_of_interest,
            features=self.features,
            objects=self.objects,
            state=self.state,
            change_type=change_type,
            change_reason=change_reason,
            changed_by=changed_by
        )
        
        # Update current version
        self.versions.append(version)
        self.current_version = version
        
        return version
        
    def log_change(self, version_id: int, field_name: str, old_value: Any, new_value: Any, 
                   change_type: str = 'modify') -> 'LocationChangeLog':
        """Log a change to a specific field."""
        from app.core.models.location_version import LocationChangeLog
        
        log = LocationChangeLog(
            location_id=self.id,
            version_id=version_id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            change_type=change_type
        )
        
        self.change_logs.append(log)
        return log
        
    def revert_to_version(self, version_number: int) -> bool:
        """Revert the location to a specific version."""
        target_version = next((v for v in self.versions if v.version_number == version_number), None)
        if not target_version:
            return False
            
        # Update fields from version
        self.name = target_version.name
        self.description = target_version.description
        self.type = target_version.type
        self.coordinates = target_version.coordinates
        self.size = target_version.size
        self.level = target_version.level
        self.difficulty = target_version.difficulty
        self.resources = target_version.resources
        self.npcs = target_version.npcs
        self.quests = target_version.quests
        self.points_of_interest = target_version.points_of_interest
        self.features = target_version.features
        self.objects = target_version.objects
        self.state = target_version.state
        
        # Create new version for the revert
        self.create_version(
            change_type='revert',
            change_reason=f'Reverted to version {version_number}',
            changed_by='system'
        )
        
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'coordinates': self.coordinates,
            'level': self.level,
            'difficulty': self.difficulty,
            'resources': self.resources,
            'npcs': self.npcs,
            'quests': self.quests,
            'points_of_interest': self.points_of_interest,
            'region_id': self.region_id,
            'combats': [combat.to_dict() for combat in self.combats],
            'current_version_id': self.current_version_id,
            'features': self.features,
            'objects': self.objects,
            'state': self.state,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 