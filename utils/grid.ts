import { Grid, GridCell, GridPosition, GridDimensions, CellType } from '../types/grid';

export class GridManager {
  private grid: Grid;

  constructor(dimensions: GridDimensions) {
    this.grid = this.initializeGrid(dimensions);
  }

  private initializeGrid(dimensions: GridDimensions): Grid {
    const cells: GridCell[][] = Array(dimensions.height).fill(null).map((_, y) =>
      Array(dimensions.width).fill(null).map((_, x) => ({
        position: { x, y },
        isOccupied: false,
        cellType: CellType.EMPTY,
        walkable: true,
        tags: []
      }))
    );

    return {
      dimensions,
      cells,
      buildings: new Map()
    };
  }

  public getCellAt(position: GridPosition): GridCell | null {
    if (this.isValidPosition(position)) {
      return this.grid.cells[position.y][position.x];
    }
    return null;
  }

  public setCellType(position: GridPosition, type: CellType): boolean {
    const cell = this.getCellAt(position);
    if (cell) {
      cell.cellType = type;
      cell.walkable = type !== CellType.WALL && type !== CellType.BLOCKED;
      return true;
    }
    return false;
  }

  public isValidPosition(position: GridPosition): boolean {
    return position.x >= 0 &&
           position.x < this.grid.dimensions.width &&
           position.y >= 0 &&
           position.y < this.grid.dimensions.height;
  }

  public getAdjacentCells(position: GridPosition): GridCell[] {
    const adjacent: GridCell[] = [];
    const directions = [
      { x: 0, y: -1 },  // North
      { x: 1, y: 0 },   // East
      { x: 0, y: 1 },   // South
      { x: -1, y: 0 }   // West
    ];

    for (const dir of directions) {
      const newPos = {
        x: position.x + dir.x,
        y: position.y + dir.y
      };
      const cell = this.getCellAt(newPos);
      if (cell) {
        adjacent.push(cell);
      }
    }

    return adjacent;
  }

  public isAreaAvailable(position: GridPosition, dimensions: GridDimensions): boolean {
    for (let y = position.y; y < position.y + dimensions.height; y++) {
      for (let x = position.x; x < position.x + dimensions.width; x++) {
        const cell = this.getCellAt({ x, y });
        if (!cell || cell.isOccupied) {
          return false;
        }
      }
    }
    return true;
  }

  public occupyArea(position: GridPosition, dimensions: GridDimensions, buildingId: string): boolean {
    if (!this.isAreaAvailable(position, dimensions)) {
      return false;
    }

    for (let y = position.y; y < position.y + dimensions.height; y++) {
      for (let x = position.x; x < position.x + dimensions.width; x++) {
        const cell = this.getCellAt({ x, y })!;
        cell.isOccupied = true;
        cell.buildingId = buildingId;
        cell.cellType = CellType.BUILDING;
      }
    }

    this.grid.buildings.set(buildingId, position);
    return true;
  }

  public clearArea(position: GridPosition, dimensions: GridDimensions): void {
    for (let y = position.y; y < position.y + dimensions.height; y++) {
      for (let x = position.x; x < position.x + dimensions.width; x++) {
        const cell = this.getCellAt({ x, y });
        if (cell) {
          cell.isOccupied = false;
          cell.buildingId = undefined;
          cell.cellType = CellType.EMPTY;
        }
      }
    }
  }

  public getBuildingPosition(buildingId: string): GridPosition | undefined {
    return this.grid.buildings.get(buildingId);
  }

  public getGrid(): Grid {
    return this.grid;
  }
} 