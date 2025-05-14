import { isRegion, sampleRegion, Region } from '../regionMap';

describe('Region type validation', () => {
  it('should validate a correct region object', () => {
    expect(isRegion(sampleRegion)).toBe(true);
  });

  it('should reject an invalid region object', () => {
    const invalidRegion = {
      id: 123, // Should be string
      name: 'Test Region',
      boundaries: 'not-an-array', // Should be array
      properties: { population: 1000 },
    };
    expect(isRegion(invalidRegion)).toBe(false);
  });
});
