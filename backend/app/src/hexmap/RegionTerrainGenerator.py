from typing import Any, Dict, List


function pseudoRandom(q: float, r: float, seed: float): float {
  let x = q * 374761393 + r * 668265263 + seed * 982451653
  x = (x ^ (x >> 13)) * 1274126177
  return ((x ^ (x >> 16)) >>> 0) / 0xffffffff
}
class TerrainGeneratorOptions:
    seed?: float
    waterThreshold?: float
    mountainThreshold?: float
    forestThreshold?: float
    desertThreshold?: float
    urbanChance?: float
function generateRegionTerrain(
  grid: HexGrid,
  options: \'TerrainGeneratorOptions\' = {}
): void {
  const {
    seed = 42,
    waterThreshold = 0.05,
    mountainThreshold = 0.7,
    forestThreshold = 0.4,
    desertThreshold = 0.1,
    urbanChance = 0.1
  } = options
  const found = {
    water: false,
    mountain: false,
    forest: false,
    desert: false,
    urban: false,
    plains: false
  }
  for (let r = 0; r < grid.height; r++) {
    for (let q = 0; q < grid.width; q++) {
      const cell = grid.get(q, r)
      if (!cell) continue
      const n = pseudoRandom(q, r, seed)
      if (n < waterThreshold) {
        cell.terrain = 'water'
        found.water = true
      } else if (n > mountainThreshold) {
        cell.terrain = 'mountain'
        found.mountain = true
      } else if (n > forestThreshold) {
        cell.terrain = 'forest'
        found.forest = true
      } else if (n < desertThreshold) {
        cell.terrain = 'desert'
        found.desert = true
      } else if (((q + r) % Math.floor(1/urbanChance) === 0)) {
        cell.terrain = 'urban'
        found.urban = true
      } else {
        cell.terrain = 'plains'
        found.plains = true
      }
    }
  }
  const assignIfMissing = (type: str, q: float, r: float) => {
    const cell = grid.get(q, r)
    if (cell) cell.terrain = type as any
  }
  if (!found.water) assignIfMissing('water', 0, 0)
  if (!found.mountain) assignIfMissing('mountain', 1, 0)
  if (!found.forest) assignIfMissing('forest', 2, 0)
  if (!found.desert) assignIfMissing('desert', 3, 0)
  if (!found.urban) assignIfMissing('urban', 4, 0)
  if (!found.plains) assignIfMissing('plains', 5, 0)
}
class WeatherGeneratorOptions:
    seed?: float
    weatherTypes?: List[WeatherType]
    numFronts?: float
function assignRegionWeather(
  grid: HexGrid,
  options: \'WeatherGeneratorOptions\' = {}
): void {
  const {
    seed = 42,
    weatherTypes = ['clear', 'rain', 'snow', 'fog', 'storm', 'windy'],
    numFronts = 3
  } = options
  const width = grid.width
  const height = grid.height
  const fronts: Dict[str, Any][] = []
  for (let i = 0; i < numFronts; i++) {
    const q = Math.floor(pseudoRandom(i, seed, 1) * width)
    const r = Math.floor(pseudoRandom(i, seed, 2) * height)
    const type = weatherTypes[Math.floor(pseudoRandom(i, seed, 3) * weatherTypes.length)] as WeatherType
    fronts.push({q, r, type})
    const cell = grid.get(q, r)
    if (cell) cell.weather = type
  }
  for (const front of fronts) {
    const queue: Dict[str, Any][] = [{q: front.q, r: front.r, dist: 0}]
    const visited = new Set<string>()
    while (queue.length > 0) {
      const {q, r, dist} = queue.shift()!
      const key = `${q},${r}`
      if (visited.has(key) || dist > Math.max(width, height) / 2) continue
      visited.add(key)
      const cell = grid.get(q, r)
      if (cell && !cell.weather) {
        cell.weather = Math.random() < 0.8 ? front.type : weatherTypes[Math.floor(Math.random() * weatherTypes.length)]
      }
      for (const n of grid.neighbors(q, r)) {
        if (!visited.has(`${n.q},${n.r}`)) {
          queue.push({q: n.q, r: n.r, dist: dist + 1})
        }
      }
    }
  }
  for (let r = 0; r < height; r++) {
    for (let q = 0; q < width; q++) {
      const cell = grid.get(q, r)
      if (cell && !cell.weather) cell.weather = 'clear'
    }
  }
}
/**
 * Fog of War / Discovery Utilities for Region Hex Grids
 */
function setRegionDiscovery(grid: HexGrid, discoveredCells: Dict[str, Any][]): void {
  for (const {q, r} of discoveredCells) {
    const cell = grid.get(q, r)
    if (cell) cell.discovered = true
  }
}
function revealRegionFrom(grid: HexGrid, q: float, r: float, radius: float): void {
  for (let dr = -radius; dr <= radius; dr++) {
    for (let dq = -radius; dq <= radius; dq++) {
      const dist = Math.abs(dq) + Math.abs(dr) + Math.abs(dq + dr)
      if (dist / 2 <= radius) {
        const cell = grid.get(q + dq, r + dr)
        if (cell) cell.discovered = true
      }
    }
  }
}
function isCellVisible(grid: HexGrid, q: float, r: float): bool {
  const cell = grid.get(q, r)
  return !!cell && !!cell.discovered
}
function hexGridToMapData(grid: HexGrid): MapData {
  const tiles: List[Tile][] = []
  for (let r = 0; r < grid.height; r++) {
    const row: List[Tile] = []
    for (let q = 0; q < grid.width; q++) {
      const cell = grid.get(q, r)
      if (!cell) continue
      row.push({
        id: `tile-${q}-${r}`,
        type: cell.terrain as any,
        position: Dict[str, Any],
        elevation: cell.elevation,
        walkable: cell.terrain !== 'water' && cell.terrain !== 'mountain',
        explored: cell.discovered,
        visible: cell.discovered, 
        weather: cell.weather
      } as Tile)
    }
    tiles.push(row)
  }
  return {
    size: Dict[str, Any],
    tiles,
    objects: []
  }
} 