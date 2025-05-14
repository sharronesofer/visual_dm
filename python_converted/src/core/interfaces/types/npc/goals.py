from typing import Any, Dict, List
from enum import Enum


class NPCGoal:
    id: str
    type: \'GoalType\'
    priority: float
    description: str
    status: \'GoalStatus\'
    progress: float
    deadline?: float
    dependencies: List[str]
    subgoals: List[str]
    requirements: Dict[str, Any][]
    relationships?: {
      npcId: str
      minValue: float
    }[]
    conditions?: {
      type: str
      value: Any
    }[]
  }
  rewards?: {
    reputation?: float
    resources?: {
      type: str
      amount: float
    }[]
    relationships?: {
      npcId: str
      change: float
    }[]
  }
  completion: Dict[str, Any]
}
class GoalType(Enum):
    PERSONAL = 'personal'
    PROFESSIONAL = 'professional'
    SOCIAL = 'social'
    ECONOMIC = 'economic'
    FACTION = 'faction'
    QUEST = 'quest'
class GoalStatus(Enum):
    ACTIVE = 'active'
    COMPLETED = 'completed'
    FAILED = 'failed'
    ABANDONED = 'abandoned'
    BLOCKED = 'blocked'
    DEFERRED = 'deferred' 