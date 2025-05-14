import { HexCell, TerrainType } from './HexCell';

const axialDirections = [
  { q: 1, r: 0 }, { q: 1, r: -1 }, { q: 0, r: -1 },
  { q: -1, r: 0 }, { q: -1, r: 1 }, { q: 0, r: 1 }
];

export class HexGrid {
  cells: Map<string, HexCell>;
  width: number;
  height: number;

  constructor(width: number, height: number) {
    this.width = width;
    this.height = height;
    this.cells = new Map();
    for (let r = 0; r < height; r++) {
      for (let q = 0; q < width; q++) {
        const cell = new HexCell(q, r);
        this.cells.set(this.key(q, r), cell);
      }
    }
  }

  key(q: number, r: number): string {
    return `${q},${r}`;
  }

  get(q: number, r: number): HexCell | undefined {
    return this.cells.get(this.key(q, r));
  }

  setTerrain(q: number, r: number, terrain: TerrainType) {
    const cell = this.get(q, r);
    if (cell) cell.terrain = terrain;
  }

  neighbors(q: number, r: number): HexCell[] {
    return axialDirections
      .map(dir => this.get(q + dir.q, r + dir.r))
      .filter((cell): cell is HexCell => !!cell);
  }

  distance(aq: number, ar: number, bq: number, br: number): number {
    return (Math.abs(aq - bq) + Math.abs(aq + ar - bq - br) + Math.abs(ar - br)) / 2;
  }

  serialize(): object {
    return {
      width: this.width,
      height: this.height,
      cells: Array.from(this.cells.values()).map(cell => cell.serialize())
    };
  }

  static deserialize(data: any): HexGrid {
    const grid = new HexGrid(data.width, data.height);
    for (const cellData of data.cells) {
      const cell = new HexCell(
        cellData.q,
        cellData.r,
        cellData.terrain,
        cellData.elevation,
        cellData.discovered,
        cellData.weather
      );
      grid.cells.set(grid.key(cell.q, cell.r), cell);
    }
    return grid;
  }
} 