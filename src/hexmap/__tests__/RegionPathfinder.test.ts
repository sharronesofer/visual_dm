import { HexGrid } from '../HexGrid';
import { regionAStarPathfind } from '../RegionPathfinder';

describe('regionAStarPathfind', () => {
  it('finds a straight path on plains', () => {
    const grid = new HexGrid(5, 5);
    for (let r = 0; r < 5; r++) for (let q = 0; q < 5; q++) grid.get(q, r)!.terrain = 'plains';
    const result = regionAStarPathfind(grid, 0, 0, 4, 0);
    expect(result).not.toBeNull();
    expect(result!.path[0]).toEqual([0, 0]);
    expect(result!.path[result!.path.length - 1]).toEqual([4, 0]);
    expect(result!.cost).toBe(4);
  });

  it('returns null if blocked by water', () => {
    const grid = new HexGrid(3, 3);
    for (let r = 0; r < 3; r++) for (let q = 0; q < 3; q++) grid.get(q, r)!.terrain = 'plains';
    grid.get(1, 0)!.terrain = 'water';
    grid.get(1, 1)!.terrain = 'water';
    grid.get(1, 2)!.terrain = 'water';
    const result = regionAStarPathfind(grid, 0, 1, 2, 1);
    expect(result).toBeNull();
  });

  it('accounts for mixed terrain costs', () => {
    const grid = new HexGrid(3, 1);
    grid.get(0, 0)!.terrain = 'plains';
    grid.get(1, 0)!.terrain = 'forest';
    grid.get(2, 0)!.terrain = 'plains';
    const result = regionAStarPathfind(grid, 0, 0, 2, 0);
    expect(result).not.toBeNull();
    expect(result!.cost).toBe(1 + 2); // plains->forest->plains
  });

  it('returns null if target is unreachable', () => {
    const grid = new HexGrid(2, 2);
    for (let r = 0; r < 2; r++) for (let q = 0; q < 2; q++) grid.get(q, r)!.terrain = 'water';
    grid.get(0, 0)!.terrain = 'plains';
    grid.get(1, 1)!.terrain = 'plains';
    const result = regionAStarPathfind(grid, 0, 0, 1, 1);
    expect(result).toBeNull();
  });
}); 