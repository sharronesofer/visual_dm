from typing import Any, Dict, List


  POIType,
  POISubtype,
  Coordinates,
  ConnectionPoint,
  ThematicElements,
  StateTracking
} from '../types/POITypes'
/**
 * Abstract base class implementing common POI functionality
 */
abstract class BasePOI implements IPOI {
  id: str
  name: str
  type: POIType
  subtype: POISubtype
  description: str
  coordinates: Coordinates
  boundingBox: Dict[str, Any]
  connections: List[ConnectionPoint]
  adjacentPOIs: List[string]
  features: Dict[str, Any][]
  npcs: List[string]
  items: List[string]
  quests: List[string]
  thematicElements: ThematicElements
  stateTracking: StateTracking
  isActive: bool
  isDiscovered: bool
  isExplored: bool
  canExpand: bool
  expansionRules?: { direction: 'north' | 'south' | 'east' | 'west' | 'up' | 'down'; conditions: List[string]; probability: float; }[]
  constructor(
    id: str,
    name: str,
    type: POIType,
    subtype: POISubtype,
    coordinates: Coordinates,
    thematicElements: ThematicElements
  ) {
    this.id = id
    this.name = name
    this.type = type
    this.subtype = subtype
    this.coordinates = coordinates
    this.thematicElements = thematicElements
    this.description = ''
    this.boundingBox = { width: 1, height: 1, depth: 1 }
    this.connections = []
    this.adjacentPOIs = []
    this.features = []
    this.npcs = []
    this.items = []
    this.quests = []
    this.isActive = false
    this.isDiscovered = false
    this.isExplored = false
    this.canExpand = true
    this.stateTracking = {
      version: 1,
      lastModified: new Date(),
      modifiedBy: 'system',
      changeHistory: [{
        timestamp: new Date(),
        type: 'creation',
        details: 'POI created'
      }]
    }
  }
  serialize(): Record<string, unknown> {
    return {
      id: this.id,
      name: this.name,
      type: this.type,
      subtype: this.subtype,
      description: this.description,
      coordinates: this.coordinates,
      boundingBox: this.boundingBox,
      connections: this.connections,
      adjacentPOIs: this.adjacentPOIs,
      features: this.features,
      npcs: this.npcs,
      items: this.items,
      quests: this.quests,
      thematicElements: this.thematicElements,
      stateTracking: Dict[str, Any]))
      },
      isActive: this.isActive,
      isDiscovered: this.isDiscovered,
      isExplored: this.isExplored,
      canExpand: this.canExpand,
      expansionRules: this.expansionRules
    }
  }
  deserialize(data: Record<string, unknown>): void {
    if (typeof data.stateTracking === 'object' && data.stateTracking) {
      const stateData = data.stateTracking as {
        lastModified: str
        changeHistory: Array<{
          timestamp: str
          type: 'creation' | 'modification' | 'expansion' | 'deletion'
          details: str
        }>
      }
      this.stateTracking = {
        ...data.stateTracking as StateTracking,
        lastModified: new Date(stateData.lastModified),
        changeHistory: stateData.changeHistory.map(ch => ({
          ...ch,
          timestamp: new Date(ch.timestamp)
        }))
      }
      const { stateTracking, ...restData } = data
      const typedData = restData as {
        isActive: bool
        isDiscovered: bool
        isExplored: bool
        canExpand: bool
      }
      Object.assign(this, {
        ...restData,
        isActive: Boolean(typedData.isActive),
        isDiscovered: Boolean(typedData.isDiscovered),
        isExplored: Boolean(typedData.isExplored),
        canExpand: Boolean(typedData.canExpand)
      })
    } else {
      throw new Error('Invalid state tracking data in POI deserialization')
    }
  }
  activate(): void {
    this.isActive = true
    this.trackChange('modification', 'POI activated')
  }
  deactivate(): void {
    this.isActive = false
    this.trackChange('modification', 'POI deactivated')
  }
  discover(): void {
    this.isDiscovered = true
    this.trackChange('modification', 'POI discovered')
  }
  explore(): void {
    this.isExplored = true
    this.trackChange('modification', 'POI explored')
  }
  validate(): bool {
    return (
      this.validateBasicProperties() &&
      this.validateConnections() &&
      this.validateThematicCoherence()
    )
  }
  validateConnections(): bool {
    return this.connections.every(connection => 
      this.validateCoordinates(connection.sourceCoords) &&
      this.validateCoordinates(connection.targetCoords)
    )
  }
  validateThematicCoherence(): bool {
    return (
      this.thematicElements.biome &&
      this.thematicElements.climate &&
      this.thematicElements.era &&
      this.thematicElements.culture &&
      this.thematicElements.dangerLevel >= 0 &&
      this.thematicElements.dangerLevel <= 10
    )
  }
  protected validateBasicProperties(): bool {
    return (
      !!this.id &&
      !!this.name &&
      !!this.type &&
      !!this.subtype &&
      this.validateCoordinates(this.coordinates)
    )
  }
  protected validateCoordinates(coords: Coordinates): bool {
    return (
      typeof coords.x === 'number' &&
      typeof coords.y === 'number' &&
      typeof coords.z === 'number' &&
      typeof coords.level === 'number'
    )
  }
  protected trackChange(type: 'creation' | 'modification' | 'expansion' | 'deletion', details: str): void {
    this.stateTracking.version++
    this.stateTracking.lastModified = new Date()
    this.stateTracking.changeHistory.push({
      timestamp: new Date(),
      type,
      details
    })
  }
} 