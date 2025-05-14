from typing import Any


describe('PathfindingSystem', () => {
  let gridManager: GridManager
  let collisionSystem: CollisionSystem
  let pathfinding: PathfindingSystem
  beforeEach(() => {
    gridManager = new GridManager(10, 10)
    collisionSystem = new CollisionSystem()
    pathfinding = new PathfindingSystem(gridManager, collisionSystem)
  })
  describe('Basic Pathfinding', () => {
    test('finds direct path when no obstacles', () => {
      const start: GridPosition = { x: 0, y: 0 }
      const end: GridPosition = { x: 2, y: 2 }
      const path = pathfinding.findPath(start, end)
      expect(path).toHaveLength(5) 
      expect(path[0]).toEqual(start)
      expect(path[path.length - 1]).toEqual(end)
    })
    test('returns empty path when no route possible', () => {
      gridManager.setCellType({ x: 1, y: 1 }, CellType.WALL)
      gridManager.setCellType({ x: 2, y: 1 }, CellType.WALL)
      gridManager.setCellType({ x: 1, y: 2 }, CellType.WALL)
      const start: GridPosition = { x: 0, y: 0 }
      const end: GridPosition = { x: 2, y: 2 }
      const path = pathfinding.findPath(start, end)
      expect(path).toHaveLength(0)
    })
  })
  describe('Category-Specific Routing', () => {
    test('SOCIAL category prefers roads', () => {
      gridManager.setCellType({ x: 1, y: 0 }, CellType.ROAD)
      gridManager.setCellType({ x: 2, y: 0 }, CellType.ROAD)
      gridManager.setCellType({ x: 2, y: 1 }, CellType.ROAD)
      gridManager.setCellType({ x: 2, y: 2 }, CellType.ROAD)
      const start: GridPosition = { x: 0, y: 0 }
      const end: GridPosition = { x: 2, y: 2 }
      const path = pathfinding.findPath(start, end, POICategory.SOCIAL)
      expect(path).toHaveLength(6)
      expect(path[1]).toEqual({ x: 1, y: 0 }) 
    })
    test('DUNGEON category avoids roads', () => {
      gridManager.setCellType({ x: 1, y: 0 }, CellType.ROAD)
      gridManager.setCellType({ x: 2, y: 0 }, CellType.ROAD)
      const start: GridPosition = { x: 0, y: 0 }
      const end: GridPosition = { x: 2, y: 2 }
      const path = pathfinding.findPath(start, end, POICategory.DUNGEON)
      expect(path[1]).toEqual({ x: 1, y: 1 }) 
    })
  })
  describe('Path Caching', () => {
    test('returns cached path for same request', () => {
      const start: GridPosition = { x: 0, y: 0 }
      const end: GridPosition = { x: 2, y: 2 }
      const firstPath = pathfinding.findPath(start, end)
      const secondPath = pathfinding.findPath(start, end)
      expect(secondPath).toEqual(firstPath)
    })
    test('invalidates cache when terrain changes', () => {
      const start: GridPosition = { x: 0, y: 0 }
      const end: GridPosition = { x: 2, y: 2 }
      const firstPath = pathfinding.findPath(start, end)
      gridManager.setCellType({ x: 1, y: 1 }, CellType.WALL)
      pathfinding.invalidateCache({ x: 1, y: 1 })
      const secondPath = pathfinding.findPath(start, end)
      expect(secondPath).not.toEqual(firstPath)
    })
  })
  describe('Dynamic Path Updates', () => {
    test('updates path segment when obstacle appears', () => {
      const start: GridPosition = { x: 0, y: 0 }
      const end: GridPosition = { x: 4, y: 4 }
      const originalPath = pathfinding.findPath(start, end)
      gridManager.setCellType({ x: 2, y: 2 }, CellType.WALL)
      const updatedPath = pathfinding.updatePathSegment(originalPath, 1, 3)
      expect(updatedPath).not.toEqual(originalPath)
      expect(updatedPath[0]).toEqual(start)
      expect(updatedPath[updatedPath.length - 1]).toEqual(end)
    })
    test('keeps original path if no better alternative found', () => {
      const start: GridPosition = { x: 0, y: 0 }
      const end: GridPosition = { x: 2, y: 2 }
      const originalPath = pathfinding.findPath(start, end)
      const updatedPath = pathfinding.updatePathSegment(originalPath, 1, 1)
      expect(updatedPath).toEqual(originalPath)
    })
  })
  describe('Collision Integration', () => {
    test('avoids crowded areas', () => {
      const start: GridPosition = { x: 0, y: 0 }
      const end: GridPosition = { x: 3, y: 3 }
      collisionSystem.addObject({ x: 1, y: 1 }, { width: 1, height: 1 }, 'obstacle1')
      collisionSystem.addObject({ x: 2, y: 2 }, { width: 1, height: 1 }, 'obstacle2')
      const path = pathfinding.findPath(start, end)
      expect(path[1]).not.toEqual({ x: 1, y: 1 })
      expect(path[2]).not.toEqual({ x: 2, y: 2 })
    })
    test('still finds path through moderately crowded areas if necessary', () => {
      const start: GridPosition = { x: 0, y: 0 }
      const end: GridPosition = { x: 2, y: 2 }
      collisionSystem.addObject({ x: 2, y: 0 }, { width: 1, height: 1 }, 'obstacle1')
      collisionSystem.addObject({ x: 0, y: 2 }, { width: 1, height: 1 }, 'obstacle2')
      const path = pathfinding.findPath(start, end)
      expect(path).toHaveLength(5) 
    })
  })
}) 