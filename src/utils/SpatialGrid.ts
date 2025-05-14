import { EventBus } from '../core/events/EventBus';
import { SceneEventType, ISceneEvent } from '../core/events/SceneEventTypes';

interface Position {
  x: number;
  y: number;
}

interface GridCell {
  entities: Set<string>;
}

/**
 * Event subscriber for spatial grid integration with scene events
 */
class SpatialEventSubscriber {
  constructor(private spatialGrid: SpatialGrid) {
    const eventBus = EventBus.getInstance();
    // Subscribe to relevant scene event types
    eventBus.on(SceneEventType.SCENE_LOADED, this.handleSceneEvent.bind(this));
    eventBus.on(SceneEventType.SCENE_UNLOADED, this.handleSceneEvent.bind(this));
    eventBus.on(SceneEventType.SCENE_ACTIVATED, this.handleSceneEvent.bind(this));
    eventBus.on(SceneEventType.SCENE_DEACTIVATED, this.handleSceneEvent.bind(this));
    eventBus.on(SceneEventType.SCENE_OBJECT_ADDED, this.handleSceneEvent.bind(this));
    eventBus.on(SceneEventType.SCENE_OBJECT_REMOVED, this.handleSceneEvent.bind(this));
    eventBus.on(SceneEventType.COORDINATES_CHANGED, this.handleSceneEvent.bind(this));
    eventBus.on(SceneEventType.BOUNDARY_CROSSED, this.handleSceneEvent.bind(this));
  }

  /**
   * Handle scene events and trigger spatial-specific updates
   */
  private async handleSceneEvent(event: ISceneEvent): Promise<void> {
    // Log the event for monitoring
    console.log('[SpatialEventSubscriber] Received scene event:', event.type, event);
    // TODO: Implement spatial-specific update logic based on event type
    // Example: if (event.type === SceneEventType.COORDINATES_CHANGED) { ... }
  }
}

export class SpatialGrid {
  private grid: Map<string, Set<string>>;
  private entityPositions: Map<string, { x: number; y: number }>;
  private cellSize: number;

  constructor(cellSize: number = 100) {
    this.grid = new Map();
    this.entityPositions = new Map();
    this.cellSize = cellSize;
    // Register the event subscriber for scene events
    new SpatialEventSubscriber(this);
  }

  /**
   * Add an entity to the grid
   */
  public addEntity(entityId: string, x: number, y: number): void {
    // Remove from old position if exists
    this.removeEntity(entityId);

    // Store new position
    this.entityPositions.set(entityId, { x, y });

    // Add to grid
    const cellKey = this.getCellKey(x, y);
    if (!this.grid.has(cellKey)) {
      this.grid.set(cellKey, new Set());
    }
    this.grid.get(cellKey)!.add(entityId);
  }

  /**
   * Remove an entity from the grid
   */
  public removeEntity(entityId: string): void {
    const position = this.entityPositions.get(entityId);
    if (position) {
      const cellKey = this.getCellKey(position.x, position.y);
      const cell = this.grid.get(cellKey);
      if (cell) {
        cell.delete(entityId);
        if (cell.size === 0) {
          this.grid.delete(cellKey);
        }
      }
      this.entityPositions.delete(entityId);
    }
  }

  /**
   * Update an entity's position
   */
  public updateEntity(entityId: string, x: number, y: number): void {
    this.addEntity(entityId, x, y);
  }

  /**
   * Get all entities within a radius of a given entity
   */
  public getEntitiesInRange(entityId: string, radius: number): string[] {
    const position = this.entityPositions.get(entityId);
    if (!position) return [];

    const cellRadius = Math.ceil(radius / this.cellSize);
    const centerX = Math.floor(position.x / this.cellSize);
    const centerY = Math.floor(position.y / this.cellSize);
    const nearbyEntities = new Set<string>();

    // Check cells in a square around the center
    for (let dx = -cellRadius; dx <= cellRadius; dx++) {
      for (let dy = -cellRadius; dy <= cellRadius; dy++) {
        const cellKey = this.getCellKey(
          (centerX + dx) * this.cellSize,
          (centerY + dy) * this.cellSize
        );
        const cellEntities = this.grid.get(cellKey);
        if (cellEntities) {
          for (const entity of cellEntities) {
            const entityPos = this.entityPositions.get(entity);
            if (entityPos) {
              const distance = Math.sqrt(
                Math.pow(entityPos.x - position.x, 2) +
                Math.pow(entityPos.y - position.y, 2)
              );
              if (distance <= radius) {
                nearbyEntities.add(entity);
              }
            }
          }
        }
      }
    }

    return Array.from(nearbyEntities);
  }

  /**
   * Get the key for a grid cell containing the given coordinates
   */
  private getCellKey(x: number, y: number): string {
    const cellX = Math.floor(x / this.cellSize);
    const cellY = Math.floor(y / this.cellSize);
    return `${cellX},${cellY}`;
  }

  public getDistance(pos1: Position, pos2: Position): number {
    const dx = pos2.x - pos1.x;
    const dy = pos2.y - pos1.y;
    return Math.sqrt(dx * dx + dy * dy);
  }

  public getNearbyEntities(position: Position, radius: number): string[] {
    const cellRadius = Math.ceil(radius / this.cellSize);
    const nearby: string[] = [];

    // Check cells within radius
    for (let x = Math.max(0, position.x - cellRadius); x <= Math.min(position.x + cellRadius, this.cellSize - 1); x++) {
      for (let y = Math.max(0, position.y - cellRadius); y <= Math.min(position.y + cellRadius, this.cellSize - 1); y++) {
        const cellKey = this.getCellKey(x, y);
        const cellEntities = this.grid.get(cellKey);
        if (cellEntities) {
          cellEntities.forEach(entityId => {
            const entityPos = this.entityPositions.get(entityId);
            if (entityPos && this.getDistance(position, entityPos) <= radius) {
              nearby.push(entityId);
            }
          });
        }
      }
    }

    return nearby;
  }

  public getEntityPosition(entityId: string): Position | undefined {
    return this.entityPositions.get(entityId);
  }

  /**
   * Get all entities in a specific cell
   */
  public getEntitiesInCell(position: Position): string[] {
    const cellKey = this.getCellKey(position.x, position.y);
    const cell = this.grid.get(cellKey);
    return cell ? Array.from(cell) : [];
  }
} 