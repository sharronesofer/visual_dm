"""
NPC model for game characters.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Float, Boolean, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel
from app.core.models.version_control import CodeVersion
from enum import Enum

class NPCType(Enum):
    """Types of NPCs in the game."""
    MERCHANT = "merchant"
    QUEST_GIVER = "quest_giver"
    GUARD = "guard"
    TRAINER = "trainer"
    CIVILIAN = "civilian"
    ENEMY = "enemy"

class NPCDisposition(Enum):
    """NPC's disposition towards the player."""
    HOSTILE = -1
    NEUTRAL = 0
    FRIENDLY = 1

class NPC(BaseModel):
    """Model for non-player characters."""
    __tablename__ = 'npcs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[NPCType] = mapped_column(SQLEnum(NPCType))
    level: Mapped[int] = mapped_column(Integer, default=1)
    disposition: Mapped[NPCDisposition] = mapped_column(SQLEnum(NPCDisposition), default=NPCDisposition.NEUTRAL)
    base_disposition: Mapped[float] = mapped_column(Float, default=0.0)
    level_requirement: Mapped[int] = mapped_column(Integer, default=1)
    interaction_cooldown: Mapped[int] = mapped_column(Integer, default=5)  # minutes
    last_interaction: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Location tracking
    current_location_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('locations.id'))
    home_location_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('locations.id'))
    
    # Schedule and behavior
    schedule: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    dialogue_options: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    behavior_flags: Mapped[Dict[str, bool]] = mapped_column(JSON, default=dict)
    
    # Inventory and trading
    inventory: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    gold: Mapped[int] = mapped_column(Integer, default=0)
    trade_inventory: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    
    # Quest-related
    available_quests: Mapped[List[int]] = mapped_column(JSON, default=list)  # List of quest IDs
    completed_quests: Mapped[List[int]] = mapped_column(JSON, default=list)  # List of completed quest IDs
    
    # Combat stats
    combat_stats_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('combat_stats.id'))
    
    # Goal-driven behavior
    goals: Mapped[Dict[str, Any]] = mapped_column(JSON, default=lambda: {
        'current': [],
        'completed': [],
        'failed': []
    })
    # Relationships (NPC-to-NPC, key: str(target_npc_id), value: {'value': float, ...})
    relationships: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # Memory and interaction history
    memories: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    
    # Version control
    current_version_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('npc_versions.id'))
    
    # Relationships
    current_location = relationship('Location', foreign_keys=[current_location_id])
    home_location = relationship('Location', foreign_keys=[home_location_id])
    combat_stats = relationship('CombatStats', back_populates='npc', foreign_keys='CombatStats.npc_id')
    quests = relationship('app.core.models.quest.Quest', back_populates='npc', foreign_keys='app.core.models.quest.Quest.npc_id')
    current_version = relationship('NPCVersion', foreign_keys=[current_version_id])
    led_faction = relationship('Faction', back_populates='leader', foreign_keys='Faction.leader_id')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.schedule = kwargs.get('schedule', [])
        self.dialogue_options = kwargs.get('dialogue_options', {})
        self.behavior_flags = kwargs.get('behavior_flags', {})
        self.inventory = kwargs.get('inventory', [])
        self.trade_inventory = kwargs.get('trade_inventory', [])
        self.available_quests = kwargs.get('available_quests', [])
        self.completed_quests = kwargs.get('completed_quests', [])
        if not kwargs.get('skip_initial_version', False):
            db.session.flush()  # Ensure we have an ID
            # NPCVersionService.create_version(
            #     npc=self,
            #     change_type="creation",
            #     change_description="Initial NPC creation",
            #     changed_fields=list(kwargs.keys())
            # )

    def to_dict(self) -> Dict[str, Any]:
        """Convert NPC to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.value,
            'level': self.level,
            'disposition': self.disposition.value,
            'base_disposition': self.base_disposition,
            'level_requirement': self.level_requirement,
            'interaction_cooldown': self.interaction_cooldown,
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None,
            'current_location_id': self.current_location_id,
            'home_location_id': self.home_location_id,
            'schedule': self.schedule,
            'dialogue_options': self.dialogue_options,
            'behavior_flags': self.behavior_flags,
            'inventory': self.inventory,
            'gold': self.gold,
            'trade_inventory': self.trade_inventory,
            'available_quests': self.available_quests,
            'completed_quests': self.completed_quests,
            'combat_stats_id': self.combat_stats_id,
            'goals': self.goals,
            'relationships': self.relationships,
            'memories': self.memories,
            'current_version_id': self.current_version_id
        }

    def update_disposition(self, change: float) -> None:
        """Update NPC's disposition within bounds."""
        current_value = self.disposition.value + change
        if current_value <= -1:
            self.disposition = NPCDisposition.HOSTILE
        elif current_value >= 1:
            self.disposition = NPCDisposition.FRIENDLY
        else:
            self.disposition = NPCDisposition.NEUTRAL

    def add_to_inventory(self, item: Dict[str, Any]) -> None:
        """Add an item to NPC's inventory."""
        self.inventory.append(item)

    def create_version(self, change_type: str, change_description: str, 
                      changed_fields: List[str], code_version_id: Optional[int] = None) -> None:
        """Create a new version of this NPC."""
        from app.core.models.npc_version import NPCVersion
        
        # Create new version
        new_version = NPCVersion.create_from_npc(
            self, 
            change_type=change_type,
            change_description=change_description,
            changed_fields=changed_fields,
            code_version_id=code_version_id
        )
        
        # Save the version
        db.session.add(new_version)
        db.session.flush()  # Get the ID without committing
        
        # Update current version
        self.current_version_id = new_version.id
        
        return new_version

    def revert_to_version(self, version_number: int) -> bool:
        """Revert NPC to a specific version."""
        from app.core.models.npc_version import NPCVersion
        
        # Find the version
        target_version = NPCVersion.query.filter_by(
            npc_id=self.id,
            version_number=version_number
        ).first()
        
        if not target_version:
            return False
        
        # Apply the version data
        target_version.apply_to_npc(self)
        
        # Create a new version to record the revert
        self.create_version(
            change_type='revert',
            change_description=f'Reverted to version {version_number}',
            changed_fields=['all']  # Revert affects all fields
        )
        return True

    def get_version_history(self) -> List[Dict[str, Any]]:
        """Get the version history of this NPC."""
        from app.core.models.npc_version import NPCVersion
        
        versions = NPCVersion.query.filter_by(npc_id=self.id).order_by(NPCVersion.version_number.desc()).all()
        return [version.to_dict() for version in versions]

    def get_version(self, version_number: int) -> Optional[Dict[str, Any]]:
        """Get a specific version of this NPC."""
        from app.core.models.npc_version import NPCVersion
        
        version = NPCVersion.query.filter_by(
            npc_id=self.id,
            version_number=version_number
        ).first()
        
        return version.to_dict() if version else None

    def add_quest(self, quest_id: int) -> None:
        """Add a quest to NPC's available quests."""
        if quest_id not in self.available_quests:
            self.available_quests.append(quest_id)

    def complete_quest(self, quest_id: int) -> None:
        """Mark a quest as completed."""
        if quest_id in self.available_quests:
            self.available_quests.remove(quest_id)
            self.completed_quests.append(quest_id)

    def is_merchant(self) -> bool:
        """Check if NPC is a merchant."""
        return self.type == NPCType.MERCHANT

    def is_quest_giver(self) -> bool:
        """Check if NPC is a quest giver."""
        return self.type == NPCType.QUEST_GIVER

    def is_trainer(self) -> bool:
        """Check if NPC is a trainer."""
        return self.type == NPCType.TRAINER

    def can_trade(self) -> bool:
        """Check if NPC can trade."""
        return self.is_merchant() and bool(self.trade_inventory)

    def has_available_quests(self) -> bool:
        """Check if NPC has available quests."""
        return self.is_quest_giver() and bool(self.available_quests)

    def update_goals(self) -> Optional[Dict[str, Any]]:
        """
        Update NPC goals and progress. Returns changes if any occurred.
        """
        changes = []
        for goal in list(self.goals['current']):
            # Check for completion
            if self._check_goal_completion(goal):
                self.goals['current'].remove(goal)
                self.goals['completed'].append(goal)
                changes.append({
                    'type': 'goal_completed',
                    'goal': goal['description']
                })
            # Check for failure
            elif self._check_goal_failure(goal):
                self.goals['current'].remove(goal)
                self.goals['failed'].append(goal)
                changes.append({
                    'type': 'goal_failed',
                    'goal': goal['description'],
                    'reason': goal.get('failure_reason', 'unknown')
                })
            # Update progress
            else:
                new_progress = self._calculate_goal_progress(goal)
                if new_progress != goal.get('progress', 0):
                    goal['progress'] = new_progress
                    changes.append({
                        'type': 'goal_progress',
                        'goal': goal['description'],
                        'progress': new_progress
                    })
        # Generate new goals if needed
        if len(self.goals['current']) < 2:  # Maintain at least 2 active goals
            new_goal = self._generate_new_goal()
            if new_goal:
                self.goals['current'].append(new_goal)
                changes.append({
                    'type': 'new_goal',
                    'goal': new_goal['description']
                })
        return changes if changes else None

    def _check_goal_completion(self, goal: Dict[str, Any]) -> bool:
        """
        Check if a goal has been completed.
        """
        if 'conditions' not in goal:
            return False
        for condition in goal['conditions']:
            if not self._evaluate_condition(condition):
                return False
        return True

    def _check_goal_failure(self, goal: Dict[str, Any]) -> bool:
        """
        Check if a goal has failed.
        """
        if 'failure_conditions' not in goal:
            return False
        for condition in goal['failure_conditions']:
            if self._evaluate_condition(condition):
                return True
        return False

    def _calculate_goal_progress(self, goal: Dict[str, Any]) -> float:
        """
        Calculate progress towards a goal (0-100).
        """
        if 'progress_calculation' not in goal:
            return goal.get('progress', 0)
        calc = goal['progress_calculation']
        if calc['type'] == 'resource':
            current = sum(item.get('amount', 0) for item in self.inventory if item.get('type') == calc['resource'])
            return min(100, (current / calc['target']) * 100)
        elif calc['type'] == 'relationship':
            # Relationship progress: value/target (e.g., reach 0.8 with npc_id)
            target_npc_id = str(calc.get('target_npc_id'))
            required_value = calc.get('target_value', 1.0)
            rel = self.relationships.get(target_npc_id, {})
            current_value = rel.get('value', 0.0)
            progress = min(100, max(0, (current_value / required_value) * 100)) if required_value != 0 else 0
            return progress
        elif calc['type'] == 'quest':
            return 100 if calc['quest_id'] in self.completed_quests else 0
        return goal.get('progress', 0)

    def _generate_new_goal(self) -> Optional[Dict[str, Any]]:
        """
        Generate a new goal based on NPC state, traits, or world context.
        """
        # TODO: Implement goal generation logic (stub)
        return None

    def _evaluate_condition(self, condition: Dict[str, Any]) -> bool:
        """
        Evaluate a single goal condition.
        """
        condition_type = condition.get('type')
        if condition_type == 'resource':
            resource = condition['resource']
            amount = condition['amount']
            current = sum(item.get('amount', 0) for item in self.inventory if item.get('type') == resource)
            return current >= amount
        elif condition_type == 'quest_completed':
            quest_id = condition['quest_id']
            return quest_id in self.completed_quests
        elif condition_type == 'relationship':
            # Check if relationship with target_npc_id meets/exceeds value
            target_npc_id = str(condition.get('target_npc_id'))
            required_value = condition.get('target_value', 1.0)
            rel = self.relationships.get(target_npc_id, {})
            current_value = rel.get('value', 0.0)
            return current_value >= required_value
        return False

    def add_memory(self, event_type: str, description: str, importance: float = 1.0, decay_rate: float = 0.01, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a new memory to the NPC's memory list.
        """
        memory = {
            'event_type': event_type,
            'description': description,
            'timestamp': datetime.utcnow().isoformat(),
            'importance': importance,
            'decay_rate': decay_rate,
            'metadata': metadata or {}
        }
        if self.memories is None:
            self.memories = []
        self.memories.append(memory)

    def get_memories(self, min_importance: float = 0.0) -> List[Dict[str, Any]]:
        """
        Retrieve all memories above a certain importance threshold.
        """
        if not self.memories:
            return []
        return [m for m in self.memories if m.get('importance', 0.0) >= min_importance]

    def decay_memories(self) -> None:
        """
        Apply decay to all memories, reducing their importance over time. Remove memories below a threshold.
        """
        if not self.memories:
            return
        now = datetime.utcnow()
        new_memories = []
        for m in self.memories:
            # Parse timestamp
            try:
                mem_time = datetime.fromisoformat(m['timestamp'])
            except Exception:
                mem_time = now
            # Decay importance
            days_passed = (now - mem_time).days
            importance = m.get('importance', 1.0) * (1.0 - m.get('decay_rate', 0.01)) ** days_passed
            if importance >= 0.05:
                m['importance'] = importance
                new_memories.append(m)
        self.memories = new_memories

    def update(self, **kwargs):
        """Update NPC attributes with version tracking."""
        changed_fields = []
        for key, value in kwargs.items():
            if hasattr(self, key) and getattr(self, key) != value:
                setattr(self, key, value)
                changed_fields.append(key)
        
        if changed_fields:
            db.session.flush()  # Ensure changes are reflected
            # NPCVersionService.create_version(
            #     npc=self,
            #     change_type="update",
            #     change_description=f"Updated fields: {', '.join(changed_fields)}",
            #     changed_fields=changed_fields
            # )

    def get_latest_version(self) -> Optional['NPCVersion']:
        """Get the latest version of this NPC."""
        return self.current_version.first()

    def compare_versions(self, version1_num: int, version2_num: int) -> List[Dict[str, Any]]:
        """Compare two versions of this NPC."""
        v1 = self.current_version.filter_by(version_number=version1_num).first()
        v2 = self.current_version.filter_by(version_number=version2_num).first()
        
        if not v1 or not v2:
            return []
            
        return NPCVersionService.compare_versions(v1, v2) 