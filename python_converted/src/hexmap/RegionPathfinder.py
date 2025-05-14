from typing import Any, Dict, List


class RegionAStarOptions:
    impassableTerrains?: List[TerrainType]
    movementCostMap?: Partial[Dict[TerrainType, float>]
/**
 * A* pathfinding for region-level HexGrid.
 * Returns path as array of [q, r] and total cost, or null if no path.
 */
function regionAStarPathfind(
  grid: HexGrid,
  fromQ: float,
  fromR: float,
  toQ: float,
  toR: float,
  options: \'RegionAStarOptions\' = {}
): { path: [number, number][], cost: float } | null {
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
  } = options
  const open: Dict[str, Any][] = [
    { q: fromQ, r: fromR, cost: 0, est: grid.distance(fromQ, fromR, toQ, toR), path: [[fromQ, fromR]] }
  ]
  const closed = new Set<string>()
  while (open.length > 0) {
    open.sort((a, b) => (a.cost + a.est) - (b.cost + b.est))
    const curr = open.shift()!
    if (curr.q === toQ && curr.r === toR) return { path: curr.path, cost: curr.cost }
    closed.add(`${curr.q},${curr.r}`)
    for (const n of grid.neighbors(curr.q, curr.r)) {
      const key = `${n.q},${n.r}`
      if (closed.has(key)) continue
      if (impassableTerrains.includes(n.terrain)) continue
      let moveCost = movementCostMap[n.terrain] ?? 1
      moveCost += Math.max(0, n.elevation || 0)
      const newCost = curr.cost + moveCost
      open.push({
        q: n.q,
        r: n.r,
        cost: newCost,
        est: grid.distance(n.q, n.r, toQ, toR),
        path: [...curr.path, [n.q, n.r]]
      })
    }
  }
  return null
} 