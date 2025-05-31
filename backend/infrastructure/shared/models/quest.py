from sqlalchemy import Column, String, Integer, Float, Enum, Text, Boolean, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
import enum
from backend.infrastructure.models import BaseModel

class QuestStatus(enum.Enum):
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

class ConditionType(enum.Enum):
    KILL = "kill"
    COLLECT = "collect"
    VISIT = "visit"
    TALK = "talk"
    ESCORT = "escort"
    DEFEND = "defend"
    DELIVER = "deliver"
    USE_SKILL = "use_skill"
    USE_ITEM = "use_item"
    CUSTOM = "custom"

class Quest(BaseModel):
    """Quest model representing missions and tasks for players."""
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Quest properties
    status = Column(Enum(QuestStatus), default=QuestStatus.AVAILABLE)
    level = Column(Integer, default=1)  # Recommended player level
    difficulty = Column(Integer, default=1)  # 1-10 difficulty scale
    is_main_story = Column(Boolean, default=False)
    is_repeatable = Column(Boolean, default=False)
    time_limit = Column(Integer)  # Time limit in game hours (null if no limit)
    
    # Prerequisites and availability
    prerequisites = Column(JSON)  # List of quest IDs or conditions required
    availability_conditions = Column(JSON)  # Conditions under which quest becomes available
    
    # Quest structure
    stages = Column(JSON)  # Ordered list of quest stages with conditions
    objectives = Column(JSON)  # List of objectives with completion conditions
    branching_choices = Column(JSON)  # Decision points and their effects
    
    # Related entities
    giver_npc_id = Column(Integer, ForeignKey('npc.id'))
    giver_npc = relationship("NPC")
    location_id = Column(Integer, ForeignKey('location.id'))
    location = relationship("Location")
    faction_id = Column(Integer, ForeignKey('faction.id'))
    faction = relationship("Faction")
    
    # Rewards
    xp_reward = Column(Integer, default=0)
    currency_reward = Column(Integer, default=0)
    item_rewards = Column(JSON)  # List of item rewards with quantities
    faction_reputation_rewards = Column(JSON)  # Reputation changes with factions
    
    # Failure consequences
    failure_penalties = Column(JSON)  # Penalties for failing the quest
    
    def __repr__(self):
        return f"<Quest {self.name} ({self.status.name})>" 