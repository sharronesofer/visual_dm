import POIGenerationService from '../POIGenerationService';
import { POIGenerationParams } from '../../types/poi';
import seedrandom from 'seedrandom';

describe('POIGenerationService - Core Unit Tests', () => {
  const service = POIGenerationService.getInstance();

  const baseParams: POIGenerationParams = {
    type: 'dungeon',
    size: 'medium',
    theme: 'medieval',
    complexity: 0.5,
    seed: 'test-seed-123',
  };

  it('should generate identical POIs for the same seed (deterministic)', async () => {
    const seed = 'repeatable-seed';
    const rng = seedrandom(seed);
    let idCounter = 0;
    const deterministicIdGen = () => `id-${idCounter++}`;
    const fixedNow = () => '2020-01-01T00:00:00.000Z';
    // Bypass singleton for test: direct instantiation
    const DeterministicPOIGenerationService = POIGenerationService as any;
    const deterministicService = new DeterministicPOIGenerationService(
      () => rng(),
      deterministicIdGen,
      fixedNow
    );
    const poi1 = await deterministicService.generatePOI({
      ...baseParams,
      seed,
    });
    idCounter = 0; // Reset for second run
    const rng2 = seedrandom(seed);
    const deterministicService2 = new DeterministicPOIGenerationService(
      () => rng2(),
      deterministicIdGen,
      fixedNow
    );
    const poi2 = await deterministicService2.generatePOI({
      ...baseParams,
      seed,
    });
    expect(poi1).toEqual(poi2);
  });

  it('should generate different POIs for different seeds', async () => {
    const poi1 = await service.generatePOI({ ...baseParams, seed: 'seed-one' });
    const poi2 = await service.generatePOI({ ...baseParams, seed: 'seed-two' });
    expect(poi1).not.toEqual(poi2);
  });

  it('should handle boundary condition: empty world (size = "tiny")', async () => {
    const params: POIGenerationParams = { ...baseParams, size: 'tiny' };
    const poi = await service.generatePOI(params);
    expect(poi.layout.rooms.length).toBeGreaterThanOrEqual(1); // Should still create at least entrance
  });

  it('should handle boundary condition: maximum density', async () => {
    const params: POIGenerationParams = {
      ...baseParams,
      complexity: 1.0,
      size: 'huge',
    };
    const poi = await service.generatePOI(params);
    expect(poi.layout.rooms.length).toBeGreaterThan(1);
  });

  it('should produce room sizes within expected mathematical distribution', async () => {
    const params: POIGenerationParams = {
      ...baseParams,
      size: 'huge',
      complexity: 0.8,
    };
    const poi = await service.generatePOI(params);
    const roomSizes = poi.layout.rooms.map(r => r.width * r.height);
    // Check that all room sizes are within expected range (3x3 to 7x7)
    roomSizes.forEach(size => {
      expect(size).toBeGreaterThanOrEqual(9);
      expect(size).toBeLessThanOrEqual(49);
    });
  });

  // Helper: Compare generated outputs
  function comparePOIs(poiA: any, poiB: any) {
    expect(poiA).toEqual(poiB);
  }
});
