from enum import Enum, auto
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class BaseEventType(Enum):
    """Base class for event types"""
    pass

class BaseEvent(BaseModel):
    """Base class for all events in the system"""
    event_type: str = Field(..., description="Type of event")
    model_config = {"extra": "allow"}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to a dictionary"""
        return self.model_dump()

class RelationshipEventType(str, Enum):
    """Event types for relationship events"""
    RELATIONSHIP_CHANGED = "relationship_changed"
    REPUTATION_CHANGED = "reputation_changed"

class RelationshipEvent(BaseEvent):
    """Event for relationship changes"""
    source_id: int = Field(..., description="ID of the source entity")
    target_id: int = Field(..., description="ID of the target entity")
    relationship_type: str = Field(..., description="Type of relationship")
    relationship_data: Optional[Dict[str, Any]] = Field(default=None, description="Relationship data")
    action: str = Field(..., description="Action taken: created, updated, or deleted")

class CharacterEventType(str, Enum):
    """Event types for character events"""
    CHARACTER_CREATED = "character_created"
    CHARACTER_UPDATED = "character_updated"
    CHARACTER_DELETED = "character_deleted"
    LEVEL_UP = "level_up"
    SKILL_CHANGED = "skill_changed"

class CharacterEvent(BaseEvent):
    """Event for character changes"""
    character_id: int = Field(..., description="ID of the character")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")

class QuestEventType(str, Enum):
    """Event types for quest events"""
    QUEST_STARTED = "quest_started"
    QUEST_COMPLETED = "quest_completed"
    QUEST_FAILED = "quest_failed"
    QUEST_PROGRESS = "quest_progress"

class QuestEvent(BaseEvent):
    """Event for quest changes"""
    character_id: int = Field(..., description="ID of the character")
    quest_id: int = Field(..., description="ID of the quest")
    status: str = Field(..., description="Quest status")
    progress: Optional[float] = Field(default=None, description="Quest progress")

class LocationEventType(str, Enum):
    """Event types for location events"""
    LOCATION_ENTERED = "location_entered"
    LOCATION_EXITED = "location_exited"
    LOCATION_DISCOVERED = "location_discovered"

class LocationEvent(BaseEvent):
    """Event for location changes"""
    character_id: int = Field(..., description="ID of the character")
    location_id: int = Field(..., description="ID of the location")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")

class CombatEventType(str, Enum):
    """Event types for combat events"""
    COMBAT_STARTED = "combat_started"
    COMBAT_ENDED = "combat_ended"
    COMBAT_TURN = "combat_turn"
    ATTACK = "attack"
    DAMAGE = "damage"
    HEAL = "heal"

class CombatEvent(BaseEvent):
    """Event for combat changes"""
    combat_id: int = Field(..., description="ID of the combat")
    source_id: Optional[int] = Field(default=None, description="ID of the source (attacker/healer)")
    target_id: Optional[int] = Field(default=None, description="ID of the target")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")

class InventoryEventType(str, Enum):
    """Event types for inventory events"""
    ITEM_ADDED = "item_added"
    ITEM_REMOVED = "item_removed"
    ITEM_USED = "item_used"
    ITEM_EQUIPPED = "item_equipped"
    ITEM_UNEQUIPPED = "item_unequipped"
    
class InventoryEvent(BaseEvent):
    """Event for inventory changes"""
    character_id: int = Field(..., description="ID of the character")
    item_id: int = Field(..., description="ID of the item")
    quantity: Optional[int] = Field(default=None, description="Quantity affected")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data") 
