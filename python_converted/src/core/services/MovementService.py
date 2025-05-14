from typing import Any, Dict, List


  MovementDirection,
  MovementOptions,
  MovementResult,
  MovementState,
  PlayerMovementState,
  MovementRules,
  TerrainEffect,
} from '../types/player'
  calculateDistance,
  calculatePath,
  calculateMovementCost,
  getDirectionFromPositions,
  isWithinBounds,
  isAdjacent,
  getAdjacentPositions,
} from '../utils/movementUtils'
class MovementService {
  private static instance: \'MovementService\'
  private rules: MovementRules
  private mapBounds: Dict[str, Any]
  private obstacles: Set<string>
  private constructor() {
    this.rules = {
      baseMovementPoints: 30,
      diagonalMovement: false,
      terrainEffects: {},
      maxPathLength: 100,
    }
    this.mapBounds = { width: 100, height: 100 }
    this.obstacles = new Set()
  }
  public static getInstance(): \'MovementService\' {
    if (!MovementService.instance) {
      MovementService.instance = new MovementService()
    }
    return MovementService.instance
  }
  public setRules(rules: Partial<MovementRules>): void {
    this.rules = { ...this.rules, ...rules }
  }
  public setMapBounds(bounds: Dict[str, Any]): void {
    this.mapBounds = bounds
  }
  public setObstacles(positions: List[Position]): void {
    this.obstacles = new Set(positions.map(p => `${p.x},${p.y}`))
  }
  public addTerrainEffect(effect: TerrainEffect): void {
    this.rules.terrainEffects[effect.id] = effect
  }
  private isObstacle(position: Position): bool {
    return this.obstacles.has(`${position.x},${position.y}`)
  }
  public validateMovement(
    from: Position,
    to: Position,
    options: MovementOptions = {}
  ): MovementResult {
    if (!isWithinBounds(to, this.mapBounds)) {
      return {
        success: false,
        newPosition: from,
        cost: 0,
        path: [],
        error: 'Destination is out of bounds',
      }
    }
    const path = calculatePath(from, to)
    if (this.rules.maxPathLength && path.length > this.rules.maxPathLength) {
      return {
        success: false,
        newPosition: from,
        cost: 0,
        path: [],
        error: 'Path exceeds maximum length',
      }
    }
    if (!options.ignoreObstacles && path.some(pos => this.isObstacle(pos))) {
      return {
        success: false,
        newPosition: from,
        cost: 0,
        path: [],
        error: 'Path blocked by obstacle',
      }
    }
    const cost = calculateMovementCost(path, this.rules.terrainEffects)
    return {
      success: true,
      newPosition: to,
      cost,
      path,
    }
  }
  public movePlayer(
    currentState: PlayerMovementState,
    targetPosition: Position,
    options: MovementOptions = {}
  ): MovementResult {
    const result = this.validateMovement(currentState.position, targetPosition, options)
    if (!result.success) {
      return result
    }
    if (currentState.movementPoints < result.cost) {
      return {
        success: false,
        newPosition: currentState.position,
        cost: result.cost,
        path: result.path,
        error: 'Insufficient movement points',
      }
    }
    return result
  }
  public getAvailableMoves(position: Position, movementPoints: float): Position[] {
    const available: List[Position] = []
    const adjacent = getAdjacentPositions(position)
    for (const pos of adjacent) {
      if (
        isWithinBounds(pos, this.mapBounds) &&
        !this.isObstacle(pos) &&
        this.validateMovement(position, pos).success
      ) {
        available.push(pos)
      }
    }
    return available
  }
  public updatePlayerState(
    state: PlayerMovementState,
    targetPosition: Position
  ): PlayerMovementState {
    const movement = this.movePlayer(state, targetPosition)
    if (!movement.success) {
      return state
    }
    return {
      ...state,
      position: movement.newPosition,
      facing: getDirectionFromPositions(state.position, movement.newPosition),
      movement: Dict[str, Any],
      movementPoints: state.movementPoints - movement.cost,
    }
  }
  public isValidPosition(position: Position): bool {
    return isWithinBounds(position, this.mapBounds) && !this.isObstacle(position)
  }
}