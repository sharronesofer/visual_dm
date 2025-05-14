from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from app.websockets.event_types import EventType

@dataclass
class EventPayload:
    event_type: EventType
    timestamp: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(event_type: EventType, data: Dict[str, Any], metadata: Dict[str, Any] = None) -> 'EventPayload':
        return EventPayload(
            event_type=event_type,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            data=data,
            metadata=metadata or {}
        )

def validate_payload(payload: EventPayload) -> bool:
    if not isinstance(payload.event_type, EventType):
        return False
    if not isinstance(payload.timestamp, str):
        return False
    if not isinstance(payload.data, dict):
        return False
    if not isinstance(payload.metadata, dict):
        return False
    return True

@dataclass
class TurnChangePayload:
    combat_id: str
    current_actor: str
    next_actor: str
    round_number: int

@dataclass
class InitiativeUpdatePayload:
    combat_id: str
    actor_id: str
    new_initiative: int
    initiative_order: List[str]

@dataclass
class CombatResultPayload:
    combat_id: str
    action_type: str
    actor_id: str
    target_ids: List[str]
    damage: Optional[int] = None
    effects: Optional[List[str]] = None

@dataclass
class CombatSummaryPayload:
    combat_id: str
    duration: float
    participants: List[str]
    outcome: str
    rewards: Optional[List[str]] = None

@dataclass
class LocationChangePayload:
    npc_id: str
    previous_location: str
    new_location: str
    movement_type: str

@dataclass
class BehaviorChangePayload:
    npc_id: str
    previous_behavior: str
    new_behavior: str
    trigger: str

@dataclass
class TimeChangePayload:
    world_id: str
    new_time: str  # ISO timestamp or game time string
    previous_time: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WeatherUpdatePayload:
    world_id: str
    new_weather: str
    previous_weather: str
    affected_regions: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FactionUpdatePayload:
    faction_id: str
    previous_status: str
    new_status: str
    affected_factions: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GlobalEventPayload:
    event_id: str
    event_type: str
    description: str
    priority: str  # e.g., 'normal', 'high', 'critical'
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QuestAvailablePayload:
    quest_id: str
    quest_name: str
    eligible_players: List[str]
    location: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QuestProgressPayload:
    quest_id: str
    player_id: str
    progress: float  # 0.0 - 1.0
    stage: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QuestCompletePayload:
    quest_id: str
    player_id: str
    success: bool
    rewards: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict) 