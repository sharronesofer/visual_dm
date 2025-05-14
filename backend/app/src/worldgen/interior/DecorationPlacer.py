from typing import Any, List


class DecorationPlacer {
  placeDecorations(rooms: List[Room], decorationSchemes: List[DecorationScheme]): DecorationPlacement[] {
    const placements: List[DecorationPlacement] = []
    for (const room of rooms) {
      const scheme = this.findSchemeForRoom(room, decorationSchemes)
      if (!scheme) continue
      const roomDecorations = this.placeRoomDecorations(room, scheme)
      placements.push(...roomDecorations)
    }
    return placements
  }
  private findSchemeForRoom(room: Room, schemes: List[DecorationScheme]): DecorationScheme | undefined {
    return schemes.find(scheme => scheme.roomType === room.type)
  }
  private placeRoomDecorations(room: Room, scheme: DecorationScheme): DecorationPlacement[] {
    const placements: List[DecorationPlacement] = []
    for (const rule of scheme.decorations) {
      const count = this.getDecorationCount(rule, scheme.density)
      const positions = this.generateDecorationPositions(room, rule, count)
      for (const pos of positions) {
        placements.push({
          roomId: room.id,
          type: rule.type,
          x: pos.x,
          y: pos.y,
          rotation: this.getDecorationRotation(rule.type),
          colorPalette: scheme.colorPalette
        })
      }
    }
    return placements
  }
  private getDecorationCount(rule: DecorationRule, density: float): float {
    const range = rule.maxCount - rule.minCount
    const count = rule.minCount + Math.floor(range * density)
    return Math.min(rule.maxCount, Math.max(rule.minCount, count))
  }
  private generateDecorationPositions(room: Room, rule: DecorationRule, count: float): Vector2[] {
    const positions: List[Vector2] = []
    const placementType = rule.placementRules[0]?.type || DecorationPlacementType.ON_FLOOR
    switch (placementType) {
      case DecorationPlacementType.ON_WALL:
        positions.push(...this.generateWallPositions(room, count))
        break
      case DecorationPlacementType.ON_FLOOR:
        positions.push(...this.generateFloorPositions(room, count))
        break
      case DecorationPlacementType.ON_CEILING:
        positions.push(...this.generateCeilingPositions(room, count))
        break
      case DecorationPlacementType.ON_FURNITURE:
        positions.push(...this.generateFloorPositions(room, count))
        break
    }
    return positions
  }
  private generateWallPositions(room: Room, count: float): Vector2[] {
    const positions: List[Vector2] = []
    const perimeter = 2 * (room.width + room.length)
    const spacing = perimeter / count
    for (let i = 0; i < count; i++) {
      const distance = i * spacing
      let pos: Vector2
      if (distance < room.width) {
        pos = { x: room.x + distance, y: room.y }
      } else if (distance < room.width + room.length) {
        pos = { x: room.x + room.width, y: room.y + (distance - room.width) }
      } else if (distance < 2 * room.width + room.length) {
        pos = { x: room.x + room.width - (distance - (room.width + room.length)), y: room.y + room.length }
      } else {
        pos = { x: room.x, y: room.y + room.length - (distance - (2 * room.width + room.length)) }
      }
      positions.push(pos)
    }
    return positions
  }
  private generateFloorPositions(room: Room, count: float): Vector2[] {
    const positions: List[Vector2] = []
    const area = room.width * room.length
    const cellSize = Math.sqrt(area / count)
    for (let i = 0; i < count; i++) {
      const x = room.x + Math.random() * (room.width - 1)
      const y = room.y + Math.random() * (room.length - 1)
      positions.push({ x, y })
    }
    return this.preventOverlap(positions, cellSize)
  }
  private generateCeilingPositions(room: Room, count: float): Vector2[] {
    return this.generateFloorPositions(room, count)
  }
  private preventOverlap(positions: List[Vector2], minDistance: float): Vector2[] {
    const result: List[Vector2] = []
    for (const pos of positions) {
      let valid = true
      for (const existing of result) {
        const dx = pos.x - existing.x
        const dy = pos.y - existing.y
        const distance = Math.sqrt(dx * dx + dy * dy)
        if (distance < minDistance) {
          valid = false
          break
        }
      }
      if (valid) {
        result.push(pos)
      }
    }
    return result
  }
  private getDecorationRotation(type: DecorationType): float {
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
} 