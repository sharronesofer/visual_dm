import { GridDimensions, CellType } from '../../types/grid';

export class GridManager {
  private grid: CellType[][];
  private dimensions: GridDimensions;

  constructor(dimensions: GridDimensions) {
    this.dimensions = dimensions;
    this.grid = Array(dimensions.height).fill(null)
      .map(() => Array(dimensions.width).fill(CellType.EMPTY));
  }

  public initializeGrid(grid: CellType[][]): void {
    this.grid = grid;
  }

  public reset(): void {
    this.grid = Array(this.dimensions.height).fill(null)
      .map(() => Array(this.dimensions.width).fill(CellType.EMPTY));
  }

  public getDimensions(): GridDimensions {
    return this.dimensions;
  }

  public getCell(x: number, y: number): CellType {
    return this.grid[y][x];
  }

  public setCell(x: number, y: number, type: CellType): void {
    this.grid[y][x] = type;
  }

  public isWithinBounds(x: number, y: number): boolean {
    return x >= 0 && x < this.dimensions.width && y >= 0 && y < this.dimensions.height;
  }

  public getGrid(): CellType[][] {
    return this.grid;
  }
} 