import { POIManager } from '../../../poi/managers/POIManager';
import { SpatialLayoutGenerator } from '../../../generators/SpatialLayoutGenerator';
import { GridManager } from '../../../utils/grid';
import { CollisionSystem } from '../../../utils/collision';
import { TerrainManager } from '../../../utils/terrain';
import { 
  POICategory,
  POIPlacementRules,
  PlacementPattern,
  SpatialLayoutConfig
} from '../../../types/spatial';
import { GridDimensions, CellType } from '../../../types/grid';
import { TerrainFeatureType, TerrainData } from '../../../types/terrain';
import { POIType, POISubtype, Coordinates } from '../../../poi/types/POITypes';

describe('POI Layout System - Integration Tests', () => {
  let poiManager: POIManager;
  let gridManager: GridManager;
  let collisionSystem: CollisionSystem;
  let terrainManager: TerrainManager;
  let layoutGenerator: SpatialLayoutGenerator;
  let config: SpatialLayoutConfig;

  beforeEach(() => {
    // Initialize grid
    const dimensions: GridDimensions = { width: 20, height: 20 };
    gridManager = new GridManager(dimensions);

    // Initialize terrain
    const terrainData: TerrainData = {
      heightMap: Array(dimensions.height).fill(null).map(() => Array(dimensions.width).fill(0)),
      features: [
        {
          type: TerrainFeatureType.WATER,
          position: { x: 5, y: 5 },
          size: { width: 2, height: 2 },
          elevation: -1
        },
        {
          type: TerrainFeatureType.MOUNTAIN,
          position: { x: 15, y: 15 },
          size: { width: 3, height: 3 },
          elevation: 5
        }
      ],
      buildableAreas: [
        {
          position: { x: 2, y: 2 },
          size: { width: 3, height: 3 },
          slope: 0,
          preferredCategories: ['SOCIAL']
        }
      ]
    };
    terrainManager = new TerrainManager(terrainData);

    // Initialize other components
    collisionSystem = new CollisionSystem(gridManager);
    poiManager = POIManager.getInstance();
    
    // Configure layout generator
    config = {
      minDistance: 2,
      maxDistance: 5,
      placementRules: new Map<POICategory, POIPlacementRules>([
        ['SOCIAL', {
          pattern: PlacementPattern.CLUSTER,
          minElevation: -1,
          maxElevation: 3,
          terrainPreferences: [TerrainFeatureType.WATER],
          avoidFeatures: [TerrainFeatureType.MOUNTAIN]
        }]
      ])
    };

    layoutGenerator = new SpatialLayoutGenerator(
      gridManager,
      collisionSystem,
      terrainManager,
      config
    );
  });

  afterEach(() => {
    // Clean up POIs
    for (const poi of poiManager.getAllPOIs()) {
      poiManager.deregisterPOI(poi.id);
    }
  });

  describe('POI Placement', () => {
    test('places POIs according to terrain constraints', async () => {
      // Create a social POI
      const poi = poiManager.createPOI(
        POIType.TAVERN,
        POISubtype.COMMON,
        { name: 'Test Tavern' }
      );

      // Try to place it
      const placement = await layoutGenerator.placePOI(poi, 'SOCIAL');
      expect(placement).toBeDefined();
      expect(placement?.success).toBe(true);

      if (placement?.success) {
        const coords = placement.coordinates;
        
        // Verify terrain constraints
        const terrain = terrainManager.analyzeTerrain(coords);
        expect(terrain.elevation).toBeGreaterThanOrEqual(config.placementRules.get('SOCIAL')!.minElevation);
        expect(terrain.elevation).toBeLessThanOrEqual(config.placementRules.get('SOCIAL')!.maxElevation);
        
        // Verify grid cell is now occupied
        const cell = gridManager.getCellAt(coords);
        expect(cell?.isOccupied).toBe(true);
        expect(cell?.cellType).toBe(CellType.BUILDING);
      }
    });

    test('respects minimum distance between POIs', async () => {
      // Create two POIs
      const poi1 = poiManager.createPOI(
        POIType.TAVERN,
        POISubtype.COMMON,
        { name: 'Tavern 1' }
      );

      const poi2 = poiManager.createPOI(
        POIType.TAVERN,
        POISubtype.COMMON,
        { name: 'Tavern 2' }
      );

      // Place first POI
      const placement1 = await layoutGenerator.placePOI(poi1, 'SOCIAL');
      expect(placement1?.success).toBe(true);

      // Place second POI
      const placement2 = await layoutGenerator.placePOI(poi2, 'SOCIAL');
      expect(placement2?.success).toBe(true);

      if (placement1?.success && placement2?.success) {
        // Calculate distance between POIs
        const distance = Math.sqrt(
          Math.pow(placement2.coordinates.x - placement1.coordinates.x, 2) +
          Math.pow(placement2.coordinates.y - placement1.coordinates.y, 2)
        );

        expect(distance).toBeGreaterThanOrEqual(config.minDistance);
      }
    });

    test('avoids placing POIs in invalid terrain', async () => {
      // Create a POI
      const poi = poiManager.createPOI(
        POIType.TAVERN,
        POISubtype.COMMON,
        { name: 'Mountain Tavern' }
      );

      // Try to place it near mountain (should avoid)
      const placement = await layoutGenerator.placePOI(poi, 'SOCIAL', {
        preferredPosition: { x: 15, y: 15 } // Mountain location
      });

      // Should still succeed but place it elsewhere
      expect(placement?.success).toBe(true);
      if (placement?.success) {
        const terrain = terrainManager.analyzeTerrain(placement.coordinates);
        expect(terrain.nearbyFeatures).not.toContain(TerrainFeatureType.MOUNTAIN);
      }
    });
  });

  describe('Path Generation', () => {
    test('generates valid paths between POIs', async () => {
      // Create and place two POIs
      const poi1 = poiManager.createPOI(
        POIType.TAVERN,
        POISubtype.COMMON,
        { name: 'Start Tavern' }
      );

      const poi2 = poiManager.createPOI(
        POIType.TAVERN,
        POISubtype.COMMON,
        { name: 'End Tavern' }
      );

      const placement1 = await layoutGenerator.placePOI(poi1, 'SOCIAL');
      const placement2 = await layoutGenerator.placePOI(poi2, 'SOCIAL');

      expect(placement1?.success).toBe(true);
      expect(placement2?.success).toBe(true);

      if (placement1?.success && placement2?.success) {
        // Generate path
        const path = await layoutGenerator.generatePath(
          placement1.coordinates,
          placement2.coordinates
        );

        expect(path).toBeDefined();
        expect(path.length).toBeGreaterThan(0);

        // Verify path properties
        for (let i = 0; i < path.length - 1; i++) {
          // Check each segment is adjacent
          const dx = Math.abs(path[i + 1].x - path[i].x);
          const dy = Math.abs(path[i + 1].y - path[i].y);
          expect(dx + dy).toBeLessThanOrEqual(2); // Allow diagonal movement

          // Check terrain is walkable
          const cell = gridManager.getCellAt(path[i]);
          expect(cell?.walkable).toBe(true);
        }
      }
    });

    test('paths avoid obstacles and terrain features', async () => {
      // Create and place two POIs on opposite sides of water feature
      const poi1 = poiManager.createPOI(
        POIType.TAVERN,
        POISubtype.COMMON,
        { name: 'West Tavern' }
      );

      const poi2 = poiManager.createPOI(
        POIType.TAVERN,
        POISubtype.COMMON,
        { name: 'East Tavern' }
      );

      const placement1 = await layoutGenerator.placePOI(poi1, 'SOCIAL', {
        preferredPosition: { x: 3, y: 5 } // West of water
      });

      const placement2 = await layoutGenerator.placePOI(poi2, 'SOCIAL', {
        preferredPosition: { x: 8, y: 5 } // East of water
      });

      expect(placement1?.success).toBe(true);
      expect(placement2?.success).toBe(true);

      if (placement1?.success && placement2?.success) {
        // Generate path
        const path = await layoutGenerator.generatePath(
          placement1.coordinates,
          placement2.coordinates
        );

        expect(path).toBeDefined();
        expect(path.length).toBeGreaterThan(0);

        // Verify path avoids water
        for (const point of path) {
          const terrain = terrainManager.analyzeTerrain(point);
          expect(terrain.nearbyFeatures).not.toContain(TerrainFeatureType.WATER);
        }
      }
    });
  });
});