import { renderHook, act } from '@testing-library/react-hooks';
import { usePlayerMovement } from '../hooks/usePlayerMovement';
import { MovementService } from '../services/MovementService';
import { Position } from '../types/common';

describe('usePlayerMovement Hook', () => {
  const mockInitialPosition: Position = { x: 5, y: 5 };
  const mockMapBounds = { width: 10, height: 10 };
  const mockObstacles: Position[] = [
    { x: 6, y: 5 }, // Right of initial position
    { x: 5, y: 6 }, // Below initial position
  ];

  beforeEach(() => {
    // Reset movement service before each test
    const movementService = MovementService.getInstance();
    movementService.setMapBounds(mockMapBounds);
    movementService.setObstacles(mockObstacles);
  });

  test('initializes with correct state', () => {
    const { result } = renderHook(() => usePlayerMovement(mockInitialPosition));

    expect(result.current.position).toEqual(mockInitialPosition);
    expect(result.current.facing).toBe('south');
    expect(result.current.isMoving).toBe(false);
    expect(result.current.movementPoints).toBe(30);
    expect(result.current.currentPath).toEqual([]);
  });

  test('moves to valid position', () => {
    const { result } = renderHook(() => usePlayerMovement(mockInitialPosition));

    act(() => {
      const targetPosition = { x: 4, y: 5 }; // Valid move to the left
      result.current.move(targetPosition);
    });

    expect(result.current.position).toEqual({ x: 4, y: 5 });
    expect(result.current.isMoving).toBe(true);
    expect(result.current.movementPoints).toBe(29);
  });

  test('prevents movement to invalid position', () => {
    const { result } = renderHook(() => usePlayerMovement(mockInitialPosition));

    act(() => {
      const targetPosition = { x: 6, y: 5 }; // Position with obstacle
      result.current.move(targetPosition);
    });

    expect(result.current.position).toEqual(mockInitialPosition); // Position unchanged
    expect(result.current.isMoving).toBe(false);
    expect(result.current.movementPoints).toBe(30); // Points unchanged
  });

  test('updates available moves correctly', () => {
    const { result } = renderHook(() => usePlayerMovement(mockInitialPosition));

    const availableMoves = result.current.getAvailableMoves();

    expect(availableMoves).toContainEqual({ x: 4, y: 5 }); // Left is valid
    expect(availableMoves).toContainEqual({ x: 5, y: 4 }); // Up is valid
    expect(availableMoves).not.toContainEqual({ x: 6, y: 5 }); // Right has obstacle
    expect(availableMoves).not.toContainEqual({ x: 5, y: 6 }); // Down has obstacle
  });

  test('resets movement points correctly', () => {
    const { result } = renderHook(() => usePlayerMovement(mockInitialPosition));

    // Make a move to reduce points
    act(() => {
      result.current.move({ x: 4, y: 5 });
    });
    expect(result.current.movementPoints).toBe(29);

    // Reset points
    act(() => {
      result.current.resetMovementPoints();
    });
    expect(result.current.movementPoints).toBe(30);
  });

  test('updates facing direction correctly', () => {
    const { result } = renderHook(() => usePlayerMovement(mockInitialPosition));

    act(() => {
      result.current.setFacing('north');
    });
    expect(result.current.facing).toBe('north');

    act(() => {
      result.current.setFacing('east');
    });
    expect(result.current.facing).toBe('east');
  });

  test('validates moves correctly', () => {
    const { result } = renderHook(() => usePlayerMovement(mockInitialPosition));

    // Valid move
    const validResult = result.current.validateMove({ x: 4, y: 5 });
    expect(validResult.success).toBe(true);
    expect(validResult.newPosition).toEqual({ x: 4, y: 5 });

    // Invalid move (obstacle)
    const invalidResult = result.current.validateMove({ x: 6, y: 5 });
    expect(invalidResult.success).toBe(false);
    expect(invalidResult.error).toBeDefined();
  });

  test('handles path updates during movement', () => {
    const { result } = renderHook(() => usePlayerMovement(mockInitialPosition));

    act(() => {
      result.current.move({ x: 4, y: 5 });
    });

    expect(result.current.currentPath).toEqual([{ x: 4, y: 5 }]);
  });
});
