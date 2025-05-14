from typing import Any, Dict



jest.mock('../../../utils/logger', () => ({
  Logger: Dict[str, Any])
    })
  }
}))
describe('SpatialIndex', () => {
  let spatialIndex: SpatialIndex
  let mockBuilding: Building
  beforeEach(() => {
    spatialIndex = new SpatialIndex()
    mockBuilding = {
      id: 'building1',
      name: 'Test Building',
      type: 'inn',
      position: Dict[str, Any],
      dimensions: Dict[str, Any],
      createdAt: new Date(),
      updatedAt: new Date()
    }
  })
  describe('insert', () => {
    it('should insert a building into the spatial index', () => {
      spatialIndex.insert(mockBuilding)
      const results = spatialIndex.search({
        minX: 80,
        minY: 80,
        maxX: 120,
        maxY: 120
      })
      expect(results).toHaveLength(1)
      expect(results[0]).toEqual(mockBuilding)
    })
    it('should update existing building in the spatial index', () => {
      spatialIndex.insert(mockBuilding)
      const updatedBuilding = {
        ...mockBuilding,
        position: Dict[str, Any]
      }
      spatialIndex.insert(updatedBuilding)
      const oldResults = spatialIndex.search({
        minX: 80,
        minY: 80,
        maxX: 120,
        maxY: 120
      })
      expect(oldResults).toHaveLength(0)
      const newResults = spatialIndex.search({
        minX: 180,
        minY: 180,
        maxX: 220,
        maxY: 220
      })
      expect(newResults).toHaveLength(1)
      expect(newResults[0]).toEqual(updatedBuilding)
    })
    it('should handle errors gracefully', () => {
      const invalidBuilding = { ...mockBuilding, position: undefined }
      expect(() => spatialIndex.insert(invalidBuilding as any)).toThrow()
    })
  })
  describe('remove', () => {
    it('should remove a building from the spatial index', () => {
      spatialIndex.insert(mockBuilding)
      spatialIndex.remove(mockBuilding.id)
      const results = spatialIndex.search({
        minX: 80,
        minY: 80,
        maxX: 120,
        maxY: 120
      })
      expect(results).toHaveLength(0)
    })
    it('should handle non-existent building gracefully', () => {
      expect(() => spatialIndex.remove('nonexistent')).not.toThrow()
    })
  })
  describe('search', () => {
    beforeEach(() => {
      spatialIndex.insert(mockBuilding)
      spatialIndex.insert({
        ...mockBuilding,
        id: 'building2',
        position: Dict[str, Any]
      })
      spatialIndex.insert({
        ...mockBuilding,
        id: 'building3',
        position: Dict[str, Any]
      })
    })
    it('should find buildings within search bounds', () => {
      const results = spatialIndex.search({
        minX: 90,
        minY: 90,
        maxX: 160,
        maxY: 160
      })
      expect(results).toHaveLength(2)
      expect(results.map(b => b.id)).toEqual(['building1', 'building2'])
    })
    it('should return empty array for out-of-bounds search', () => {
      const results = spatialIndex.search({
        minX: 300,
        minY: 300,
        maxX: 400,
        maxY: 400
      })
      expect(results).toHaveLength(0)
    })
    it('should handle errors gracefully', () => {
      expect(() => spatialIndex.search({} as any)).toThrow()
    })
  })
  describe('findNearest', () => {
    beforeEach(() => {
      spatialIndex.insert(mockBuilding) 
      spatialIndex.insert({
        ...mockBuilding,
        id: 'building2',
        position: Dict[str, Any]
      })
      spatialIndex.insert({
        ...mockBuilding,
        id: 'building3',
        position: Dict[str, Any]
      })
    })
    it('should find k nearest buildings', () => {
      const nearest = spatialIndex.findNearest(120, 120, 2)
      expect(nearest).toHaveLength(2)
      expect(nearest.map(b => b.id)).toEqual(['building1', 'building2'])
    })
    it('should handle k larger than available buildings', () => {
      const nearest = spatialIndex.findNearest(120, 120, 5)
      expect(nearest).toHaveLength(3)
    })
    it('should handle errors gracefully', () => {
      expect(() => spatialIndex.findNearest(NaN, 120, 2)).toThrow()
    })
  })
  describe('clear', () => {
    it('should remove all buildings from the spatial index', () => {
      spatialIndex.insert(mockBuilding)
      spatialIndex.insert({
        ...mockBuilding,
        id: 'building2',
        position: Dict[str, Any]
      })
      spatialIndex.clear()
      const results = spatialIndex.search({
        minX: 0,
        minY: 0,
        maxX: 1000,
        maxY: 1000
      })
      expect(results).toHaveLength(0)
    })
  })
  describe('getAll', () => {
    it('should return all buildings in the spatial index', () => {
      spatialIndex.insert(mockBuilding)
      spatialIndex.insert({
        ...mockBuilding,
        id: 'building2',
        position: Dict[str, Any]
      })
      const all = spatialIndex.getAll()
      expect(all).toHaveLength(2)
      expect(all.map(b => b.id)).toEqual(['building1', 'building2'])
    })
    it('should return empty array when index is empty', () => {
      const all = spatialIndex.getAll()
      expect(all).toHaveLength(0)
    })
  })
  describe('bulkLoad', () => {
    it('should load multiple buildings at once', () => {
      const buildings = [
        mockBuilding,
        {
          ...mockBuilding,
          id: 'building2',
          position: Dict[str, Any]
        },
        {
          ...mockBuilding,
          id: 'building3',
          position: Dict[str, Any]
        }
      ]
      spatialIndex.bulkLoad(buildings)
      const all = spatialIndex.getAll()
      expect(all).toHaveLength(3)
      expect(all.map(b => b.id)).toEqual(['building1', 'building2', 'building3'])
    })
    it('should handle empty array gracefully', () => {
      expect(() => spatialIndex.bulkLoad([])).not.toThrow()
    })
    it('should handle errors gracefully', () => {
      const invalidBuildings = [{ ...mockBuilding, position: undefined }]
      expect(() => spatialIndex.bulkLoad(invalidBuildings as any[])).toThrow()
    })
  })
  describe('edge cases and performance', () => {
    it('should handle large number of items efficiently', () => {
      const items = Array.from({ length: 1000 }, (_, i) => ({
        id: `item-${i}`,
        name: `Building ${i}`,
        type: 'residential',
        position: Dict[str, Any],
        dimensions: Dict[str, Any]
      }))
      const startInsert = performance.now()
      spatialIndex.bulkLoad(items)
      const endInsert = performance.now()
      expect(endInsert - startInsert).toBeLessThan(1000) 
      const startSearch = performance.now()
      const results = spatialIndex.search({
        minX: 400,
        minY: 400,
        maxX: 600,
        maxY: 600
      })
      const endSearch = performance.now()
      expect(endSearch - startSearch).toBeLessThan(100) 
    })
    it('should handle overlapping items correctly', () => {
      const item1 = {
        id: 'overlap-1',
        name: 'Overlap Building 1',
        type: 'residential',
        position: Dict[str, Any],
        dimensions: Dict[str, Any]
      }
      const item2 = {
        id: 'overlap-2',
        name: 'Overlap Building 2',
        type: 'residential',
        position: Dict[str, Any],
        dimensions: Dict[str, Any]
      }
      spatialIndex.insert(item1)
      spatialIndex.insert(item2)
      const results = spatialIndex.search({
        minX: 4,
        minY: 4,
        maxX: 6,
        maxY: 6
      })
      expect(results).toHaveLength(2)
      expect(results.map(r => r.id)).toContain('overlap-1')
      expect(results.map(r => r.id)).toContain('overlap-2')
    })
    it('should handle items at boundary conditions', () => {
      const boundaryItem = {
        id: 'boundary',
        name: 'Boundary Building',
        type: 'residential',
        position: Dict[str, Any],
        dimensions: Dict[str, Any]
      }
      expect(() => spatialIndex.insert(boundaryItem)).not.toThrow()
      const results = spatialIndex.search({
        minX: Number.MAX_SAFE_INTEGER - 150,
        minY: Number.MAX_SAFE_INTEGER - 150,
        maxX: Number.MAX_SAFE_INTEGER - 50,
        maxY: Number.MAX_SAFE_INTEGER - 50
      })
      expect(results).toHaveLength(1)
      expect(results[0].id).toBe('boundary')
    })
    it('should handle item removal and reinsertion correctly', () => {
      const item = {
        id: 'moving',
        name: 'Moving Building',
        type: 'residential',
        position: Dict[str, Any],
        dimensions: Dict[str, Any]
      }
      spatialIndex.insert(item)
      for (let i = 1; i <= 10; i++) {
        const newPosition = {
          x: i * 10,
          y: i * 10,
          z: i * 10
        }
        spatialIndex.remove(item.id)
        spatialIndex.insert({
          ...item,
          position: newPosition
        })
        const results = spatialIndex.search({
          minX: newPosition.x - 1,
          minY: newPosition.y - 1,
          maxX: newPosition.x + 1,
          maxY: newPosition.y + 1
        })
        expect(results).toHaveLength(1)
        expect(results[0].id).toBe('moving')
        expect(results[0].position).toEqual(newPosition)
      }
    })
  })
}) 