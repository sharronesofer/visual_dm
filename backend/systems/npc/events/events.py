"""
NPC Events
----------
Defines NPC-specific event types for the event system.
These events are published when NPCs undergo state changes, enabling
real-time communication with other systems and the Unity frontend.
"""

from datetime import datetime
from typing import List, Optional, Any, Dict, Union
from uuid import UUID
from pydantic import BaseModel, Field

from backend.infrastructure.events.core.event_base import EventBase

# Core NPC Events
class NPCCreated(EventBase):
    """Event emitted when a new NPC is created."""
    npc_id: UUID
    name: str
    race: str
    region_id: Optional[str] = None
    location: Optional[str] = None
    npc_data: Optional[Dict[str, Any]] = None
    
    def __init__(self, **data):
        data["event_type"] = "npc.created"
        super().__init__(**data)

class NPCUpdated(EventBase):
    """Event emitted when NPC data is updated."""
    npc_id: UUID
    changes: Dict[str, Any]
    old_values: Optional[Dict[str, Any]] = None
    
    def __init__(self, **data):
        data["event_type"] = "npc.updated"
        super().__init__(**data)

class NPCDeleted(EventBase):
    """Event emitted when an NPC is deleted."""
    npc_id: UUID
    name: str
    soft_delete: bool = True
    
    def __init__(self, **data):
        data["event_type"] = "npc.deleted"
        super().__init__(**data)

class NPCStatusChanged(EventBase):
    """Event emitted when NPC status changes."""
    npc_id: UUID
    old_status: str
    new_status: str
    reason: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "npc.status_changed"
        super().__init__(**data)

# Location and Movement Events
class NPCMoved(EventBase):
    """Event emitted when NPC changes location."""
    npc_id: UUID
    old_region_id: Optional[str]
    new_region_id: str
    old_location: Optional[str]
    new_location: str
    travel_motive: str = "wander"
    activity: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "npc.moved"
        super().__init__(**data)

class NPCMigrationScheduled(EventBase):
    """Event emitted when NPC migration is scheduled."""
    npc_ids: List[UUID]
    source_region: str
    target_region: str
    migration_reason: Optional[str] = None
    estimated_arrival: Optional[datetime] = None
    
    def __init__(self, **data):
        data["event_type"] = "npc.migration_scheduled"
        super().__init__(**data)

# Memory System Events
class NPCMemoryCreated(EventBase):
    """Event emitted when NPC gains a new memory."""
    npc_id: UUID
    memory_id: str
    content: str
    memory_type: str
    importance: float
    emotion: Optional[str] = None
    location: Optional[str] = None
    participants: List[str] = Field(default_factory=list)
    
    def __init__(self, **data):
        data["event_type"] = "npc.memory_created"
        super().__init__(**data)

class NPCMemoryRecalled(EventBase):
    """Event emitted when NPC recalls a memory."""
    npc_id: UUID
    memory_id: str
    recalled_count: int
    importance: float
    
    def __init__(self, **data):
        data["event_type"] = "npc.memory_recalled"
        super().__init__(**data)

class NPCMemoryForgotten(EventBase):
    """Event emitted when NPC forgets a memory."""
    npc_id: UUID
    memory_id: str
    reason: str  # decay, deleted, replaced
    
    def __init__(self, **data):
        data["event_type"] = "npc.memory_forgotten"
        super().__init__(**data)

# Faction and Relationship Events
class NPCFactionJoined(EventBase):
    """Event emitted when NPC joins a faction."""
    npc_id: UUID
    faction_id: UUID
    role: str = "member"
    loyalty: float = 5.0
    
    def __init__(self, **data):
        data["event_type"] = "npc.faction_joined"
        super().__init__(**data)

class NPCFactionLeft(EventBase):
    """Event emitted when NPC leaves a faction."""
    npc_id: UUID
    faction_id: UUID
    role: str
    final_loyalty: float
    reason: str  # expelled, left, etc.
    
    def __init__(self, **data):
        data["event_type"] = "npc.faction_left"
        super().__init__(**data)

class NPCFactionLoyaltyChanged(EventBase):
    """Event emitted when NPC's faction loyalty changes significantly."""
    npc_id: UUID
    faction_id: UUID
    old_loyalty: float
    new_loyalty: float
    reason: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "npc.faction_loyalty_changed"
        super().__init__(**data)

# Rumor and Information Events
class NPCRumorLearned(EventBase):
    """Event emitted when NPC learns a new rumor."""
    npc_id: UUID
    rumor_id: str
    content: str
    source: Optional[str] = None
    credibility: float
    
    def __init__(self, **data):
        data["event_type"] = "npc.rumor_learned"
        super().__init__(**data)

class NPCRumorShared(EventBase):
    """Event emitted when NPC shares a rumor."""
    npc_id: UUID
    target_npc_id: Optional[UUID] = None
    rumor_id: str
    credibility: float
    times_shared: int
    
    def __init__(self, **data):
        data["event_type"] = "npc.rumor_shared"
        super().__init__(**data)

class NPCRumorForgotten(EventBase):
    """Event emitted when NPC forgets a rumor."""
    npc_id: UUID
    rumor_id: str
    reason: str  # low_credibility, time_decay, replaced
    
    def __init__(self, **data):
        data["event_type"] = "npc.rumor_forgotten"
        super().__init__(**data)

# Motif and Behavior Events
class NPCMotifApplied(EventBase):
    """Event emitted when a motif is applied to an NPC."""
    npc_id: UUID
    motif_id: str
    motif_type: str
    strength: float
    description: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "npc.motif_applied"
        super().__init__(**data)

class NPCMotifCompleted(EventBase):
    """Event emitted when an NPC completes a motif."""
    npc_id: UUID
    motif_id: str
    motif_type: str
    final_strength: float
    outcome: str  # completed, abandoned, failed
    
    def __init__(self, **data):
        data["event_type"] = "npc.motif_completed"
        super().__init__(**data)

class NPCMotifEvolved(EventBase):
    """Event emitted when an NPC's motif evolves or changes."""
    npc_id: UUID
    motif_id: str
    old_strength: float
    new_strength: float
    entropy_change: float
    
    def __init__(self, **data):
        data["event_type"] = "npc.motif_evolved"
        super().__init__(**data)

# Goal and Autonomous Behavior Events
class NPCGoalCreated(EventBase):
    """Event emitted when NPC generates a new autonomous goal."""
    npc_id: UUID
    goal_id: str
    goal_type: str
    description: str
    priority: str
    estimated_duration: Optional[int] = None
    
    def __init__(self, **data):
        data["event_type"] = "npc.goal_created"
        super().__init__(**data)

class NPCGoalCompleted(EventBase):
    """Event emitted when NPC completes a goal."""
    npc_id: UUID
    goal_id: str
    goal_type: str
    success: bool
    outcome_description: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "npc.goal_completed"
        super().__init__(**data)

class NPCGoalAbandoned(EventBase):
    """Event emitted when NPC abandons a goal."""
    npc_id: UUID
    goal_id: str
    goal_type: str
    reason: str
    progress_lost: float = 0.0
    
    def __init__(self, **data):
        data["event_type"] = "npc.goal_abandoned"
        super().__init__(**data)

# Social and Interaction Events
class NPCRelationshipFormed(EventBase):
    """Event emitted when NPC forms a new relationship."""
    npc_id: UUID
    target_id: UUID
    relationship_type: str  # friendship, rivalry, romance, etc.
    initial_strength: float
    context: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "npc.relationship_formed"
        super().__init__(**data)

class NPCRelationshipChanged(EventBase):
    """Event emitted when NPC relationship changes."""
    npc_id: UUID
    target_id: UUID
    relationship_type: str
    old_strength: float
    new_strength: float
    trigger_event: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "npc.relationship_changed"
        super().__init__(**data)

class NPCInteractionOccurred(EventBase):
    """Event emitted when NPCs interact with each other or players."""
    npc_id: UUID
    target_id: Optional[UUID] = None  # None if interacting with player
    interaction_type: str
    location: Optional[str] = None
    outcome: Optional[str] = None
    consequences: Optional[Dict[str, Any]] = None
    
    def __init__(self, **data):
        data["event_type"] = "npc.interaction_occurred"
        super().__init__(**data)

# Economic and Task Events
class NPCTaskScheduled(EventBase):
    """Event emitted when a task is scheduled for an NPC."""
    npc_id: UUID
    task_id: str
    task_type: str
    scheduled_time: datetime
    estimated_duration: Optional[int] = None
    task_data: Optional[Dict[str, Any]] = None
    
    def __init__(self, **data):
        data["event_type"] = "npc.task_scheduled"
        super().__init__(**data)

class NPCTaskCompleted(EventBase):
    """Event emitted when NPC completes a scheduled task."""
    npc_id: UUID
    task_id: str
    task_type: str
    success: bool
    duration_actual: int
    rewards: Optional[Dict[str, Any]] = None
    
    def __init__(self, **data):
        data["event_type"] = "npc.task_completed"
        super().__init__(**data)

class NPCLoyaltyChanged(EventBase):
    """Event emitted when NPC loyalty to player/faction changes."""
    npc_id: UUID
    target_id: Optional[str] = None  # player ID or faction ID
    old_loyalty: int
    new_loyalty: int
    goodwill_change: int = 0
    trigger: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "npc.loyalty_changed"
        super().__init__(**data)

# Population and Statistics Events
class NPCPopulationChanged(EventBase):
    """Event emitted when regional NPC population changes."""
    region_id: str
    old_population: int
    new_population: int
    change_reason: str  # migration, creation, deletion, death
    affected_npcs: Optional[List[UUID]] = None
    
    def __init__(self, **data):
        data["event_type"] = "npc.population_changed"
        super().__init__(**data)

class NPCSystemStatistics(EventBase):
    """Event emitted periodically with NPC system statistics."""
    total_npcs: int
    active_npcs: int
    npcs_by_region: Dict[str, int]
    average_loyalty: float
    total_memories: int
    total_rumors: int
    total_motifs: int
    
    def __init__(self, **data):
        data["event_type"] = "npc.system_statistics"
        super().__init__(**data)

# Error and Debug Events
class NPCError(EventBase):
    """Event emitted when an NPC system error occurs."""
    npc_id: Optional[UUID] = None
    error_type: str
    error_message: str
    operation: str
    stack_trace: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "npc.error"
        super().__init__(**data)

class NPCDebugEvent(EventBase):
    """Event emitted for NPC system debugging."""
    npc_id: Optional[UUID] = None
    debug_type: str
    debug_data: Dict[str, Any]
    operation: str
    
    def __init__(self, **data):
        data["event_type"] = "npc.debug"
        super().__init__(**data) 