import { Position, Viewport } from '../types/common';
import { MapChunk, Region, POI, TerrainType, MapChunkKey } from '../types/map';

/**
 * Generate a chunk key from a position
 */
export function generateChunkKey(position: Position): string {
  return `${position.x},${position.y}`;
}

/**
 * Parse a chunk key into a position
 */
export function parseChunkKey(key: string): Position {
  const [x, y] = key.split(',').map(Number);
  return { x, y };
}

/**
 * Check if a region intersects with a viewport
 */
export function regionIntersectsViewport(
  region: Region,
  viewport: Viewport,
  buffer: number = 0
): boolean {
  return !(
    region.position.x + region.width < viewport.x - buffer ||
    region.position.x > viewport.x + viewport.width + buffer ||
    region.position.y + region.height < viewport.y - buffer ||
    region.position.y > viewport.y + viewport.height + buffer
  );
}

/**
 * Get POIs within a region
 */
export function getPOIsInRegion(region: Region, pois: POI[]): POI[] {
  return pois.filter(
    poi =>
      poi.position.x >= region.position.x &&
      poi.position.x < region.position.x + region.width &&
      poi.position.y >= region.position.y &&
      poi.position.y < region.position.y + region.height
  );
}

/**
 * Get visible chunks within a viewport
 */
export function getVisibleChunks(viewport: Viewport, chunkSize: number): Position[] {
  const startX = Math.floor(viewport.x / chunkSize);
  const startY = Math.floor(viewport.y / chunkSize);
  const endX = Math.ceil((viewport.x + viewport.width) / chunkSize);
  const endY = Math.ceil((viewport.y + viewport.height) / chunkSize);

  const chunks: Position[] = [];
  for (let x = startX; x < endX; x++) {
    for (let y = startY; y < endY; y++) {
      chunks.push({ x, y });
    }
  }
  return chunks;
}

/**
 * Get the terrain type at a specific position
 */
export function getTerrainAtPosition(chunk: MapChunk, localPosition: Position): TerrainType | null {
  if (
    localPosition.x < 0 ||
    localPosition.x >= chunk.width ||
    localPosition.y < 0 ||
    localPosition.y >= chunk.height
  ) {
    return null;
  }
  return chunk.terrain[localPosition.y][localPosition.x];
}

/**
 * Convert world coordinates to chunk coordinates
 */
export function worldToChunkCoordinates(
  worldPosition: Position,
  chunkSize: number
): { chunkPos: Position; localPos: Position } {
  const chunkX = Math.floor(worldPosition.x / chunkSize);
  const chunkY = Math.floor(worldPosition.y / chunkSize);
  const localX = worldPosition.x % chunkSize;
  const localY = worldPosition.y % chunkSize;

  return {
    chunkPos: { x: chunkX, y: chunkY },
    localPos: { x: localX, y: localY },
  };
}

/**
 * Convert chunk coordinates to world coordinates
 */
export function chunkToWorldCoordinates(
  chunkPos: Position,
  localPos: Position,
  chunkSize: number
): Position {
  return {
    x: chunkPos.x * chunkSize + localPos.x,
    y: chunkPos.y * chunkSize + localPos.y,
  };
}

/**
 * Get adjacent chunks
 */
export function getAdjacentChunks(position: Position): Position[] {
  return [
    { x: position.x - 1, y: position.y },
    { x: position.x + 1, y: position.y },
    { x: position.x, y: position.y - 1 },
    { x: position.x, y: position.y + 1 },
  ];
}

/**
 * Check if two chunks are adjacent
 */
export function areChunksAdjacent(chunk1: Position, chunk2: Position): boolean {
  const dx = Math.abs(chunk2.x - chunk1.x);
  const dy = Math.abs(chunk2.y - chunk1.y);
  return (dx === 1 && dy === 0) || (dx === 0 && dy === 1);
}

/**
 * Serialize a chunk key
 */
export function serializeChunkKey(key: MapChunkKey): string {
  return `${key.x},${key.y}`;
}

/**
 * Deserialize a chunk key
 */
export function deserializeChunkKey(key: string): MapChunkKey {
  const [x, y] = key.split(',').map(Number);
  return {
    x,
    y,
    toString: () => key,
  };
}

/**
 * Calculate chunk loading priority based on distance from viewport center
 */
export function calculateChunkPriority(chunk: Position, viewport: Viewport): number {
  const viewportCenter = {
    x: viewport.x + viewport.width / 2,
    y: viewport.y + viewport.height / 2,
  };
  const chunkCenter = {
    x: chunk.x + 0.5,
    y: chunk.y + 0.5,
  };
  const distance = Math.sqrt(
    Math.pow(chunkCenter.x - viewportCenter.x, 2) + Math.pow(chunkCenter.y - viewportCenter.y, 2)
  );
  return 1 / (distance + 1);
}
