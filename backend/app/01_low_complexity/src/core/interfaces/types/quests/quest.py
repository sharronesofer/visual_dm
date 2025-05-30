from typing import Any, List
from enum import Enum



class QuestType(Enum):
    MAJOR = 'MAJOR'
    MINOR = 'MINOR'
    SIDE = 'SIDE'
    FACTION = 'FACTION'
    DYNAMIC = 'DYNAMIC'
class QuestStatus(Enum):
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'
class QuestEvent:
    questId: str
    type: \'QuestType\'
    status: \'QuestStatus\'
    playerId: str
    involvedNpcIds: List[str]
    outcome: \'QuestStatus\'
    factionId?: str
    tags?: List[str]
    description: str 