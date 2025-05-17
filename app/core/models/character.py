"""
Character model for game characters.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Boolean, Index, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel
from app.core.models.inventory import InventoryItem
from app.core.models.equipment import EquipmentInstance
from app.core.models.spell import Spell
from .feats import Feat, FeatManager
from dataclasses import dataclass

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

@dataclass
class CharacterSkills:
    """Character skill values"""
    # Base skills
    acrobatics: int = 0
    arcana: int = 0
    athletics: int = 0
    deception: int = 0
    history: int = 0
    insight: int = 0
    intimidation: int = 0
    investigation: int = 0
    medicine: int = 0
    nature: int = 0
    perception: int = 0
    performance: int = 0
    persuasion: int = 0
    religion: int = 0
    sleight_of_hand: int = 0
    stealth: int = 0
    survival: int = 0
    
    # Custom skills can be added dynamically
    def __getattr__(self, name):
        # For unknown attributes, return 0 instead of raising AttributeError
        return 0

@dataclass
class CharacterRanks:
    """Character rank values for different progressions"""
    combat: int = 0
    arcane: int = 0
    divine: int = 0
    social: int = 0
    stealth: int = 0
    knowledge: int = 0
    
    # Custom ranks can be added dynamically
    def __getattr__(self, name):
        # For unknown attributes, return 0 instead of raising AttributeError
        return 0

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
    initiated_interactions = relationship(
        'app.social.models.social.Interaction',
        back_populates='initiator',
        foreign_keys='Interaction.initiator_id'
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.skills = CharacterSkills()
        self.ranks = CharacterRanks()
        self.damage_modifier = 1.0
        self.damage_modifiers = {}  # By damage type
        self.temp_modifiers = {}  # For temporary effects
    
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

    def add_feat(self, feat: Feat) -> bool:
        """Add a feat to the character
        
        Args:
            feat: The feat to add
            
        Returns:
            Boolean indicating success
        """
        # Check if character already has this feat
        if any(f.id == feat.id for f in self.feats):
            return False
            
        # Check prerequisites
        if not feat.check_prerequisites(self):
            return False
            
        # Add feat and activate passive effects
        self.feats.append(feat)
        if feat.feat_type.name == "PASSIVE":
            feat.activate(self)
            
        return True
    
    def remove_feat(self, feat_id: str) -> bool:
        """Remove a feat from the character
        
        Args:
            feat_id: ID of the feat to remove
            
        Returns:
            Boolean indicating success
        """
        for i, feat in enumerate(self.feats):
            if feat.id == feat_id:
                # Deactivate feat effects first
                if feat.active:
                    feat.deactivate(self)
                
                # Remove feat
                self.feats.pop(i)
                return True
                
        return False
    
    def get_available_progression_paths(self, feat_manager: FeatManager) -> Dict[str, Tuple[str, int, int]]:
        """Get progressions the character has started or can start
        
        Returns:
            Dictionary mapping path names to tuples containing:
                - Path description
                - Number of feats acquired in the path
                - Total number of feats in the path
        """
        character_feat_ids = {feat.id for feat in self.feats}
        available_paths = {}
        
        for path_name, feat_ids in feat_manager.progression_paths.items():
            # Check if character has any feats in this path
            feats_in_path = sum(1 for feat_id in feat_ids if feat_id in character_feat_ids)
            
            if feats_in_path > 0:
                # Already started this progression
                description = f"Progression {feats_in_path}/{len(feat_ids)} complete"
                available_paths[path_name] = (description, feats_in_path, len(feat_ids))
            else:
                # Check if character can start this progression
                first_feat_id = feat_ids[0]
                first_feat = feat_manager.get_feat(first_feat_id)
                
                if first_feat and first_feat.check_prerequisites(self):
                    description = "Available to start"
                    available_paths[path_name] = (description, 0, len(feat_ids))
        
        return available_paths
    
    def get_completed_progression_paths(self, feat_manager: FeatManager) -> List[str]:
        """Get names of completely finished progression paths"""
        character_feat_ids = {feat.id for feat in self.feats}
        completed_paths = []
        
        for path_name, feat_ids in feat_manager.progression_paths.items():
            if all(feat_id in character_feat_ids for feat_id in feat_ids):
                completed_paths.append(path_name)
                
        return completed_paths
    
    def get_progress_in_path(self, feat_manager: FeatManager, path_name: str) -> Tuple[List[Feat], List[Tuple[Feat, List[str]]]]:
        """Get detailed progress in a specific path
        
        Returns:
            Tuple containing:
                - List of acquired feats in the path
                - List of tuples with remaining feats and their unmet prerequisites
        """
        if path_name not in feat_manager.progression_paths:
            raise ValueError(f"Path '{path_name}' not found")
            
        character_feat_ids = {feat.id for feat in self.feats}
        feat_ids = feat_manager.progression_paths[path_name]
        
        acquired_feats = []
        remaining_feats = []
        
        for feat_id in feat_ids:
            feat = feat_manager.get_feat(feat_id)
            
            if feat_id in character_feat_ids:
                # Find the actual instance in character's feats
                for character_feat in self.feats:
                    if character_feat.id == feat_id:
                        acquired_feats.append(character_feat)
                        break
            else:
                # Add to remaining with unmet prerequisites
                unmet_prerequisites = feat.get_unmet_prerequisites(self)
                remaining_feats.append((feat, unmet_prerequisites))
                
        return (acquired_feats, remaining_feats)
    
    def get_feat_recommendations(self, feat_manager: FeatManager, limit: int = 5) -> List[Tuple[Feat, str]]:
        """Get recommended feats based on character build and progression paths"""
        return feat_manager.recommend_next_feats(self, limit)
    
    def activate_feat(self, feat_id: str, target=None) -> bool:
        """Activate a feat
        
        Args:
            feat_id: ID of the feat to activate
            target: Optional target for the feat effect
            
        Returns:
            Boolean indicating success
        """
        for feat in self.feats:
            if feat.id == feat_id:
                return feat.activate(self, target)
                
        return False
    
    def deactivate_feat(self, feat_id: str, target=None) -> bool:
        """Deactivate a feat
        
        Args:
            feat_id: ID of the feat to deactivate
            target: Optional target for the feat effect
            
        Returns:
            Boolean indicating success
        """
        for feat in self.feats:
            if feat.id == feat_id:
                return feat.deactivate(self, target)
                
        return False 