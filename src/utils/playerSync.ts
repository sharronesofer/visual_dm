import { Position } from '../types/common';
import { PlayerState } from '../types/player';
import { updatePlayerPosition, getPlayerPosition } from '../api/player';
import { MovementService } from '../services/MovementService';

interface SyncOptions {
  retries?: number;
  forceSync?: boolean;
}

interface SyncResult {
  success: boolean;
  position?: Position;
  error?: string;
}

interface MovementResponse {
  success: boolean;
  position?: Position;
  error?: string;
}

export const syncPlayerPosition = async (
  position: Position,
  options: SyncOptions = {}
): Promise<SyncResult> => {
  const { retries = 0, forceSync = false } = options;
  let attempts = 0;

  // If forceSync is true, get the current server position first
  if (forceSync) {
    try {
      const response = await getPlayerPosition();
      if (!isValidPosition(response.position)) {
        return {
          success: false,
          error: 'Invalid server position',
        };
      }
      return {
        success: true,
        position: response.position,
      };
    } catch (error) {
      console.error('Failed to get server position:', error);
    }
  }

  // Try to update the position
  while (attempts <= retries) {
    try {
      const response = await updatePlayerPosition(position);
      return {
        success: response.success,
        position: response.position,
      };
    } catch (error) {
      console.error(`Sync attempt ${attempts + 1} failed:`, error);
      attempts++;

      if (attempts <= retries) {
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
  }

  return {
    success: false,
    error: 'Failed to sync position with server',
  };
};

export const handleMovementResponse = (
  response: MovementResponse,
  currentState: PlayerState
): Partial<PlayerState> => {
  if (!response.success) {
    return {
      position: currentState.position,
      targetPosition: null,
      movementState: 'blocked',
    };
  }

  if (!response.position) {
    return currentState;
  }

  // Check if server position matches client position
  const positionsMatch =
    response.position.x === currentState.position.x &&
    response.position.y === currentState.position.y;

  return {
    position: response.position,
    movementState: positionsMatch ? 'idle' : 'correcting',
    targetPosition: positionsMatch ? currentState.targetPosition : null,
  };
};

const isValidPosition = (position: Position): boolean => {
  const movementService = MovementService.getInstance();
  return movementService.isValidPosition(position);
};
