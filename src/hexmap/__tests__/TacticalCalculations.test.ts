import { TacticalHexGrid } from '../TacticalHexGrid';
import { lineOfSight, range, tacticalPathfind, terrainCombatBonus, areaOfEffect } from '../TacticalCalculations';

describe('TacticalCalculations', () => {
  it('calculates line of sight with and without obstacles', () => {
    const grid = new TacticalHexGrid(5, 1);
    // No obstacles
    expect(lineOfSight(grid, 0, 0, 4, 0)).toBe(true);
    // Add impassable in the middle
    grid.setCombatProps(2, 0, { terrainEffect: 'impassable' });
    expect(lineOfSight(grid, 0, 0, 4, 0)).toBe(false);
    // Add high cover
    grid.setCombatProps(2, 0, { terrainEffect: '', cover: 0.9 });
    expect(lineOfSight(grid, 0, 0, 4, 0)).toBe(false);
  });

  it('calculates hex range correctly', () => {
    const grid = new TacticalHexGrid(5, 5);
    expect(range(grid, 0, 0, 3, 0)).toBe(3);
    expect(range(grid, 0, 0, 0, 0)).toBe(0);
    expect(range(grid, 1, 1, 3, 3)).toBe(4);
  });

  it('finds tactical path with movement cost and impassable', () => {
    const grid = new TacticalHexGrid(3, 1);
    grid.setCombatProps(1, 0, { terrainEffect: 'impassable' });
    const result = tacticalPathfind(grid, 0, 0, 2, 0, 10);
    expect(result).toBeNull();
    grid.setCombatProps(1, 0, { terrainEffect: '', movementCost: 2 });
    const result2 = tacticalPathfind(grid, 0, 0, 2, 0, 10);
    expect(result2).not.toBeNull();
    expect(result2!.cost).toBe(3);
    expect(result2!.path[0]).toEqual([0, 0]);
    expect(result2!.path[result2!.path.length - 1]).toEqual([2, 0]);
  });

  it('calculates terrain combat bonus', () => {
    const grid = new TacticalHexGrid(1, 1);
    grid.setCombatProps(0, 0, { terrainEffect: 'highground' });
    expect(terrainCombatBonus(grid.get(0, 0)!)).toBe(0.3);
    grid.setCombatProps(0, 0, { terrainEffect: 'exposure' });
    expect(terrainCombatBonus(grid.get(0, 0)!)).toBe(-0.2);
    grid.setCombatProps(0, 0, { terrainEffect: '' });
    expect(terrainCombatBonus(grid.get(0, 0)!)).toBe(0);
  });

  it('returns correct area of effect', () => {
    const grid = new TacticalHexGrid(5, 5);
    const aoe = areaOfEffect(grid, 2, 2, 1);
    expect(aoe).toContainEqual([2, 2]);
    expect(aoe.length).toBeGreaterThan(1);
    // All affected cells should exist
    for (const [q, r] of aoe) {
      expect(grid.get(q, r)).toBeDefined();
    }
  });
}); 