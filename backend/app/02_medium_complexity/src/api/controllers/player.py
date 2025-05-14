from typing import Any, Dict



class PlayerPositionResponse:
    success: bool
    position?: Position
    error?: str
const updatePlayerPosition = async (position: Position): Promise<PlayerPositionResponse> => {
  try {
    const response = await fetch('/api/player/position', {
      method: 'POST',
      headers: Dict[str, Any],
      body: JSON.stringify({ position }),
    })
    if (!response.ok) {
      throw new Error('Failed to update position')
    }
    return await response.json()
  } catch (error) {
    console.error('Error updating player position:', error)
    throw error
  }
}
const getPlayerPosition = async (): Promise<PlayerPositionResponse> => {
  try {
    const response = await fetch('/api/player/position')
    if (!response.ok) {
      throw new Error('Failed to get position')
    }
    return await response.json()
  } catch (error) {
    console.error('Error getting player position:', error)
    throw error
  }
}