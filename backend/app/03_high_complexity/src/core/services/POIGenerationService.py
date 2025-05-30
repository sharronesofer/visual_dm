from typing import Any, Dict, List



  POI,
  POIGenerationParams,
  POIGenerationProgress,
  POILayout,
  POIFeature,
  POIEntity,
  POIRoom,
  POIConnection,
} from '../types/poi'
const POITypeMap: Record<string, POIType> = {
  city: POIType.SETTLEMENT,
  town: POIType.SETTLEMENT,
  village: POIType.SETTLEMENT,
  dungeon: POIType.DUNGEON,
  landmark: POIType.LANDMARK,
  resource: POIType.RESOURCE,
}
const POISubtypeMap: Record<string, POISubtype> = {
  city: POISubtype.CITY,
  town: POISubtype.TOWN,
  village: POISubtype.VILLAGE,
  dungeon: POISubtype.CAVE,
  landmark: POISubtype.MONUMENT,
  resource: POISubtype.MINE,
}
function createPOIObject(params: Dict[str, Any]) {
  return { ...params }
}
class POIGenerationService {
  private static instance: \'POIGenerationService\'
  private progressCallback?: (progress: POIGenerationProgress) => void
  private random: () => number
  private idGen: () => string
  private now: () => string
  private constructor(random?: () => number, idGen?: () => string, now?: () => string) {
    this.random = random || Math.random
    this.idGen = idGen || uuidv4
    this.now = now || (() => new Date().toISOString())
  }
  public static getInstance(random?: () => number, idGen?: () => string, now?: () => string) {
    if (!POIGenerationService.instance) {
      POIGenerationService.instance = new POIGenerationService(random, idGen, now)
    }
    return POIGenerationService.instance
  }
  public setProgressCallback(callback: (progress: POIGenerationProgress) => void) {
    this.progressCallback = callback
  }
  private updateProgress(
    stage: POIGenerationProgress['stage'],
    progress: float,
    currentTask: str
  ) {
    if (this.progressCallback) {
      this.progressCallback({
        stage,
        progress,
        currentTask,
      })
    }
  }
  private async generateLayout(params: POIGenerationParams): Promise<POILayout> {
    this.updateProgress('layout', 0, 'Initializing layout generation')
    const numRooms = this.calculateRoomCount(params)
    const rooms: List[POIRoom] = []
    const connections: List[POIConnection] = []
    const startingRoomId = this.idGen()
    const layoutDimensions = this.calculateLayoutDimensions(params.size)
    const entrancePosition = this.calculateEntrancePosition(layoutDimensions)
    rooms.push({
      id: startingRoomId,
      type: 'entrance',
      position: entrancePosition,
      width: 5,
      height: 5,
      properties: Dict[str, Any]`,
      },
    })
    for (let i = 1; i < numRooms; i++) {
      const roomId = this.idGen()
      const room: POIRoom = {
        id: roomId,
        type: this.getRoomType(params, i),
        position: this.calculateRoomPosition(layoutDimensions, rooms),
        width: Math.floor(this.random() * 5) + 3,
        height: Math.floor(this.random() * 5) + 3,
        properties: Dict[str, Any]`,
          description: `A room in this ${params.type}`,
        },
      }
      const connectTo = rooms[Math.floor(this.random() * rooms.length)]
      connections.push({
        from: connectTo.id,
        to: roomId,
        type: 'door',
        properties: Dict[str, Any],
      })
      rooms.push(room)
    }
    return {
      width: layoutDimensions.width,
      height: layoutDimensions.height,
      rooms,
      connections,
    }
  }
  private calculateLayoutDimensions(size: POIGenerationParams['size']): {
    width: float
    height: float
  } {
    const baseDimension = {
      tiny: 20,
      small: 30,
      medium: 50,
      large: 80,
      huge: 120,
    }[size]
    return {
      width: baseDimension,
      height: baseDimension,
    }
  }
  private calculateEntrancePosition(dimensions: Dict[str, Any]): Position {
    return {
      x: Math.floor(dimensions.width / 2),
      y: dimensions.height - 1, 
    }
  }
  private calculateExitPositions(
    dimensions: Dict[str, Any],
    rooms: List[POIRoom]
  ): Position[] {
    return [
      {
        x: Math.floor(dimensions.width / 2),
        y: 0,
      },
    ]
  }
  private calculateRoomPosition(
    dimensions: Dict[str, Any],
    existingRooms: List[POIRoom]
  ): Position {
    return {
      x: Math.floor(this.random() * (dimensions.width - 10)) + 5,
      y: Math.floor(this.random() * (dimensions.height - 10)) + 5,
    }
  }
  private getRoomType(params: POIGenerationParams, index: float): str {
    const roomTypes = {
      city: ['residential', 'commercial', 'government', 'religious', 'military'],
      town: ['residential', 'shop', 'tavern', 'smithy', 'temple'],
      village: ['house', 'farm', 'storage', 'community', 'crafting'],
      dungeon: ['chamber', 'corridor', 'vault', 'ritual', 'prison'],
      landmark: ['monument', 'natural', 'magical', 'historical', 'sacred'],
    }[params.type] || ['generic']
    return roomTypes[index % roomTypes.length]
  }
  private calculateRoomCount(params: POIGenerationParams): float {
    const baseCount = {
      tiny: 3,
      small: 5,
      medium: 8,
      large: 12,
      huge: 20,
    }[params.size]
    const typeMultiplier =
      {
        city: 2,
        town: 1.5,
        village: 1,
        dungeon: 1.2,
        landmark: 0.8,
        wilderness: 1,
        mixed: 1.2,
      }[params.type] ?? 1
    return Math.floor(baseCount * typeMultiplier)
  }
  private getRandomDirection(): str {
    const directions = ['north', 'south', 'east', 'west']
    return directions[Math.floor(this.random() * directions.length)]
  }
  private getOppositeDirection(direction: str): str {
    const opposites: Record<string, string> = {
      north: 'south',
      south: 'north',
      east: 'west',
      west: 'east',
    }
    return opposites[direction] || direction
  }
  private async generateFeatures(
    params: POIGenerationParams,
    layout: POILayout
  ): Promise<POIFeature[]> {
    this.updateProgress('features', 0, 'Starting feature generation')
    const features: List[POIFeature] = []
    const totalRooms = layout.rooms.length
    for (let i = 0; i < totalRooms; i++) {
      this.updateProgress(
        'features',
        (i / totalRooms) * 100,
        `Generating features for room ${i + 1}`
      )
      const numFeatures = Math.floor(this.random() * 3) + 1
      const room = layout.rooms[i]
      for (let j = 0; j < numFeatures; j++) {
        features.push({
          id: this.idGen(),
          type: this.getRandomFeatureType(params),
          position: Dict[str, Any],
          properties: Dict[str, Any]`,
            description: `A feature in this ${params.type}`,
          },
        })
      }
    }
    return features
  }
  private getRandomFeatureType(params: POIGenerationParams): str {
    const featureTypes = {
      city: ['building', 'market', 'fountain', 'statue'],
      town: ['shop', 'inn', 'well', 'garden'],
      village: ['house', 'farm', 'well', 'shrine'],
      dungeon: ['trap', 'treasure', 'altar', 'barrier'],
      landmark: ['monument', 'ruin', 'natural formation', 'magical anomaly'],
    }[params.type] || ['generic']
    return featureTypes[Math.floor(this.random() * featureTypes.length)]
  }
  private async generateEntities(
    params: POIGenerationParams,
    layout: POILayout,
    poiId: str
  ): Promise<POIEntity[]> {
    this.updateProgress('entities', 0, 'Starting entity generation')
    const entities: List[POIEntity] = []
    const totalRooms = layout.rooms.length
    for (let i = 0; i < totalRooms; i++) {
      this.updateProgress(
        'entities',
        (i / totalRooms) * 100,
        `Generating entities for room ${i + 1}`
      )
      const numEntities = Math.floor(this.random() * 2) + 1
      const room = layout.rooms[i]
      for (let j = 0; j < numEntities; j++) {
        const now = new Date().toISOString()
        entities.push({
          id: this.idGen(),
          poiId,
          chunkId: room.id,
          type: this.getRandomEntityType(params),
          name: `Entity ${entities.length + 1}`,
          position: Dict[str, Any],
          properties: Dict[str, Any]`,
            description: `An entity in this ${params.type}`,
            stats: Dict[str, Any],
            inventory: [],
            interactions: [],
          },
          createdAt: now,
          updatedAt: now,
        })
      }
    }
    return entities
  }
  private getRandomEntityType(params: POIGenerationParams): str {
    const entityTypes = {
      city: ['merchant', 'guard', 'noble', 'citizen'],
      town: ['shopkeeper', 'innkeeper', 'farmer', 'craftsman'],
      village: ['villager', 'elder', 'farmer', 'hunter'],
      dungeon: ['monster', 'undead', 'cultist', 'guardian'],
      landmark: ['guardian', 'pilgrim', 'scholar', 'spirit'],
    }[params.type] || ['generic']
    return entityTypes[Math.floor(this.random() * entityTypes.length)]
  }
  public async generatePOI(params: POIGenerationParams): Promise<ReturnType<typeof createPOIObject>> {
    try {
      const layout = await this.generateLayout(params)
      const mappedType = POITypeMap[(params.type as string).toLowerCase()] || POIType.SETTLEMENT
      const mappedSubtype = POISubtypeMap[(params.type as string).toLowerCase()] || POISubtype.TOWN
      const integrationResult = POIIntegrationSystem.generateForPOI({
        poiType: mappedType,
        poiSubtype: mappedSubtype,
        dangerLevel: 5,
        bounds: Dict[str, Any],
        thematicElements: Dict[str, Any]
      })
      const features = await this.generateFeatures(params, layout)
      const entities = await this.generateEntities(params, layout, layout.rooms[0]?.id || '')
      this.updateProgress('finalization', 0, 'Distributing features and entities')
      this.distributeToRooms(layout, features, entities)
      (layout as any).buildings = integrationResult.buildings
      (layout as any).roads = integrationResult.roads
      this.updateProgress('finalization', 50, 'Creating POI object')
      const now = new Date()
      const poi = createPOIObject({
        id: this.idGen(),
        name: `${params.theme} ${params.type}`,
        type: params.type,
        size: params.size,
        theme: params.theme,
        description: `A ${params.size} ${params.theme} ${params.type}`,
        layout,
        position: layout.rooms[0]?.position || { x: 0, y: 0 },
        coordinates: [layout.rooms[0]?.position.x || 0, layout.rooms[0]?.position.y || 0],
        state: 'active',
        regionId: 'default-region',
        createdAt: now,
        updatedAt: now,
        chunks: {},
        activeChunks: [],
        isActive: true,
        properties: Dict[str, Any],
      })
      this.updateProgress('finalization', 100, 'POI generation complete')
      return poi
    } catch (error) {
      if (this.progressCallback) {
        this.progressCallback({
          stage: 'finalization',
          progress: 0,
          currentTask: 'Generation failed',
          error: error as Error,
        })
      }
      throw error
    }
  }
  private distributeToRooms(layout: POILayout, features: List[POIFeature], entities: List[POIEntity]) {
    let featureIndex = 0
    let entityIndex = 0
    for (const room of layout.rooms) {
      if (!Array.isArray(room.properties.features)) room.properties.features = []
      if (!Array.isArray(room.properties.entities)) room.properties.entities = []
      const numFeatures = Math.floor(this.random() * 3) + 1
      for (let i = 0; i < numFeatures && featureIndex < features.length; i++) {
        (room.properties.features as any[]).push(features[featureIndex++])
      }
      const numEntities = Math.floor(this.random() * 2) + 1
      for (let i = 0; i < numEntities && entityIndex < entities.length; i++) {
        (room.properties.entities as any[]).push(entities[entityIndex++])
      }
    }
  }
}
default POIGenerationService