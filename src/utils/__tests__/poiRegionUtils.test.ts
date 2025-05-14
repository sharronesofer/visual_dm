import { describe, it, expect } from 'vitest';
import { determineContainingRegion } from '../poiRegionUtils';
import type { POI, Region, TerrainType } from '@/types/map';

describe('poiRegionUtils', () => {
  const testRegion: Region = {
    id: 'region1',
    name: 'Test Region',
    type: 'city',
    position: { x: 0, y: 0 },
    width: 100,
    height: 100,
    terrain: 'plains',
    borders: [],
    boundaries: [
      [0, 0],
      [100, 0],
      [100, 100],
      [0, 100],
    ],
  };

  const insidePOI: POI = {
    id: 'poi1',
    name: 'Inside POI',
    type: 'landmark',
    position: { x: 50, y: 50 },
  };

  const outsidePOI: POI = {
    id: 'poi2',
    name: 'Outside POI',
    type: 'landmark',
    position: { x: 150, y: 150 },
  };

  const edgePOI: POI = {
    id: 'poi3',
    name: 'Edge POI',
    type: 'landmark',
    position: { x: 100, y: 100 },
  };

  it('should detect POI inside region', () => {
    const result = determineContainingRegion(insidePOI, [testRegion]);
    expect(result).toBe(testRegion);
  });

  it('should return null for POI outside region', () => {
    const result = determineContainingRegion(outsidePOI, [testRegion]);
    expect(result).toBeNull();
  });

  it('should handle POI on region boundary', () => {
    const result = determineContainingRegion(edgePOI, [testRegion]);
    expect(result).toBe(testRegion);
  });

  it('should handle multiple regions', () => {
    const region2: Region = {
      id: 'region2',
      name: 'Test Region 2',
      type: 'dungeon',
      position: { x: 200, y: 200 },
      width: 100,
      height: 100,
      terrain: 'mountain',
      borders: [],
      boundaries: [
        [200, 200],
        [300, 200],
        [300, 300],
        [200, 300],
      ],
    };

    const poi: POI = {
      id: 'poi4',
      name: 'POI in Region 2',
      type: 'landmark',
      position: { x: 250, y: 250 },
    };

    const result = determineContainingRegion(poi, [testRegion, region2]);
    expect(result).toBe(region2);
  });

  it('should handle overlapping regions', () => {
    const overlappingRegion: Region = {
      id: 'region3',
      name: 'Overlapping Region',
      type: 'city',
      position: { x: 50, y: 50 },
      width: 100,
      height: 100,
      terrain: 'plains',
      borders: [],
      boundaries: [
        [50, 50],
        [150, 50],
        [150, 150],
        [50, 150],
      ],
    };

    const poi: POI = {
      id: 'poi5',
      name: 'POI in Overlap',
      type: 'landmark',
      position: { x: 75, y: 75 },
    };

    const result = determineContainingRegion(poi, [testRegion, overlappingRegion]);
    expect(result).toBe(testRegion); // Should return first matching region
  });

  it('should handle empty regions array', () => {
    const result = determineContainingRegion(insidePOI, []);
    expect(result).toBeNull();
  });

  it('should handle invalid region boundaries', () => {
    const invalidRegion: Region = {
      id: 'invalid',
      name: 'Invalid Region',
      type: 'city',
      position: { x: 0, y: 0 },
      width: 100,
      height: 100,
      terrain: 'plains',
      borders: [],
      boundaries: [], // Empty boundaries
    };

    const result = determineContainingRegion(insidePOI, [invalidRegion]);
    expect(result).toBeNull();
  });
});
