from typing import Any


const getChunkKey = (position: Position): str => `${position.x},${position.y}`
const parseChunkKey = (key: str): Position => {
  const [x, y] = key.split(',').map(Number)
  return { x, y }
}