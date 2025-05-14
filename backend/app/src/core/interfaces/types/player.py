from typing import Any, Dict, List, Union


MovementDirection = Union['north', 'south', 'east', 'west']
class MovementState:
    isMoving: bool
    direction: Union[MovementDirection, None]
    speed: float
    path: List[Position]
    destination: Union[Position, None]
class MovementOptions:
    diagonal?: bool
    ignoreObstacles?: bool
    maxDistance?: float
    autoDiscover?: bool
class MovementResult:
    success: bool
    newPosition: Position
    cost: float
    path: List[Position]
    error?: str
class PlayerMovementState:
    position: Position
    facing: MovementDirection
    movement: \'MovementState\'
    movementPoints: float
    isPathfinding: bool
class TerrainEffect:
    id: str
    name: str
    movementCost: float
    description: str
    isObstacle: bool
class MovementRules:
    baseMovementPoints: float
    diagonalMovement: bool
    terrainEffects: Dict[str, TerrainEffect>
    maxPathLength?: float
    pathfindingAlgorithm?: Union['astar', 'dijkstra']
const calculateDistance = (from: Position, to: Position): float => {
  const dx = to.x - from.x
  const dy = to.y - from.y
  return Math.sqrt(dx * dx + dy * dy)
}
const getDirectionFromPositions = (from: Position, to: Position): MovementDirection => {
  const dx = to.x - from.x
  const dy = to.y - from.y
  if (Math.abs(dx) > Math.abs(dy)) {
    return dx > 0 ? 'east' : 'west'
  }
  return dy > 0 ? 'south' : 'north'
}
const isAdjacent = (pos1: Position, pos2: Position): bool => {
  const dx = Math.abs(pos2.x - pos1.x)
  const dy = Math.abs(pos2.y - pos1.y)
  return (dx === 1 && dy === 0) || (dx === 0 && dy === 1)
}
PlayerState = {
  id: str
  name: str
  position: Position
  health: float
  maxHealth: float
  inventory: List[any]
  movement: \'MovementState\'
}