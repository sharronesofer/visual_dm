import { POIManager } from '../../poi/managers/POIManager';
import { SpatialLayoutGenerator } from '../../generators/SpatialLayoutGenerator';
import { GridManager } from '../../utils/grid';
import { CollisionSystem } from '../../utils/collision';
import { TerrainManager } from '../../utils/terrain';
import { BasePOI } from '../../poi/BasePOI';
import { 
  POICategory,
  POIPlacementRules,
  SpatialLayoutConfig,
  PlacementPattern,
  CategoryConfig
} from '../../types/spatial';
import { GridDimensions, CellType } from '../../types/grid';
import { TerrainFeatureType, TerrainFeature, TerrainData } from '../../types/terrain';
import { POIType, POISubtype, Coordinates, POISize } from '../../poi/types/POITypes';
import { IPOI } from '../../poi/interfaces/IPOI';

describe('POI Layout System - Integration Tests', () => {
  let poiManager: POIManager;
  let gridManager: GridManager;
  let collisionSystem: CollisionSystem;
  let terrainManager: TerrainManager;
  let layoutGenerator: SpatialLayoutGenerator;
  let config: SpatialLayoutConfig;

  beforeEach(() => {
    // Initialize core components
    const dimensions: GridDimensions = { width: 100, height: 100 };
    
    // Initialize grid with empty cells
    gridManager = new GridManager(dimensions);

    // Initialize collision system with grid manager
    collisionSystem = new CollisionSystem(gridManager);

    // Initialize terrain with basic data
    const terrainData: TerrainData = {
      heightMap: Array(dimensions.height).fill(null)
        .map(() => Array(dimensions.width).fill(0)),
      features: [],
      buildableAreas: [{
        position: { x: 0, y: 0, z: 0, level: 0 },
        size: dimensions,
        slope: 0,
        preferredCategories: []
      }]
    };
    terrainManager = new TerrainManager(terrainData);

    poiManager = POIManager.getInstance();

    // Configure layout generator
    config = {
      minDistance: 5,
      maxPOIs: 10,
      placementPattern: PlacementPattern.ORGANIC,
      categories: [
        {
          type: POIType.SETTLEMENT,
          subtype: POISubtype.VILLAGE,
          count: 3,
          rules: {
            minElevation: 0,
            maxElevation: 100,
            validTerrainTypes: [TerrainFeatureType.PLAIN],
            invalidTerrainTypes: [TerrainFeatureType.WATER, TerrainFeatureType.MOUNTAIN],
            minDistanceFromType: new Map([
              [POIType.SETTLEMENT, 10],
              [POIType.DUNGEON, 5]
            ])
          }
        }
      ]
    };

    layoutGenerator = new SpatialLayoutGenerator(
      poiManager,
      gridManager,
      collisionSystem,
      terrainManager,
      config
    );
  });

  afterEach(() => {
    // Clean up
    poiManager.reset();
    gridManager.reset();
    collisionSystem.reset();
    terrainManager.reset();
  });

  test('POIs are placed according to terrain constraints', async () => {
    // Add terrain features
    const mountainFeature: TerrainFeature = {
      type: TerrainFeatureType.MOUNTAIN,
      position: { x: 0, y: 0, z: 0, level: 0 },
      size: { width: 20, height: 20 }
    };
    terrainManager.addFeature(mountainFeature);

    const waterFeature: TerrainFeature = {
      type: TerrainFeatureType.WATER,
      position: { x: 30, y: 30, z: 0, level: 0 },
      size: { width: 20, height: 20 }
    };
    terrainManager.addFeature(waterFeature);

    // Generate layout
    await layoutGenerator.generate();

    // Get all POIs
    const pois = poiManager.getAllPOIs();

    // Verify POI placement
    for (const poi of pois) {
      const terrain = terrainManager.getTerrainAt(poi.position);
      expect(terrain).toBe(TerrainFeatureType.PLAIN);
    }
  });

  test('POIs maintain minimum distance requirements', async () => {
    await layoutGenerator.generate();
    const pois = poiManager.getAllPOIs();

    // Check distances between all POI pairs
    for (let i = 0; i < pois.length; i++) {
      for (let j = i + 1; j < pois.length; j++) {
        const distance = calculateDistance(pois[i].position, pois[j].position);
        expect(distance).toBeGreaterThanOrEqual(config.minDistance);
      }
    }
  });

  // Helper function to calculate distance between two points
  function calculateDistance(pos1: Coordinates, pos2: Coordinates): number {
    const dx = pos2.x - pos1.x;
    const dy = pos2.y - pos1.y;
    const dz = pos2.z - pos1.z;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }

  describe('Layout Generation and POI Integration', () => {
    it('generates layout and creates corresponding POIs', async () => {
      // Generate layout
      const layout = layoutGenerator.generateLayout();
      expect(layout.placements.length).toBeGreaterThan(0);

      // Create POIs based on layout
      const createdPOIs = await Promise.all(
        layout.placements.map(placement => {
          const poiType = getCategoryPOIType(placement.category);
          return poiManager.createPOI(
            poiType,
            POISubtype.DEFAULT,
            {
              name: `${poiType}-${placement.id}`,
              coordinates: {
                x: placement.position.x,
                y: placement.position.y,
                z: 0,
                level: 0
              },
              thematicElements: {
                themes: [],
                difficulty: 1
              }
            }
          );
        })
      );

      // Verify POIs were created correctly
      expect(createdPOIs.length).toBe(layout.placements.length);
      createdPOIs.forEach(poi => {
        expect(poi).toBeDefined();
        expect(poiManager.getPOI(poi.id)).toBeDefined();
      });

      // Verify POI positions match layout
      layout.placements.forEach((placement, index) => {
        const poi = createdPOIs[index];
        expect(poi.coordinates.x).toBe(placement.position.x);
        expect(poi.coordinates.y).toBe(placement.position.y);
      });
    });

    it('respects terrain constraints when placing POIs', async () => {
      // Add some terrain features
      terrainManager.addFeature({
        type: TerrainFeatureType.MOUNTAIN,
        position: { x: 30, y: 30 },
        size: { width: 10, height: 10 }
      });

      terrainManager.addFeature({
        type: TerrainFeatureType.WATER,
        position: { x: 70, y: 70 },
        size: { width: 15, height: 15 }
      });

      // Generate layout
      const layout = layoutGenerator.generateLayout();

      // Verify POIs are not placed on invalid terrain
      layout.placements.forEach(placement => {
        const terrain = terrainManager.getTerrainAt(placement.position);
        expect(terrain.buildable).toBe(true);
        
        const rules = config.poiRules.find(r => r.category === placement.category)!;
        expect(rules.avoidTerrainTypes).not.toContain(terrain.type);
      });
    });

    it('generates valid paths between POIs', async () => {
      // Generate layout
      const layout = layoutGenerator.generateLayout();

      // Verify path connectivity
      layout.paths.forEach(path => {
        expect(path.length).toBeGreaterThan(1);

        // Check path continuity
        for (let i = 1; i < path.length; i++) {
          const dx = Math.abs(path[i].x - path[i - 1].x);
          const dy = Math.abs(path[i].y - path[i - 1].y);
          expect(dx + dy).toBeLessThanOrEqual(1); // Ensure adjacent cells
        }

        // Check path endpoints connect to POIs
        const startPlacement = layout.placements.find(p => 
          p.position.x === path[0].x && p.position.y === path[0].y
        );
        const endPlacement = layout.placements.find(p => 
          p.position.x === path[path.length - 1].x && 
          p.position.y === path[path.length - 1].y
        );

        expect(startPlacement).toBeDefined();
        expect(endPlacement).toBeDefined();
      });
    });

    it('handles POI lifecycle with layout updates', async () => {
      // Generate initial layout
      const layout = layoutGenerator.generateLayout();
      
      // Create POIs
      const createdPOIs = await Promise.all(
        layout.placements.map(placement => {
          const poiType = getCategoryPOIType(placement.category);
          return poiManager.createPOI(
            poiType,
            POISubtype.DEFAULT,
            {
              name: `${poiType}-${placement.id}`,
              coordinates: {
                x: placement.position.x,
                y: placement.position.y,
                z: 0,
                level: 0
              },
              thematicElements: {
                themes: [],
                difficulty: 1
              }
            }
          );
        })
      );

      // Verify POIs are registered
      createdPOIs.forEach(poi => {
        expect(poiManager.getPOI(poi.id)).toBeDefined();
      });

      // Simulate region change by deregistering some POIs
      const centerX = 75;
      const centerY = 75;
      const radius = 20;

      createdPOIs.forEach(poi => {
        const distance = Math.sqrt(
          Math.pow(poi.coordinates.x - centerX, 2) +
          Math.pow(poi.coordinates.y - centerY, 2)
        );

        if (distance > radius) {
          poiManager.deregisterPOI(poi.id);
        }
      });

      // Verify POIs outside radius are deregistered
      createdPOIs.forEach(poi => {
        const distance = Math.sqrt(
          Math.pow(poi.coordinates.x - centerX, 2) +
          Math.pow(poi.coordinates.y - centerY, 2)
        );

        if (distance <= radius) {
          expect(poiManager.getPOI(poi.id)).toBeDefined();
        } else {
          expect(poiManager.getPOI(poi.id)).toBeUndefined();
        }
      });
    });
  });

  describe('Layout Patterns and Category Distribution', () => {
    it('follows pattern-specific placement rules', () => {
      const layout = layoutGenerator.generateLayout();

      // Test cluster pattern (SOCIAL)
      const socialPlacements = layout.placements.filter(p => 
        p.category === POICategory.SOCIAL
      );
      const focusPoint = config.patterns[POICategory.SOCIAL].focusPoint!;
      
      socialPlacements.forEach(placement => {
        const distance = Math.sqrt(
          Math.pow(placement.position.x - focusPoint.x, 2) +
          Math.pow(placement.position.y - focusPoint.y, 2)
        );
        expect(distance).toBeLessThanOrEqual(20); // Within cluster radius
      });

      // Test linear pattern (EXPLORATION)
      const explorationPlacements = layout.placements.filter(p => 
        p.category === POICategory.EXPLORATION
      );
      const orientation = config.patterns[POICategory.EXPLORATION].orientation!;
      
      if (explorationPlacements.length >= 2) {
        const angles = [];
        for (let i = 1; i < explorationPlacements.length; i++) {
          const dx = explorationPlacements[i].position.x - explorationPlacements[i-1].position.x;
          const dy = explorationPlacements[i].position.y - explorationPlacements[i-1].position.y;
          const angle = Math.atan2(dy, dx) * (180 / Math.PI);
          angles.push(angle);
        }

        const avgAngle = angles.reduce((a, b) => a + b) / angles.length;
        expect(Math.abs(avgAngle - orientation)).toBeLessThanOrEqual(30);
      }

      // Test scattered pattern (DUNGEON)
      const dungeonPlacements = layout.placements.filter(p => 
        p.category === POICategory.DUNGEON
      );
      
      expect(dungeonPlacements.length).toBeGreaterThanOrEqual(1);
      expect(dungeonPlacements.length).toBeLessThanOrEqual(
        Math.floor(config.gridDimensions.width * config.gridDimensions.height * 
        config.patterns[POICategory.DUNGEON].density)
      );
    });

    it('maintains balanced category distribution', () => {
      const layout = layoutGenerator.generateLayout();

      const categoryCounts = {
        [POICategory.SOCIAL]: 0,
        [POICategory.DUNGEON]: 0,
        [POICategory.EXPLORATION]: 0
      };

      layout.placements.forEach(placement => {
        categoryCounts[placement.category]++;
      });

      // Check minimum counts based on rules
      Object.entries(categoryCounts).forEach(([category, count]) => {
        const rules = config.poiRules.find(r => r.category === category as POICategory)!;
        expect(count).toBeGreaterThanOrEqual(rules.minGroupSize);
        expect(count).toBeLessThanOrEqual(rules.maxGroupSize);
      });

      // Check overall balance
      const totalPOIs = layout.placements.length;
      const expectedPerCategory = totalPOIs / Object.keys(POICategory).length;
      
      Object.values(categoryCounts).forEach(count => {
        const deviation = Math.abs(count - expectedPerCategory);
        expect(deviation / expectedPerCategory).toBeLessThanOrEqual(0.5);
      });
    });
  });

  describe('Terrain Modification and POI Placement', () => {
    it('properly modifies terrain for social POI placement', async () => {
      const socialConfig = {
        type: POIType.SETTLEMENT,
        subtype: POISubtype.CITY,
        count: 1,
        rules: {
          minElevation: 0,
          maxElevation: 50,
          validTerrainTypes: [TerrainFeatureType.PLAIN],
          invalidTerrainTypes: [TerrainFeatureType.WATER, TerrainFeatureType.MOUNTAIN],
          minDistanceFromType: new Map([
            [POIType.SETTLEMENT, 20]
          ])
        }
      };

      // Add uneven terrain
      terrainManager.setElevationAt({ x: 50, y: 50, z: 0, level: 0 }, 10);
      terrainManager.setElevationAt({ x: 51, y: 50, z: 0, level: 0 }, 15);
      terrainManager.setElevationAt({ x: 50, y: 51, z: 0, level: 0 }, 12);

      // Generate layout with social POI
      config.categories = [socialConfig];
      await layoutGenerator.generate();

      // Verify terrain has been leveled
      const pois = poiManager.getPOIsByType(POIType.SETTLEMENT);
      expect(pois.length).toBe(1);

      const poi = pois[0];
      const elevation1 = terrainManager.getElevationAt(poi.position);
      const elevation2 = terrainManager.getElevationAt({
        ...poi.position,
        x: poi.position.x + 1
      });
      const elevation3 = terrainManager.getElevationAt({
        ...poi.position,
        y: poi.position.y + 1
      });

      // Check if terrain has been leveled (elevations should be equal or very close)
      expect(Math.abs(elevation1 - elevation2)).toBeLessThanOrEqual(1);
      expect(Math.abs(elevation1 - elevation3)).toBeLessThanOrEqual(1);
    });

    it('creates appropriate terrain modifications for dungeon POIs', async () => {
      const dungeonConfig = {
        type: POIType.DUNGEON,
        subtype: POISubtype.CAVE,
        count: 1,
        rules: {
          minElevation: 10,
          maxElevation: 100,
          validTerrainTypes: [TerrainFeatureType.MOUNTAIN],
          invalidTerrainTypes: [TerrainFeatureType.WATER],
          minDistanceFromType: new Map([
            [POIType.DUNGEON, 15]
          ])
        }
      };

      // Add mountainous terrain
      terrainManager.addFeature({
        type: TerrainFeatureType.MOUNTAIN,
        position: { x: 40, y: 40, z: 0, level: 0 },
        size: { width: 20, height: 20 }
      });

      // Generate layout with dungeon POI
      config.categories = [dungeonConfig];
      await layoutGenerator.generate();

      // Verify terrain has appropriate elevation changes for dungeon entrance
      const pois = poiManager.getPOIsByType(POIType.DUNGEON);
      expect(pois.length).toBe(1);

      const poi = pois[0];
      const entranceElevation = terrainManager.getElevationAt(poi.position);
      const surroundingElevation = terrainManager.getElevationAt({
        ...poi.position,
        x: poi.position.x + 2
      });

      // Check if entrance has been properly modified (should be lower than surroundings)
      expect(entranceElevation).toBeLessThan(surroundingElevation);
    });
  });

  describe('Path Generation Edge Cases', () => {
    it('generates valid paths around obstacles', async () => {
      // Create two POIs with obstacles between them
      const startPOI = await poiManager.createPOI(
        POIType.SETTLEMENT,
        POISubtype.VILLAGE,
        {
          name: 'Start Village',
          coordinates: { x: 20, y: 20, z: 0, level: 0 },
          thematicElements: { themes: [], difficulty: 1 }
        }
      );

      const endPOI = await poiManager.createPOI(
        POIType.SETTLEMENT,
        POISubtype.VILLAGE,
        {
          name: 'End Village',
          coordinates: { x: 80, y: 80, z: 0, level: 0 },
          thematicElements: { themes: [], difficulty: 1 }
        }
      );

      // Add obstacles between POIs
      terrainManager.addFeature({
        type: TerrainFeatureType.MOUNTAIN,
        position: { x: 45, y: 45, z: 0, level: 0 },
        size: { width: 10, height: 10 }
      });

      terrainManager.addFeature({
        type: TerrainFeatureType.WATER,
        position: { x: 55, y: 55, z: 0, level: 0 },
        size: { width: 10, height: 10 }
      });

      // Generate layout
      const layout = layoutGenerator.generateLayout();

      // Find path between the two POIs
      const path = layout.paths.find(p => 
        (p[0].x === startPOI.position.x && p[0].y === startPOI.position.y) ||
        (p[p.length - 1].x === startPOI.position.x && p[p.length - 1].y === startPOI.position.y)
      );

      expect(path).toBeDefined();
      expect(path!.length).toBeGreaterThan(
        Math.abs(endPOI.position.x - startPOI.position.x) +
        Math.abs(endPOI.position.y - startPOI.position.y)
      );

      // Verify path doesn't intersect with obstacles
      for (const pos of path!) {
        const terrain = terrainManager.getTerrainAt(pos);
        expect(terrain).not.toBe(TerrainFeatureType.MOUNTAIN);
        expect(terrain).not.toBe(TerrainFeatureType.WATER);
      }
    });
  });

  describe('Category-Specific Placement Rules', () => {
    it('respects category-specific terrain preferences', async () => {
      // Configure category-specific rules
      config.categories = [
        {
          type: POIType.SETTLEMENT,
          subtype: POISubtype.CITY,
          count: 2,
          rules: {
            minElevation: 0,
            maxElevation: 30,
            validTerrainTypes: [TerrainFeatureType.PLAIN],
            invalidTerrainTypes: [TerrainFeatureType.MOUNTAIN, TerrainFeatureType.WATER],
            minDistanceFromType: new Map([[POIType.SETTLEMENT, 20]])
          }
        },
        {
          type: POIType.DUNGEON,
          subtype: POISubtype.CAVE,
          count: 2,
          rules: {
            minElevation: 20,
            maxElevation: 100,
            validTerrainTypes: [TerrainFeatureType.MOUNTAIN],
            invalidTerrainTypes: [TerrainFeatureType.WATER],
            minDistanceFromType: new Map([[POIType.DUNGEON, 15]])
          }
        }
      ];

      // Add varied terrain
      terrainManager.addFeature({
        type: TerrainFeatureType.MOUNTAIN,
        position: { x: 70, y: 70, z: 0, level: 0 },
        size: { width: 20, height: 20 }
      });

      // Generate layout
      await layoutGenerator.generate();

      // Verify settlements are on plains
      const settlements = poiManager.getPOIsByType(POIType.SETTLEMENT);
      expect(settlements.length).toBe(2);
      for (const settlement of settlements) {
        const terrain = terrainManager.getTerrainAt(settlement.position);
        expect(terrain).toBe(TerrainFeatureType.PLAIN);
        const elevation = terrainManager.getElevationAt(settlement.position);
        expect(elevation).toBeLessThanOrEqual(30);
      }

      // Verify dungeons are in mountains
      const dungeons = poiManager.getPOIsByType(POIType.DUNGEON);
      expect(dungeons.length).toBe(2);
      for (const dungeon of dungeons) {
        const terrain = terrainManager.getTerrainAt(dungeon.position);
        expect(terrain).toBe(TerrainFeatureType.MOUNTAIN);
        const elevation = terrainManager.getElevationAt(dungeon.position);
        expect(elevation).toBeGreaterThanOrEqual(20);
      }
    });
  });

  describe('Performance and Scale Testing', () => {
    it('handles maximum grid size and POI count efficiently', async () => {
      // Configure large grid and many POIs
      const largeDimensions: GridDimensions = { width: 500, height: 500 };
      gridManager = new GridManager(largeDimensions);
      collisionSystem = new CollisionSystem(gridManager);

      const largeTerrainData = {
        heightMap: Array(largeDimensions.height).fill(null)
          .map(() => Array(largeDimensions.width).fill(0)),
        features: [],
        buildableAreas: [{
          position: { x: 0, y: 0, z: 0, level: 0 },
          size: largeDimensions,
          slope: 0,
          preferredCategories: []
        }]
      };
      terrainManager = new TerrainManager(largeTerrainData);

      // Configure many POIs
      config.categories = [
        {
          type: POIType.SETTLEMENT,
          subtype: POISubtype.VILLAGE,
          count: 50,
          rules: {
            minElevation: 0,
            maxElevation: 100,
            validTerrainTypes: [TerrainFeatureType.PLAIN],
            invalidTerrainTypes: [TerrainFeatureType.WATER],
            minDistanceFromType: new Map([[POIType.SETTLEMENT, 10]])
          }
        }
      ];

      layoutGenerator = new SpatialLayoutGenerator(
        poiManager,
        gridManager,
        collisionSystem,
        terrainManager,
        config
      );

      // Measure generation time
      const startTime = Date.now();
      await layoutGenerator.generate();
      const endTime = Date.now();
      const generationTime = endTime - startTime;

      // Verify results
      const pois = poiManager.getAllPOIs();
      expect(pois.length).toBe(50);
      expect(generationTime).toBeLessThan(5000); // Should complete within 5 seconds

      // Verify POI distribution
      const positions = new Set<string>();
      for (const poi of pois) {
        const posKey = `${poi.position.x},${poi.position.y}`;
        expect(positions.has(posKey)).toBe(false);
        positions.add(posKey);
      }
    });
  });
});

// Helper function to map POI categories to types
function getCategoryPOIType(category: POICategory): POIType {
  switch (category) {
    case POICategory.SOCIAL:
      return POIType.CITY;
    case POICategory.DUNGEON:
      return POIType.DUNGEON;
    case POICategory.EXPLORATION:
      return POIType.LANDMARK;
    default:
      return POIType.CITY;
  }
} 