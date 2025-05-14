import { Position } from '../types/common';

export const getChunkKey = (position: Position): string => `${position.x},${position.y}`;

export const parseChunkKey = (key: string): Position => {
  const [x, y] = key.split(',').map(Number);
  return { x, y };
};
