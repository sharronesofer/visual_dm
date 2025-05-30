from typing import Any, Dict, List


class CacheKey:
    buildingType: BuildingType
    width: float
    length: float
    height: float
    region?: str
    culture?: str
class CacheEntry:
    params: InteriorParams
    layout: InteriorLayout
    timestamp: float
class NPCZone:
    id: str
    type: NPCZoneType
    area: Dict[str, Any]
class InteractiveObject:
    id: str
    type: InteractivedictType
    position: Vector2
    rotation: float
    roomId: str
class InteriorGenerator {
  private templateManager: InteriorTemplateManager
  private layoutCache: Map<string, CacheEntry> = new Map()
  private readonly CACHE_EXPIRY_MS = 30 * 60 * 1000 
  private readonly DOOR_SPACING = 2 
  private rooms: List[Room] = []
  private template: Dict[str, Any]>
    interactiveObjects: Array<{
      roomType: str
      objectType: InteractiveObjectType
      count: float
      requiredSpace: float
      placementRules: Array<{
        type: InteractiveObjectPlacementType
        parameters: Dict[str, Any]
      }>
    }>
  }
  constructor(
    private readonly params: InteriorParams,
    private readonly templateManager: InteriorTemplateManager
  ) {
    this.templateManager = templateManager
    this.template = templateManager.getTemplateForBuilding(params.buildingType)
  }
  generate(params: InteriorParams): InteriorLayout {
    const cached = this.getCachedLayout(params)
    if (cached) return cached
    const template = this.templateManager.getTemplateForBuilding(params.buildingType)
    if (!template) {
      throw new Error(`No template found for building type ${params.buildingType}`)
    }
    const bsp = new BSPLayout(params)
    let rooms = bsp.generateRooms()
    rooms = rooms.map((room, i) => ({
      ...room,
      type: template.roomLayouts[i % template.roomLayouts.length]?.type || 'generic'
    }))
    const doors = this.generateDoors(rooms, template)
    const furniturePlacer = new FurniturePlacer()
    const furniture = furniturePlacer.placeFurniture(rooms)
    const decorationPlacer = new DecorationPlacer()
    const decorations = decorationPlacer.placeDecorations(rooms, template.decorationSchemes)
    const layout = {
      rooms,
      doors,
      furniture,
      decorations
    }
    this.cacheLayout(params, layout)
    return layout
  }
  private generateDoors(rooms: List[Room], template: Any): Door[] {
    const doors: List[Door] = []
    const processedPairs = new Set<string>()
    const getPairKey = (r1: str, r2: str) => [r1, r2].sort().join('-')
    for (const room1 of rooms) {
      for (const room2 of rooms) {
        if (room1.id === room2.id) continue
        const pairKey = getPairKey(room1.id, room2.id)
        if (processedPairs.has(pairKey)) continue
        processedPairs.add(pairKey)
        if (this.areRoomsAdjacent(room1, room2)) {
          const room1Layout = template.roomLayouts.find((l: Any) => l.type === room1.type)
          const room2Layout = template.roomLayouts.find((l: Any) => l.type === room2.type)
          if (this.canRoomsConnect(room1Layout, room2Layout)) {
            const doorPos = this.findDoorPosition(room1, room2, doors)
            if (doorPos) {
              doors.push({
                fromRoom: room1.id,
                toRoom: room2.id,
                x: doorPos.x,
                y: doorPos.y
              })
            }
          }
        }
      }
    }
    return doors
  }
  private areRoomsAdjacent(room1: Room, room2: Room): bool {
    const shareVerticalWall = (
      Math.abs((room1.x + room1.width) - room2.x) <= 1 ||
      Math.abs((room2.x + room2.width) - room1.x) <= 1
    ) && (
      Math.max(room1.y, room2.y) < Math.min(room1.y + room1.length, room2.y + room2.length)
    )
    const shareHorizontalWall = (
      Math.abs((room1.y + room1.length) - room2.y) <= 1 ||
      Math.abs((room2.y + room2.length) - room1.y) <= 1
    ) && (
      Math.max(room1.x, room2.x) < Math.min(room1.x + room1.width, room2.x + room2.width)
    )
    return shareVerticalWall || shareHorizontalWall
  }
  private canRoomsConnect(room1Layout: Any, room2Layout: Any): bool {
    if (!room1Layout || !room2Layout) return true 
    return (
      room1Layout.requiredConnections.includes(room2Layout.type) ||
      room1Layout.optionalConnections.includes(room2Layout.type) ||
      room2Layout.requiredConnections.includes(room1Layout.type) ||
      room2Layout.optionalConnections.includes(room1Layout.type)
    )
  }
  private findDoorPosition(room1: Room, room2: Room, existingDoors: List[Door]): Vector2 | null {
    let sharedWallStart: Vector2
    let sharedWallEnd: Vector2
    if (Math.abs((room1.x + room1.width) - room2.x) <= 1 || Math.abs((room2.x + room2.width) - room1.x) <= 1) {
      const x = Math.abs((room1.x + room1.width) - room2.x) <= 1 ? room1.x + room1.width : room1.x
      const y1 = Math.max(room1.y, room2.y)
      const y2 = Math.min(room1.y + room1.length, room2.y + room2.length)
      sharedWallStart = { x, y: y1 }
      sharedWallEnd = { x, y: y2 }
    } else {
      const y = Math.abs((room1.y + room1.length) - room2.y) <= 1 ? room1.y + room1.length : room1.y
      const x1 = Math.max(room1.x, room2.x)
      const x2 = Math.min(room1.x + room1.width, room2.x + room2.width)
      sharedWallStart = { x: x1, y }
      sharedWallEnd = { x: x2, y }
    }
    const midPoint: Vector2 = {
      x: (sharedWallStart.x + sharedWallEnd.x) / 2,
      y: (sharedWallStart.y + sharedWallEnd.y) / 2
    }
    if (this.isValidDoorPosition(midPoint, existingDoors)) {
      return midPoint
    }
    const wallLength = distance(sharedWallStart, sharedWallEnd)
    const steps = Math.floor(wallLength / this.DOOR_SPACING)
    for (let i = 1; i <= steps; i++) {
      const t = i / (steps + 1)
      const pos: Vector2 = {
        x: sharedWallStart.x + (sharedWallEnd.x - sharedWallStart.x) * t,
        y: sharedWallStart.y + (sharedWallEnd.y - sharedWallStart.y) * t
      }
      if (this.isValidDoorPosition(pos, existingDoors)) {
        return pos
      }
    }
    return null
  }
  private isValidDoorPosition(pos: Vector2, existingDoors: List[Door]): bool {
    for (const door of existingDoors) {
      const doorPos: Vector2 = { x: door.x, y: door.y }
      if (distance(pos, doorPos) < this.DOOR_SPACING) {
        return false
      }
    }
    return true
  }
  generateMesh(layout: InteriorLayout, lod: float): InteriorMesh {
    const vertices: List[number][] = []
    const faces: List[number][] = []
    for (const room of layout.rooms) {
      const baseIndex = vertices.length
      vertices.push([room.x, 0, room.y])
      vertices.push([room.x + room.width, 0, room.y])
      vertices.push([room.x + room.width, 0, room.y + room.length])
      vertices.push([room.x, 0, room.y + room.length])
      faces.push([baseIndex, baseIndex + 1, baseIndex + 2, baseIndex + 3])
      if (lod > 1) {
        const height = 3 
        vertices.push([room.x, height, room.y])
        vertices.push([room.x + room.width, height, room.y])
        vertices.push([room.x + room.width, height, room.y + room.length])
        vertices.push([room.x, height, room.y + room.length])
        faces.push([baseIndex, baseIndex + 1, baseIndex + 5, baseIndex + 4]) 
        faces.push([baseIndex + 1, baseIndex + 2, baseIndex + 6, baseIndex + 5]) 
        faces.push([baseIndex + 2, baseIndex + 3, baseIndex + 7, baseIndex + 6]) 
        faces.push([baseIndex + 3, baseIndex, baseIndex + 4, baseIndex + 7]) 
      }
    }
    return {
      vertices,
      faces,
      lod
    }
  }
  private getCacheKey(params: InteriorParams): str {
    const key: \'CacheKey\' = {
      buildingType: params.buildingType,
      width: params.width,
      length: params.length,
      height: params.height,
      region: params.region,
      culture: params.culture
    }
    return JSON.stringify(key)
  }
  cacheLayout(params: InteriorParams, layout: InteriorLayout): void {
    const key = this.getCacheKey(params)
    this.layoutCache.set(key, {
      params,
      layout,
      timestamp: Date.now()
    })
    this.cleanCache()
  }
  getCachedLayout(params: InteriorParams): InteriorLayout | null {
    const key = this.getCacheKey(params)
    const cached = this.layoutCache.get(key)
    if (!cached) return null
    if (Date.now() - cached.timestamp > this.CACHE_EXPIRY_MS) {
      this.layoutCache.delete(key)
      return null
    }
    return cached.layout
  }
  private cleanCache(): void {
    const now = Date.now()
    for (const [key, entry] of this.layoutCache.entries()) {
      if (now - entry.timestamp > this.CACHE_EXPIRY_MS) {
        this.layoutCache.delete(key)
      }
    }
  }
  /**
   * Define NPC zones in rooms based on template rules
   */
  private defineNPCZones(): NPCZone[] {
    const zones: List[NPCZone] = []
    for (const room of this.rooms) {
      const roomZones = this.template.npcZones.filter((zone: Dict[str, Any]) => zone.roomType === room.type)
      for (const zoneDefinition of roomZones) {
        const zoneSize = this.calculateNPCZoneSize(zoneDefinition, room)
        if (!zoneSize) continue
        const zonePosition = this.findNPCZonePosition(room, zoneSize, zoneDefinition, zones)
        if (!zonePosition) continue
        zones.push({
          id: crypto.randomUUID(),
          type: zoneDefinition.zoneType,
          area: Dict[str, Any],
          roomId: room.id,
          capacity: zoneDefinition.capacity
        })
      }
    }
    return zones
  }
  /**
   * Calculate appropriate size for an NPC zone based on capacity and room size
   */
  private calculateNPCZoneSize(
    zoneDefinition: NPCZoneDefinition,
    room: Room
  ): { width: float; length: float } | null {
    const spacePerNPC = this.getSpacePerNPC(zoneDefinition.zoneType)
    const totalArea = spacePerNPC * zoneDefinition.capacity
    const maxWidth = room.width * 0.8 
    const maxLength = room.length * 0.8 
    let width = Math.sqrt(totalArea)
    let length = width
    if (width > maxWidth) {
      width = maxWidth
      length = totalArea / width
    }
    if (length > maxLength) {
      length = maxLength
      width = totalArea / length
    }
    if (width > maxWidth || length > maxLength) {
      return null
    }
    return { width, length }
  }
  /**
   * Get space needed per NPC based on zone type
   */
  private getSpacePerNPC(zoneType: NPCZoneType): float {
    switch (zoneType) {
      case NPCZoneType.SERVICE:
        return 4 
      case NPCZoneType.SOCIAL:
        return 3 
      case NPCZoneType.WORK:
        return 4 
      case NPCZoneType.REST:
        return 6 
      case NPCZoneType.GUARD:
        return 2 
      default:
        return 3
    }
  }
  /**
   * Find a valid position for an NPC zone in a room
   */
  private findNPCZonePosition(
    room: Room,
    zoneSize: Dict[str, Any],
    zoneDefinition: NPCZoneDefinition,
    existingZones: List[NPCZone]
  ): Vector2 | null {
    if (zoneDefinition.requiredFurniture.length > 0) {
      return this.findZoneNearFurniture(room, zoneSize, zoneDefinition.requiredFurniture[0], existingZones)
    }
    const stepX = (room.width - zoneSize.width) / 4
    const stepY = (room.length - zoneSize.length) / 4
    for (let x = room.x; x <= room.x + room.width - zoneSize.width; x += stepX) {
      for (let y = room.y; y <= room.y + room.length - zoneSize.length; y += stepY) {
        const pos = { x, y }
        if (this.isValidZonePosition(pos, zoneSize, room, existingZones)) {
          return pos
        }
      }
    }
    return null
  }
  /**
   * Find a zone position near required furniture
   */
  private findZoneNearFurniture(
    room: Room,
    zoneSize: Dict[str, Any],
    requiredFurnitureType: FurnitureType,
    existingZones: List[NPCZone]
  ): Vector2 | null {
    const furniture = this.rooms
      .find(r => r.id === room.id)?.furniture
      .filter(f => f.type === requiredFurnitureType)
    if (!furniture || furniture.length === 0) return null
    for (const piece of furniture) {
      const positions = [
        { x: piece.position.x - zoneSize.width, y: piece.position.y },
        { x: piece.position.x + 1, y: piece.position.y },
        { x: piece.position.x, y: piece.position.y - zoneSize.length },
        { x: piece.position.x, y: piece.position.y + 1 }
      ]
      for (const pos of positions) {
        if (this.isValidZonePosition(pos, zoneSize, room, existingZones)) {
          return pos
        }
      }
    }
    return null
  }
  /**
   * Check if a position is valid for an NPC zone
   */
  private isValidZonePosition(
    position: Vector2,
    zoneSize: Dict[str, Any],
    room: Room,
    existingZones: List[NPCZone]
  ): bool {
    if (
      position.x < room.x ||
      position.y < room.y ||
      position.x + zoneSize.width > room.x + room.width ||
      position.y + zoneSize.length > room.y + room.length
    ) {
      return false
    }
    for (const zone of existingZones.filter(z => z.roomId === room.id)) {
      if (
        position.x < zone.area.x + zone.area.width &&
        position.x + zoneSize.width > zone.area.x &&
        position.y < zone.area.y + zone.area.length &&
        position.y + zoneSize.length > zone.area.y
      ) {
        return false
      }
    }
    return true
  }
  /**
   * Place interactive objects in rooms according to template rules
   */
  private placeInteractiveObjects(): InteractiveObject[] {
    const objects: List[InteractiveObject] = []
    for (const room of this.rooms) {
      const roomObjects = this.template.interactiveObjects.filter((obj: Dict[str, Any]) => obj.roomType === room.type)
      for (const objectRule of roomObjects) {
        for (let i = 0; i < objectRule.count; i++) {
          const position = this.findObjectPosition(room, objectRule, objects)
          if (!position) continue
          objects.push({
            id: crypto.randomUUID(),
            type: objectRule.objectType,
            position,
            rotation: this.calculateObjectRotation(position, room, objectRule),
            roomId: room.id
          })
        }
      }
    }
    return objects
  }
  /**
   * Find a valid position for an interactive object
   */
  private findObjectPosition(
    room: Room,
    rule: InteractiveObjectRule,
    existingObjects: List[InteractiveObject]
  ): Vector2 | null {
    const placementType = rule.placementRules[0]?.type || InteractiveObjectPlacementType.RANDOM
    const requiredSpace = rule.requiredSpace
    switch (placementType) {
      case InteractiveObjectPlacementType.NEAR_WALL:
        return this.findPositionNearWall(room, requiredSpace, existingObjects)
      case InteractiveObjectPlacementType.NEAR_FURNITURE:
        if (rule.placementRules[0].parameters.furnitureType) {
          return this.findPositionNearFurniture(
            room,
            rule.placementRules[0].parameters.furnitureType,
            requiredSpace,
            existingObjects
          )
        }
        return this.findRandomPosition(room, requiredSpace, existingObjects)
      case InteractiveObjectPlacementType.CENTER:
        return this.findCenterPosition(room, requiredSpace, existingObjects)
      case InteractiveObjectPlacementType.CORNER:
        return this.findCornerPosition(room, requiredSpace, existingObjects)
      case InteractiveObjectPlacementType.RANDOM:
      default:
        return this.findRandomPosition(room, requiredSpace, existingObjects)
    }
  }
  /**
   * Find a position near a wall for an interactive object
   */
  private findPositionNearWall(
    room: Room,
    requiredSpace: float,
    existingObjects: List[InteractiveObject]
  ): Vector2 | null {
    const wallPositions = [
      ...Array.from({ length: room.length - requiredSpace }, (_, i) => ({
        x: room.x,
        y: room.y + i
      })),
      ...Array.from({ length: room.length - requiredSpace }, (_, i) => ({
        x: room.x + room.width - requiredSpace,
        y: room.y + i
      })),
      ...Array.from({ length: room.width - requiredSpace }, (_, i) => ({
        x: room.x + i,
        y: room.y
      })),
      ...Array.from({ length: room.width - requiredSpace }, (_, i) => ({
        x: room.x + i,
        y: room.y + room.length - requiredSpace
      }))
    ]
    for (let i = wallPositions.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1))
      [wallPositions[i], wallPositions[j]] = [wallPositions[j], wallPositions[i]]
    }
    for (const pos of wallPositions) {
      if (this.isValidObjectPosition(pos, requiredSpace, room, existingObjects)) {
        return pos
      }
    }
    return null
  }
  /**
   * Find a position near specific furniture
   */
  private findPositionNearFurniture(
    room: Room,
    furnitureType: FurnitureType,
    requiredSpace: float,
    existingObjects: List[InteractiveObject]
  ): Vector2 | null {
    const furniture = this.rooms
      .find(r => r.id === room.id)?.furniture
      .filter(f => f.type === furnitureType)
    if (!furniture || furniture.length === 0) return null
    for (const piece of furniture) {
      const positions = [
        { x: piece.position.x - requiredSpace, y: piece.position.y },
        { x: piece.position.x + 1, y: piece.position.y },
        { x: piece.position.x, y: piece.position.y - requiredSpace },
        { x: piece.position.x, y: piece.position.y + 1 }
      ]
      for (const pos of positions) {
        if (this.isValidObjectPosition(pos, requiredSpace, room, existingObjects)) {
          return pos
        }
      }
    }
    return null
  }
  /**
   * Find a position in the center of the room
   */
  private findCenterPosition(
    room: Room,
    requiredSpace: float,
    existingObjects: List[InteractiveObject]
  ): Vector2 | null {
    const center = {
      x: room.x + Math.floor(room.width / 2) - Math.floor(requiredSpace / 2),
      y: room.y + Math.floor(room.length / 2) - Math.floor(requiredSpace / 2)
    }
    if (this.isValidObjectPosition(center, requiredSpace, room, existingObjects)) {
      return center
    }
    const radius = 1
    for (let dx = -radius; dx <= radius; dx++) {
      for (let dy = -radius; dy <= radius; dy++) {
        const pos = {
          x: center.x + dx,
          y: center.y + dy
        }
        if (this.isValidObjectPosition(pos, requiredSpace, room, existingObjects)) {
          return pos
        }
      }
    }
    return null
  }
  /**
   * Find a position in a corner of the room
   */
  private findCornerPosition(
    room: Room,
    requiredSpace: float,
    existingObjects: List[InteractiveObject]
  ): Vector2 | null {
    const corners = [
      { x: room.x, y: room.y },
      { x: room.x + room.width - requiredSpace, y: room.y },
      { x: room.x, y: room.y + room.length - requiredSpace },
      { x: room.x + room.width - requiredSpace, y: room.y + room.length - requiredSpace }
    ]
    for (const pos of corners) {
      if (this.isValidObjectPosition(pos, requiredSpace, room, existingObjects)) {
        return pos
      }
    }
    return null
  }
  /**
   * Find a random position in the room
   */
  private findRandomPosition(
    room: Room,
    requiredSpace: float,
    existingObjects: List[InteractiveObject]
  ): Vector2 | null {
    for (let attempts = 0; attempts < 10; attempts++) {
      const pos = {
        x: room.x + Math.floor(Math.random() * (room.width - requiredSpace)),
        y: room.y + Math.floor(Math.random() * (room.length - requiredSpace))
      }
      if (this.isValidObjectPosition(pos, requiredSpace, room, existingObjects)) {
        return pos
      }
    }
    return null
  }
  /**
   * Check if a position is valid for an interactive object
   */
  private isValidObjectPosition(
    position: Vector2,
    requiredSpace: float,
    room: Room,
    existingObjects: List[InteractiveObject]
  ): bool {
    if (
      position.x < room.x ||
      position.y < room.y ||
      position.x + requiredSpace > room.x + room.width ||
      position.y + requiredSpace > room.y + room.length
    ) {
      return false
    }
    for (const obj of existingObjects.filter(o => o.roomId === room.id)) {
      const dist = distance(position, obj.position)
      if (dist < requiredSpace) {
        return false
      }
    }
    return true
  }
  /**
   * Calculate rotation for an interactive object
   */
  private calculateObjectRotation(
    position: Vector2,
    room: Room,
    rule: InteractiveObjectRule
  ): float {
    const placementType = rule.placementRules[0]?.type || InteractiveObjectPlacementType.RANDOM
    switch (placementType) {
      case InteractiveObjectPlacementType.NEAR_WALL:
        if (position.x === room.x) return 0 
        if (position.x === room.x + room.width - rule.requiredSpace) return Math.PI 
        if (position.y === room.y) return Math.PI / 2 
        if (position.y === room.y + room.length - rule.requiredSpace) return -Math.PI / 2 
        break
      case InteractiveObjectPlacementType.CENTER:
      case InteractiveObjectPlacementType.CORNER:
        const centerX = room.x + room.width / 2
        const centerY = room.y + room.length / 2
        return Math.atan2(centerY - position.y, centerX - position.x)
      case InteractiveObjectPlacementType.RANDOM:
      default:
        return Math.random() * Math.PI * 2
    }
    return 0
  }
} 