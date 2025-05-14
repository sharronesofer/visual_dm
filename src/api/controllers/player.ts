import { Position } from '../types/common';

interface PlayerPositionResponse {
  success: boolean;
  position?: Position;
  error?: string;
}

export const updatePlayerPosition = async (position: Position): Promise<PlayerPositionResponse> => {
  try {
    const response = await fetch('/api/player/position', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ position }),
    });

    if (!response.ok) {
      throw new Error('Failed to update position');
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating player position:', error);
    throw error;
  }
};

export const getPlayerPosition = async (): Promise<PlayerPositionResponse> => {
  try {
    const response = await fetch('/api/player/position');

    if (!response.ok) {
      throw new Error('Failed to get position');
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting player position:', error);
    throw error;
  }
};
