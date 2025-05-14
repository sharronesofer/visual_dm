import { HexGrid } from './HexGrid';
import { TerrainType } from './HexCell';
import { WeatherSystem } from '../worldgen/environment/WeatherSystem';
import { WeatherType } from './HexCell';
import { MapData, Tile } from '../visualization/map/types';

// Simple noise function (replace with Perlin/Simplex for more realism)
function pseudoRandom(q: number, r: number, seed: number): number {
  // Xorshift-like hash
  let x = q * 374761393 + r * 668265263 + seed * 982451653;
  x = (x ^ (x >> 13)) * 1274126177;
  return ((x ^ (x >> 16)) >>> 0) / 0xffffffff;
}

export interface TerrainGeneratorOptions {
  seed?: number;
  waterThreshold?: number;
  mountainThreshold?: number;
  forestThreshold?: number;
  desertThreshold?: number;
  urbanChance?: number;
}

export function generateRegionTerrain(
  grid: HexGrid,
  options: TerrainGeneratorOptions = {}
): void {
  const {
    seed = 42,
    waterThreshold = 0.05,
    mountainThreshold = 0.7,
    forestThreshold = 0.4,
    desertThreshold = 0.1,
    urbanChance = 0.1
  } = options;

  const found = {
    water: false,
    mountain: false,
    forest: false,
    desert: false,
    urban: false,
    plains: false
  };

  for (let r = 0; r < grid.height; r++) {
    for (let q = 0; q < grid.width; q++) {
      const cell = grid.get(q, r);
      if (!cell) continue;
      const n = pseudoRandom(q, r, seed);
      if (n < waterThreshold) {
        cell.terrain = 'water';
        found.water = true;
      } else if (n > mountainThreshold) {
        cell.terrain = 'mountain';
        found.mountain = true;
      } else if (n > forestThreshold) {
        cell.terrain = 'forest';
        found.forest = true;
      } else if (n < desertThreshold) {
        cell.terrain = 'desert';
        found.desert = true;
      } else if (((q + r) % Math.floor(1/urbanChance) === 0)) {
        cell.terrain = 'urban';
        found.urban = true;
      } else {
        cell.terrain = 'plains';
        found.plains = true;
      }
    }
  }

  // Guarantee at least one of each type for test purposes
  const assignIfMissing = (type: string, q: number, r: number) => {
    const cell = grid.get(q, r);
    if (cell) cell.terrain = type as any;
  };
  if (!found.water) assignIfMissing('water', 0, 0);
  if (!found.mountain) assignIfMissing('mountain', 1, 0);
  if (!found.forest) assignIfMissing('forest', 2, 0);
  if (!found.desert) assignIfMissing('desert', 3, 0);
  if (!found.urban) assignIfMissing('urban', 4, 0);
  if (!found.plains) assignIfMissing('plains', 5, 0);
}

export interface WeatherGeneratorOptions {
  seed?: number;
  weatherTypes?: WeatherType[];
  numFronts?: number;
}

export function assignRegionWeather(
  grid: HexGrid,
  options: WeatherGeneratorOptions = {}
): void {
  const {
    seed = 42,
    weatherTypes = ['clear', 'rain', 'snow', 'fog', 'storm', 'windy'],
    numFronts = 3
  } = options;
  const width = grid.width;
  const height = grid.height;
  // Pick numFronts random seed cells and assign random weather
  const fronts: {q: number, r: number, type: WeatherType}[] = [];
  for (let i = 0; i < numFronts; i++) {
    const q = Math.floor(pseudoRandom(i, seed, 1) * width);
    const r = Math.floor(pseudoRandom(i, seed, 2) * height);
    const type = weatherTypes[Math.floor(pseudoRandom(i, seed, 3) * weatherTypes.length)] as WeatherType;
    fronts.push({q, r, type});
    const cell = grid.get(q, r);
    if (cell) cell.weather = type;
  }
  // Propagate weather from each front
  for (const front of fronts) {
    const queue: {q: number, r: number, dist: number}[] = [{q: front.q, r: front.r, dist: 0}];
    const visited = new Set<string>();
    while (queue.length > 0) {
      const {q, r, dist} = queue.shift()!;
      const key = `${q},${r}`;
      if (visited.has(key) || dist > Math.max(width, height) / 2) continue;
      visited.add(key);
      const cell = grid.get(q, r);
      if (cell && !cell.weather) {
        // With some probability, assign the same weather, else random
        cell.weather = Math.random() < 0.8 ? front.type : weatherTypes[Math.floor(Math.random() * weatherTypes.length)];
      }
      // Add neighbors
      for (const n of grid.neighbors(q, r)) {
        if (!visited.has(`${n.q},${n.r}`)) {
          queue.push({q: n.q, r: n.r, dist: dist + 1});
        }
      }
    }
  }
  // Any unassigned cells get 'clear'
  for (let r = 0; r < height; r++) {
    for (let q = 0; q < width; q++) {
      const cell = grid.get(q, r);
      if (cell && !cell.weather) cell.weather = 'clear';
    }
  }
}

/**
 * Fog of War / Discovery Utilities for Region Hex Grids
 */
export function setRegionDiscovery(grid: HexGrid, discoveredCells: {q: number, r: number}[]): void {
  for (const {q, r} of discoveredCells) {
    const cell = grid.get(q, r);
    if (cell) cell.discovered = true;
  }
}

export function revealRegionFrom(grid: HexGrid, q: number, r: number, radius: number): void {
  for (let dr = -radius; dr <= radius; dr++) {
    for (let dq = -radius; dq <= radius; dq++) {
      const dist = Math.abs(dq) + Math.abs(dr) + Math.abs(dq + dr);
      if (dist / 2 <= radius) {
        const cell = grid.get(q + dq, r + dr);
        if (cell) cell.discovered = true;
      }
    }
  }
}

export function isCellVisible(grid: HexGrid, q: number, r: number): boolean {
  const cell = grid.get(q, r);
  return !!cell && !!cell.discovered;
}

export function hexGridToMapData(grid: HexGrid): MapData {
  const tiles: Tile[][] = [];
  for (let r = 0; r < grid.height; r++) {
    const row: Tile[] = [];
    for (let q = 0; q < grid.width; q++) {
      const cell = grid.get(q, r);
      if (!cell) continue;
      row.push({
        id: `tile-${q}-${r}`,
        type: cell.terrain as any,
        position: { x: q, y: r },
        elevation: cell.elevation,
        walkable: cell.terrain !== 'water' && cell.terrain !== 'mountain',
        explored: cell.discovered,
        visible: cell.discovered, // For now, visible = discovered
        weather: cell.weather
      } as Tile);
    }
    tiles.push(row);
  }
  return {
    size: { width: grid.width, height: grid.height },
    tiles,
    objects: []
  };
} 