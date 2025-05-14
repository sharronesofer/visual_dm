from typing import Any, Dict



  TerrainData,
  TerrainFeatureType,
  TerrainModificationType
} from '../../types/terrain'
describe('TerrainManager', () => {
  let terrainManager: TerrainManager
  let mockTerrainData: TerrainData
  beforeEach(() => {
    mockTerrainData = {
      heightMap: Array(10).fill(null).map(() => Array(10).fill(0)),
      features: [
        {
          type: TerrainFeatureType.WATER,
          position: Dict[str, Any],
          size: Dict[str, Any],
          elevation: -1
        },
        {
          type: TerrainFeatureType.MOUNTAIN,
          position: Dict[str, Any],
          size: Dict[str, Any],
          elevation: 5
        }
      ],
      buildableAreas: [
        {
          position: Dict[str, Any],
          size: Dict[str, Any],
          slope: 0,
          preferredCategories: ['SOCIAL']
        },
        {
          position: Dict[str, Any],
          size: Dict[str, Any],
          slope: 5,
          preferredCategories: ['DUNGEON']
        }
      ]
    }
    mockTerrainData.heightMap[7][7] = 5 
    mockTerrainData.heightMap[2][2] = -1 
    terrainManager = new TerrainManager(mockTerrainData)
  })
  describe('Terrain Analysis', () => {
    test('analyzes terrain at flat position', () => {
      const result = terrainManager.analyzeTerrain({ x: 0, y: 0 })
      expect(result.slope).toBe(0)
      expect(result.elevation).toBe(0)
      expect(result.buildabilityScore).toBeGreaterThan(0.5)
      expect(result.environmentalImpact).toBeLessThan(0.5)
    })
    test('analyzes terrain near water feature', () => {
      const result = terrainManager.analyzeTerrain({ x: 2, y: 2 })
      expect(result.elevation).toBe(-1)
      expect(result.nearbyFeatures).toHaveLength(1)
      expect(result.nearbyFeatures[0].type).toBe(TerrainFeatureType.WATER)
      expect(result.environmentalImpact).toBeGreaterThan(0.5)
    })
    test('analyzes terrain near mountain with slope', () => {
      const result = terrainManager.analyzeTerrain({ x: 7, y: 7 })
      expect(result.elevation).toBe(5)
      expect(result.slope).toBeGreaterThan(0)
      expect(result.buildabilityScore).toBeLessThan(0.5)
    })
  })
  describe('Terrain Modification', () => {
    test('levels terrain to target height', () => {
      terrainManager.modifyTerrain({
        position: Dict[str, Any],
        type: TerrainModificationType.LEVEL,
        params: Dict[str, Any]
      })
      const analysis = terrainManager.analyzeTerrain({ x: 3, y: 3 })
      expect(analysis.elevation).toBe(2)
    })
    test('smooths terrain gradients', () => {
      terrainManager.modifyTerrain({
        position: Dict[str, Any],
        type: TerrainModificationType.LEVEL,
        params: Dict[str, Any]
      })
      terrainManager.modifyTerrain({
        position: Dict[str, Any],
        type: TerrainModificationType.SMOOTH,
        params: Dict[str, Any]
      })
      const analysis = terrainManager.analyzeTerrain({ x: 4, y: 4 })
      expect(analysis.slope).toBeLessThan(3)
    })
    test('creates ramp between elevations', () => {
      terrainManager.modifyTerrain({
        position: Dict[str, Any],
        type: TerrainModificationType.RAMP,
        params: Dict[str, Any]
      })
      const analysis = terrainManager.analyzeTerrain({ x: 5, y: 5 }, 2)
      expect(analysis.slope).toBeGreaterThan(0)
      expect(analysis.slope).toBeLessThan(45) 
    })
    test('adjusts foundation for building placement', () => {
      terrainManager.modifyTerrain({
        position: Dict[str, Any],
        type: TerrainModificationType.FOUNDATION,
        params: {}
      })
      const analysis = terrainManager.analyzeTerrain({ x: 1, y: 1 })
      expect(analysis.buildabilityScore).toBeGreaterThan(0.7)
    })
  })
  describe('Buildable Area Search', () => {
    test('finds suitable area for small structure', () => {
      const area = terrainManager.findBuildableArea(
        { width: 2, height: 2 },
        [TerrainFeatureType.MOUNTAIN]
      )
      expect(area).toBeTruthy()
      expect(area?.size.width).toBeGreaterThanOrEqual(2)
      expect(area?.size.height).toBeGreaterThanOrEqual(2)
    })
    test('returns null for oversized structure', () => {
      const area = terrainManager.findBuildableArea(
        { width: 20, height: 20 }
      )
      expect(area).toBeNull()
    })
    test('prefers areas near requested features', () => {
      const area = terrainManager.findBuildableArea(
        { width: 2, height: 2 },
        [TerrainFeatureType.WATER]
      )
      expect(area).toBeTruthy()
      const distanceToWater = Math.sqrt(
        Math.pow(area!.position.x - 2, 2) + 
        Math.pow(area!.position.y - 2, 2)
      )
      expect(distanceToWater).toBeLessThan(5)
    })
  })
  describe('Cache Management', () => {
    test('caches analysis results', () => {
      const position = { x: 6, y: 6 }
      const result1 = terrainManager.analyzeTerrain(position)
      terrainManager.modifyTerrain({
        position: Dict[str, Any],
        type: TerrainModificationType.LEVEL,
        params: Dict[str, Any]
      })
      const result2 = terrainManager.analyzeTerrain(position)
      expect(result2).toEqual(result1)
    })
    test('invalidates cache when terrain is modified', () => {
      const position = { x: 6, y: 6 }
      const result1 = terrainManager.analyzeTerrain(position)
      terrainManager.modifyTerrain({
        position,
        type: TerrainModificationType.LEVEL,
        params: Dict[str, Any]
      })
      const result2 = terrainManager.analyzeTerrain(position)
      expect(result2).not.toEqual(result1)
      expect(result2.elevation).toBe(2)
    })
  })
}) 