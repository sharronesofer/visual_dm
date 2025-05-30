from typing import Any, Dict, List, Union
from enum import Enum



class FactionType(Enum):
    MERCHANTS = 'MERCHANTS'
    WARRIORS = 'WARRIORS'
    SCHOLARS = 'SCHOLARS'
    NOBLES = 'NOBLES'
    OUTLAWS = 'OUTLAWS'
    RELIGIOUS = 'RELIGIOUS'
    NEUTRAL = 'NEUTRAL'
class FactionRelationship:
    faction: \'FactionType\'
    attitude: float
    lastInteraction: float
class Faction:
    type: \'FactionType\'
    name: str
    description: str
    influence: float
    territory: List[str]
    relationships: Dict[FactionType, FactionRelationship>
    resources: Dict[str, float>
    goals: List[str]
    activeMembers: Set[str>
class FactionProfile:
    id: \'FactionType\'
    name: str
    description: str
    values: Dict[str, Any]
  relationships: Map<FactionType, number>
  tier: float
  reputation: float
}
class FactionStanding:
    reputation: float
    tier: float
    completedQuests: float
    failedQuests: float
    specialActions: List[{
    type: str
    impact: float
    timestamp: float>
}
QuestType = Union['combat', 'diplomacy', 'stealth', 'trade', 'exploration'] 