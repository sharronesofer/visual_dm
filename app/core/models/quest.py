"""
Quest model for tracking player quests and objectives.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Float, Boolean, Table, Enum as SQLEnum, Text
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
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Quest(BaseModel):
    """
    Model for quests in the game.
    Fields:
        id (int): Primary key.
        name (str): Quest name.
        description (str): Quest description.
        status (QuestStatus): Status of the quest.
        objectives (list): List of quest objectives.
        rewards (dict): Rewards for completing the quest.
        requirements (dict): Requirements to start the quest.
        is_main_quest (bool): Whether this is a main quest.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        party_id (int): Foreign key to party.
        party (Party): Related party.
    """
    __tablename__ = 'quests'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, doc="Primary key.")
    name: Mapped[str] = mapped_column(String(100), nullable=False, doc="Quest name.")
    description: Mapped[Optional[str]] = mapped_column(Text, doc="Quest description.")
    status: Mapped[QuestStatus] = mapped_column(SQLEnum(QuestStatus), default=QuestStatus.NOT_STARTED, doc="Status of the quest.")
    objectives: Mapped[list] = mapped_column(JSON, default=list, doc="List of quest objectives.")
    rewards: Mapped[dict] = mapped_column(JSON, default=dict, doc="Rewards for completing the quest.")
    requirements: Mapped[dict] = mapped_column(JSON, default=dict, doc="Requirements to start the quest.")
    is_main_quest: Mapped[bool] = mapped_column(Boolean, default=False, doc="Whether this is a main quest.")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, doc="Creation timestamp.")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, doc="Last update timestamp.")

    party_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('parties.id'), doc="Foreign key to party.")
    party: Mapped[Optional['Party']] = relationship('Party', back_populates='quests')

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the quest to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value if self.status else None,
            "objectives": self.objectives,
            "rewards": self.rewards,
            "requirements": self.requirements,
            "is_main_quest": self.is_main_quest,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "party_id": self.party_id
        }

    def is_available(self, character: 'Character') -> bool:
        """Check if quest is available for a character."""
        if self.status != QuestStatus.NOT_STARTED:
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
            
        self.status = QuestStatus.IN_PROGRESS
        character.quests.append(self)
        return True

    def complete(self, character: 'Character') -> bool:
        """Complete the quest and grant rewards."""
        if self.status != QuestStatus.IN_PROGRESS:
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
        self.status = QuestStatus.FAILED

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