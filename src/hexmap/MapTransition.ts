import { HexGrid } from './HexGrid';
import { TacticalHexGrid } from './TacticalHexGrid';

/**
 * Extracts a square area from the region grid and returns a TacticalHexGrid.
 * @param regionGrid The full region HexGrid
 * @param centerQ Center q coordinate
 * @param centerR Center r coordinate
 * @param size Side length of the square area (odd number recommended)
 */
export function regionToTactical(regionGrid: HexGrid, centerQ: number, centerR: number, size: number): TacticalHexGrid {
  const half = Math.floor(size / 2);
  const tacticalGrid = new TacticalHexGrid(size, size);
  for (let dq = -half; dq <= half; dq++) {
    for (let dr = -half; dr <= half; dr++) {
      const q = centerQ + dq;
      const r = centerR + dr;
      const regionCell = regionGrid.get(q, r);
      const tq = dq + half;
      const tr = dr + half;
      const tacticalCell = tacticalGrid.get(tq, tr);
      if (regionCell && tacticalCell) {
        tacticalCell.terrain = regionCell.terrain;
        tacticalCell.elevation = regionCell.elevation;
        tacticalCell.weather = regionCell.weather;
        // Set combat props as in TacticalHexGrid.fromRegionGrid
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
  return tacticalGrid;
}

/**
 * Syncs tactical grid state back to the region grid (stub).
 */
export function tacticalToRegion(regionGrid: HexGrid, tacticalGrid: TacticalHexGrid, centerQ: number, centerR: number): void {
  // TODO: Implement state sync (e.g., terrain changes, unit positions)
} 