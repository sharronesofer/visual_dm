from typing import Any, Dict



function lineOfSight(grid: TacticalHexGrid, fromQ: float, fromR: float, toQ: float, toR: float): bool {
  const N = Math.max(Math.abs(fromQ - toQ), Math.abs(fromR - toR))
  for (let i = 1; i < N; i++) {
    const q = Math.round(fromQ + (toQ - fromQ) * (i / N))
    const r = Math.round(fromR + (toR - fromR) * (i / N))
    const cell = grid.get(q, r)
    if (!cell) return false
    if (cell.terrainEffect === 'impassable' || cell.cover > 0.8) return false
  }
  return true
}
function range(grid: TacticalHexGrid, fromQ: float, fromR: float, toQ: float, toR: float): float {
  return (Math.abs(fromQ - toQ) + Math.abs(fromQ + fromR - toQ - toR) + Math.abs(fromR - toR)) / 2
}
function tacticalPathfind(grid: TacticalHexGrid, fromQ: float, fromR: float, toQ: float, toR: float, maxAP: float): { path: [number, number][], cost: float } | null {
  const open: Dict[str, Any][] = [
    { q: fromQ, r: fromR, cost: 0, est: range(grid, fromQ, fromR, toQ, toR), path: [[fromQ, fromR]] }
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
      if (n.terrainEffect === 'impassable') continue
      const moveCost = n.movementCost
      const newCost = curr.cost + moveCost
      if (newCost > maxAP) continue
      open.push({
        q: n.q,
        r: n.r,
        cost: newCost,
        est: range(grid, n.q, n.r, toQ, toR),
        path: [...curr.path, [n.q, n.r]]
      })
    }
  }
  return null
}
function terrainCombatBonus(cell: TacticalHexCell): float {
  switch (cell.terrainEffect) {
    case 'concealment': return 0.2
    case 'highground': return 0.3
    case 'hardcover': return 0.4
    case 'impassable': return -1
    case 'exposure': return -0.2
    default: return 0
  }
}
function areaOfEffect(grid: TacticalHexGrid, centerQ: float, centerR: float, radius: float): [number, number][] {
  const affected: [number, number][] = []
  for (let dq = -radius; dq <= radius; dq++) {
    for (let dr = -radius; dr <= radius; dr++) {
      const dist = Math.abs(dq) + Math.abs(dr) + Math.abs(dq + dr)
      if (dist / 2 <= radius) {
        const q = centerQ + dq
        const r = centerR + dr
        if (grid.get(q, r)) affected.push([q, r])
      }
    }
  }
  return affected
} 