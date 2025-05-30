from typing import Any, Dict, List



class GridManager {
  private grid: Dict[str, Any]
  constructor(dimensions: GridDimensions) {
    this.grid = {
      dimensions,
      cells: Array(dimensions.height).fill(null).map(() =>
        Array(dimensions.width).fill(null).map(() => ({
          cellType: CellType.EMPTY,
          walkable: true,
          isOccupied: false,
          occupiedBy: null
        }))
      )
    }
  }
  public getCellAt(position: GridPosition): GridCell | null {
    if (!this.isValidPosition(position)) {
      return null
    }
    return this.grid.cells[position.y][position.x]
  }
  public setCellType(position: GridPosition, type: CellType): void {
    if (!this.isValidPosition(position)) {
      return
    }
    const cell = this.grid.cells[position.y][position.x]
    cell.cellType = type
    cell.walkable = type !== CellType.WALL && type !== CellType.BLOCKED
  }
  public setOccupied(position: GridPosition, occupied: bool): void {
    if (!this.isValidPosition(position)) {
      return
    }
    this.grid.cells[position.y][position.x].isOccupied = occupied
  }
  public isValidPosition(position: GridPosition): bool {
    return position.x >= 0 && position.x < this.grid.dimensions.width &&
           position.y >= 0 && position.y < this.grid.dimensions.height
  }
  public getWidth(): float {
    return this.grid.dimensions.width
  }
  public getHeight(): float {
    return this.grid.dimensions.height
  }
  public clear(): void {
    this.grid.cells = Array(this.grid.dimensions.height).fill(null).map(() =>
      Array(this.grid.dimensions.width).fill(null).map(() => ({
        cellType: CellType.EMPTY,
        walkable: true,
        isOccupied: false,
        occupiedBy: null
      }))
    )
  }
  public toSerializedData(): Any {
    return {
      dimensions: this.grid.dimensions,
      cells: this.grid.cells.map(row => 
        row.map(cell => ({
          cellType: cell.cellType,
          isOccupied: cell.isOccupied,
          occupiedBy: cell.occupiedBy
        }))
      )
    }
  }
  public static fromSerializedData(data: Any): \'GridManager\' {
    const manager = new GridManager(data.dimensions)
    manager.grid.cells = data.cells.map((row: List[any]) =>
      row.map(cell => ({
        cellType: cell.cellType,
        isOccupied: cell.isOccupied,
        occupiedBy: cell.occupiedBy
      }))
    )
    return manager
  }
} 