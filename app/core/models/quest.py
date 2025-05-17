"""
Quest model for tracking player quests and objectives.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Float, Boolean, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel
from enum import Enum
from app.core.models.character import character_quests

class QuestType(Enum):
    MAIN = "main"
    SIDE = "side"
    DAILY = "daily"
    WEEKLY = "weekly"
    EVENT = "event"

class QuestStatus(Enum):
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

class Quest(BaseModel):
    """Model for tracking quests."""
    __tablename__ = 'quests'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500))
    type: Mapped[QuestType] = mapped_column(SQLEnum(QuestType), default=QuestType.SIDE)
    status: Mapped[QuestStatus] = mapped_column(SQLEnum(QuestStatus), default=QuestStatus.AVAILABLE)
    level_requirement: Mapped[int] = mapped_column(Integer, default=1)
    experience_reward: Mapped[int] = mapped_column(Integer, default=0)
    gold_reward: Mapped[int] = mapped_column(Integer, default=0)
    item_rewards: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    prerequisites: Mapped[List[int]] = mapped_column(JSON, default=list)  # List of quest IDs
    objectives: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    location_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('locations.id'))
    npc_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('npcs.id'))
    region_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('regions.id'))
    faction_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('factions.id'))
    
    # Relationships
    location = relationship('app.core.models.location.Location', back_populates='quests')
    npc = relationship('NPC', back_populates='quests', foreign_keys=[npc_id])
    characters = relationship('app.core.models.character.Character', secondary=character_quests, back_populates='quests')
    region = relationship('Region', back_populates='quests')
    faction = relationship('Faction', back_populates='quests')
    progress_records = relationship('QuestProgress', back_populates='quest')
    rewards = relationship('app.core.models.quest.QuestReward', back_populates='quest')
    world_impacts = relationship('app.core.models.quest.QuestWorldImpact', back_populates='quest')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.item_rewards = kwargs.get('item_rewards', [])
        self.prerequisites = kwargs.get('prerequisites', [])
        self.objectives = kwargs.get('objectives', [])

    def to_dict(self) -> Dict[str, Any]:
        """Convert quest to dictionary representation."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type.value,
            'status': self.status.value,
            'level_requirement': self.level_requirement,
            'experience_reward': self.experience_reward,
            'gold_reward': self.gold_reward,
            'item_rewards': self.item_rewards,
            'prerequisites': self.prerequisites,
            'objectives': self.objectives,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'location_id': self.location_id,
            'npc_id': self.npc_id,
            'region_id': self.region_id,
            'faction_id': self.faction_id
        }

    def is_available(self, character: 'Character') -> bool:
        """Check if quest is available for a character."""
        if self.status != QuestStatus.AVAILABLE:
            return False
            
        if character.level < self.level_requirement:
            return False
            
        if self.start_date and datetime.utcnow() < self.start_date:
            return False
            
        if self.end_date and datetime.utcnow() > self.end_date:
            return False
            
        # Check prerequisites
        for quest_id in self.prerequisites:
            prereq = Quest.query.get(quest_id)
            if not prereq or prereq.status != QuestStatus.COMPLETED:
                return False
                
        return True

    def start(self, character: 'Character') -> bool:
        """Start the quest for a character."""
        if not self.is_available(character):
            return False
            
        self.status = QuestStatus.ACTIVE
        character.quests.append(self)
        return True

    def complete(self, character: 'Character') -> bool:
        """Complete the quest and grant rewards."""
        if self.status != QuestStatus.ACTIVE:
            return False
            
        # Check if all objectives are complete
        for objective in self.objectives:
            if not objective.get('completed', False):
                return False
                
        # Grant rewards
        character.experience += self.experience_reward
        character.gold += self.gold_reward
        
        # Add item rewards to inventory
        for item in self.item_rewards:
            character.add_to_inventory(item)
            
        self.status = QuestStatus.COMPLETED
        return True

    def fail(self) -> None:
        """Mark the quest as failed."""
        self.status = QuestStatus.FAILED

    def expire(self) -> None:
        """Mark the quest as expired."""
        self.status = QuestStatus.EXPIRED

    def update_objective(self, objective_id: int, progress: int) -> bool:
        """Update progress on a quest objective."""
        for objective in self.objectives:
            if objective.get('id') == objective_id:
                objective['progress'] = progress
                if progress >= objective.get('required', 0):
                    objective['completed'] = True
                return True
        return False

class QuestStage(BaseModel):
    """Model for quest stages (multi-stage quests)."""
    __tablename__ = 'quest_stages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quest_id: Mapped[int] = mapped_column(Integer, ForeignKey('quests.id'), nullable=False)
    description: Mapped[str] = mapped_column(String(500))
    objectives: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    completion_criteria: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    order: Mapped[int] = mapped_column(Integer, default=0)

    quest = relationship('app.core.models.quest.Quest', backref='stages', foreign_keys=[quest_id])

class QuestDependency(BaseModel):
    """Model to track prerequisites between quests."""
    __tablename__ = 'quest_dependencies'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quest_id: Mapped[int] = mapped_column(Integer, ForeignKey('quests.id'), nullable=False)
    prerequisite_quest_id: Mapped[int] = mapped_column(Integer, ForeignKey('quests.id'), nullable=False)

    quest = relationship('app.core.models.quest.Quest', foreign_keys=[quest_id], backref='quest_dependencies')
    prerequisite_quest = relationship('app.core.models.quest.Quest', foreign_keys=[prerequisite_quest_id])

class QuestReward(BaseModel):
    """Model for quest rewards."""
    __tablename__ = 'quest_rewards'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quest_id: Mapped[int] = mapped_column(Integer, ForeignKey('quests.id'), nullable=False)
    reward_type: Mapped[str] = mapped_column(String(50))  # e.g., 'item', 'gold', 'reputation', 'experience'
    value: Mapped[Any] = mapped_column(JSON)  # Flexible for different reward types

    quest = relationship('app.core.models.quest.Quest', back_populates='rewards')

class QuestWorldImpact(BaseModel):
    """Model to track changes to world state from quest outcomes."""
    __tablename__ = 'quest_world_impacts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quest_id: Mapped[int] = mapped_column(Integer, ForeignKey('quests.id'), nullable=False)
    impact_type: Mapped[str] = mapped_column(String(100))  # e.g., 'faction', 'npc', 'environment'
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    quest = relationship('app.core.models.quest.Quest', back_populates='world_impacts') 