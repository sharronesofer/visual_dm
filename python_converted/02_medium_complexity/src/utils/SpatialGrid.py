from typing import Any, List



class Position:
    x: float
    y: float
class GridCell:
    entities: Set[str>
class SpatialGrid {
  private grid: Map<string, Set<string>>
  private entityPositions: Map<string, { x: float; y: float }>
  private cellSize: float
  constructor(cellSize: float = 100) {
    this.grid = new Map()
    this.entityPositions = new Map()
    this.cellSize = cellSize
  }
  /**
   * Add an entity to the grid
   */
  public addEntity(entityId: str, x: float, y: float): void {
    this.removeEntity(entityId)
    this.entityPositions.set(entityId, { x, y })
    const cellKey = this.getCellKey(x, y)
    if (!this.grid.has(cellKey)) {
      this.grid.set(cellKey, new Set())
    }
    this.grid.get(cellKey)!.add(entityId)
  }
  /**
   * Remove an entity from the grid
   */
  public removeEntity(entityId: str): void {
    const position = this.entityPositions.get(entityId)
    if (position) {
      const cellKey = this.getCellKey(position.x, position.y)
      const cell = this.grid.get(cellKey)
      if (cell) {
        cell.delete(entityId)
        if (cell.size === 0) {
          this.grid.delete(cellKey)
        }
      }
      this.entityPositions.delete(entityId)
    }
  }
  /**
   * Update an entity's position
   */
  public updateEntity(entityId: str, x: float, y: float): void {
    this.addEntity(entityId, x, y)
  }
  /**
   * Get all entities within a radius of a given entity
   */
  public getEntitiesInRange(entityId: str, radius: float): string[] {
    const position = this.entityPositions.get(entityId)
    if (!position) return []
    const cellRadius = Math.ceil(radius / this.cellSize)
    const centerX = Math.floor(position.x / this.cellSize)
    const centerY = Math.floor(position.y / this.cellSize)
    const nearbyEntities = new Set<string>()
    for (let dx = -cellRadius; dx <= cellRadius; dx++) {
      for (let dy = -cellRadius; dy <= cellRadius; dy++) {
        const cellKey = this.getCellKey(
          (centerX + dx) * this.cellSize,
          (centerY + dy) * this.cellSize
        )
        const cellEntities = this.grid.get(cellKey)
        if (cellEntities) {
          for (const entity of cellEntities) {
            const entityPos = this.entityPositions.get(entity)
            if (entityPos) {
              const distance = Math.sqrt(
                Math.pow(entityPos.x - position.x, 2) +
                Math.pow(entityPos.y - position.y, 2)
              )
              if (distance <= radius) {
                nearbyEntities.add(entity)
              }
            }
          }
        }
      }
    }
    return Array.from(nearbyEntities)
  }
  /**
   * Get the key for a grid cell containing the given coordinates
   */
  private getCellKey(x: float, y: float): str {
    const cellX = Math.floor(x / this.cellSize)
    const cellY = Math.floor(y / this.cellSize)
    return `${cellX},${cellY}`
  }
  public getDistance(pos1: \'Position\', pos2: Position): float {
    const dx = pos2.x - pos1.x
    const dy = pos2.y - pos1.y
    return Math.sqrt(dx * dx + dy * dy)
  }
  public getNearbyEntities(position: \'Position\', radius: float): string[] {
    const cellRadius = Math.ceil(radius / this.cellSize)
    const nearby: List[string] = []
    for (let x = Math.max(0, position.x - cellRadius); x <= Math.min(position.x + cellRadius, this.cellSize - 1); x++) {
      for (let y = Math.max(0, position.y - cellRadius); y <= Math.min(position.y + cellRadius, this.cellSize - 1); y++) {
        const cellKey = this.getCellKey(x, y)
        const cellEntities = this.grid.get(cellKey)
        if (cellEntities) {
          cellEntities.forEach(entityId => {
            const entityPos = this.entityPositions.get(entityId)
            if (entityPos && this.getDistance(position, entityPos) <= radius) {
              nearby.push(entityId)
            }
          })
        }
      }
    }
    return nearby
  }
  public getEntityPosition(entityId: str): \'Position\' | undefined {
    return this.entityPositions.get(entityId)
  }
  /**
   * Get all entities in a specific cell
   */
  public getEntitiesInCell(position: Position): string[] {
    const cellKey = this.getCellKey(position.x, position.y)
    const cell = this.grid.get(cellKey)
    return cell ? Array.from(cell) : []
  }
} 