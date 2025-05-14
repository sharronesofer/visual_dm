import { Position } from './common';

export type MovementDirection = 'north' | 'south' | 'east' | 'west';

export interface MovementState {
  isMoving: boolean;
  direction: MovementDirection | null;
  speed: number;
  path: Position[];
  destination: Position | null;
}

export interface MovementOptions {
  diagonal?: boolean;
  ignoreObstacles?: boolean;
  maxDistance?: number;
  autoDiscover?: boolean;
}

export interface MovementResult {
  success: boolean;
  newPosition: Position;
  cost: number;
  path: Position[];
  error?: string;
}

export interface PlayerMovementState {
  position: Position;
  facing: MovementDirection;
  movement: MovementState;
  movementPoints: number;
  isPathfinding: boolean;
}

export interface TerrainEffect {
  id: string;
  name: string;
  movementCost: number;
  description: string;
  isObstacle: boolean;
}

export interface MovementRules {
  baseMovementPoints: number;
  diagonalMovement: boolean;
  terrainEffects: Record<string, TerrainEffect>;
  maxPathLength?: number;
  pathfindingAlgorithm?: 'astar' | 'dijkstra';
}

// Helper functions
export const calculateDistance = (from: Position, to: Position): number => {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  return Math.sqrt(dx * dx + dy * dy);
};

export const getDirectionFromPositions = (from: Position, to: Position): MovementDirection => {
  const dx = to.x - from.x;
  const dy = to.y - from.y;

  // Use the larger component to determine primary direction
  if (Math.abs(dx) > Math.abs(dy)) {
    return dx > 0 ? 'east' : 'west';
  }
  return dy > 0 ? 'south' : 'north';
};

export const isAdjacent = (pos1: Position, pos2: Position): boolean => {
  const dx = Math.abs(pos2.x - pos1.x);
  const dy = Math.abs(pos2.y - pos1.y);
  return (dx === 1 && dy === 0) || (dx === 0 && dy === 1);
};

export type PlayerState = {
  id: string;
  name: string;
  position: Position;
  health: number;
  maxHealth: number;
  inventory: any[];
  movement: MovementState;
  // Add more fields as needed
};
