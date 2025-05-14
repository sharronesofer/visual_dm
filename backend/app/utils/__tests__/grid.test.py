from typing import Any


describe('GridManager', () => {
  let gridManager: GridManager
  const dimensions: GridDimensions = { width: 10, height: 10 }
  beforeEach(() => {
    gridManager = new GridManager(dimensions)
  })
  describe('Grid Initialization', () => {
    test('creates grid with correct dimensions', () => {
      const grid = gridManager.getGrid()
      expect(grid.cells.length).toBe(dimensions.height)
      expect(grid.cells[0].length).toBe(dimensions.width)
    })
    test('initializes cells with default values', () => {
      const cell = gridManager.getCellAt({ x: 0, y: 0 })
      expect(cell).toBeDefined()
      expect(cell?.isOccupied).toBeFalsy()
      expect(cell?.cellType).toBe(CellType.EMPTY)
    })
  })
  describe('Cell Operations', () => {
    test('sets cell type correctly', () => {
      const position: GridPosition = { x: 1, y: 1 }
      gridManager.setCellType(position, CellType.BUILDING)
      const cell = gridManager.getCellAt(position)
      expect(cell?.cellType).toBe(CellType.BUILDING)
    })
    test('validates positions correctly', () => {
      expect(gridManager.isValidPosition({ x: 0, y: 0 })).toBeTruthy()
      expect(gridManager.isValidPosition({ x: -1, y: 0 })).toBeFalsy()
      expect(gridManager.isValidPosition({ x: dimensions.width, y: 0 })).toBeFalsy()
    })
    test('gets adjacent cells correctly', () => {
      const position: GridPosition = { x: 1, y: 1 }
      const adjacent = gridManager.getAdjacentCells(position)
      expect(adjacent.length).toBe(4) 
    })
    test('handles edge cells correctly', () => {
      const position: GridPosition = { x: 0, y: 0 }
      const adjacent = gridManager.getAdjacentCells(position)
      expect(adjacent.length).toBe(2) 
    })
  })
  describe('Area Operations', () => {
    test('checks area availability correctly', () => {
      const position: GridPosition = { x: 0, y: 0 }
      const buildingDimensions: GridDimensions = { width: 2, height: 2 }
      expect(gridManager.isAreaAvailable(position, buildingDimensions)).toBeTruthy()
      gridManager.setCellType({ x: 0, y: 0 }, CellType.BUILDING)
      expect(gridManager.isAreaAvailable(position, buildingDimensions)).toBeFalsy()
    })
    test('occupies area correctly', () => {
      const position: GridPosition = { x: 0, y: 0 }
      const buildingDimensions: GridDimensions = { width: 2, height: 2 }
      const buildingId = 'test-building'
      expect(gridManager.occupyArea(position, buildingDimensions, buildingId)).toBeTruthy()
      for (let y = 0; y < buildingDimensions.height; y++) {
        for (let x = 0; x < buildingDimensions.width; x++) {
          const cell = gridManager.getCellAt({ x: position.x + x, y: position.y + y })
          expect(cell?.isOccupied).toBeTruthy()
          expect(cell?.buildingId).toBe(buildingId)
          expect(cell?.cellType).toBe(CellType.BUILDING)
        }
      }
    })
    test('clears area correctly', () => {
      const position: GridPosition = { x: 0, y: 0 }
      const buildingDimensions: GridDimensions = { width: 2, height: 2 }
      const buildingId = 'test-building'
      gridManager.occupyArea(position, buildingDimensions, buildingId)
      gridManager.clearArea(position, buildingDimensions)
      for (let y = 0; y < buildingDimensions.height; y++) {
        for (let x = 0; x < buildingDimensions.width; x++) {
          const cell = gridManager.getCellAt({ x: position.x + x, y: position.y + y })
          expect(cell?.isOccupied).toBeFalsy()
          expect(cell?.buildingId).toBeUndefined()
          expect(cell?.cellType).toBe(CellType.EMPTY)
        }
      }
    })
    test('tracks building positions correctly', () => {
      const position: GridPosition = { x: 0, y: 0 }
      const buildingDimensions: GridDimensions = { width: 2, height: 2 }
      const buildingId = 'test-building'
      gridManager.occupyArea(position, buildingDimensions, buildingId)
      expect(gridManager.getBuildingPosition(buildingId)).toEqual(position)
    })
  })
  describe('Cell Type and Walkability', () => {
    test('updates walkability based on cell type', () => {
      const position: GridPosition = { x: 1, y: 1 }
      gridManager.setCellType(position, CellType.WALL)
      expect(gridManager.getCellAt(position)?.walkable).toBeFalsy()
      gridManager.setCellType(position, CellType.BLOCKED)
      expect(gridManager.getCellAt(position)?.walkable).toBeFalsy()
      gridManager.setCellType(position, CellType.ROAD)
      expect(gridManager.getCellAt(position)?.walkable).toBeTruthy()
    })
  })
}) 