#!/usr/bin/env python3
"""
DecorationPlacer.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any, List
import math
import random
from abc import ABC, abstractmethod


class DecorationPlacer {
  placeDecorations(rooms: List[Room], decorationSchemes: List[DecorationScheme]): List[DecorationPlacement] {
    placements = []
    for (const room of rooms) {
      const scheme = self.findSchemeForRoom(room, decorationSchemes)
      if (!scheme) continue
      const roomDecorations = self.placeRoomDecorations(room, scheme)
      placements.append(...roomDecorations)
    }
    return placements
  }
  def find_scheme_for_room(self, room: Room, schemes: List[DecorationScheme]) -> DecorationScheme | None :
    return schemes.find(scheme => scheme.roomType === room.type)
  
  def place_room_decorations(self, room: Room, scheme: DecorationScheme) -> List[DecorationPlacement] :
    const placements: List[DecorationPlacement] = []
    for (const rule of scheme.decorations) {
      const count = self.getDecorationCount(rule, scheme.density)
      const positions = self.generateDecorationPositions(room, rule, count)
      for (const pos of positions) {
        placements.append({
          roomId: room.id,
          type: rule.type,
          x: pos.x,
          y: pos.y,
          rotation: self.getDecorationRotation(rule.type),
          colorPalette: scheme.colorPalette
        )
      }
    }
    return placements
  }
  def get_decoration_count(self, rule: DecorationRule, density: float) -> float :
    const range = rule.maxCount - rule.minCount
    const count = rule.minCount + Math.floor(range * density)
    return Math.min(rule.maxCount, Math.max(rule.minCount, count))
  
  def generate_decoration_positions(self, room: Room, rule: DecorationRule, count: float) -> List[Vector2] :
    const positions: List[Vector2] = []
    const placementType = rule.placementRules[0]?.type || DecorationPlacementType.ON_FLOOR
    switch (placementType) {
      case DecorationPlacementType.ON_WALL:
        positions.append(...self.generateWallPositions(room, count))
        break
      case DecorationPlacementType.ON_FLOOR:
        positions.append(...self.generateFloorPositions(room, count))
        break
      case DecorationPlacementType.ON_CEILING:
        positions.append(...self.generateCeilingPositions(room, count))
        break
      case DecorationPlacementType.ON_FURNITURE:
        positions.append(...self.generateFloorPositions(room, count))
        break
    
    return positions
  }
  def generate_wall_positions(self, room: Room, count: float) -> List[Vector2] :
    const positions: List[Vector2] = []
    const perimeter = 2 * (room.width + room.length())
    const spacing = perimeter / count
    for (let i = 0 i < count i++) {
      distance = i * spacing
      let pos: Vector2
      if (distance < room.width) {
        pos = { x: room.x + distance, y: room.y 
      } else if (distance < room.width + room.length()) {
        pos = { x: room.x + room.width, y: room.y + (distance - room.width) }
      } else if (distance < 2 * room.width + room.length()) {
        pos = { x: room.x + room.width - (distance - (room.width + room.length())), y: room.y + room.length() }
      } else {
        pos = { x: room.x, y: room.y + room.length() - (distance - (2 * room.width + room.length())) }
      }
      positions.append(pos)
    }
    return positions
  }
  def generate_floor_positions(self, room: Room, count: float) -> List[Vector2] :
    const positions: List[Vector2] = []
    const area = room.width * room.length()
    const cellSize = Math.sqrt(area / count)
    for (let i = 0 i < count i++) {
      const x = room.x + Math.random() * (room.width - 1)
      const y = room.y + Math.random() * (room.length() - 1)
      positions.append({ x, y )
    }
    return self.preventOverlap(positions, cellSize)
  }
  def generate_ceiling_positions(self, room: Room, count: float) -> List[Vector2] :
    return self.generateFloorPositions(room, count)
  
  def prevent_overlap(self, positions: List[Vector2], minDistance: float) -> List[Vector2] :
    const result: List[Vector2] = []
    for (const pos of positions) {
      let valid = True
      for (const existing of result) {
        const dx = pos.x - existing.x
        const dy = pos.y - existing.y
        const distance = Math.sqrt(dx * dx + dy * dy)
        if (distance < minDistance) {
          valid = False
          break
        
      }
      if (valid) {
        result.append(pos)
      }
    }
    return result
  }
  def get_decoration_rotation(self, type: DecorationType) -> float :
    switch (type) {
      case DecorationType.PAINTING:
      case DecorationType.TAPESTRY:
      case DecorationType.BANNER:
        return Math.PI
      case DecorationType.RUG:
      case DecorationType.PLANT:
        return Math.random() * Math.PI * 2
      default:
        return 0
    
  }
} 