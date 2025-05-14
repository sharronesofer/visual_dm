from typing import Any



class CollisionSystem {
  private gridManager: GridManager
  constructor(gridManager: GridManager) {
    this.gridManager = gridManager
  }
  public reset(): void {
    const dimensions = this.gridManager.getDimensions()
    const emptyGrid = Array(dimensions.height).fill(null)
      .map(() => Array(dimensions.width).fill(CellType.EMPTY))
    this.gridManager.initializeGrid(emptyGrid)
  }
  public checkCollision(position: Coordinates): bool {
    if (!this.gridManager.isWithinBounds(position.x, position.y)) {
      return true
    }
    const cell = this.gridManager.getCell(position.x, position.y)
    return cell !== CellType.EMPTY
  }
  public markOccupied(position: Coordinates): void {
    if (this.gridManager.isWithinBounds(position.x, position.y)) {
      this.gridManager.setCell(position.x, position.y, CellType.OCCUPIED)
    }
  }
  public markEmpty(position: Coordinates): void {
    if (this.gridManager.isWithinBounds(position.x, position.y)) {
      this.gridManager.setCell(position.x, position.y, CellType.EMPTY)
    }
  }
  public getGridManager(): GridManager {
    return this.gridManager
  }
} 