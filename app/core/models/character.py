"""
Character model for game characters.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Boolean, Index, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel
from app.core.models.inventory import InventoryItem
from app.core.models.equipment import EquipmentInstance
from app.core.models.magic import Spell

# Association table for many-to-many relationship between Character and Quest
character_quests = Table(
    'character_quests',
    BaseModel.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('quest_id', Integer, ForeignKey('quests.id'), primary_key=True)
)

# Association table for many-to-many relationship between Character and Spell
character_spells = Table(
    'character_spells',
    BaseModel.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('spell_id', Integer, ForeignKey('spells.id'), primary_key=True)
)

class Character(BaseModel):
    """Model for game characters."""
    __tablename__ = 'characters'
    __table_args__ = (
        Index('ix_characters_party_id', 'party_id'),
        Index('ix_characters_region_id', 'region_id'),
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    race = Column(String(50))
    gender = Column(String(20))
    age = Column(Integer)
    alignment = Column(String(50))
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    attributes = Column(JSON, default=dict)
    skills = Column(JSON, default=list)
    feats = Column(JSON, default=list)
    inventory = Column(JSON, default=dict)
    spells = Column(JSON, default=dict)
    
    # Foreign Keys
    region_id = Column(Integer, ForeignKey('regions.id', use_alter=True, name='fk_character_region'))
    party_id = Column(Integer, ForeignKey('parties.id', use_alter=True, name='fk_character_party'))
    
    # Relationships
    region = relationship('Region', back_populates='characters', foreign_keys=[region_id])
    party = relationship('Party', back_populates='members', foreign_keys=[party_id])
    led_party = relationship('Party', back_populates='leader', foreign_keys='Party.leader_id')
    combat_stats = relationship('CombatStats', back_populates='character', uselist=False, cascade='all, delete-orphan')
    combat_participants = relationship('CombatParticipant', back_populates='character', cascade='all, delete-orphan')
    quests = relationship('app.core.models.quest.Quest', secondary=character_quests, back_populates='characters')
    quest_progress = relationship('QuestProgress', back_populates='character')
    inventory_items = relationship('InventoryItem', back_populates='owner')
    equipment = relationship('EquipmentInstance', back_populates='character')
    spells = relationship('Spell', secondary=character_spells, back_populates='characters')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'race': self.race,
            'gender': self.gender,
            'age': self.age,
            'alignment': self.alignment,
            'level': self.level,
            'xp': self.xp,
            'attributes': self.attributes,
            'skills': self.skills,
            'feats': self.feats,
            'inventory': self.inventory,
            'spells': self.spells,
            'region_id': self.region_id,
            'party_id': self.party_id,
            'combat_stats': self.combat_stats.to_dict() if self.combat_stats else None,
            'combat_participants': [participant.to_dict() for participant in self.combat_participants],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Character {self.name}>' 