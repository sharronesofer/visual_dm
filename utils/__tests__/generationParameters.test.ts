import { GenerationParametersCalculator } from '../generationParameters';
import { POICategory } from '../../types/buildings/base';
import { GridDimensions } from '../../types/grid';

describe('GenerationParametersCalculator', () => {
  let calculator: GenerationParametersCalculator;

  beforeEach(() => {
    calculator = new GenerationParametersCalculator();
  });

  describe('calculateBuildingDistribution', () => {
    const baseParams = {
      poiDangerLevel: 5,
      poiCategory: POICategory.SOCIAL,
      narrativeContext: [],
      areaSizeConstraints: { width: 20, height: 20 } as GridDimensions
    };

    test('returns valid distribution for social area', () => {
      const distribution = calculator.calculateBuildingDistribution(baseParams);

      expect(distribution.density).toBeGreaterThan(0);
      expect(distribution.density).toBeLessThanOrEqual(1);
      expect(distribution.organizationFactor).toBeGreaterThan(0);
      expect(distribution.organizationFactor).toBeLessThanOrEqual(1);
      expect(distribution.minSpacing).toBeGreaterThanOrEqual(1);
      expect(distribution.roadDensity).toBeGreaterThan(0);
      expect(distribution.roadDensity).toBeLessThanOrEqual(1);
      expect(distribution.buildingCounts.size).toBeGreaterThan(0);
    });

    test('adjusts for danger level', () => {
      const lowDanger = calculator.calculateBuildingDistribution({
        ...baseParams,
        poiDangerLevel: 1
      });

      const highDanger = calculator.calculateBuildingDistribution({
        ...baseParams,
        poiDangerLevel: 15
      });

      expect(highDanger.density).toBeGreaterThan(lowDanger.density);
    });

    test('respects area size constraints', () => {
      const smallArea = calculator.calculateBuildingDistribution({
        ...baseParams,
        areaSizeConstraints: { width: 10, height: 10 }
      });

      const largeArea = calculator.calculateBuildingDistribution({
        ...baseParams,
        areaSizeConstraints: { width: 40, height: 40 }
      });

      expect(largeArea.buildingCounts).not.toEqual(smallArea.buildingCounts);
    });

    test('applies narrative context modifiers', () => {
      const baseDistribution = calculator.calculateBuildingDistribution(baseParams);

      const modifiedDistribution = calculator.calculateBuildingDistribution({
        ...baseParams,
        narrativeContext: ['crowded', 'commercial', 'planned']
      });

      expect(modifiedDistribution.density).toBeGreaterThan(baseDistribution.density);
      expect(modifiedDistribution.organizationFactor).toBeGreaterThan(baseDistribution.organizationFactor);
    });

    test('handles different POI categories', () => {
      const social = calculator.calculateBuildingDistribution(baseParams);
      
      const dungeon = calculator.calculateBuildingDistribution({
        ...baseParams,
        poiCategory: POICategory.DUNGEON
      });

      const exploration = calculator.calculateBuildingDistribution({
        ...baseParams,
        poiCategory: POICategory.EXPLORATION
      });

      // Social areas should be more organized and dense
      expect(social.organizationFactor).toBeGreaterThan(dungeon.organizationFactor);
      expect(social.organizationFactor).toBeGreaterThan(exploration.organizationFactor);
      expect(social.density).toBeGreaterThan(exploration.density);

      // Building types should be different
      expect(social.buildingCounts.has('Shop')).toBeTruthy();
      expect(dungeon.buildingCounts.has('EnemyLair')).toBeTruthy();
      expect(exploration.buildingCounts.has('Ruins')).toBeTruthy();
    });

    test('validates and adjusts distribution', () => {
      const distribution = calculator.calculateBuildingDistribution({
        ...baseParams,
        narrativeContext: ['extremely crowded', 'densely packed', 'overcrowded']
      });

      // Even with extreme modifiers, values should stay within bounds
      expect(distribution.density).toBeLessThanOrEqual(1);
      expect(distribution.organizationFactor).toBeLessThanOrEqual(1);
      expect(distribution.roadDensity).toBeLessThanOrEqual(1);

      // Total buildings should not exceed maximum
      let totalBuildings = 0;
      for (const count of distribution.buildingCounts.values()) {
        totalBuildings += count;
      }
      expect(totalBuildings).toBeLessThanOrEqual(15); // MAX_BUILDING_COUNT
    });

    test('handles empty narrative context', () => {
      const distribution = calculator.calculateBuildingDistribution({
        ...baseParams,
        narrativeContext: []
      });

      expect(distribution).toBeDefined();
      expect(distribution.buildingCounts.size).toBeGreaterThan(0);
    });

    test('maintains minimum building counts', () => {
      const distribution = calculator.calculateBuildingDistribution({
        ...baseParams,
        areaSizeConstraints: { width: 5, height: 5 } // Very small area
      });

      let totalBuildings = 0;
      for (const count of distribution.buildingCounts.values()) {
        totalBuildings += count;
      }
      expect(totalBuildings).toBeGreaterThanOrEqual(3); // MIN_BUILDING_COUNT
    });
  });
}); 