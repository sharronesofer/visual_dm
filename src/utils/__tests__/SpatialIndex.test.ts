import { GridSpatialIndex, Region } from '../SpatialIndex';

describe('GridSpatialIndex', () => {
  let index: GridSpatialIndex;
  beforeEach(() => {
    index = new GridSpatialIndex(10); // Small cell size for testing
  });

  it('inserts and queries a single region', () => {
    const region: Region = { id: 'r1', bbox: [0, 0, 5, 5] };
    index.insert(region);
    const result = index.query({ minX: 0, minY: 0, maxX: 10, maxY: 10 });
    expect(result).toContain('r1');
  });

  it('removes a region', () => {
    const region: Region = { id: 'r2', bbox: [0, 0, 5, 5] };
    index.insert(region);
    expect(index.remove('r2')).toBe(true);
    expect(index.query({ minX: 0, minY: 0, maxX: 10, maxY: 10 })).not.toContain(
      'r2'
    );
  });

  it('updates a region', () => {
    const region: Region = { id: 'r3', bbox: [0, 0, 5, 5] };
    index.insert(region);
    const updated: Region = { id: 'r3', bbox: [20, 20, 25, 25] };
    expect(index.update(updated)).toBe(true);
    expect(index.query({ minX: 0, minY: 0, maxX: 10, maxY: 10 })).not.toContain(
      'r3'
    );
    expect(index.query({ minX: 20, minY: 20, maxX: 30, maxY: 30 })).toContain(
      'r3'
    );
  });

  it('returns only regions intersecting the viewport', () => {
    index.insert({ id: 'a', bbox: [0, 0, 5, 5] });
    index.insert({ id: 'b', bbox: [20, 20, 25, 25] });
    index.insert({ id: 'c', bbox: [5, 5, 15, 15] });
    const result = index.query({ minX: 0, minY: 0, maxX: 10, maxY: 10 });
    expect(result).toContain('a');
    expect(result).toContain('c');
    expect(result).not.toContain('b');
  });

  it('handles overlapping and touching regions', () => {
    index.insert({ id: 'd', bbox: [0, 0, 10, 10] });
    index.insert({ id: 'e', bbox: [10, 10, 20, 20] }); // Touches at corner
    index.insert({ id: 'f', bbox: [5, 5, 15, 15] }); // Overlaps
    const result = index.query({ minX: 10, minY: 10, maxX: 15, maxY: 15 });
    expect(result).toContain('e');
    expect(result).toContain('f');
    // 'd' should not be included as it only touches at the corner
    expect(result).not.toContain('d');
  });

  it('returns empty array for out-of-bounds query', () => {
    index.insert({ id: 'g', bbox: [0, 0, 5, 5] });
    const result = index.query({ minX: 100, minY: 100, maxX: 200, maxY: 200 });
    expect(result).toEqual([]);
  });

  it('removes non-existent region gracefully', () => {
    expect(index.remove('not-there')).toBe(false);
  });

  it('updates non-existent region gracefully', () => {
    expect(index.update({ id: 'not-there', bbox: [0, 0, 1, 1] })).toBe(false);
  });
});
