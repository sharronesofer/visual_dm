import { MovementService } from '../services/MovementService';
import { Position } from '../types/common';
import { PlayerState } from '../types/player';
import {
  syncPlayerPosition,
  handleMovementResponse,
} from '../utils/playerSync';

// Mock the API calls
jest.mock('../api/player', () => ({
  updatePlayerPosition: jest.fn(),
  getPlayerPosition: jest.fn(),
}));

import { updatePlayerPosition, getPlayerPosition } from '../api/player';

describe('Player Synchronization', () => {
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

    // Clear mock calls
    (updatePlayerPosition as jest.Mock).mockClear();
    (getPlayerPosition as jest.Mock).mockClear();
  });

  test('syncs player position with backend', async () => {
    const newPosition: Position = { x: 4, y: 5 };
    (updatePlayerPosition as jest.Mock).mockResolvedValueOnce({
      success: true,
    });

    const result = await syncPlayerPosition(newPosition);

    expect(updatePlayerPosition).toHaveBeenCalledWith(newPosition);
    expect(result.success).toBe(true);
  });

  test('handles backend sync failure gracefully', async () => {
    const newPosition: Position = { x: 4, y: 5 };
    (updatePlayerPosition as jest.Mock).mockRejectedValueOnce(
      new Error('Network error')
    );

    const result = await syncPlayerPosition(newPosition);

    expect(updatePlayerPosition).toHaveBeenCalledWith(newPosition);
    expect(result.success).toBe(false);
    expect(result.error).toBe('Failed to sync position with server');
  });

  test('retries failed sync attempts', async () => {
    const newPosition: Position = { x: 4, y: 5 };
    (updatePlayerPosition as jest.Mock)
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({ success: true });

    const result = await syncPlayerPosition(newPosition, { retries: 1 });

    expect(updatePlayerPosition).toHaveBeenCalledTimes(2);
    expect(result.success).toBe(true);
  });

  test('handles movement response with valid position', () => {
    const serverPosition: Position = { x: 4, y: 5 };
    const clientState: PlayerState = {
      position: { x: 4, y: 5 },
      targetPosition: null,
      movementState: 'idle',
      facing: 'west',
      visionRadius: 3,
      discoveredRegions: new Set(),
      visitedPOIs: new Set(),
    };

    const result = handleMovementResponse(
      { success: true, position: serverPosition },
      clientState
    );

    expect(result.position).toEqual(serverPosition);
    expect(result.movementState).toBe('idle');
  });

  test('handles movement response with position mismatch', () => {
    const serverPosition: Position = { x: 4, y: 5 };
    const clientState: PlayerState = {
      position: { x: 3, y: 5 }, // Different from server
      targetPosition: null,
      movementState: 'idle',
      facing: 'west',
      visionRadius: 3,
      discoveredRegions: new Set(),
      visitedPOIs: new Set(),
    };

    const result = handleMovementResponse(
      { success: true, position: serverPosition },
      clientState
    );

    expect(result.position).toEqual(serverPosition);
    expect(result.movementState).toBe('correcting');
  });

  test('handles failed movement response', () => {
    const clientState: PlayerState = {
      position: { x: 4, y: 5 },
      targetPosition: { x: 5, y: 5 },
      movementState: 'moving',
      facing: 'east',
      visionRadius: 3,
      discoveredRegions: new Set(),
      visitedPOIs: new Set(),
    };

    const result = handleMovementResponse(
      { success: false, error: 'Invalid move' },
      clientState
    );

    expect(result.position).toEqual(clientState.position);
    expect(result.movementState).toBe('blocked');
    expect(result.targetPosition).toBeNull();
  });

  test('recovers from server-client desync', async () => {
    const serverPosition: Position = { x: 7, y: 7 };
    (getPlayerPosition as jest.Mock).mockResolvedValueOnce({
      position: serverPosition,
    });

    const clientState: PlayerState = {
      position: { x: 4, y: 5 },
      targetPosition: null,
      movementState: 'idle',
      facing: 'west',
      visionRadius: 3,
      discoveredRegions: new Set(),
      visitedPOIs: new Set(),
    };

    const result = await syncPlayerPosition(clientState.position, {
      forceSync: true,
    });

    expect(getPlayerPosition).toHaveBeenCalled();
    expect(result.success).toBe(true);
    expect(result.position).toEqual(serverPosition);
  });

  test('validates server position before syncing', async () => {
    const invalidServerPosition: Position = { x: -1, y: -1 };
    (getPlayerPosition as jest.Mock).mockResolvedValueOnce({
      position: invalidServerPosition,
    });

    const clientState: PlayerState = {
      position: { x: 4, y: 5 },
      targetPosition: null,
      movementState: 'idle',
      facing: 'west',
      visionRadius: 3,
      discoveredRegions: new Set(),
      visitedPOIs: new Set(),
    };

    const result = await syncPlayerPosition(clientState.position, {
      forceSync: true,
    });

    expect(result.success).toBe(false);
    expect(result.error).toBe('Invalid server position');
  });
});
