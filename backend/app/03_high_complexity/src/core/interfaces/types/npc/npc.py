from typing import Any, Dict, List, Union



class NPCPosition:
    x: float
    y: float
class NPCGoal:
    id: str
    type: str
    priority: float
    progress: float
    deadline?: float
    dependencies?: List[str]
    conflicts?: List[str]
    requirements?: List[{
    resources?: str]
    relationships?: { [key: str]: float
    skills?: string[]
  }
}
class NPCInteraction:
    timestamp: float
    type: str
    targetId: str
    outcome: Union['positive', 'neutral', 'negative']
class NPCStats:
    strength: float
    dexterity: float
    constitution: float
    intelligence: float
    wisdom: float
    charisma: float
    perception: float
    leadership: float
class NPCPersonality:
    aggressiveness: float
    cautiousness: float
    friendliness: float
    ambition: float
    loyalty: float
    leadership: float
    adaptability: float
    curiosity: float
    empathy: float
    integrity: float
    openness: float
    trustworthiness: float
    conformity: float
    diplomacy: float
    extraversion: float
class NPCData:
    id: str
    name: str
    faction: Faction
    position: Position
    traits: List[str]
    values: List[str]
    goals: List[NPCGoal]
    stats: \'NPCStats\'
    personality: Dict[str, Any]
      leadershipStyle: 'dominant' | 'collaborative' | 'supportive'
      conflictResolution: 'aggressive' | 'diplomatic' | 'avoidant'
    }
  }
  skills: Map<string, number>
  inventory: List[any]
  relationships: Map<string, { score: float }>
  memories: List[Memory]
  location: str
  groupAffiliations: Dict[str, Any][]
  economicData?: {
    wealth: float
    income: float
    expenses: float
    marketPreferences: Dict[str, Any]
  }
  socialStatus: Dict[str, Any][]
  }
  learningProgress: Map<string, {
    skillId: str
    currentLevel: float
    experience: float
    teachingAbility: float
  }>
  recentInteractions: Dict[str, Any][]
  interactionHistory: Dict[str, Any]>
    group: Map<string, {
      role: str
      contribution: float
      conflicts: float
      lastActive: float
      satisfaction: float
    }>
  }
  groupFormationPreferences: Dict[str, Any]
    rolePreferences: List[string]
    purposeWeights: Map<string, number>
    minTrustThreshold: float
  }
} 