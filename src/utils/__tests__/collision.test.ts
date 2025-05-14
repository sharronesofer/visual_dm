import { GridManager } from '../grid';
import { CollisionSystem } from '../collision';
import { GridDimensions, CellType } from '../../types/grid';

describe('CollisionSystem', () => {
  let gridManager: GridManager;
  let collisionSystem: CollisionSystem;
  const dimensions: GridDimensions = { width: 20, height: 20 };

  beforeEach(() => {
    gridManager = new GridManager(dimensions);
    collisionSystem = new CollisionSystem(gridManager);
  });

  describe('Object Management', () => {
    test('inserts and removes objects correctly', () => {
      const objectId = 'test-object';
      const position = { x: 5, y: 5 };
      const dimensions = { width: 2, height: 2 };

      // Insert object
      collisionSystem.insert(objectId, position, dimensions);
      expect(collisionSystem.findCollisions(position, dimensions)).toContain(objectId);

      // Remove object
      collisionSystem.remove(objectId, position, dimensions);
      expect(collisionSystem.findCollisions(position, dimensions)).not.toContain(objectId);
    });

    test('updates object position correctly', () => {
      const objectId = 'test-object';
      const oldPos = { x: 5, y: 5 };
      const newPos = { x: 10, y: 10 };
      const dimensions = { width: 2, height: 2 };

      collisionSystem.insert(objectId, oldPos, dimensions);
      collisionSystem.update(objectId, oldPos, newPos, dimensions);

      expect(collisionSystem.findCollisions(oldPos, dimensions)).not.toContain(objectId);
      expect(collisionSystem.findCollisions(newPos, dimensions)).toContain(objectId);
    });

    test('clears all objects correctly', () => {
      const objects = [
        { id: 'obj1', pos: { x: 5, y: 5 } },
        { id: 'obj2', pos: { x: 10, y: 10 } }
      ];

      const dimensions = { width: 2, height: 2 };
      objects.forEach(obj => collisionSystem.insert(obj.id, obj.pos, dimensions));

      collisionSystem.clear();

      objects.forEach(obj => {
        expect(collisionSystem.findCollisions(obj.pos, dimensions)).not.toContain(obj.id);
      });
    });
  });

  describe('Collision Detection', () => {
    test('detects overlapping objects', () => {
      const obj1 = { id: 'obj1', pos: { x: 5, y: 5 }, dim: { width: 2, height: 2 } };
      const obj2 = { id: 'obj2', pos: { x: 6, y: 6 }, dim: { width: 2, height: 2 } };

      collisionSystem.insert(obj1.id, obj1.pos, obj1.dim);
      collisionSystem.insert(obj2.id, obj2.pos, obj2.dim);

      const collisions = collisionSystem.findCollisions(obj2.pos, obj2.dim);
      expect(collisions).toContain(obj1.id);
    });

    test('does not detect non-overlapping objects', () => {
      const obj1 = { id: 'obj1', pos: { x: 5, y: 5 }, dim: { width: 2, height: 2 } };
      const obj2 = { id: 'obj2', pos: { x: 10, y: 10 }, dim: { width: 2, height: 2 } };

      collisionSystem.insert(obj1.id, obj1.pos, obj1.dim);
      collisionSystem.insert(obj2.id, obj2.pos, obj2.dim);

      const collisions = collisionSystem.findCollisions(obj2.pos, obj2.dim);
      expect(collisions).not.toContain(obj1.id);
    });

    test('handles edge-to-edge collisions', () => {
      const obj1 = { id: 'obj1', pos: { x: 5, y: 5 }, dim: { width: 2, height: 2 } };
      const obj2 = { id: 'obj2', pos: { x: 7, y: 5 }, dim: { width: 2, height: 2 } };

      collisionSystem.insert(obj1.id, obj1.pos, obj1.dim);
      collisionSystem.insert(obj2.id, obj2.pos, obj2.dim);

      const collisions = collisionSystem.findCollisions(obj2.pos, obj2.dim);
      expect(collisions).not.toContain(obj1.id);
    });
  });

  describe('Position Validation', () => {
    test('finds valid position when original position is valid', () => {
      const objectId = 'test-object';
      const position = { x: 5, y: 5 };
      const dimensions = { width: 2, height: 2 };

      const validPos = collisionSystem.findValidPosition(objectId, position, dimensions);
      expect(validPos).toEqual(position);
    });

    test('finds alternative position when original position is invalid', () => {
      const obj1 = { id: 'obj1', pos: { x: 5, y: 5 }, dim: { width: 2, height: 2 } };
      const obj2 = { id: 'obj2', pos: { x: 5, y: 5 }, dim: { width: 2, height: 2 } };

      collisionSystem.insert(obj1.id, obj1.pos, obj1.dim);
      const validPos = collisionSystem.findValidPosition(obj2.id, obj2.pos, obj2.dim);

      expect(validPos).not.toBeNull();
      expect(validPos).not.toEqual(obj2.pos);
    });

    test('returns null when no valid position is found', () => {
      // Fill the entire grid with walls
      for (let y = 0; y < dimensions.height; y++) {
        for (let x = 0; x < dimensions.width; x++) {
          gridManager.setCellType({ x, y }, CellType.WALL);
        }
      }

      const objectId = 'test-object';
      const position = { x: 5, y: 5 };
      const dimensions = { width: 2, height: 2 };

      const validPos = collisionSystem.findValidPosition(objectId, position, dimensions);
      expect(validPos).toBeNull();
    });

    test('respects grid boundaries', () => {
      const objectId = 'test-object';
      const position = { x: dimensions.width - 1, y: dimensions.height - 1 };
      const objDimensions = { width: 2, height: 2 };

      const validPos = collisionSystem.findValidPosition(objectId, position, objDimensions);
      expect(validPos).not.toEqual(position);

      if (validPos) {
        expect(validPos.x + objDimensions.width).toBeLessThanOrEqual(dimensions.width);
        expect(validPos.y + objDimensions.height).toBeLessThanOrEqual(dimensions.height);
      }
    });
  });

  describe('Performance', () => {
    test('handles large number of objects efficiently', () => {
      const numObjects = 100;
      const objects = Array.from({ length: numObjects }, (_, i) => ({
        id: `obj${i}`,
        pos: { x: i % 10, y: Math.floor(i / 10) },
        dim: { width: 1, height: 1 }
      }));

      const startTime = performance.now();

      // Insert all objects
      objects.forEach(obj => collisionSystem.insert(obj.id, obj.pos, obj.dim));

      // Query collisions for each object
      objects.forEach(obj => {
        collisionSystem.findCollisions(obj.pos, obj.dim);
      });

      const endTime = performance.now();
      const duration = endTime - startTime;

      // Operations should complete in reasonable time (adjust threshold as needed)
      expect(duration).toBeLessThan(1000); // 1 second
    });
  });
}); 