import { Position } from '../types/common';
import { MovementDirection, TerrainEffect } from '../types/player';

export const calculateDistance = (from: Position, to: Position): number => {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  return Math.sqrt(dx * dx + dy * dy);
};

export const isAdjacent = (pos1: Position, pos2: Position): boolean => {
  const dx = Math.abs(pos2.x - pos1.x);
  const dy = Math.abs(pos2.y - pos1.y);
  return (dx === 1 && dy === 0) || (dx === 0 && dy === 1);
};

export const getDirectionFromPositions = (from: Position, to: Position): MovementDirection => {
  const dx = to.x - from.x;
  const dy = to.y - from.y;

  if (Math.abs(dx) > Math.abs(dy)) {
    return dx > 0 ? 'east' : 'west';
  }
  return dy > 0 ? 'south' : 'north';
};

export const calculatePath = (start: Position, end: Position): Position[] => {
  const path: Position[] = [];
  const current = { ...start };

  while (current.x !== end.x || current.y !== end.y) {
    // Move horizontally first, then vertically
    if (current.x !== end.x) {
      current.x += current.x < end.x ? 1 : -1;
    } else if (current.y !== end.y) {
      current.y += current.y < end.y ? 1 : -1;
    }
    path.push({ ...current });
  }

  return path;
};

export const calculateMovementCost = (
  path: Position[],
  terrainEffects: Record<string, TerrainEffect> = {}
): number => {
  return path.reduce((cost, _position, index) => {
    if (index === 0) return cost;

    // Get terrain at current position (simplified - you'll need to implement actual terrain lookup)
    const terrain = terrainEffects['default'] || { movementCost: 1 };
    return cost + terrain.movementCost;
  }, 0);
};

export const getAdjacentPositions = (position: Position): Position[] => {
  return [
    { x: position.x, y: position.y - 1 }, // North
    { x: position.x + 1, y: position.y }, // East
    { x: position.x, y: position.y + 1 }, // South
    { x: position.x - 1, y: position.y }, // West
  ];
};

export const isWithinBounds = (
  position: Position,
  bounds: { width: number; height: number }
): boolean => {
  return (
    position.x >= 0 && position.x < bounds.width && position.y >= 0 && position.y < bounds.height
  );
};
