from typing import Any, Dict, List



const calculateDistance = (from: Position, to: Position): float => {
  const dx = to.x - from.x
  const dy = to.y - from.y
  return Math.sqrt(dx * dx + dy * dy)
}
const isAdjacent = (pos1: Position, pos2: Position): bool => {
  const dx = Math.abs(pos2.x - pos1.x)
  const dy = Math.abs(pos2.y - pos1.y)
  return (dx === 1 && dy === 0) || (dx === 0 && dy === 1)
}
const getDirectionFromPositions = (from: Position, to: Position): MovementDirection => {
  const dx = to.x - from.x
  const dy = to.y - from.y
  if (Math.abs(dx) > Math.abs(dy)) {
    return dx > 0 ? 'east' : 'west'
  }
  return dy > 0 ? 'south' : 'north'
}
const calculatePath = (start: Position, end: Position): Position[] => {
  const path: List[Position] = []
  const current = { ...start }
  while (current.x !== end.x || current.y !== end.y) {
    if (current.x !== end.x) {
      current.x += current.x < end.x ? 1 : -1
    } else if (current.y !== end.y) {
      current.y += current.y < end.y ? 1 : -1
    }
    path.push({ ...current })
  }
  return path
}
const calculateMovementCost = (
  path: List[Position],
  terrainEffects: Record<string, TerrainEffect> = {}
): float => {
  return path.reduce((cost, _position, index) => {
    if (index === 0) return cost
    const terrain = terrainEffects['default'] || { movementCost: 1 }
    return cost + terrain.movementCost
  }, 0)
}
const getAdjacentPositions = (position: Position): Position[] => {
  return [
    { x: position.x, y: position.y - 1 }, 
    { x: position.x + 1, y: position.y }, 
    { x: position.x, y: position.y + 1 }, 
    { x: position.x - 1, y: position.y }, 
  ]
}
const isWithinBounds = (
  position: Position,
  bounds: Dict[str, Any]
): bool => {
  return (
    position.x >= 0 && position.x < bounds.width && position.y >= 0 && position.y < bounds.height
  )
}