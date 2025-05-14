from typing import Any, Dict, List


  calculateDistance,
  calculatePath,
  calculateMovementCost,
  getDirectionFromPositions,
  isWithinBounds,
  isAdjacent,
  getAdjacentPositions,
} from '../utils/movementUtils'
describe('Movement Utilities', () => {
  describe('calculateDistance', () => {
    test('calculates correct horizontal distance', () => {
      const from: Position = { x: 0, y: 0 }
      const to: Position = { x: 3, y: 0 }
      expect(calculateDistance(from, to)).toBe(3)
    })
    test('calculates correct vertical distance', () => {
      const from: Position = { x: 0, y: 0 }
      const to: Position = { x: 0, y: 4 }
      expect(calculateDistance(from, to)).toBe(4)
    })
    test('calculates correct diagonal distance', () => {
      const from: Position = { x: 0, y: 0 }
      const to: Position = { x: 3, y: 4 }
      expect(calculateDistance(from, to)).toBe(5)
    })
  })
  describe('calculatePath', () => {
    test('generates correct horizontal path', () => {
      const start: Position = { x: 0, y: 0 }
      const end: Position = { x: 2, y: 0 }
      const path = calculatePath(start, end)
      expect(path).toEqual([
        { x: 1, y: 0 },
        { x: 2, y: 0 },
      ])
    })
    test('generates correct vertical path', () => {
      const start: Position = { x: 0, y: 0 }
      const end: Position = { x: 0, y: 2 }
      const path = calculatePath(start, end)
      expect(path).toEqual([
        { x: 0, y: 1 },
        { x: 0, y: 2 },
      ])
    })
    test('generates correct diagonal path', () => {
      const start: Position = { x: 0, y: 0 }
      const end: Position = { x: 2, y: 2 }
      const path = calculatePath(start, end)
      expect(path).toEqual([
        { x: 1, y: 0 },
        { x: 2, y: 0 },
        { x: 2, y: 1 },
        { x: 2, y: 2 },
      ])
    })
    test('returns empty path for same position', () => {
      const pos: Position = { x: 0, y: 0 }
      expect(calculatePath(pos, pos)).toEqual([])
    })
  })
  describe('calculateMovementCost', () => {
    test('returns base cost for normal terrain', () => {
      const path: List[Position] = [
        { x: 0, y: 0 },
        { x: 1, y: 0 },
      ]
      expect(calculateMovementCost(path)).toBe(1)
    })
    test('returns correct cost for diagonal movement', () => {
      const path: List[Position] = [
        { x: 0, y: 0 },
        { x: 1, y: 1 },
      ]
      expect(calculateMovementCost(path)).toBe(1)
    })
    test('applies terrain effect multiplier', () => {
      const path: List[Position] = [
        { x: 0, y: 0 },
        { x: 1, y: 0 },
      ]
      const terrainEffects: Record<string, TerrainEffect> = {
        default: Dict[str, Any],
      }
      expect(calculateMovementCost(path, terrainEffects)).toBe(1)
    })
  })
  describe('getDirectionFromPositions', () => {
    test('returns correct cardinal directions', () => {
      const from: Position = { x: 0, y: 0 }
      expect(getDirectionFromPositions(from, { x: 1, y: 0 })).toBe('east')
      expect(getDirectionFromPositions(from, { x: -1, y: 0 })).toBe('west')
      expect(getDirectionFromPositions(from, { x: 0, y: 1 })).toBe('south')
      expect(getDirectionFromPositions(from, { x: 0, y: -1 })).toBe('north')
    })
    test('returns primary direction for diagonal movement', () => {
      const from: Position = { x: 0, y: 0 }
      expect(getDirectionFromPositions(from, { x: 2, y: 1 })).toBe('east')
      expect(getDirectionFromPositions(from, { x: 1, y: 2 })).toBe('south')
    })
  })
  describe('isWithinBounds', () => {
    const bounds = { width: 10, height: 10 }
    test('returns true for valid positions', () => {
      expect(isWithinBounds({ x: 0, y: 0 }, bounds)).toBe(true)
      expect(isWithinBounds({ x: 9, y: 9 }, bounds)).toBe(true)
      expect(isWithinBounds({ x: 5, y: 5 }, bounds)).toBe(true)
    })
    test('returns false for out-of-bounds positions', () => {
      expect(isWithinBounds({ x: -1, y: 0 }, bounds)).toBe(false)
      expect(isWithinBounds({ x: 0, y: -1 }, bounds)).toBe(false)
      expect(isWithinBounds({ x: 10, y: 0 }, bounds)).toBe(false)
      expect(isWithinBounds({ x: 0, y: 10 }, bounds)).toBe(false)
    })
  })
  describe('isAdjacent', () => {
    const center: Position = { x: 5, y: 5 }
    test('returns true for adjacent positions', () => {
      expect(isAdjacent(center, { x: 4, y: 5 })).toBe(true)
      expect(isAdjacent(center, { x: 6, y: 5 })).toBe(true)
      expect(isAdjacent(center, { x: 5, y: 4 })).toBe(true)
      expect(isAdjacent(center, { x: 5, y: 6 })).toBe(true)
    })
    test('returns false for non-adjacent positions', () => {
      expect(isAdjacent(center, { x: 3, y: 5 })).toBe(false)
      expect(isAdjacent(center, { x: 5, y: 7 })).toBe(false)
      expect(isAdjacent(center, { x: 4, y: 4 })).toBe(false) 
    })
    test('returns false for same position', () => {
      expect(isAdjacent(center, center)).toBe(false)
    })
  })
  describe('getAdjacentPositions', () => {
    test('returns all adjacent positions', () => {
      const center: Position = { x: 5, y: 5 }
      const adjacent = getAdjacentPositions(center)
      expect(adjacent).toContainEqual({ x: 4, y: 5 })
      expect(adjacent).toContainEqual({ x: 6, y: 5 })
      expect(adjacent).toContainEqual({ x: 5, y: 4 })
      expect(adjacent).toContainEqual({ x: 5, y: 6 })
      expect(adjacent.length).toBe(4)
    })
  })
})