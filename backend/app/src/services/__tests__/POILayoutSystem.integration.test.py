from typing import Any, Dict


  POICategory,
  POIPlacementRules,
  SpatialLayoutConfig,
  PlacementPattern,
  CategoryConfig
} from '../../types/spatial'
describe('POI Layout System - Integration Tests', () => {
  let poiManager: POIManager
  let gridManager: GridManager
  let collisionSystem: CollisionSystem
  let terrainManager: TerrainManager
  let layoutGenerator: SpatialLayoutGenerator
  let config: SpatialLayoutConfig
  beforeEach(() => {
    const dimensions: GridDimensions = { width: 100, height: 100 }
    gridManager = new GridManager(dimensions)
    collisionSystem = new CollisionSystem(gridManager)
    const terrainData: TerrainData = {
      heightMap: Array(dimensions.height).fill(null)
        .map(() => Array(dimensions.width).fill(0)),
      features: [],
      buildableAreas: [{
        position: Dict[str, Any],
        size: dimensions,
        slope: 0,
        preferredCategories: []
      }]
    }
    terrainManager = new TerrainManager(terrainData)
    poiManager = POIManager.getInstance()
    config = {
      minDistance: 5,
      maxPOIs: 10,
      placementPattern: PlacementPattern.ORGANIC,
      categories: [
        {
          type: POIType.SETTLEMENT,
          subtype: POISubtype.VILLAGE,
          count: 3,
          rules: Dict[str, Any]
        }
      ]
    }
    layoutGenerator = new SpatialLayoutGenerator(
      poiManager,
      gridManager,
      collisionSystem,
      terrainManager,
      config
    )
  })
  afterEach(() => {
    poiManager.reset()
    gridManager.reset()
    collisionSystem.reset()
    terrainManager.reset()
  })
  test('POIs are placed according to terrain constraints', async () => {
    const mountainFeature: TerrainFeature = {
      type: TerrainFeatureType.MOUNTAIN,
      position: Dict[str, Any],
      size: Dict[str, Any]
    }
    terrainManager.addFeature(mountainFeature)
    const waterFeature: TerrainFeature = {
      type: TerrainFeatureType.WATER,
      position: Dict[str, Any],
      size: Dict[str, Any]
    }
    terrainManager.addFeature(waterFeature)
    await layoutGenerator.generate()
    const pois = poiManager.getAllPOIs()
    for (const poi of pois) {
      const terrain = terrainManager.getTerrainAt(poi.position)
      expect(terrain).toBe(TerrainFeatureType.PLAIN)
    }
  })
  test('POIs maintain minimum distance requirements', async () => {
    await layoutGenerator.generate()
    const pois = poiManager.getAllPOIs()
    for (let i = 0; i < pois.length; i++) {
      for (let j = i + 1; j < pois.length; j++) {
        const distance = calculateDistance(pois[i].position, pois[j].position)
        expect(distance).toBeGreaterThanOrEqual(config.minDistance)
      }
    }
  })
  function calculateDistance(pos1: Coordinates, pos2: Coordinates): float {
    const dx = pos2.x - pos1.x
    const dy = pos2.y - pos1.y
    const dz = pos2.z - pos1.z
    return Math.sqrt(dx * dx + dy * dy + dz * dz)
  }
  describe('Layout Generation and POI Integration', () => {
    it('generates layout and creates corresponding POIs', async () => {
      const layout = layoutGenerator.generateLayout()
      expect(layout.placements.length).toBeGreaterThan(0)
      const createdPOIs = await Promise.all(
        layout.placements.map(placement => {
          const poiType = getCategoryPOIType(placement.category)
          return poiManager.createPOI(
            poiType,
            POISubtype.DEFAULT,
            {
              name: `${poiType}-${placement.id}`,
              coordinates: Dict[str, Any],
              thematicElements: Dict[str, Any]
            }
          )
        })
      )
      expect(createdPOIs.length).toBe(layout.placements.length)
      createdPOIs.forEach(poi => {
        expect(poi).toBeDefined()
        expect(poiManager.getPOI(poi.id)).toBeDefined()
      })
      layout.placements.forEach((placement, index) => {
        const poi = createdPOIs[index]
        expect(poi.coordinates.x).toBe(placement.position.x)
        expect(poi.coordinates.y).toBe(placement.position.y)
      })
    })
    it('respects terrain constraints when placing POIs', async () => {
      terrainManager.addFeature({
        type: TerrainFeatureType.MOUNTAIN,
        position: Dict[str, Any],
        size: Dict[str, Any]
      })
      terrainManager.addFeature({
        type: TerrainFeatureType.WATER,
        position: Dict[str, Any],
        size: Dict[str, Any]
      })
      const layout = layoutGenerator.generateLayout()
      layout.placements.forEach(placement => {
        const terrain = terrainManager.getTerrainAt(placement.position)
        expect(terrain.buildable).toBe(true)
        const rules = config.poiRules.find(r => r.category === placement.category)!
        expect(rules.avoidTerrainTypes).not.toContain(terrain.type)
      })
    })
    it('generates valid paths between POIs', async () => {
      const layout = layoutGenerator.generateLayout()
      layout.paths.forEach(path => {
        expect(path.length).toBeGreaterThan(1)
        for (let i = 1; i < path.length; i++) {
          const dx = Math.abs(path[i].x - path[i - 1].x)
          const dy = Math.abs(path[i].y - path[i - 1].y)
          expect(dx + dy).toBeLessThanOrEqual(1) 
        }
        const startPlacement = layout.placements.find(p => 
          p.position.x === path[0].x && p.position.y === path[0].y
        )
        const endPlacement = layout.placements.find(p => 
          p.position.x === path[path.length - 1].x && 
          p.position.y === path[path.length - 1].y
        )
        expect(startPlacement).toBeDefined()
        expect(endPlacement).toBeDefined()
      })
    })
    it('handles POI lifecycle with layout updates', async () => {
      const layout = layoutGenerator.generateLayout()
      const createdPOIs = await Promise.all(
        layout.placements.map(placement => {
          const poiType = getCategoryPOIType(placement.category)
          return poiManager.createPOI(
            poiType,
            POISubtype.DEFAULT,
            {
              name: `${poiType}-${placement.id}`,
              coordinates: Dict[str, Any],
              thematicElements: Dict[str, Any]
            }
          )
        })
      )
      createdPOIs.forEach(poi => {
        expect(poiManager.getPOI(poi.id)).toBeDefined()
      })
      const centerX = 75
      const centerY = 75
      const radius = 20
      createdPOIs.forEach(poi => {
        const distance = Math.sqrt(
          Math.pow(poi.coordinates.x - centerX, 2) +
          Math.pow(poi.coordinates.y - centerY, 2)
        )
        if (distance > radius) {
          poiManager.deregisterPOI(poi.id)
        }
      })
      createdPOIs.forEach(poi => {
        const distance = Math.sqrt(
          Math.pow(poi.coordinates.x - centerX, 2) +
          Math.pow(poi.coordinates.y - centerY, 2)
        )
        if (distance <= radius) {
          expect(poiManager.getPOI(poi.id)).toBeDefined()
        } else {
          expect(poiManager.getPOI(poi.id)).toBeUndefined()
        }
      })
    })
  })
  describe('Layout Patterns and Category Distribution', () => {
    it('follows pattern-specific placement rules', () => {
      const layout = layoutGenerator.generateLayout()
      const socialPlacements = layout.placements.filter(p => 
        p.category === POICategory.SOCIAL
      )
      const focusPoint = config.patterns[POICategory.SOCIAL].focusPoint!
      socialPlacements.forEach(placement => {
        const distance = Math.sqrt(
          Math.pow(placement.position.x - focusPoint.x, 2) +
          Math.pow(placement.position.y - focusPoint.y, 2)
        )
        expect(distance).toBeLessThanOrEqual(20) 
      })
      const explorationPlacements = layout.placements.filter(p => 
        p.category === POICategory.EXPLORATION
      )
      const orientation = config.patterns[POICategory.EXPLORATION].orientation!
      if (explorationPlacements.length >= 2) {
        const angles = []
        for (let i = 1; i < explorationPlacements.length; i++) {
          const dx = explorationPlacements[i].position.x - explorationPlacements[i-1].position.x
          const dy = explorationPlacements[i].position.y - explorationPlacements[i-1].position.y
          const angle = Math.atan2(dy, dx) * (180 / Math.PI)
          angles.push(angle)
        }
        const avgAngle = angles.reduce((a, b) => a + b) / angles.length
        expect(Math.abs(avgAngle - orientation)).toBeLessThanOrEqual(30)
      }
      const dungeonPlacements = layout.placements.filter(p => 
        p.category === POICategory.DUNGEON
      )
      expect(dungeonPlacements.length).toBeGreaterThanOrEqual(1)
      expect(dungeonPlacements.length).toBeLessThanOrEqual(
        Math.floor(config.gridDimensions.width * config.gridDimensions.height * 
        config.patterns[POICategory.DUNGEON].density)
      )
    })
    it('maintains balanced category distribution', () => {
      const layout = layoutGenerator.generateLayout()
      const categoryCounts = {
        [POICategory.SOCIAL]: 0,
        [POICategory.DUNGEON]: 0,
        [POICategory.EXPLORATION]: 0
      }
      layout.placements.forEach(placement => {
        categoryCounts[placement.category]++
      })
      Object.entries(categoryCounts).forEach(([category, count]) => {
        const rules = config.poiRules.find(r => r.category === category as POICategory)!
        expect(count).toBeGreaterThanOrEqual(rules.minGroupSize)
        expect(count).toBeLessThanOrEqual(rules.maxGroupSize)
      })
      const totalPOIs = layout.placements.length
      const expectedPerCategory = totalPOIs / Object.keys(POICategory).length
      Object.values(categoryCounts).forEach(count => {
        const deviation = Math.abs(count - expectedPerCategory)
        expect(deviation / expectedPerCategory).toBeLessThanOrEqual(0.5)
      })
    })
  })
  describe('Terrain Modification and POI Placement', () => {
    it('properly modifies terrain for social POI placement', async () => {
      const socialConfig = {
        type: POIType.SETTLEMENT,
        subtype: POISubtype.CITY,
        count: 1,
        rules: Dict[str, Any]
      }
      terrainManager.setElevationAt({ x: 50, y: 50, z: 0, level: 0 }, 10)
      terrainManager.setElevationAt({ x: 51, y: 50, z: 0, level: 0 }, 15)
      terrainManager.setElevationAt({ x: 50, y: 51, z: 0, level: 0 }, 12)
      config.categories = [socialConfig]
      await layoutGenerator.generate()
      const pois = poiManager.getPOIsByType(POIType.SETTLEMENT)
      expect(pois.length).toBe(1)
      const poi = pois[0]
      const elevation1 = terrainManager.getElevationAt(poi.position)
      const elevation2 = terrainManager.getElevationAt({
        ...poi.position,
        x: poi.position.x + 1
      })
      const elevation3 = terrainManager.getElevationAt({
        ...poi.position,
        y: poi.position.y + 1
      })
      expect(Math.abs(elevation1 - elevation2)).toBeLessThanOrEqual(1)
      expect(Math.abs(elevation1 - elevation3)).toBeLessThanOrEqual(1)
    })
    it('creates appropriate terrain modifications for dungeon POIs', async () => {
      const dungeonConfig = {
        type: POIType.DUNGEON,
        subtype: POISubtype.CAVE,
        count: 1,
        rules: Dict[str, Any]
      }
      terrainManager.addFeature({
        type: TerrainFeatureType.MOUNTAIN,
        position: Dict[str, Any],
        size: Dict[str, Any]
      })
      config.categories = [dungeonConfig]
      await layoutGenerator.generate()
      const pois = poiManager.getPOIsByType(POIType.DUNGEON)
      expect(pois.length).toBe(1)
      const poi = pois[0]
      const entranceElevation = terrainManager.getElevationAt(poi.position)
      const surroundingElevation = terrainManager.getElevationAt({
        ...poi.position,
        x: poi.position.x + 2
      })
      expect(entranceElevation).toBeLessThan(surroundingElevation)
    })
  })
  describe('Path Generation Edge Cases', () => {
    it('generates valid paths around obstacles', async () => {
      const startPOI = await poiManager.createPOI(
        POIType.SETTLEMENT,
        POISubtype.VILLAGE,
        {
          name: 'Start Village',
          coordinates: Dict[str, Any],
          thematicElements: Dict[str, Any]
        }
      )
      const endPOI = await poiManager.createPOI(
        POIType.SETTLEMENT,
        POISubtype.VILLAGE,
        {
          name: 'End Village',
          coordinates: Dict[str, Any],
          thematicElements: Dict[str, Any]
        }
      )
      terrainManager.addFeature({
        type: TerrainFeatureType.MOUNTAIN,
        position: Dict[str, Any],
        size: Dict[str, Any]
      })
      terrainManager.addFeature({
        type: TerrainFeatureType.WATER,
        position: Dict[str, Any],
        size: Dict[str, Any]
      })
      const layout = layoutGenerator.generateLayout()
      const path = layout.paths.find(p => 
        (p[0].x === startPOI.position.x && p[0].y === startPOI.position.y) ||
        (p[p.length - 1].x === startPOI.position.x && p[p.length - 1].y === startPOI.position.y)
      )
      expect(path).toBeDefined()
      expect(path!.length).toBeGreaterThan(
        Math.abs(endPOI.position.x - startPOI.position.x) +
        Math.abs(endPOI.position.y - startPOI.position.y)
      )
      for (const pos of path!) {
        const terrain = terrainManager.getTerrainAt(pos)
        expect(terrain).not.toBe(TerrainFeatureType.MOUNTAIN)
        expect(terrain).not.toBe(TerrainFeatureType.WATER)
      }
    })
  })
  describe('Category-Specific Placement Rules', () => {
    it('respects category-specific terrain preferences', async () => {
      config.categories = [
        {
          type: POIType.SETTLEMENT,
          subtype: POISubtype.CITY,
          count: 2,
          rules: Dict[str, Any]
        },
        {
          type: POIType.DUNGEON,
          subtype: POISubtype.CAVE,
          count: 2,
          rules: Dict[str, Any]
        }
      ]
      terrainManager.addFeature({
        type: TerrainFeatureType.MOUNTAIN,
        position: Dict[str, Any],
        size: Dict[str, Any]
      })
      await layoutGenerator.generate()
      const settlements = poiManager.getPOIsByType(POIType.SETTLEMENT)
      expect(settlements.length).toBe(2)
      for (const settlement of settlements) {
        const terrain = terrainManager.getTerrainAt(settlement.position)
        expect(terrain).toBe(TerrainFeatureType.PLAIN)
        const elevation = terrainManager.getElevationAt(settlement.position)
        expect(elevation).toBeLessThanOrEqual(30)
      }
      const dungeons = poiManager.getPOIsByType(POIType.DUNGEON)
      expect(dungeons.length).toBe(2)
      for (const dungeon of dungeons) {
        const terrain = terrainManager.getTerrainAt(dungeon.position)
        expect(terrain).toBe(TerrainFeatureType.MOUNTAIN)
        const elevation = terrainManager.getElevationAt(dungeon.position)
        expect(elevation).toBeGreaterThanOrEqual(20)
      }
    })
  })
  describe('Performance and Scale Testing', () => {
    it('handles maximum grid size and POI count efficiently', async () => {
      const largeDimensions: GridDimensions = { width: 500, height: 500 }
      gridManager = new GridManager(largeDimensions)
      collisionSystem = new CollisionSystem(gridManager)
      const largeTerrainData = {
        heightMap: Array(largeDimensions.height).fill(null)
          .map(() => Array(largeDimensions.width).fill(0)),
        features: [],
        buildableAreas: [{
          position: Dict[str, Any],
          size: largeDimensions,
          slope: 0,
          preferredCategories: []
        }]
      }
      terrainManager = new TerrainManager(largeTerrainData)
      config.categories = [
        {
          type: POIType.SETTLEMENT,
          subtype: POISubtype.VILLAGE,
          count: 50,
          rules: Dict[str, Any]
        }
      ]
      layoutGenerator = new SpatialLayoutGenerator(
        poiManager,
        gridManager,
        collisionSystem,
        terrainManager,
        config
      )
      const startTime = Date.now()
      await layoutGenerator.generate()
      const endTime = Date.now()
      const generationTime = endTime - startTime
      const pois = poiManager.getAllPOIs()
      expect(pois.length).toBe(50)
      expect(generationTime).toBeLessThan(5000) 
      const positions = new Set<string>()
      for (const poi of pois) {
        const posKey = `${poi.position.x},${poi.position.y}`
        expect(positions.has(posKey)).toBe(false)
        positions.add(posKey)
      }
    })
  })
})
function getCategoryPOIType(category: POICategory): POIType {
  switch (category) {
    case POICategory.SOCIAL:
      return POIType.CITY
    case POICategory.DUNGEON:
      return POIType.DUNGEON
    case POICategory.EXPLORATION:
      return POIType.LANDMARK
    default:
      return POIType.CITY
  }
} 