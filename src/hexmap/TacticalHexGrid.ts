import { HexGrid } from './HexGrid';
import { HexCell, TerrainType, WeatherType } from './HexCell';

export interface TacticalHexCellProps {
  cover: number; // 0-1
  movementCost: number;
  terrainEffect: string;
  unitOccupants: string[]; // unit IDs
}

export class TacticalHexCell extends HexCell {
  cover: number;
  movementCost: number;
  terrainEffect: string;
  unitOccupants: string[];

  constructor(q: number, r: number, terrain: TerrainType = 'plains', elevation = 0, discovered = false, weather?: WeatherType, props?: Partial<TacticalHexCellProps>) {
    super(q, r, terrain, elevation, discovered, weather);
    this.cover = props?.cover ?? 0;
    this.movementCost = props?.movementCost ?? 1;
    this.terrainEffect = props?.terrainEffect ?? '';
    this.unitOccupants = props?.unitOccupants ?? [];
  }
}

export class TacticalHexGrid extends HexGrid {
  cells: Map<string, TacticalHexCell>;

  constructor(width: number, height: number) {
    super(width, height);
    this.cells = new Map();
    for (let r = 0; r < height; r++) {
      for (let q = 0; q < width; q++) {
        const cell = new TacticalHexCell(q, r);
        this.cells.set(this.key(q, r), cell);
      }
    }
  }

  get(q: number, r: number): TacticalHexCell | undefined {
    return this.cells.get(this.key(q, r));
  }

  setCombatProps(q: number, r: number, props: Partial<TacticalHexCellProps>) {
    const cell = this.get(q, r);
    if (!cell) return;
    if (props.cover !== undefined) cell.cover = props.cover;
    if (props.movementCost !== undefined) cell.movementCost = props.movementCost;
    if (props.terrainEffect !== undefined) cell.terrainEffect = props.terrainEffect;
    if (props.unitOccupants !== undefined) cell.unitOccupants = props.unitOccupants;
  }

  addUnit(q: number, r: number, unitId: string) {
    const cell = this.get(q, r);
    if (cell && !cell.unitOccupants.includes(unitId)) cell.unitOccupants.push(unitId);
  }

  removeUnit(q: number, r: number, unitId: string) {
    const cell = this.get(q, r);
    if (cell) cell.unitOccupants = cell.unitOccupants.filter(id => id !== unitId);
  }

  static fromRegionGrid(regionGrid: HexGrid): TacticalHexGrid {
    const grid = new TacticalHexGrid(regionGrid.width, regionGrid.height);
    for (let r = 0; r < regionGrid.height; r++) {
      for (let q = 0; q < regionGrid.width; q++) {
        const regionCell = regionGrid.get(q, r);
        const tacticalCell = grid.get(q, r);
        if (regionCell && tacticalCell) {
          tacticalCell.terrain = regionCell.terrain;
          tacticalCell.elevation = regionCell.elevation;
          tacticalCell.weather = regionCell.weather as import('./HexCell').WeatherType | undefined;
          // Set combat props based on terrain
          switch (regionCell.terrain) {
            case 'forest':
              tacticalCell.cover = 0.7;
              tacticalCell.movementCost = 2;
              tacticalCell.terrainEffect = 'concealment';
              break;
            case 'mountain':
              tacticalCell.cover = 0.5;
              tacticalCell.movementCost = 3;
              tacticalCell.terrainEffect = 'highground';
              break;
            case 'urban':
              tacticalCell.cover = 0.9;
              tacticalCell.movementCost = 1;
              tacticalCell.terrainEffect = 'hardcover';
              break;
            case 'water':
              tacticalCell.cover = 0.0;
              tacticalCell.movementCost = 99;
              tacticalCell.terrainEffect = 'impassable';
              break;
            case 'desert':
              tacticalCell.cover = 0.1;
              tacticalCell.movementCost = 2;
              tacticalCell.terrainEffect = 'exposure';
              break;
            default:
              tacticalCell.cover = 0.2;
              tacticalCell.movementCost = 1;
              tacticalCell.terrainEffect = '';
          }
        }
      }
    }
    return grid;
  }

  neighbors(q: number, r: number): TacticalHexCell[] {
    const axialDirections = [
      { q: 1, r: 0 }, { q: 1, r: -1 }, { q: 0, r: -1 },
      { q: -1, r: 0 }, { q: -1, r: 1 }, { q: 0, r: 1 }
    ];
    return axialDirections
      .map(dir => this.get(q + dir.q, r + dir.r))
      .filter((cell): cell is TacticalHexCell => !!cell);
  }

  // Get all cells within a certain range of a position
  getNeighborsInRange(q: number, r: number, range: number): TacticalHexCell[] {
    const neighbors: TacticalHexCell[] = [];
    for (let dq = -range; dq <= range; dq++) {
      for (let dr = -range; dr <= range; dr++) {
        if (Math.abs(dq + dr) <= range) {
          const cell = this.get(q + dq, r + dr);
          if (cell) {
            neighbors.push(cell);
          }
        }
      }
    }
    return neighbors;
  }

  // Calculate the distance between two hex coordinates
  getDistance(q1: number, r1: number, q2: number, r2: number): number {
    return Math.max(
      Math.abs(q1 - q2),
      Math.abs(r1 - r2),
      Math.abs((q1 + r1) - (q2 + r2))
    );
  }
} 