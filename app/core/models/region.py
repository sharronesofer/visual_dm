"""
Region model for game regions.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Float, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel
from dataclasses import dataclass, field
from app.core.models.resource import Resource
from app.core.models.point_of_interest import PointOfInterest

class Region(BaseModel):
    """
    Represents a region in the game world
    """
    __tablename__ = 'regions'
    __table_args__ = (
        Index('ix_regions_type', 'type'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(String(50))  # continent, country, province, etc.
    climate = Column(String(50))
    terrain = Column(String(50))
    level_range = Column(JSON)  # {min: int, max: int}
    danger_level = Column(Float, default=0.0)
    history = Column(Text)
    terrain_data = Column(JSON)  # Stores the terrain map as a JSON object
    width = Column(Integer, default=50)
    height = Column(Integer, default=50)
    
    # Foreign Keys
    controlling_faction_id = Column(Integer, ForeignKey('factions.id', use_alter=True, name='fk_region_controlling_faction'))
    
    # Relationships
    locations = relationship('Location', back_populates='region', cascade='all, delete-orphan')
    quests = relationship('app.core.models.quest.Quest', back_populates='region', cascade='all, delete-orphan')
    characters = relationship('Character', back_populates='region', cascade='all, delete-orphan')
    parties = relationship('Party', back_populates='region', cascade='all, delete-orphan')
    based_factions = relationship('app.core.models.faction.Faction', back_populates='headquarters', foreign_keys='app.core.models.faction.Faction.headquarters_id')
    controlling_faction = relationship('app.core.models.faction.Faction', back_populates='controlled_regions', foreign_keys=[controlling_faction_id])
    world_id = Column(Integer, ForeignKey('worlds.id'))
    world = relationship("World", back_populates="regions")
    resources = relationship('Resource', back_populates='region')
    events = relationship('WorldEvent', back_populates='region')
    points_of_interest = relationship('PointOfInterest', back_populates='region')

    def __init__(self, name: str, description: str = "", width: int = 50, height: int = 50):
        self.name = name
        self.description = description
        self.width = width
        self.height = height
        self.terrain_data = self._initialize_terrain()

    def _initialize_terrain(self) -> Dict:
        """Initialize empty terrain data"""
        return {
            'cells': {
                f"{x},{y}": {
                    'terrain': 'plain',
                    'elevation': 0,
                    'features': [],
                    'discovered': False
                }
                for x in range(self.width)
                for y in range(self.height)
            }
        }

    def get_cell(self, x: int, y: int) -> Optional[Dict]:
        """Get cell data at the specified coordinates"""
        return self.terrain_data['cells'].get(f"{x},{y}")

    def set_cell(self, x: int, y: int, data: Dict):
        """Set cell data at the specified coordinates"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.terrain_data['cells'][f"{x},{y}"] = data

    def discover_cell(self, x: int, y: int):
        """Mark a cell as discovered by the player"""
        cell = self.get_cell(x, y)
        if cell:
            cell['discovered'] = True

    def is_discovered(self, x: int, y: int) -> bool:
        """Check if a cell has been discovered"""
        cell = self.get_cell(x, y)
        return cell.get('discovered', False) if cell else False

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'climate': self.climate,
            'terrain': self.terrain,
            'level_range': self.level_range,
            'danger_level': self.danger_level,
            'history': self.history,
            'controlling_faction_id': self.controlling_faction_id,
            'locations': [location.to_dict() for location in self.locations],
            'quests': [quest.to_dict() for quest in self.quests],
            'characters': [character.to_dict() for character in self.characters],
            'parties': [party.to_dict() for party in self.parties],
            'resources': [resource.to_dict() for resource in self.resources],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Region {self.name}>'

    def add_point_of_interest(self, poi_id: str) -> None:
        """Add a point of interest to the region."""
        if poi_id not in self.points_of_interest:
            self.points_of_interest.append(poi_id)

    def remove_point_of_interest(self, poi_id: str) -> bool:
        """Remove a point of interest from the region."""
        if poi_id in self.points_of_interest:
            self.points_of_interest.remove(poi_id)
            return True
        return False

    def add_npc(self, npc_id: str) -> None:
        """Add an NPC to the region."""
        if npc_id not in self.npcs:
            self.npcs.append(npc_id)

    def remove_npc(self, npc_id: str) -> bool:
        """Remove an NPC from the region."""
        if npc_id in self.npcs:
            self.npcs.remove(npc_id)
            return True
        return False

    def add_quest(self, quest_id: str) -> None:
        """Add a quest to the region."""
        if quest_id not in self.quests:
            self.quests.append(quest_id)

    def remove_quest(self, quest_id: str) -> bool:
        """Remove a quest from the region."""
        if quest_id in self.quests:
            self.quests.remove(quest_id)
            return True
        return False 