import { PathfindingSystem } from '../pathfinding';
import { GridManager } from '../grid';
import { GridPosition, GridDimensions, CellType } from '../../types/grid';

describe('PathfindingSystem', () => {
  let gridManager: GridManager;
  let pathfinding: PathfindingSystem;
  const dimensions: GridDimensions = { width: 10, height: 10 };

  beforeEach(() => {
    gridManager = new GridManager(dimensions);
    pathfinding = new PathfindingSystem(gridManager);
  });

  describe('Path Finding', () => {
    test('finds direct path in empty grid', () => {
      const start: GridPosition = { x: 0, y: 0 };
      const end: GridPosition = { x: 2, y: 0 };
      
      const path = pathfinding.findPath(start, end);
      expect(path.length).toBe(3); // [0,0] -> [1,0] -> [2,0]
      expect(path[0]).toEqual(start);
      expect(path[path.length - 1]).toEqual(end);
    });

    test('finds path around obstacle', () => {
      const start: GridPosition = { x: 0, y: 0 };
      const end: GridPosition = { x: 2, y: 0 };
      
      gridManager.setCellType({ x: 1, y: 0 }, CellType.WALL);
      
      const path = pathfinding.findPath(start, end);
      expect(path.length).toBe(4); // [0,0] -> [0,1] -> [1,1] -> [2,1] -> [2,0]
      expect(path[0]).toEqual(start);
      expect(path[path.length - 1]).toEqual(end);
    });

    test('returns empty path when no route exists', () => {
      const start: GridPosition = { x: 0, y: 0 };
      const end: GridPosition = { x: 2, y: 0 };
      
      // Create wall blocking all paths
      gridManager.setCellType({ x: 1, y: 0 }, CellType.WALL);
      gridManager.setCellType({ x: 1, y: 1 }, CellType.WALL);
      gridManager.setCellType({ x: 0, y: 1 }, CellType.WALL);
      
      const path = pathfinding.findPath(start, end);
      expect(path.length).toBe(0);
    });

    test('handles diagonal paths efficiently', () => {
      const start: GridPosition = { x: 0, y: 0 };
      const end: GridPosition = { x: 2, y: 2 };
      
      const path = pathfinding.findPath(start, end);
      expect(path.length).toBe(5); // Should find a path with 5 steps
      expect(path[0]).toEqual(start);
      expect(path[path.length - 1]).toEqual(end);
    });
  });

  describe('Path Possibility', () => {
    test('confirms possible path', () => {
      const start: GridPosition = { x: 0, y: 0 };
      const end: GridPosition = { x: 2, y: 2 };
      
      expect(pathfinding.isPathPossible(start, end)).toBeTruthy();
    });

    test('identifies impossible path', () => {
      const start: GridPosition = { x: 0, y: 0 };
      const end: GridPosition = { x: 2, y: 0 };
      
      // Create wall blocking all paths
      gridManager.setCellType({ x: 1, y: 0 }, CellType.WALL);
      gridManager.setCellType({ x: 1, y: 1 }, CellType.WALL);
      gridManager.setCellType({ x: 0, y: 1 }, CellType.WALL);
      
      expect(pathfinding.isPathPossible(start, end)).toBeFalsy();
    });
  });

  describe('Accessible Area', () => {
    test('finds accessible area within range', () => {
      const start: GridPosition = { x: 5, y: 5 };
      const maxDistance = 2;
      
      const accessible = pathfinding.findAccessibleArea(start, maxDistance);
      // Should include start + 12 surrounding cells within Manhattan distance 2
      expect(accessible.size).toBe(13);
    });

    test('respects obstacles in accessible area calculation', () => {
      const start: GridPosition = { x: 5, y: 5 };
      const maxDistance = 2;
      
      gridManager.setCellType({ x: 5, y: 6 }, CellType.WALL);
      gridManager.setCellType({ x: 6, y: 5 }, CellType.WALL);
      
      const accessible = pathfinding.findAccessibleArea(start, maxDistance);
      // Should exclude walled cells and cells only reachable through walls
      expect(accessible.size).toBe(9);
    });

    test('handles edge of grid correctly', () => {
      const start: GridPosition = { x: 0, y: 0 };
      const maxDistance = 2;
      
      const accessible = pathfinding.findAccessibleArea(start, maxDistance);
      // Should only include cells within the grid bounds
      expect(accessible.size).toBe(6); // Corner position limits accessible cells
    });

    test('respects maximum distance limit', () => {
      const start: GridPosition = { x: 5, y: 5 };
      const maxDistance = 1;
      
      const accessible = pathfinding.findAccessibleArea(start, maxDistance);
      // Should only include start + immediate neighbors
      expect(accessible.size).toBe(5);
    });
  });

  describe('Edge Cases', () => {
    test('handles start position same as end position', () => {
      const position: GridPosition = { x: 0, y: 0 };
      const path = pathfinding.findPath(position, position);
      expect(path.length).toBe(1);
      expect(path[0]).toEqual(position);
    });

    test('handles invalid positions', () => {
      const start: GridPosition = { x: 0, y: 0 };
      const invalidEnd: GridPosition = { x: -1, y: 0 };
      
      const path = pathfinding.findPath(start, invalidEnd);
      expect(path.length).toBe(0);
    });

    test('handles positions at grid boundaries', () => {
      const start: GridPosition = { x: 0, y: 0 };
      const end: GridPosition = { x: dimensions.width - 1, y: dimensions.height - 1 };
      
      const path = pathfinding.findPath(start, end);
      expect(path.length).toBeGreaterThan(0);
      expect(path[0]).toEqual(start);
      expect(path[path.length - 1]).toEqual(end);
    });
  });
}); 