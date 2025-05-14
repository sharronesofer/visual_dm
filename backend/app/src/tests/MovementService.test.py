from typing import Any, Dict, List


describe('MovementService', () => {
  let movementService: MovementService
  const mapBounds = { width: 10, height: 10 }
  const obstacles: List[Position] = [
    { x: 5, y: 5 },
    { x: 3, y: 3 },
  ]
  beforeEach(() => {
    movementService = MovementService.getInstance()
    movementService.setMapBounds(mapBounds)
    movementService.setObstacles(obstacles)
  })
  describe('validateMovement', () => {
    test('allows valid movement within bounds', () => {
      const from: Position = { x: 0, y: 0 }
      const to: Position = { x: 1, y: 0 }
      const result = movementService.validateMovement(from, to)
      expect(result.success).toBe(true)
      expect(result.newPosition).toEqual(to)
    })
    test('prevents movement outside bounds', () => {
      const from: Position = { x: 0, y: 0 }
      const to: Position = { x: -1, y: 0 }
      const result = movementService.validateMovement(from, to)
      expect(result.success).toBe(false)
      expect(result.error).toContain('bounds')
    })
    test('prevents movement into obstacles', () => {
      const from: Position = { x: 4, y: 5 }
      const to: Position = { x: 5, y: 5 }
      const result = movementService.validateMovement(from, to)
      expect(result.success).toBe(false)
      expect(result.error).toContain('obstacle')
    })
    test('allows diagonal movement when enabled', () => {
      movementService.setRules({ diagonalMovement: true })
      const from: Position = { x: 0, y: 0 }
      const to: Position = { x: 1, y: 1 }
      const result = movementService.validateMovement(from, to)
      expect(result.success).toBe(true)
    })
    test('prevents diagonal movement when disabled', () => {
      movementService.setRules({ diagonalMovement: false })
      const from: Position = { x: 0, y: 0 }
      const to: Position = { x: 1, y: 1 }
      const result = movementService.validateMovement(from, to)
      expect(result.success).toBe(false)
      expect(result.error).toContain('diagonal')
    })
  })
  describe('movePlayer', () => {
    const initialState: PlayerMovementState = {
      position: Dict[str, Any],
      facing: 'south',
      movement: Dict[str, Any],
      movementPoints: 30,
      isPathfinding: false,
    }
    test('successfully moves player to valid position', () => {
      const targetPosition: Position = { x: 1, y: 0 }
      const result = movementService.movePlayer(initialState, targetPosition)
      expect(result.success).toBe(true)
      expect(result.newPosition).toEqual(targetPosition)
      expect(result.cost).toBe(1)
    })
    test('fails when insufficient movement points', () => {
      const targetPosition: Position = { x: 1, y: 0 }
      const lowPointsState: PlayerMovementState = {
        ...initialState,
        movementPoints: 0,
      }
      const result = movementService.movePlayer(lowPointsState, targetPosition)
      expect(result.success).toBe(false)
      expect(result.error).toContain('movement points')
    })
    test('calculates correct movement cost with terrain effects', () => {
      movementService.setRules({
        terrainEffects: Dict[str, Any],
        },
      })
      const targetPosition: Position = { x: 1, y: 0 }
      const result = movementService.movePlayer(initialState, targetPosition, {
        terrainType: 'rough',
      })
      expect(result.success).toBe(true)
      expect(result.cost).toBe(2)
    })
  })
  describe('getAvailableMoves', () => {
    test('returns all valid adjacent positions', () => {
      const position: Position = { x: 1, y: 1 }
      const moves = movementService.getAvailableMoves(position, 30)
      expect(moves).toContainEqual({ x: 1, y: 0 })
      expect(moves).toContainEqual({ x: 0, y: 1 })
      expect(moves).toContainEqual({ x: 2, y: 1 })
      expect(moves).toContainEqual({ x: 1, y: 2 })
      expect(moves.length).toBe(4) 
    })
    test('excludes positions outside bounds', () => {
      const position: Position = { x: 0, y: 0 }
      const moves = movementService.getAvailableMoves(position, 30)
      expect(moves).not.toContainEqual({ x: -1, y: 0 })
      expect(moves).not.toContainEqual({ x: 0, y: -1 })
    })
    test('excludes obstacle positions', () => {
      const position: Position = { x: 4, y: 5 }
      const moves = movementService.getAvailableMoves(position, 30)
      expect(moves).not.toContainEqual({ x: 5, y: 5 }) 
    })
    test('limits moves by movement points', () => {
      const position: Position = { x: 1, y: 1 }
      const moves = movementService.getAvailableMoves(position, 1)
      expect(moves.length).toBeLessThanOrEqual(4)
      moves.forEach(move => {
        expect(
          Math.abs(move.x - position.x) + Math.abs(move.y - position.y)
        ).toBeLessThanOrEqual(1)
      })
    })
  })
  describe('updatePlayerState', () => {
    const initialState: PlayerMovementState = {
      position: Dict[str, Any],
      facing: 'south',
      movement: Dict[str, Any],
      movementPoints: 30,
      isPathfinding: false,
    }
    test('updates position and facing after successful move', () => {
      const targetPosition: Position = { x: 1, y: 0 }
      const newState = movementService.updatePlayerState(
        initialState,
        targetPosition
      )
      expect(newState.position).toEqual(targetPosition)
      expect(newState.facing).toBe('east')
      expect(newState.movement.isMoving).toBe(true)
      expect(newState.movement.direction).toBe('east')
    })
    test('maintains state after failed move', () => {
      const targetPosition: Position = { x: 5, y: 5 } 
      const newState = movementService.updatePlayerState(
        initialState,
        targetPosition
      )
      expect(newState).toEqual(initialState)
    })
    test('updates movement points after successful move', () => {
      const targetPosition: Position = { x: 1, y: 0 }
      const newState = movementService.updatePlayerState(
        initialState,
        targetPosition
      )
      expect(newState.movementPoints).toBe(initialState.movementPoints - 1)
    })
    test('generates correct path for movement', () => {
      const targetPosition: Position = { x: 1, y: 0 }
      const newState = movementService.updatePlayerState(
        initialState,
        targetPosition
      )
      expect(newState.movement.path).toEqual([targetPosition])
    })
  })
})