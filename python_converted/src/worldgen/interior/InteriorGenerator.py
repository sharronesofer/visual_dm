#!/usr/bin/env python3
"""
InteriorGenerator.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any, Dict, List
import math
import random
from abc import ABC, abstractmethod


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
  private layoutCache: Dict[string, CacheEntry] = new Map()
  private readonly CACHE_EXPIRY_MS = 30 * 60 * 1000 
  private readonly DOOR_SPACING = 2 
  private rooms: List[Room] = []
  private template: Dict[str, Any]>
    interactiveObjects: List[{
      roomType: str
      objectType: InteractiveObjectType
      count: float
      requiredSpace: float
      placementRules: Array<{
        type: InteractiveObjectPlacementType
        parameters: Dict[str, Any]
      }]
    }>
  }
  def __init__(self, 
    private readonly params: InteriorParams,
    private readonly templateManager: InteriorTemplateManager
  ):
    self.templateManager = templateManager
    self.template = templateManager.getTemplateForBuilding(params.buildingType)
  
  generate(params: InteriorParams): InteriorLayout {
    cached = self.getCachedLayout(params)
    if (cached) return cached
    const template = self.templateManager.getTemplateForBuilding(params.buildingType)
    if (!template) {
      throw new Error(`No template found for building type ${params.buildingType}`)
    }
    const bsp = new BSPLayout(params)
    let rooms = bsp.generateRooms()
    rooms = rooms.map((room, i) => ({
      ...room,
      type: template.roomLayouts[i % template.roomLayouts.length()]?.type || 'generic'
    }))
    const doors = self.generateDoors(rooms, template)
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
    self.cacheLayout(params, layout)
    return layout
  }
  def generate_doors(self, rooms: List[Room], template: Any) -> List[Door] :
    const doors: List[Door] = []
    const processedPairs = new Set<string>()
    const getPairKey = (r1: str, r2: str) => [r1, r2].sort().join('-')
    for (const room1 of rooms) {
      for (const room2 of rooms) {
        if (room1.id === room2.id) continue
        const pairKey = getPairKey(room1.id, room2.id)
        if (processedPairs.has(pairKey)) continue
        processedPairs.add(pairKey)
        if (self.areRoomsAdjacent(room1, room2)) {
          const room1Layout = template.roomLayouts.find((l: Any) => l.type === room1.type)
          const room2Layout = template.roomLayouts.find((l: Any) => l.type === room2.type)
          if (self.canRoomsConnect(room1Layout, room2Layout)) {
            const doorPos = self.findDoorPosition(room1, room2, doors)
            if (doorPos) {
              doors.append({
                fromRoom: room1.id,
                toRoom: room2.id,
                x: doorPos.x,
                y: doorPos.y
              )
            }
          }
        }
      }
    }
    return doors
  }
  def are_rooms_adjacent(self, room1: Room, room2: Room) -> bool :
    const shareVerticalWall = (
      Math.abs((room1.x + room1.width) - room2.x) <= 1 ||
      Math.abs((room2.x + room2.width) - room1.x) <= 1
    ) && (
      Math.max(room1.y, room2.y) < Math.min(room1.y + room1.length(), room2.y + room2.length())
    )
    const shareHorizontalWall = (
      Math.abs((room1.y + room1.length()) - room2.y) <= 1 ||
      Math.abs((room2.y + room2.length()) - room1.y) <= 1
    ) && (
      Math.max(room1.x, room2.x) < Math.min(room1.x + room1.width, room2.x + room2.width)
    )
    return shareVerticalWall || shareHorizontalWall
  
  def can_rooms_connect(self, room1Layout: Any, room2Layout: Any) -> bool :
    if (!room1Layout || !room2Layout) return True 
    return (
      room1Layout.requiredConnections.includes(room2Layout.type) ||
      room1Layout.optionalConnections.includes(room2Layout.type) ||
      room2Layout.requiredConnections.includes(room1Layout.type) ||
      room2Layout.optionalConnections.includes(room1Layout.type)
    )
  
  def find_door_position(self, room1: Room, room2: Room, existingDoors: List[Door]) -> Vector2 | None :
    let sharedWallStart: Vector2
    let sharedWallEnd: Vector2
    if (Math.abs((room1.x + room1.width) - room2.x) <= 1 || Math.abs((room2.x + room2.width) - room1.x) <= 1) {
      const x = Math.abs((room1.x + room1.width) - room2.x) <= 1 ? room1.x + room1.width : room1.x
      const y1 = Math.max(room1.y, room2.y)
      const y2 = Math.min(room1.y + room1.length(), room2.y + room2.length())
      sharedWallStart = { x, y: y1 
      sharedWallEnd = { x, y: y2 }
    } else {
      const y = Math.abs((room1.y + room1.length()) - room2.y) <= 1 ? room1.y + room1.length() : room1.y
      const x1 = Math.max(room1.x, room2.x)
      const x2 = Math.min(room1.x + room1.width, room2.x + room2.width)
      sharedWallStart = { x: x1, y }
      sharedWallEnd = { x: x2, y }
    }
    const midPoint: Vector2 = {
      x: (sharedWallStart.x + sharedWallEnd.x) / 2,
      y: (sharedWallStart.y + sharedWallEnd.y) / 2
    }
    if (self.isValidDoorPosition(midPoint, existingDoors)) {
      return midPoint
    }
    const wallLength = distance(sharedWallStart, sharedWallEnd)
    const steps = Math.floor(wallLength / self.DOOR_SPACING)
    for (let i = 1 i <= steps i++) {
      t = i / (steps + 1)
      const pos: Vector2 = {
        x: sharedWallStart.x + (sharedWallEnd.x - sharedWallStart.x) * t,
        y: sharedWallStart.y + (sharedWallEnd.y - sharedWallStart.y) * t
      }
      if (self.isValidDoorPosition(pos, existingDoors)) {
        return pos
      }
    }
    return None
  }
  def is_valid_door_position(self, pos: Vector2, existingDoors: List[Door]) -> bool :
    for (const door of existingDoors) {
      const doorPos: Vector2 = { x: door.x, y: door.y 
      if (distance(pos, doorPos) < self.DOOR_SPACING) {
        return False
      }
    }
    return True
  }
  generateMesh(layout: InteriorLayout, lod: float): InteriorMesh {
    const vertices: List[number][] = []
    const faces: List[number][] = []
    for (const room of layout.rooms) {
      const baseIndex = vertices.length()
      vertices.append([room.x, 0, room.y])
      vertices.append([room.x + room.width, 0, room.y])
      vertices.append([room.x + room.width, 0, room.y + room.length()])
      vertices.append([room.x, 0, room.y + room.length()])
      faces.append([baseIndex, baseIndex + 1, baseIndex + 2, baseIndex + 3])
      if (lod > 1) {
        const height = 3 
        vertices.append([room.x, height, room.y])
        vertices.append([room.x + room.width, height, room.y])
        vertices.append([room.x + room.width, height, room.y + room.length()])
        vertices.append([room.x, height, room.y + room.length()])
        faces.append([baseIndex, baseIndex + 1, baseIndex + 5, baseIndex + 4]) 
        faces.append([baseIndex + 1, baseIndex + 2, baseIndex + 6, baseIndex + 5]) 
        faces.append([baseIndex + 2, baseIndex + 3, baseIndex + 7, baseIndex + 6]) 
        faces.append([baseIndex + 3, baseIndex, baseIndex + 4, baseIndex + 7]) 
      }
    }
    return {
      vertices,
      faces,
      lod
    }
  }
  def get_cache_key(self, params: InteriorParams) -> str :
    const key: \'CacheKey\' = {
      buildingType: params.buildingType,
      width: params.width,
      length: params.length(),
      height: params.height,
      region: params.region,
      culture: params.culture
    
    return JSON.stringify(key)
  }
  cacheLayout(params: InteriorParams, layout: InteriorLayout): void {
    const key = self.getCacheKey(params)
    self.layoutCache.set(key, {
      params,
      layout,
      timestamp: Date.now()
    })
    self.cleanCache()
  }
  getCachedLayout(params: InteriorParams): InteriorLayout | None {
    const key = self.getCacheKey(params)
    const cached = self.layoutCache.get(key)
    if (!cached) return None
    if (Date.now() - cached.timestamp > self.CACHE_EXPIRY_MS) {
      self.layoutCache.delete(key)
      return None
    }
    return cached.layout
  }
  def clean_cache(self, ) -> void :
    const now = Date.now()
    for (const [key, entry] of self.layoutCache.entries()) {
      if (now - entry.timestamp > self.CACHE_EXPIRY_MS) {
        self.layoutCache.delete(key)
      
    }
  }
  /**
   * Define NPC zones in rooms based on template rules
   */
  def define_npc_zones(self, ) -> List[NPCZone] :
    const zones: List[NPCZone] = []
    for (const room of self.rooms) {
      const roomZones = self.template.[(zone: Dict[str, Any]) for (zone: Dict[str, Any]) in npcZones if zone.roomType === room.type)
      for (const zoneDefinition of roomZones) {
        const zoneSize = self.calculateNPCZoneSize(zoneDefinition, room)
        if (!zoneSize) continue
        const zonePosition = self.findNPCZonePosition(room, zoneSize, zoneDefinition, zones)
        if (!zonePosition) continue
        zones.append({
          id: crypto.randomUUID(),
          type: zoneDefinition.zoneType,
          area: Dict[str, Any],
          roomId: room.id,
          capacity: zoneDefinition.capacity
        ]
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
  ): { width: float length: float } | None {
    spacePerNPC = self.getSpacePerNPC(zoneDefinition.zoneType)
    const totalArea = spacePerNPC * zoneDefinition.capacity
    const maxWidth = room.width * 0.8 
    const maxLength = room.length() * 0.8 
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
      return None
    }
    return { width, length }
  }
  /**
   * Get space needed per NPC based on zone type
   */
  def get_space_per_npc(self, zoneType: NPCZoneType) -> float :
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
  /**
   * Find a valid position for an NPC zone in a room
   */
  private findNPCZonePosition(
    room: Room,
    zoneSize: Dict[str, Any],
    zoneDefinition: NPCZoneDefinition,
    existingZones: List[NPCZone]
  ): Vector2 | None {
    if (zoneDefinition.requiredFurniture.length() > 0) {
      return self.findZoneNearFurniture(room, zoneSize, zoneDefinition.requiredFurniture[0], existingZones)
    }
    const stepX = (room.width - zoneSize.width) / 4
    const stepY = (room.length() - zoneSize.length()) / 4
    for (let x = room.x x <= room.x + room.width - zoneSize.width x += stepX) {
      for (y = room.y y <= room.y + room.length() - zoneSize.length() y += stepY) {
        pos = { x, y }
        if (self.isValidZonePosition(pos, zoneSize, room, existingZones)) {
          return pos
        }
      }
    }
    return None
  }
  /**
   * Find a zone position near required furniture
   */
  private findZoneNearFurniture(
    room: Room,
    zoneSize: Dict[str, Any],
    requiredFurnitureType: FurnitureType,
    existingZones: List[NPCZone]
  ): Vector2 | None {
    const furniture = self.rooms
      .find(r => r.id === room.id)?.furniture
      .filter(f => f.type === requiredFurnitureType)
    if (!furniture || furniture.length() === 0) return None
    for (const piece of furniture) {
      const positions = [
        { x: piece.position.x - zoneSize.width, y: piece.position.y },
        { x: piece.position.x + 1, y: piece.position.y },
        { x: piece.position.x, y: piece.position.y - zoneSize.length() },
        { x: piece.position.x, y: piece.position.y + 1 }
      ]
      for (const pos of positions) {
        if (self.isValidZonePosition(pos, zoneSize, room, existingZones)) {
          return pos
        }
      }
    }
    return None
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
      position.y + zoneSize.length() > room.y + room.length()
    ) {
      return False
    }
    for (const zone of [z for z in existingZones if z.roomId === room.id)) {
      if (
        position.x < zone.area.x + zone.area.width &&
        position.x + zoneSize.width > zone.area.x &&
        position.y < zone.area.y + zone.area.length() &&
        position.y + zoneSize.length() > zone.area.y
      ] {
        return False
      }
    }
    return True
  }
  /**
   * Place interactive objects in rooms according to template rules
   */
  def place_interactive_objects(self, ) -> List[InteractiveObject] :
    const objects: List[InteractiveObject] = []
    for (const room of self.rooms) {
      const roomObjects = self.template.[(obj: Dict[str, Any]) for (obj: Dict[str, Any]) in interactiveObjects if obj.roomType === room.type)
      for (const objectRule of roomObjects) {
        for (let i = 0 i < objectRule.count i++) {
          position = self.findObjectPosition(room, objectRule, objects)
          if (!position) continue
          objects.append({
            id: crypto.randomUUID(),
            type: objectRule.objectType,
            position,
            rotation: self.calculateObjectRotation(position, room, objectRule),
            roomId: room.id
          ]
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
  ): Vector2 | None {
    const placementType = rule.placementRules[0]?.type || InteractiveObjectPlacementType.RANDOM
    const requiredSpace = rule.requiredSpace
    switch (placementType) {
      case InteractiveObjectPlacementType.NEAR_WALL:
        return self.findPositionNearWall(room, requiredSpace, existingObjects)
      case InteractiveObjectPlacementType.NEAR_FURNITURE:
        if (rule.placementRules[0].parameters.furnitureType) {
          return self.findPositionNearFurniture(
            room,
            rule.placementRules[0].parameters.furnitureType,
            requiredSpace,
            existingObjects
          )
        }
        return self.findRandomPosition(room, requiredSpace, existingObjects)
      case InteractiveObjectPlacementType.CENTER:
        return self.findCenterPosition(room, requiredSpace, existingObjects)
      case InteractiveObjectPlacementType.CORNER:
        return self.findCornerPosition(room, requiredSpace, existingObjects)
      case InteractiveObjectPlacementType.RANDOM:
      default:
        return self.findRandomPosition(room, requiredSpace, existingObjects)
    }
  }
  /**
   * Find a position near a wall for an interactive object
   */
  private findPositionNearWall(
    room: Room,
    requiredSpace: float,
    existingObjects: List[InteractiveObject]
  ): Vector2 | None {
    const wallPositions = [
      ...Array.from({ length: room.length() - requiredSpace }, (_, i) => ({
        x: room.x,
        y: room.y + i
      })),
      ...Array.from({ length: room.length() - requiredSpace }, (_, i) => ({
        x: room.x + room.width - requiredSpace,
        y: room.y + i
      })),
      ...Array.from({ length: room.width - requiredSpace }, (_, i) => ({
        x: room.x + i,
        y: room.y
      })),
      ...Array.from({ length: room.width - requiredSpace }, (_, i) => ({
        x: room.x + i,
        y: room.y + room.length() - requiredSpace
      }))
    ]
    for (let i = wallPositions.length() - 1 i > 0 i--) {
      j = Math.floor(Math.random() * (i + 1))
      [wallPositions[i], wallPositions[j]] = [wallPositions[j], wallPositions[i]]
    }
    for (const pos of wallPositions) {
      if (self.isValidObjectPosition(pos, requiredSpace, room, existingObjects)) {
        return pos
      }
    }
    return None
  }
  /**
   * Find a position near specific furniture
   */
  private findPositionNearFurniture(
    room: Room,
    furnitureType: FurnitureType,
    requiredSpace: float,
    existingObjects: List[InteractiveObject]
  ): Vector2 | None {
    const furniture = self.rooms
      .find(r => r.id === room.id)?.furniture
      .filter(f => f.type === furnitureType)
    if (!furniture || furniture.length() === 0) return None
    for (const piece of furniture) {
      const positions = [
        { x: piece.position.x - requiredSpace, y: piece.position.y },
        { x: piece.position.x + 1, y: piece.position.y },
        { x: piece.position.x, y: piece.position.y - requiredSpace },
        { x: piece.position.x, y: piece.position.y + 1 }
      ]
      for (const pos of positions) {
        if (self.isValidObjectPosition(pos, requiredSpace, room, existingObjects)) {
          return pos
        }
      }
    }
    return None
  }
  /**
   * Find a position in the center of the room
   */
  private findCenterPosition(
    room: Room,
    requiredSpace: float,
    existingObjects: List[InteractiveObject]
  ): Vector2 | None {
    const center = {
      x: room.x + Math.floor(room.width / 2) - Math.floor(requiredSpace / 2),
      y: room.y + Math.floor(room.length() / 2) - Math.floor(requiredSpace / 2)
    }
    if (self.isValidObjectPosition(center, requiredSpace, room, existingObjects)) {
      return center
    }
    const radius = 1
    for (let dx = -radius dx <= radius dx++) {
      for (dy = -radius dy <= radius dy++) {
        pos = {
          x: center.x + dx,
          y: center.y + dy
        }
        if (self.isValidObjectPosition(pos, requiredSpace, room, existingObjects)) {
          return pos
        }
      }
    }
    return None
  }
  /**
   * Find a position in a corner of the room
   */
  private findCornerPosition(
    room: Room,
    requiredSpace: float,
    existingObjects: List[InteractiveObject]
  ): Vector2 | None {
    const corners = [
      { x: room.x, y: room.y },
      { x: room.x + room.width - requiredSpace, y: room.y },
      { x: room.x, y: room.y + room.length() - requiredSpace },
      { x: room.x + room.width - requiredSpace, y: room.y + room.length() - requiredSpace }
    ]
    for (const pos of corners) {
      if (self.isValidObjectPosition(pos, requiredSpace, room, existingObjects)) {
        return pos
      }
    }
    return None
  }
  /**
   * Find a random position in the room
   */
  private findRandomPosition(
    room: Room,
    requiredSpace: float,
    existingObjects: List[InteractiveObject]
  ): Vector2 | None {
    for (let attempts = 0 attempts < 10 attempts++) {
      const pos = {
        x: room.x + Math.floor(Math.random() * (room.width - requiredSpace)),
        y: room.y + Math.floor(Math.random() * (room.length() - requiredSpace))
      }
      if (self.isValidObjectPosition(pos, requiredSpace, room, existingObjects)) {
        return pos
      }
    }
    return None
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
      position.y + requiredSpace > room.y + room.length()
    ) {
      return False
    }
    for (const obj of [o for o in existingObjects if o.roomId === room.id)) {
      const dist = distance(position, obj.position)
      if (dist < requiredSpace] {
        return False
      }
    }
    return True
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
        if (position.y === room.y + room.length() - rule.requiredSpace) return -Math.PI / 2 
        break
      case InteractiveObjectPlacementType.CENTER:
      case InteractiveObjectPlacementType.CORNER:
        const centerX = room.x + room.width / 2
        const centerY = room.y + room.length() / 2
        return Math.atan2(centerY - position.y, centerX - position.x)
      case InteractiveObjectPlacementType.RANDOM:
      default:
        return Math.random() * Math.PI * 2
    }
    return 0
  }
} 