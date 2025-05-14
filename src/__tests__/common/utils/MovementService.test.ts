import { MovementService } from '../../services/MovementService';
import { Position } from '../../types/common';
import { TerrainEffect } from '../../types/player';

describe('MovementService', () => {
  let movementService: MovementService;

  beforeEach(() => {
    movementService = MovementService.getInstance();
    movementService.setMapBounds({ width: 10, height: 10 });
    movementService.setObstacles([]);
  });

  describe('validateMovement', () => {
    it('should allow valid movement within bounds', () => {
      const from: Position = { x: 0, y: 0 };
      const to: Position = { x: 1, y: 1 };

      const result = movementService.validateMovement(from, to);

      expect(result.success).toBe(true);
      expect(result.newPosition).toEqual(to);
      expect(result.path).toHaveLength(2);
    });

    it('should prevent movement outside bounds', () => {
      const from: Position = { x: 0, y: 0 };
      const to: Position = { x: -1, y: 0 };

      const result = movementService.validateMovement(from, to);

      expect(result.success).toBe(false);
      expect(result.error).toBe('Destination is out of bounds');
    });

    it('should respect obstacles', () => {
      const from: Position = { x: 0, y: 0 };
      const to: Position = { x: 2, y: 0 };
      const obstacle: Position = { x: 1, y: 0 };

      movementService.setObstacles([obstacle]);

      const result = movementService.validateMovement(from, to);

      expect(result.success).toBe(false);
      expect(result.error).toBe('Path blocked by obstacle');
    });

    it('should calculate correct movement cost with terrain effects', () => {
      const from: Position = { x: 0, y: 0 };
      const to: Position = { x: 2, y: 0 };

      const swampEffect: TerrainEffect = {
        id: 'swamp',
        name: 'Swamp',
        movementCost: 2,
        description: 'Difficult terrain',
        isObstacle: false,
      };

      movementService.addTerrainEffect(swampEffect);

      const result = movementService.validateMovement(from, to);

      expect(result.success).toBe(true);
      expect(result.cost).toBe(2); // 2 steps with default cost
    });
  });

  describe('movePlayer', () => {
    it('should update player state on valid movement', () => {
      const currentState = {
        position: { x: 0, y: 0 },
        facing: 'south' as const,
        movement: {
          isMoving: false,
          direction: null,
          speed: 1,
          path: [],
          destination: null,
        },
        movementPoints: 10,
        isPathfinding: false,
      };

      const targetPosition = { x: 1, y: 0 };

      const result = movementService.movePlayer(currentState, targetPosition);

      expect(result.success).toBe(true);
      expect(result.newPosition).toEqual(targetPosition);
    });

    it('should prevent movement when insufficient points', () => {
      const currentState = {
        position: { x: 0, y: 0 },
        facing: 'south' as const,
        movement: {
          isMoving: false,
          direction: null,
          speed: 1,
          path: [],
          destination: null,
        },
        movementPoints: 0,
        isPathfinding: false,
      };

      const targetPosition = { x: 1, y: 0 };

      const result = movementService.movePlayer(currentState, targetPosition);

      expect(result.success).toBe(false);
      expect(result.error).toBe('Insufficient movement points');
    });
  });

  describe('getAvailableMoves', () => {
    it('should return all valid adjacent positions', () => {
      const position: Position = { x: 1, y: 1 };
      const movementPoints = 10;

      const availableMoves = movementService.getAvailableMoves(
        position,
        movementPoints
      );

      expect(availableMoves).toHaveLength(4); // North, East, South, West
      expect(availableMoves).toContainEqual({ x: 1, y: 0 }); // North
      expect(availableMoves).toContainEqual({ x: 2, y: 1 }); // East
      expect(availableMoves).toContainEqual({ x: 1, y: 2 }); // South
      expect(availableMoves).toContainEqual({ x: 0, y: 1 }); // West
    });

    it('should exclude positions with obstacles', () => {
      const position: Position = { x: 1, y: 1 };
      const movementPoints = 10;
      const obstacle: Position = { x: 1, y: 0 }; // North position

      movementService.setObstacles([obstacle]);

      const availableMoves = movementService.getAvailableMoves(
        position,
        movementPoints
      );

      expect(availableMoves).toHaveLength(3);
      expect(availableMoves).not.toContainEqual(obstacle);
    });
  });
});
