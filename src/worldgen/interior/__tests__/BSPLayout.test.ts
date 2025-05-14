import { BSPLayout } from '../BSPLayout';
import { InteriorParams } from '../types';

describe('BSPLayout', () => {
  it('should return an array of rooms for valid parameters', () => {
    const params: InteriorParams = {
      buildingType: 'residential',
      width: 10,
      length: 10,
      height: 3,
      entryPoints: [{ x: 0, y: 0 }]
    };
    const bsp = new BSPLayout(params);
    const rooms = bsp.generateRooms();
    expect(Array.isArray(rooms)).toBe(true);
  });

  it('should generate multiple rooms for a large space', () => {
    const params: InteriorParams = {
      buildingType: 'commercial',
      width: 20,
      length: 20,
      height: 4,
      entryPoints: [{ x: 0, y: 0 }]
    };
    const bsp = new BSPLayout(params);
    const rooms = bsp.generateRooms();
    expect(rooms.length).toBeGreaterThan(1);
    // Check unique IDs
    const ids = new Set(rooms.map(r => r.id));
    expect(ids.size).toBe(rooms.length);
    // Check valid dimensions
    rooms.forEach(room => {
      expect(room.width).toBeGreaterThan(0);
      expect(room.length).toBeGreaterThan(0);
    });
  });
}); 