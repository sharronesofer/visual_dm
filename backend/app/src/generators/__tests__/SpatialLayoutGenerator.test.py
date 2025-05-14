from typing import Any, Dict


  POICategory,
  POIPlacementRules,
  PlacementPattern,
  SpatialLayoutConfig
} from '../../types/spatial'
describe('SpatialLayoutGenerator', () => {
  let gridManager: GridManager
  let generator: SpatialLayoutGenerator
  let config: SpatialLayoutConfig
  beforeEach(() => {
    const dimensions: GridDimensions = { width: 20, height: 20 }
    gridManager = new GridManager(dimensions)
    const socialRules: POIPlacementRules = {
      category: POICategory.SOCIAL,
      minSpacing: 2,
      maxSpacing: 8,
      preferredTerrainTypes: [CellType.EMPTY],
      avoidTerrainTypes: [CellType.WALL, CellType.BLOCKED],
      minGroupSize: 3,
      maxGroupSize: 6
    }
    const dungeonRules: POIPlacementRules = {
      category: POICategory.DUNGEON,
      minSpacing: 4,
      maxSpacing: 12,
      preferredTerrainTypes: [CellType.EMPTY],
      avoidTerrainTypes: [CellType.WALL, CellType.BLOCKED],
      minGroupSize: 1,
      maxGroupSize: 3
    }
    const explorationRules: POIPlacementRules = {
      category: POICategory.EXPLORATION,
      minSpacing: 3,
      maxSpacing: 10,
      preferredTerrainTypes: [CellType.EMPTY],
      avoidTerrainTypes: [CellType.WALL, CellType.BLOCKED],
      minGroupSize: 2,
      maxGroupSize: 4
    }
    config = {
      gridDimensions: dimensions,
      poiRules: [socialRules, dungeonRules, explorationRules],
      patterns: Dict[str, Any]
        },
        [POICategory.DUNGEON]: {
          type: 'SCATTERED',
          density: 0.4
        },
        [POICategory.EXPLORATION]: {
          type: 'LINEAR',
          density: 0.5,
          orientation: 45
        }
      },
      pathfindingWeight: 0.6,
      aestheticWeight: 0.4
    }
    generator = new SpatialLayoutGenerator(gridManager, config)
  })
  describe('generateLayout', () => {
    test('generates valid layout with correct structure', () => {
      const result = generator.generateLayout()
      expect(result).toHaveProperty('placements')
      expect(result).toHaveProperty('paths')
      expect(result).toHaveProperty('patterns')
      expect(result).toHaveProperty('stats')
      expect(Array.isArray(result.placements)).toBe(true)
      expect(Array.isArray(result.paths)).toBe(true)
      expect(result.patterns).toEqual(config.patterns)
    })
    test('respects minimum spacing between POIs', () => {
      const result = generator.generateLayout()
      for (let i = 0; i < result.placements.length; i++) {
        const placement = result.placements[i]
        const rules = config.poiRules.find(r => r.category === placement.category)!
        for (let j = i + 1; j < result.placements.length; j++) {
          const other = result.placements[j]
          const distance = Math.sqrt(
            Math.pow(placement.position.x - other.position.x, 2) +
            Math.pow(placement.position.y - other.position.y, 2)
          )
          expect(distance).toBeGreaterThanOrEqual(rules.minSpacing)
        }
      }
    })
    test('generates connected paths between POIs', () => {
      const result = generator.generateLayout()
      for (const placement of result.placements) {
        expect(placement.connections.length).toBeGreaterThan(0)
      }
      for (const path of result.paths) {
        expect(path.length).toBeGreaterThan(0)
        for (let i = 1; i < path.length; i++) {
          const dx = Math.abs(path[i].x - path[i-1].x)
          const dy = Math.abs(path[i].y - path[i-1].y)
          expect(dx + dy).toBeLessThanOrEqual(1) 
        }
      }
    })
    test('generates layouts with balanced category distribution', () => {
      const result = generator.generateLayout()
      const categoryCounts = {
        [POICategory.SOCIAL]: 0,
        [POICategory.DUNGEON]: 0,
        [POICategory.EXPLORATION]: 0
      }
      for (const placement of result.placements) {
        categoryCounts[placement.category]++
      }
      for (const count of Object.values(categoryCounts)) {
        expect(count).toBeGreaterThan(0)
      }
      expect(result.stats.balance).toBeGreaterThan(0.5)
    })
    test('respects pattern-specific placement rules', () => {
      const result = generator.generateLayout()
      const socialPlacements = result.placements.filter(p => p.category === POICategory.SOCIAL)
      const focusPoint = config.patterns[POICategory.SOCIAL].focusPoint!
      for (const placement of socialPlacements) {
        const distance = Math.sqrt(
          Math.pow(placement.position.x - focusPoint.x, 2) +
          Math.pow(placement.position.y - focusPoint.y, 2)
        )
        expect(distance).toBeLessThanOrEqual(10) 
      }
      const explorationPlacements = result.placements.filter(p => p.category === POICategory.EXPLORATION)
      if (explorationPlacements.length >= 2) {
        const angle = config.patterns[POICategory.EXPLORATION].orientation!
        const rad = (angle * Math.PI) / 180
        const cos = Math.cos(rad)
        const sin = Math.sin(rad)
        const projections = explorationPlacements.map(p => ({
          placement: p,
          proj: p.position.x * cos + p.position.y * sin
        }))
        projections.sort((a, b) => a.proj - b.proj)
        for (let i = 1; i < projections.length; i++) {
          const dx = projections[i].placement.position.x - projections[i-1].placement.position.x
          const dy = projections[i].placement.position.y - projections[i-1].placement.position.y
          const actualAngle = (Math.atan2(dy, dx) * 180) / Math.PI
          const angleDiff = Math.abs(actualAngle - angle)
          expect(angleDiff).toBeLessThan(30) 
        }
      }
    })
  })
}) 