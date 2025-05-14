import { HexGrid } from '../HexGrid';
import { HexCell } from '../HexCell';

describe('HexGrid', () => {
  it('should create a grid and retrieve cells by coordinates', () => {
    const grid = new HexGrid(5, 5);
    const cell = grid.get(2, 3);
    expect(cell).toBeInstanceOf(HexCell);
    expect(cell?.q).toBe(2);
    expect(cell?.r).toBe(3);
  });

  it('should calculate neighbors correctly', () => {
    const grid = new HexGrid(3, 3);
    const neighbors = grid.neighbors(1, 1);
    expect(neighbors.length).toBeGreaterThan(0);
    neighbors.forEach(n => expect(n).toBeInstanceOf(HexCell));
  });

  it('should calculate distance correctly', () => {
    const grid = new HexGrid(5, 5);
    expect(grid.distance(0, 0, 2, 2)).toBe(4);
    expect(grid.distance(1, 1, 1, 1)).toBe(0);
  });

  it('should serialize and deserialize grid', () => {
    const grid = new HexGrid(2, 2);
    grid.setTerrain(0, 0, 'forest');
    const data = grid.serialize();
    const grid2 = HexGrid.deserialize(data);
    expect(grid2.get(0, 0)?.terrain).toBe('forest');
    expect(grid2.width).toBe(2);
    expect(grid2.height).toBe(2);
  });
}); 