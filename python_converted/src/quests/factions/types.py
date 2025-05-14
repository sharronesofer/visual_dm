from typing import Any, Dict, List, Union


{ FactionType } from '../../types/factions/faction'
/**
 * Represents a resource owned or managed by a faction (e.g., gold, territory, influence)
 */
class FactionResource:
    type: str
    amount: float
/**
 * Represents a value or trait of a faction (e.g., honor, aggression, diplomacy)
 */
class FactionValue:
    key: str
    value: float
/**
 * Represents the persistent data for a faction, including relationships, values, and resources
 */
class FactionData:
    id: FactionType
    name: str
    description: str
    relationships: Dict[FactionType, float>
    values: Dict[str, float>
    resources: Dict[str, float>
    standing: float
    tier: float
/**
 * Main profile for a faction, used at runtime
 */
class FactionProfile:
    id: FactionType
    name: str
    description: str
    relationships: Dict[FactionType, float>
    values: Dict[str, float>
    resources: Dict[str, float>
    standing: float
    tier: float
class FactionQuestTemplate:
    factionId: FactionType
    questType: QuestType
    factionRequirements: Dict[str, Any]
      territoryAccess?: string[]
    }
  }
  factionObjectives: List[QuestObjective]
  consequences?: WorldStateChange[]
  diplomaticOptions?: {
    negotiationApproaches: Dict[str, Any][]
    resourceExchangeOptions: Dict[str, Any]
    }[]
    meetingLocations: Dict[str, Any][]
    fallbackPlans: Dict[str, Any][]
  }
}
class FactionQuestConfig:
    mutuallyExclusiveThreshold: float
    standingGainMultiplier: float
    reputationGainMultiplier: float
    defaultMinimumStanding: float
    defaultMaximumStanding: float
/**
 * Represents a faction-specific objective within a quest
 */
class FactionObjective:
    type: Union['diplomacy', 'combat', 'stealth', 'trade', 'exploration']
    difficulty: float
    description: str
    factionImpact: Dict[str, Any]
  }[]
}
/**
 * Configuration for the faction quest template generator
 */
class FactionQuestGeneratorConfig:
    baseTemplateModifiers: Dict[str, Any]>
  competingQuestProbability: float
  specialRewardProbability: float
}
/**
 * Represents a faction-specific stage in a quest
 */
class FactionQuestStage:
    factionRequirements?: {
    standing: float
    specialItems?: List[str]
    specialAbilities?: List[str]
  factionBranches: List[FactionQuestBranch]
}
/**
 * Represents a faction-specific branch in quest progression
 */
class FactionQuestBranch:
    factionRequirements?: {
    minimumStanding: float
    maximumStanding: float
    diplomaticStatus?: Union['NEUTRAL', 'FRIENDLY', 'HOSTILE', 'ALLIED']
  factionConsequences?: WorldStateChange[]
} 