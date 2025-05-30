from typing import Any, Dict


describe('MovementService', () => {
  let movementService: MovementService
  beforeEach(() => {
    movementService = MovementService.getInstance()
    movementService.setMapBounds({ width: 10, height: 10 })
    movementService.setObstacles([])
  })
  describe('validateMovement', () => {
    it('should allow valid movement within bounds', () => {
      const from: Position = { x: 0, y: 0 }
      const to: Position = { x: 1, y: 1 }
      const result = movementService.validateMovement(from, to)
      expect(result.success).toBe(true)
      expect(result.newPosition).toEqual(to)
      expect(result.path).toHaveLength(2)
    })
    it('should prevent movement outside bounds', () => {
      const from: Position = { x: 0, y: 0 }
      const to: Position = { x: -1, y: 0 }
      const result = movementService.validateMovement(from, to)
      expect(result.success).toBe(false)
      expect(result.error).toBe('Destination is out of bounds')
    })
    it('should respect obstacles', () => {
      const from: Position = { x: 0, y: 0 }
      const to: Position = { x: 2, y: 0 }
      const obstacle: Position = { x: 1, y: 0 }
      movementService.setObstacles([obstacle])
      const result = movementService.validateMovement(from, to)
      expect(result.success).toBe(false)
      expect(result.error).toBe('Path blocked by obstacle')
    })
    it('should calculate correct movement cost with terrain effects', () => {
      const from: Position = { x: 0, y: 0 }
      const to: Position = { x: 2, y: 0 }
      const swampEffect: TerrainEffect = {
        id: 'swamp',
        name: 'Swamp',
        movementCost: 2,
        description: 'Difficult terrain',
        isObstacle: false,
      }
      movementService.addTerrainEffect(swampEffect)
      const result = movementService.validateMovement(from, to)
      expect(result.success).toBe(true)
      expect(result.cost).toBe(2) 
    })
  })
  describe('movePlayer', () => {
    it('should update player state on valid movement', () => {
      const currentState = {
        position: Dict[str, Any],
        facing: 'south' as const,
        movement: Dict[str, Any],
        movementPoints: 10,
        isPathfinding: false,
      }
      const targetPosition = { x: 1, y: 0 }
      const result = movementService.movePlayer(currentState, targetPosition)
      expect(result.success).toBe(true)
      expect(result.newPosition).toEqual(targetPosition)
    })
    it('should prevent movement when insufficient points', () => {
      const currentState = {
        position: Dict[str, Any],
        facing: 'south' as const,
        movement: Dict[str, Any],
        movementPoints: 0,
        isPathfinding: false,
      }
      const targetPosition = { x: 1, y: 0 }
      const result = movementService.movePlayer(currentState, targetPosition)
      expect(result.success).toBe(false)
      expect(result.error).toBe('Insufficient movement points')
    })
  })
  describe('getAvailableMoves', () => {
    it('should return all valid adjacent positions', () => {
      const position: Position = { x: 1, y: 1 }
      const movementPoints = 10
      const availableMoves = movementService.getAvailableMoves(
        position,
        movementPoints
      )
      expect(availableMoves).toHaveLength(4) 
      expect(availableMoves).toContainEqual({ x: 1, y: 0 }) 
      expect(availableMoves).toContainEqual({ x: 2, y: 1 }) 
      expect(availableMoves).toContainEqual({ x: 1, y: 2 }) 
      expect(availableMoves).toContainEqual({ x: 0, y: 1 }) 
    })
    it('should exclude positions with obstacles', () => {
      const position: Position = { x: 1, y: 1 }
      const movementPoints = 10
      const obstacle: Position = { x: 1, y: 0 } 
      movementService.setObstacles([obstacle])
      const availableMoves = movementService.getAvailableMoves(
        position,
        movementPoints
      )
      expect(availableMoves).toHaveLength(3)
      expect(availableMoves).not.toContainEqual(obstacle)
    })
  })
})