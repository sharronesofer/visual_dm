import { HexGrid } from './HexGrid';
import { TerrainType, WeatherType } from './HexCell';

interface RegionAStarOptions {
  impassableTerrains?: TerrainType[];
  movementCostMap?: Partial<Record<TerrainType, number>>;
}

/**
 * A* pathfinding for region-level HexGrid.
 * Returns path as array of [q, r] and total cost, or null if no path.
 */
export function regionAStarPathfind(
  grid: HexGrid,
  fromQ: number,
  fromR: number,
  toQ: number,
  toR: number,
  options: RegionAStarOptions = {}
): { path: [number, number][], cost: number } | null {
  const {
    impassableTerrains = ['water', 'mountain'],
    movementCostMap = {
      plains: 1,
      forest: 2,
      mountain: 99,
      water: 99,
      desert: 2,
      urban: 1
    }
  } = options;

  const open: {q: number, r: number, cost: number, est: number, path: [number, number][]}[] = [
    { q: fromQ, r: fromR, cost: 0, est: grid.distance(fromQ, fromR, toQ, toR), path: [[fromQ, fromR]] }
  ];
  const closed = new Set<string>();

  while (open.length > 0) {
    open.sort((a, b) => (a.cost + a.est) - (b.cost + b.est));
    const curr = open.shift()!;
    if (curr.q === toQ && curr.r === toR) return { path: curr.path, cost: curr.cost };
    closed.add(`${curr.q},${curr.r}`);
    for (const n of grid.neighbors(curr.q, curr.r)) {
      const key = `${n.q},${n.r}`;
      if (closed.has(key)) continue;
      if (impassableTerrains.includes(n.terrain)) continue;
      // Movement cost: base + elevation + weather (if desired)
      let moveCost = movementCostMap[n.terrain] ?? 1;
      moveCost += Math.max(0, n.elevation || 0);
      // Optionally: weather effects (not implemented here)
      const newCost = curr.cost + moveCost;
      open.push({
        q: n.q,
        r: n.r,
        cost: newCost,
        est: grid.distance(n.q, n.r, toQ, toR),
        path: [...curr.path, [n.q, n.r]]
      });
    }
  }
  return null;
} 