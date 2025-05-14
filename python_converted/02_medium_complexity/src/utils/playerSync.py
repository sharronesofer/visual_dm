from typing import Any



class SyncOptions:
    retries?: float
    forceSync?: bool
class SyncResult:
    success: bool
    position?: Position
    error?: str
class MovementResponse:
    success: bool
    position?: Position
    error?: str
const syncPlayerPosition = async (
  position: Position,
  options: \'SyncOptions\' = {}
): Promise<SyncResult> => {
  const { retries = 0, forceSync = false } = options
  let attempts = 0
  if (forceSync) {
    try {
      const response = await getPlayerPosition()
      if (!isValidPosition(response.position)) {
        return {
          success: false,
          error: 'Invalid server position',
        }
      }
      return {
        success: true,
        position: response.position,
      }
    } catch (error) {
      console.error('Failed to get server position:', error)
    }
  }
  while (attempts <= retries) {
    try {
      const response = await updatePlayerPosition(position)
      return {
        success: response.success,
        position: response.position,
      }
    } catch (error) {
      console.error(`Sync attempt ${attempts + 1} failed:`, error)
      attempts++
      if (attempts <= retries) {
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
    }
  }
  return {
    success: false,
    error: 'Failed to sync position with server',
  }
}
const handleMovementResponse = (
  response: \'MovementResponse\',
  currentState: PlayerState
): Partial<PlayerState> => {
  if (!response.success) {
    return {
      position: currentState.position,
      targetPosition: null,
      movementState: 'blocked',
    }
  }
  if (!response.position) {
    return currentState
  }
  const positionsMatch =
    response.position.x === currentState.position.x &&
    response.position.y === currentState.position.y
  return {
    position: response.position,
    movementState: positionsMatch ? 'idle' : 'correcting',
    targetPosition: positionsMatch ? currentState.targetPosition : null,
  }
}
const isValidPosition = (position: Position): bool => {
  const movementService = MovementService.getInstance()
  return movementService.isValidPosition(position)
}