from typing import Any, Dict, List, Union
from enum import Enum


PropertyValue = Union[str, float, bool, None, List[PropertyValue], { [key: str]: PropertyValue }]
Properties = Dict[str, PropertyValue>
class POIType(Enum):
    CITY = 'CITY'
    DUNGEON = 'DUNGEON'
    LANDMARK = 'LANDMARK'
    QUEST = 'QUEST'
    SHOP = 'SHOP'
    TAVERN = 'TAVERN'
class POISize(Enum):
    SMALL = 'SMALL'
    MEDIUM = 'MEDIUM'
    LARGE = 'LARGE'
class POITheme(Enum):
    MEDIEVAL = 'MEDIEVAL'
    FANTASY = 'FANTASY'
    STEAMPUNK = 'STEAMPUNK'
    MODERN = 'MODERN'
class POIMetadata:
    id: str
    name: str
    type: \'POIType\'
    position: Position
    description?: str
    status?: str
    metadata?: Dict[str, str>
class POIState:
    pois: Dict[str, POI>
    activePOIs: List[str]
    currentPOI: Union[str, None]
    isLoading: bool
    error: Union[str, None]
    getPOI: Union[(id: str) => POI, None]
    getActivePOIs: List[() => POI]
    getCurrentPOI: Union[() => POI, None]
    setError: Union[(error: str, None) => None]
    clearError: () => None
    setLoading: (isLoading: bool) => None
    createPOI: Union[(poi: Omit<POI, 'chunks', 'activeChunks', 'isActive'>) => None]
    updatePOI: (id: str, updates: Partial<POI>) => None
    removePOI: (id: str) => None
    activatePOI: (id: str) => None
    deactivatePOI: (id: str) => None
    setCurrentPOI: Union[(id: str, None) => None]
    updatePlayerPosition: (position: Position) => None
    addChunk: (poiId: str, chunk: Omit<POIChunk, 'lastAccessed'>) => None
    activateChunk: (poiId: str, position: Position) => None
    deactivateChunk: (poiId: str, position: Position) => None
    removeChunk: (poiId: str, position: Position) => None
    cleanupInactiveChunks: (poiId: str, maxChunks?: float) => None
    addEntity: (poiId: str, chunkPosition: Position, entity: Omit<POIEntity, 'id'>) => None
    updateEntity: (
    poiId: str,
    chunkPosition: Position,
    entityId: str,
    updates: Partial<POIEntity>
  ) => None
    removeEntity: (poiId: str, chunkPosition: Position, entityId: str) => None
    moveEntity: (
    poiId: str,
    entityId: str,
    fromChunkPosition: Position,
    toChunkPosition: Position,
    newPosition: Position
  ) => None
    loadPOI: (id: str) => Awaitable[POIServiceResponse>
    loadPOIChunks: (
    poiId: str,
    centerPosition: Position,
    radius?: float
  ) => Awaitable[POIServiceResponse>
    savePOIState: (poiId: str) => Awaitable[POIServiceResponse>
    syncWithMapStore: (mapChunks: Dict[str, Any>) => None
    initializeFromStorage: () => None
class POILayout:
    width: float
    height: float
    rooms: List[POIRoom]
    connections: List[POIConnection]
class POIRoom:
    id: str
    type: str
    position: Position
    width: float
    height: float
    properties: Properties
class POIConnection:
    from: str
    to: str
    type: str
    properties: Properties
class POICorridor:
    id: str
    start: Position
    end: Position
    width: float
    connects: [str, str]
    features: List[POIFeature]
class POIFeature:
    id: str
    type: str
    position: Position
    properties: Properties
class POIObstacle:
    type: str
    position: Position
    width: float
    height: float
    properties: Properties
class POIEntity:
    id: str
    poiId: str
    chunkId: str
    type: str
    name: str
    position: Position
    properties: Properties
    createdAt: str
    updatedAt: str
class POIEntityState:
    health?: float
    status?: List[str]
    inventory?: \'POIInventory\'
    behavior?: \'POIBehavior\'
    dialogue?: \'POIDialogue\'
    quest?: \'POIQuest\'
class POIInventory:
    capacity: float
    items: List[POIItem]
class POIItem:
    id: str
    type: str
    quantity: float
    properties: Dict[str, Any>
class POIBehavior:
    type: str
    params: Properties
    schedule?: List[POISchedule]
    triggers?: List[POITrigger]
class POISchedule:
    time: float
    action: str
    params: Properties
class POITrigger:
    condition: str
    action: str
    params: Properties
class POIDialogue:
    conversations: Dict[str, POIConversation>
    current?: str
class POIConversation:
    id: str
    nodes: List[POIDialogueNode]
    conditions?: Properties
class POIDialogueNode:
    id: str
    text: str
    options: List[POIDialogueOption]
class POIDialogueOption:
    text: str
    nextId?: str
    actions?: List[POIAction]
    conditions?: Properties
class POIDialogueParams:
    initialText: str
    nodes: List[POIDialogueNode]
    title?: str
class POIQuest:
    id: str
    status: Union['available', 'active', 'completed', 'failed']
    objectives: List[POIQuestdictive]
    rewards: List[POIReward]
class POIQuestObjective:
    description: str
    completed: bool
    conditions?: Dict[str, Any>
class POIQuestParams:
    title: str
    description: str
    objectives: List[POIQuestdictive]
class POIInfoParams:
    title: str
    content: React.ReactNode
class POIChunk:
    id: str
    poiId: str
    position: Position
    entities: Dict[str, POIEntity>
    createdAt: str
    updatedAt: str
/**
 * Represents a specific interaction type with a POI
 */
POIInteractionType = Union['dialogue', 'quest', 'info']
/**
 * Represents a feedback type for visual effects
 */
POIVisualFeedbackType = Union['animation', 'particle', 'highlight', 'text']
/**
 * Represents a requirement for an interaction
 */
class POIRequirement:
    type: str
    value: PropertyValue
/**
 * Represents a reward for completing an interaction
 */
class POIReward:
    type: str
    value: PropertyValue
/**
 * Represents an interaction option that a user can select
 */
class POIInteractionOption:
    id: str
    text: str
    action: () => None
/**
 * Represents a complete interaction with a POI
 */
class POIInteraction:
    id: str
    type: POIInteractionType
    title: str
    description: str
    options?: List[POIInteractionOption]
    requirements?: List[POIRequirement]
/**
 * Represents an action that can be triggered during a POI interaction
 */
class POIAction:
    type: Union['dialog', 'quest', 'state', 'animation']
    params: Properties
    conditions?: Properties
    feedback?: \'POIFeedback\'
/**
 * Represents feedback that can be given during a POI interaction
 */
class POIFeedback:
    visual?: \'POIVisualFeedback\'
    audio?: \'POIAudioFeedback\'
    haptic?: \'POIHapticFeedback\'
/**
 * Represents visual feedback during a POI interaction
 */
class POIVisualFeedback:
    type: POIVisualFeedbackType
    params: Properties
    duration: float
/**
 * Represents audio feedback during a POI interaction
 */
class POIAudioFeedback:
    type: str
    source: str
    volume: float
    loop: bool
    duration: float
    params?: Properties
/**
 * Represents haptic feedback during a POI interaction
 */
class POIHapticFeedback:
    type: 'vibration'
    intensity: float
    duration: float
    pattern?: str
/**
 * Type for feedback callback functions
 */
POIFeedbackCallbacks = {
  visual?: (message: str) => None
  audio?: (soundId: str) => void
  haptic?: (pattern: str) => void
}
interface POIServiceResponse<T = unknown> {
  success: bool
  error?: str
  data?: T
}
class POILoadOptions:
    includeChunks?: bool
    radius?: float
class POIGenerationParams:
    type: \'POIType\'
    size: \'POISize\'
    theme: \'POITheme\'
    complexity: float
    seed?: str
class POIGenerationProgress:
    stage: Union['layout', 'features', 'entities', 'finalization']
    progress: float
    currentTask: str
    error?: Error
class POI:
    id: str
    name: str
    type: \'POIType\'
    size: \'POISize\'
    theme: \'POITheme\'
    position: Position
    coordinates: [float, float]
    state: Union['active', 'inactive']
    regionId: str
    description?: str
    chunks: Dict[str, POIChunk>
    createdAt: Date
    updatedAt: Date
    layout?: \'POILayout\'
    [key: str]: unknown
class POIPersistentState:
    pois: Dict[str, POI>
    activePOIs: List[str]
    currentPOI: Union[str, None]
type * from './poi'
class IPOI:
    id: str
    name: str
    coordinates: [float, float]
    type: str
    state: Union['active', 'inactive']
    regionId: str
    distanceTo(point: [float, float]): float
    getDisplayInfo(): { title: str
    description?: str
    iconUrl?: str
}
/**
 * Concrete implementation of the IPOI interface.
 */
class POI implements IPOI {
  id: str
  name: str
  coordinates: [number, number]
  type: \'POIType\'
  state: 'active' | 'inactive'
  regionId: str
  constructor(params: Dict[str, Any]) {
    this.id = params.id
    this.name = params.name
    this.coordinates = params.coordinates
    this.type = params.type
    this.state = params.state || 'active'
    this.regionId = params.regionId
    this.validateCoordinates()
  }
  /**
   * Validates that coordinates are within valid longitude/latitude ranges.
   */
  private validateCoordinates() {
    const [lng, lat] = this.coordinates
    if (lng < -180 || lng > 180 || lat < -90 || lat > 90) {
      throw new Error(`Invalid coordinates: [${lng}, ${lat}]`)
    }
  }
  /**
   * Calculates the distance in meters to another point using the Haversine formula.
   */
  distanceTo(point: [number, number]): float {
    const toRad = (deg: float) => (deg * Math.PI) / 180
    const [lng1, lat1] = this.coordinates
    const [lng2, lat2] = point
    const R = 6371000 
    const dLat = toRad(lat2 - lat1)
    const dLng = toRad(lng2 - lng1)
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) * Math.sin(dLng / 2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    return R * c
  }
  /**
   * Returns display information for the POI.
   */
  getDisplayInfo(): { title: str; description?: str; iconUrl?: str } {
    return {
      title: this.name,
      description: `${this.type} in region ${this.regionId}`,
      iconUrl: undefined, 
    }
  }
  /**
   * Changes the state of the POI.
   */
  setState(newState: 'active' | 'inactive') {
    this.state = newState
  }
  /**
   * Serializes the POI instance to a plain object for JSON.
   */
  toJSON(): object {
    return {
      id: this.id,
      name: this.name,
      coordinates: this.coordinates,
      type: this.type,
      state: this.state,
      regionId: this.regionId,
    }
  }
  /**
   * Deserializes a POI from a plain object.
   */
  static fromJSON(obj: \'POICreateDTO\' & { id: str; state?: 'active' | 'inactive'; regionId: str }): \'POI\' {
    return new POI({
      id: obj.id,
      name: obj.name,
      coordinates: [obj.position.x, obj.position.y],
      type: obj.type,
      state: obj.state || 'inactive',
      regionId: obj.regionId
    })
  }
}
class POISearchOptions:
    radius?: float
    type?: \'POIType\'
    tags?: List[str]
    theme?: \'POITheme\'
    size?: \'POISize\'
class POICreateDTO:
    name: str
    type: \'POIType\'
    size: \'POISize\'
    theme: \'POITheme\'
    position: Position
    description?: str
    regionId?: str
    [key: str]: unknown
POIUpdateDTO = Partial[POICreateDTO]