import { GlobalEnvironmentManager } from '../GlobalEnvironmentManager';

describe('GlobalEnvironmentManager', () => {
  it('should generate a valid environmental state for a region', () => {
    const manager = new GlobalEnvironmentManager();
    const state = manager.generate('forest', 'spring', 1200);
    expect(state.weather).toBeDefined();
    expect(Array.isArray(state.hazards)).toBe(true);
    expect(typeof state.season).toBe('string');
    expect(typeof state.time).toBe('number');
    expect(state.hazards.length).toBeGreaterThan(0);
  });
}); 