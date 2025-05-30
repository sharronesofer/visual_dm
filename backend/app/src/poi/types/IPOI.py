from typing import Any, Dict, List


  POIType, 
  POISubtype, 
  Coordinates, 
  ConnectionPoint, 
  ThematicElements, 
  StateTracking 
} from './POITypes'
/**
 * Base interface for all Points of Interest (POIs) in the game world
 */
class IPOI:
    id: str
    name: str
    type: POIType
    subtype: POISubtype
    description: str
    coordinates: Coordinates
    boundingBox: Dict[str, Any][]
  npcs: List[string] 
  items: List[string] 
  quests: List[string] 
  thematicElements: ThematicElements
  stateTracking: StateTracking
  isActive: bool
  isDiscovered: bool
  isExplored: bool
  canExpand: bool
  expansionRules?: {
    direction: 'north' | 'south' | 'east' | 'west' | 'up' | 'down'
    conditions: List[string]
    probability: float
  }[]
  serialize(): Record<string, unknown>
  deserialize(data: Record<string, unknown>): void
  activate(): void
  deactivate(): void
  discover(): void
  explore(): void
  validate(): bool
  validateConnections(): bool
  validateThematicCoherence(): bool
} 