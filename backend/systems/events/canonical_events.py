"""
Canonical Events
--------------
Defines the standard event types used throughout the system.
All events should extend the EventBase class and provide appropriate fields.

This is the canonical source for all event types in Visual DM as documented
in the Development Bible.
"""

from datetime import datetime
from typing import List, Optional, Any, Dict, Union
from uuid import UUID
from pydantic import BaseModel, Field

from .base import EventBase

# Memory Events
class MemoryCreated(EventBase):
    """Event emitted when a new memory is created."""
    entity_id: Union[str, UUID]
    memory_id: Union[str, UUID]
    memory_type: str
    content: Dict[str, Any]
    importance: float
    
    def __init__(self, **data):
        data["event_type"] = "memory.created"
        super().__init__(**data)

class MemoryReinforced(EventBase):
    """Event emitted when a memory is reinforced."""
    entity_id: Union[str, UUID]
    memory_id: Union[str, UUID]
    old_importance: float
    new_importance: float
    
    def __init__(self, **data):
        data["event_type"] = "memory.reinforced"
        super().__init__(**data)

class MemoryDecayed(EventBase):
    """Event emitted when a memory naturally decays."""
    entity_id: Union[str, UUID]
    memory_id: Union[str, UUID]
    old_importance: float
    new_importance: float
    
    def __init__(self, **data):
        data["event_type"] = "memory.decayed"
        super().__init__(**data)

class MemoryDeleted(EventBase):
    """Event emitted when a memory is deleted."""
    entity_id: Union[str, UUID]
    memory_id: Union[str, UUID]
    memory_type: str
    
    def __init__(self, **data):
        data["event_type"] = "memory.deleted"
        super().__init__(**data)

class MemoryRecalled(EventBase):
    """Event emitted when an entity recalls a memory."""
    entity_id: Union[str, UUID]
    memory_ids: List[Union[str, UUID]]
    query: Optional[Dict[str, Any]] = None
    
    def __init__(self, **data):
        data["event_type"] = "memory.recalled"
        super().__init__(**data)

# Rumor Events
class RumorSpread(EventBase):
    """Event emitted when a rumor is spread."""
    source_entity_id: Union[str, UUID]
    target_entity_id: Union[str, UUID]
    rumor_id: Union[str, UUID]
    believability: float
    mutated: bool = False
    
    def __init__(self, **data):
        data["event_type"] = "rumor.spread"
        super().__init__(**data)

class RumorCreated(EventBase):
    """Event emitted when a new rumor is created."""
    entity_id: Union[str, UUID]
    rumor_id: Union[str, UUID]
    content: str
    rumor_type: str
    truth_value: float
    
    def __init__(self, **data):
        data["event_type"] = "rumor.created"
        super().__init__(**data)

class RumorMutated(EventBase):
    """Event emitted when a rumor mutates during spreading."""
    rumor_id: Union[str, UUID]
    old_content: str
    new_content: str
    old_truth_value: float
    new_truth_value: float
    entity_id: Union[str, UUID]
    
    def __init__(self, **data):
        data["event_type"] = "rumor.mutated"
        super().__init__(**data)

# Motif Events
class MotifChanged(EventBase):
    """Event emitted when a motif changes."""
    region_id: Optional[str] = None
    old_motif: Optional[str] = None
    new_motif: str
    intensity: int
    is_global: bool = False
    
    def __init__(self, **data):
        data["event_type"] = "motif.changed"
        super().__init__(**data)

# World State Events
class WorldStateChanged(EventBase):
    """Event emitted when world state variable changes."""
    key: str
    old_value: Any
    new_value: Any
    category: Optional[str] = None
    region: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "world_state.changed"
        super().__init__(**data)

# Relationship Events
class RelationshipChanged(EventBase):
    """Event emitted when relationship between entities changes."""
    source_id: Union[str, UUID]
    target_id: Union[str, UUID]
    relationship_type: str
    old_data: Dict[str, Any]
    new_data: Dict[str, Any]
    
    def __init__(self, **data):
        data["event_type"] = "relationship.changed"
        super().__init__(**data)

class RelationshipCreated(EventBase):
    """Event emitted when a new relationship is created."""
    source_id: Union[str, UUID]
    target_id: Union[str, UUID]
    relationship_type: str
    relationship_id: int
    data: Dict[str, Any]
    
    def __init__(self, **data):
        data["event_type"] = "relationship.created"
        super().__init__(**data)

class RelationshipUpdated(EventBase):
    """Event emitted when a relationship is updated."""
    source_id: Union[str, UUID]
    target_id: Union[str, UUID]
    relationship_type: str
    relationship_id: int
    old_data: Dict[str, Any]
    new_data: Dict[str, Any]
    
    def __init__(self, **data):
        data["event_type"] = "relationship.updated"
        super().__init__(**data)

class RelationshipRemoved(EventBase):
    """Event emitted when a relationship is removed."""
    source_id: Union[str, UUID]
    target_id: Union[str, UUID]
    relationship_type: str
    relationship_id: int
    data: Dict[str, Any]
    
    def __init__(self, **data):
        data["event_type"] = "relationship.removed"
        super().__init__(**data)

# Character Events
class CharacterCreated(EventBase):
    """Event emitted when a new character is created."""
    character_id: Union[str, UUID]
    name: str
    
    def __init__(self, **data):
        data["event_type"] = "character.created"
        super().__init__(**data)
        
class CharacterLeveledUp(EventBase):
    """Event emitted when a character levels up."""
    character_id: Union[str, UUID]
    old_level: int
    new_level: int
    
    def __init__(self, **data):
        data["event_type"] = "character.leveled_up"
        super().__init__(**data)

class CharacterUpdated(EventBase):
    """Event emitted when a character is updated."""
    character_id: Union[str, UUID]
    changes: Dict[str, Any]
    
    def __init__(self, **data):
        data["event_type"] = "character.updated"
        super().__init__(**data)

class CharacterDeleted(EventBase):
    """Event emitted when a character is deleted."""
    character_id: Union[str, UUID]
    
    def __init__(self, **data):
        data["event_type"] = "character.deleted"
        super().__init__(**data)

# Mood Events
class MoodChanged(EventBase):
    """Event emitted when a character's mood changes significantly."""
    character_id: str
    old_primary_mood: Optional[str]
    new_primary_mood: str
    old_intensity: Optional[str]
    new_intensity: str
    cause: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "character.mood_changed"
        super().__init__(**data)

# Goal Events
class GoalCreated(EventBase):
    """Event emitted when a new goal is created."""
    character_id: str
    goal_id: str
    goal_type: str
    description: str
    priority: str
    
    def __init__(self, **data):
        data["event_type"] = "character.goal_created"
        super().__init__(**data)

class GoalCompleted(EventBase):
    """Event emitted when a goal is completed."""
    character_id: str
    goal_id: str
    goal_type: str
    description: str
    
    def __init__(self, **data):
        data["event_type"] = "character.goal_completed"
        super().__init__(**data)

class GoalFailed(EventBase):
    """Event emitted when a goal is failed."""
    character_id: str
    goal_id: str
    goal_type: str
    description: str
    reason: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "character.goal_failed"
        super().__init__(**data)

class GoalAbandoned(EventBase):
    """Event emitted when a goal is abandoned."""
    character_id: str
    goal_id: str
    goal_type: str
    description: str
    reason: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "character.goal_abandoned"
        super().__init__(**data)

class GoalProgressUpdated(EventBase):
    """Event emitted when goal progress is updated."""
    character_id: str
    goal_id: str
    old_progress: float
    new_progress: float
    
    def __init__(self, **data):
        data["event_type"] = "character.goal_progress_updated"
        super().__init__(**data)

# Population Events
class PopulationChanged(EventBase):
    """Event emitted when population changes."""
    location_id: str
    old_population: int
    new_population: int
    reason: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "population.changed"
        super().__init__(**data)

# POI Events
class POIStateChanged(EventBase):
    """Event emitted when a POI changes state."""
    poi_id: str
    old_state: str
    new_state: str
    reason: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "poi.state_changed"
        super().__init__(**data)

# Faction Events
class FactionChanged(EventBase):
    """Event emitted when faction attributes change."""
    faction_id: str
    attribute: str
    old_value: Any
    new_value: Any
    
    def __init__(self, **data):
        data["event_type"] = "faction.changed"
        super().__init__(**data)

# Quest Events  
class QuestUpdated(EventBase):
    """Event emitted when a quest status or progress changes."""
    quest_id: str
    character_id: Optional[str] = None
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    old_progress: Optional[float] = None
    new_progress: Optional[float] = None
    
    def __init__(self, **data):
        data["event_type"] = "quest.updated"
        super().__init__(**data)

# Combat Events
class CombatEvent(EventBase):
    """Base class for combat-related events."""
    combat_id: str
    
    def __init__(self, **data):
        if "event_type" not in data:
            data["event_type"] = "combat.event"
        super().__init__(**data)

class CombatStarted(CombatEvent):
    """Event emitted when combat begins."""
    participants: List[str]
    location_id: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "combat.started"
        super().__init__(**data)

class CombatEnded(CombatEvent):
    """Event emitted when combat ends."""
    result: str  # "victory", "defeat", "draw", "fled"
    duration: float
    
    def __init__(self, **data):
        data["event_type"] = "combat.ended"
        super().__init__(**data)

# Time Events
class TimeAdvanced(EventBase):
    """Event emitted when in-game time advances."""
    old_time: Any
    new_time: Any
    delta: float
    
    def __init__(self, **data):
        data["event_type"] = "time.advanced"
        super().__init__(**data)

# Storage Events
class StorageEvent(EventBase):
    """Base class for storage-related events."""
    storage_id: str
    operation: str
    
    def __init__(self, **data):
        if "event_type" not in data:
            data["event_type"] = "storage.event"
        super().__init__(**data)

class GameSaved(StorageEvent):
    """Event emitted when the game is saved."""
    
    def __init__(self, **data):
        data["event_type"] = "storage.saved"
        data["operation"] = "save"
        super().__init__(**data)

class GameLoaded(StorageEvent):
    """Event emitted when the game is loaded."""
    
    def __init__(self, **data):
        data["event_type"] = "storage.loaded"
        data["operation"] = "load"
        super().__init__(**data)

# System Events
class EventLogged(EventBase):
    """Event emitted when an analytics event is logged."""
    original_event_type: str
    category: str
    
    def __init__(self, **data):
        data["event_type"] = "system.event_logged"
        super().__init__(**data) 