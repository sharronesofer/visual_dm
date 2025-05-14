import { HexGrid } from '../HexGrid';
import { TacticalHexGrid, TacticalHexCell } from '../TacticalHexGrid';

describe('TacticalHexGrid', () => {
  it('assigns combat properties based on terrain', () => {
    const region = new HexGrid(3, 3);
    region.get(0, 0)!.terrain = 'forest';
    region.get(1, 0)!.terrain = 'mountain';
    region.get(2, 0)!.terrain = 'urban';
    region.get(0, 1)!.terrain = 'water';
    region.get(1, 1)!.terrain = 'desert';
    region.get(2, 1)!.terrain = 'plains';
    const tactical = TacticalHexGrid.fromRegionGrid(region);
    expect(tactical.get(0, 0)!.cover).toBe(0.7);
    expect(tactical.get(1, 0)!.terrainEffect).toBe('highground');
    expect(tactical.get(2, 0)!.movementCost).toBe(1);
    expect(tactical.get(0, 1)!.terrainEffect).toBe('impassable');
    expect(tactical.get(1, 1)!.cover).toBe(0.1);
    expect(tactical.get(2, 1)!.cover).toBe(0.2);
  });

  it('can add and remove units, enforcing stacking', () => {
    const grid = new TacticalHexGrid(2, 2);
    grid.addUnit(0, 0, 'unitA');
    grid.addUnit(0, 0, 'unitB');
    expect(grid.get(0, 0)!.unitOccupants).toContain('unitA');
    expect(grid.get(0, 0)!.unitOccupants).toContain('unitB');
    grid.removeUnit(0, 0, 'unitA');
    expect(grid.get(0, 0)!.unitOccupants).not.toContain('unitA');
    expect(grid.get(0, 0)!.unitOccupants).toContain('unitB');
  });

  it('setCombatProps updates combat properties', () => {
    const grid = new TacticalHexGrid(1, 1);
    grid.setCombatProps(0, 0, { cover: 0.5, movementCost: 2, terrainEffect: 'mud', unitOccupants: ['u1'] });
    const cell = grid.get(0, 0)!;
    expect(cell.cover).toBe(0.5);
    expect(cell.movementCost).toBe(2);
    expect(cell.terrainEffect).toBe('mud');
    expect(cell.unitOccupants).toEqual(['u1']);
  });
}); 