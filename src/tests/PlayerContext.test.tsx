import React from 'react';
import { render, act } from '@testing-library/react';
import { PlayerProvider, usePlayer } from '../contexts/PlayerContext';
import { useMapGeneration } from '../contexts/MapGenerationContext';
import { Position } from '../types/common';
import { MovementOptions } from '../types/player';

// Mock the MapGenerationContext
jest.mock('../contexts/MapGenerationContext', () => ({
  useMapGeneration: jest.fn(),
}));

describe('PlayerContext', () => {
  const mockMapState = {
    mapData: {
      chunks: {
        '0,0': {
          regions: {
            '0,0': {
              id: '0,0',
              position: { x: 0, y: 0 },
              borders: [],
            },
            '1,0': {
              id: '1,0',
              position: { x: 1, y: 0 },
              borders: [],
            },
          },
        },
      },
    },
  };

  const mockDiscoverRegions = jest.fn().mockResolvedValue(undefined);

  beforeEach(() => {
    (useMapGeneration as jest.Mock).mockReturnValue({
      state: mockMapState,
      discoverRegions: mockDiscoverRegions,
    });
  });

  test('initializes with default state', () => {
    let contextValue: ReturnType<typeof usePlayer> | undefined;
    const TestComponent = () => {
      contextValue = usePlayer();
      return null;
    };

    render(
      <PlayerProvider>
        <TestComponent />
      </PlayerProvider>
    );

    expect(contextValue?.state).toEqual({
      position: { x: 0, y: 0 },
      targetPosition: null,
      movementState: 'idle',
      facing: 'south',
      visionRadius: 3,
      discoveredRegions: new Set(),
      visitedPOIs: new Set(),
    });
  });

  test('moves player to valid position', async () => {
    let contextValue: ReturnType<typeof usePlayer> | undefined;
    const TestComponent = () => {
      contextValue = usePlayer();
      return null;
    };

    render(
      <PlayerProvider>
        <TestComponent />
      </PlayerProvider>
    );

    const targetPosition: Position = { x: 1, y: 0 };
    await act(async () => {
      await contextValue?.moveToPosition(targetPosition);
    });

    expect(contextValue?.state.position).toEqual(targetPosition);
    expect(contextValue?.state.movementState).toBe('idle');
  });

  test('discovers new regions after movement', async () => {
    let contextValue: ReturnType<typeof usePlayer> | undefined;
    const TestComponent = () => {
      contextValue = usePlayer();
      return null;
    };

    render(
      <PlayerProvider>
        <TestComponent />
      </PlayerProvider>
    );

    const targetPosition: Position = { x: 1, y: 0 };
    const options: MovementOptions = { ignoreObstacles: false };
    await act(async () => {
      await contextValue?.moveToPosition(targetPosition, options);
    });

    expect(mockDiscoverRegions).toHaveBeenCalled();
    expect(contextValue?.state.discoveredRegions.size).toBeGreaterThan(0);
  });

  test('handles movement cancellation', async () => {
    let contextValue: ReturnType<typeof usePlayer> | undefined;
    const TestComponent = () => {
      contextValue = usePlayer();
      return null;
    };

    render(
      <PlayerProvider>
        <TestComponent />
      </PlayerProvider>
    );

    const targetPosition: Position = { x: 1, y: 0 };
    await act(async () => {
      contextValue?.setTargetPosition(targetPosition);
      contextValue?.cancelMovement();
    });

    expect(contextValue?.state.targetPosition).toBeNull();
    expect(contextValue?.state.movementState).toBe('idle');
  });

  test('prevents movement to invalid positions', async () => {
    let contextValue: ReturnType<typeof usePlayer> | undefined;
    const TestComponent = () => {
      contextValue = usePlayer();
      return null;
    };

    // Mock an impassable border
    const mockMapStateWithObstacle = {
      ...mockMapState,
      mapData: {
        chunks: {
          '0,0': {
            regions: {
              '0,0': {
                id: '0,0',
                position: { x: 0, y: 0 },
                borders: [],
              },
              '1,0': {
                id: '1,0',
                position: { x: 1, y: 0 },
                borders: [{ type: 'impassable' }],
              },
            },
          },
        },
      },
    };

    (useMapGeneration as jest.Mock).mockReturnValue({
      state: mockMapStateWithObstacle,
      discoverRegions: mockDiscoverRegions,
    });

    render(
      <PlayerProvider>
        <TestComponent />
      </PlayerProvider>
    );

    const targetPosition: Position = { x: 1, y: 0 };
    const result = await act(async () => {
      return await contextValue?.moveToPosition(targetPosition);
    });

    expect(result?.success).toBe(false);
    expect(contextValue?.state.position).toEqual({ x: 0, y: 0 });
    expect(contextValue?.state.movementState).toBe('blocked');
  });

  test('updates facing direction after movement', async () => {
    let contextValue: ReturnType<typeof usePlayer> | undefined;
    const TestComponent = () => {
      contextValue = usePlayer();
      return null;
    };

    render(
      <PlayerProvider>
        <TestComponent />
      </PlayerProvider>
    );

    const targetPosition: Position = { x: 1, y: 0 };
    await act(async () => {
      await contextValue?.moveToPosition(targetPosition);
    });

    expect(contextValue?.state.facing).toBe('east');
  });
});
