import { GridManager } from './grid';
import { GridPosition, PathfindingNode, CellType, GridCell } from '../core/interfaces/types/grid';
// If POICategory is not found in '../types/spatial', comment out or correct the import.
// import { POICategory } from '../types/spatial';
import { CollisionSystem } from './collision';
import { canCharacterAccessBuilding, canCharacterAccessRoom, canCharacterAccessDoor } from './accessControl';
import { Building } from '../core/interfaces/types/buildings';
import { Room } from '../core/interfaces/types/buildings';
import { Door } from '../core/interfaces/types/building';

// Define POICategory if not imported
export type POICategory = 'residential' | 'commercial' | 'industrial' | 'public' | 'restricted' | string;

interface PathCache {
  path: GridPosition[];
  timestamp: number;
  category?: POICategory;
}

interface GroupPathfindingOptions {
  groupSize?: number;
  formationWidth?: number;
  formationSpacing?: number;
  predictiveAvoidance?: boolean;
}

interface CategoryPathRules {
  preferredTypes: CellType[];
  avoidTypes: CellType[];
  weightMultiplier: number;
}

export class PathfindingSystem {
  private gridManager: GridManager;
  private collisionSystem: CollisionSystem;
  private pathCache: Map<string, PathCache>;
  private readonly CACHE_DURATION = 5000; // 5 seconds
  private categoryRules: Record<POICategory, CategoryPathRules>;
  private readonly PREDICTIVE_LOOKAHEAD = 3;

  constructor(gridManager: GridManager, collisionSystem: CollisionSystem) {
    this.gridManager = gridManager;
    this.collisionSystem = collisionSystem;
    this.pathCache = new Map();

    // Initialize category-specific routing rules
    this.categoryRules = {
      [POICategory.SOCIAL]: {
        preferredTypes: [CellType.ROAD, CellType.EMPTY],
        avoidTypes: [CellType.WALL, CellType.BLOCKED],
        weightMultiplier: 1.0
      },
      [POICategory.DUNGEON]: {
        preferredTypes: [CellType.EMPTY],
        avoidTypes: [CellType.ROAD],
        weightMultiplier: 1.5
      },
      [POICategory.EXPLORATION]: {
        preferredTypes: [CellType.EMPTY, CellType.ROAD],
        avoidTypes: [CellType.BLOCKED],
        weightMultiplier: 0.8
      }
    };
  }

  /**
   * Find a path between two points
   */
  public findPath(
    start: GridPosition,
    end: GridPosition,
    characterId?: string,
    predictiveAvoidance: boolean = false
  ): GridPosition[] {
    const openSet: PathfindingNode[] = [];
    const closedSet: Set<string> = new Set();

    const startNode: PathfindingNode = {
      position: start,
      gCost: 0,
      hCost: this.calculateHeuristic(start, end)
    };

    openSet.push(startNode);

    while (openSet.length > 0) {
      const currentNode = this.getLowestFCostNode(openSet);
      if (this.isSamePosition(currentNode.position, end)) {
        return this.reconstructPath(currentNode);
      }

      this.removeFromArray(openSet, currentNode);
      closedSet.add(this.positionToString(currentNode.position));

      const neighbors = this.getWalkableNeighbors(currentNode.position, characterId, undefined, undefined);
      for (const neighbor of neighbors) {
        if (closedSet.has(this.positionToString(neighbor))) {
          continue;
        }

        let newGCost = currentNode.gCost + this.getNodeCost({
          position: neighbor,
          gCost: 0,
          hCost: 0
        });

        if (predictiveAvoidance) {
          newGCost += this.calculatePredictiveCollisionCost(neighbor);
        }

        const neighborNode = openSet.find(node =>
          this.isSamePosition(node.position, neighbor)
        );

        if (!neighborNode) {
          openSet.push({
            position: neighbor,
            gCost: newGCost,
            hCost: this.calculateHeuristic(neighbor, end),
            parent: currentNode
          });
        } else if (newGCost < neighborNode.gCost) {
          const updatedNode = {
            ...neighborNode,
            gCost: newGCost,
            parent: currentNode
          };
          const index = openSet.indexOf(neighborNode);
          openSet[index] = updatedNode;
        }
      }
    }

    return []; // No path found
  }

  public invalidateCache(position: GridPosition, radius: number = 1): void {
    const now = Date.now();
    this.pathCache.forEach((cache, key) => {
      // Check if any point in the cached path is within the radius
      const isAffected = cache.path.some(point =>
        Math.abs(point.x - position.x) <= radius &&
        Math.abs(point.y - position.y) <= radius
      );

      if (isAffected) {
        this.pathCache.delete(key);
      }
    });

    // Also clean up old cache entries
    this.cleanCache(now);
  }

  public updatePathSegment(
    path: GridPosition[],
    startIndex: number,
    endIndex: number,
    category?: POICategory
  ): GridPosition[] {
    if (startIndex >= endIndex || startIndex < 0 || endIndex >= path.length) {
      return path;
    }

    const start = path[startIndex];
    const end = path[endIndex];
    const newSegment = this.calculatePath(start, end, category);

    // If no new path found, return original
    if (newSegment.length === 0) return path;

    // Splice in the new segment
    return [
      ...path.slice(0, startIndex),
      ...newSegment.slice(1, -1), // Exclude start/end to avoid duplicates
      ...path.slice(endIndex)
    ];
  }

  /**
   * Find a path suitable for group movement
   */
  public findGroupPath(
    start: GridPosition,
    end: GridPosition,
    options: GroupPathfindingOptions,
    characterId?: string
  ): GridPosition[] {
    const {
      groupSize = 1,
      formationWidth = 1,
      formationSpacing = 2,
      predictiveAvoidance = true
    } = options;

    // Calculate group dimensions
    const groupWidth = formationWidth * formationSpacing;
    const groupHeight = Math.ceil(groupSize / formationWidth) * formationSpacing;

    // Adjust node costs for group size
    const originalGetNodeCost = this.getNodeCost.bind(this);
    this.getNodeCost = (node: PathfindingNode): number => {
      let cost = originalGetNodeCost(node);

      // Check if group can fit at this position
      const dimensions = {
        width: groupWidth,
        height: groupHeight
      };

      // Add collision costs
      const collisions = this.collisionSystem.findCollisions(
        { x: node.position.x, y: node.position.y },
        dimensions
      );
      if (collisions.length > 0) {
        cost += collisions.length * 2;
      }

      // Add terrain costs based on group size
      const terrainCost = this.getTerrainCost(node);
      cost += terrainCost * Math.sqrt(groupSize);

      return cost;
    };

    // Find path with adjusted costs
    const path = this.findPath(start, end, characterId, predictiveAvoidance);

    // Restore original cost function
    this.getNodeCost = originalGetNodeCost;

    return path;
  }

  /**
   * Get terrain-based cost for a node
   */
  private getTerrainCost(node: PathfindingNode): number {
    const cell = this.gridManager.getCellAt(node.position);
    if (!cell) return Infinity;

    switch (cell.cellType) {
      case CellType.ROUGH:
        return 2;
      case CellType.WATER:
        return 3;
      case CellType.WALL:
      case CellType.BLOCKED:
        return Infinity;
      default:
        return 1;
    }
  }

  private calculatePath(
    start: GridPosition,
    end: GridPosition,
    category?: POICategory,
    groupOptions?: {
      groupWidth: number;
      groupHeight: number;
      predictiveAvoidance: boolean;
      formationSpacing: number;
    },
    characterId?: string
  ): GridPosition[] {
    const openSet: PathfindingNode[] = [];
    const closedSet: Set<string> = new Set();

    const startNode: PathfindingNode = {
      position: start,
      gCost: 0,
      hCost: this.calculateHeuristic(start, end, category)
    };

    openSet.push(startNode);

    while (openSet.length > 0) {
      const currentNode = this.getLowestFCostNode(openSet);
      if (this.isSamePosition(currentNode.position, end)) {
        return this.reconstructPath(currentNode);
      }

      this.removeFromArray(openSet, currentNode);
      closedSet.add(this.positionToString(currentNode.position));

      const neighbors = this.getWalkableNeighbors(currentNode.position, characterId, category, groupOptions);
      for (const neighbor of neighbors) {
        if (closedSet.has(this.positionToString(neighbor))) {
          continue;
        }

        // Calculate movement cost considering group size and formation
        const movementCost = this.calculateMovementCost(
          currentNode.position,
          neighbor,
          category,
          groupOptions
        );

        const gCost = currentNode.gCost + movementCost;
        const neighborNode = openSet.find(node =>
          this.isSamePosition(node.position, neighbor)
        );

        if (!neighborNode) {
          openSet.push({
            position: neighbor,
            gCost,
            hCost: this.calculateHeuristic(neighbor, end, category),
            parent: currentNode
          });
        } else if (gCost < neighborNode.gCost) {
          neighborNode.gCost = gCost;
          neighborNode.parent = currentNode;
        }
      }
    }

    return []; // No path found
  }

  private calculateMovementCost(
    from: GridPosition,
    to: GridPosition,
    category?: POICategory,
    groupOptions?: {
      groupWidth: number;
      groupHeight: number;
      predictiveAvoidance: boolean;
      formationSpacing: number;
    },
    characterId?: string
  ): number {
    const cell = this.gridManager.getCellAt(to);
    if (!cell) return Infinity;

    let cost = 1; // Base cost

    if (category) {
      const rules = this.categoryRules[category];

      // Apply category-specific rules
      if (rules.preferredTypes.includes(cell.cellType)) {
        cost *= 0.8; // 20% discount for preferred terrain
      }
      if (rules.avoidTypes.includes(cell.cellType)) {
        cost *= 2.0; // Double cost for terrain to avoid
      }

      cost *= rules.weightMultiplier;
    }

    // Group size considerations
    if (groupOptions) {
      const { groupWidth, groupHeight, predictiveAvoidance } = groupOptions;

      // Check if the entire group formation can fit
      const formationCollisions = this.checkFormationCollisions(to, groupWidth, groupHeight);
      if (formationCollisions > 0) {
        cost *= (1 + formationCollisions * 0.5); // Increase cost based on number of collisions
      }

      // Predictive collision avoidance
      if (predictiveAvoidance) {
        const futureCost = this.calculatePredictiveCollisionCost(to);
        cost += futureCost;
      }
    } else {
      // Single entity collision check
      const collisions = this.collisionSystem.findCollisions(to, { width: 1, height: 1 });
      if (collisions.length > 0) {
        cost *= 1.5; // 50% penalty for going through crowded areas
      }
    }

    return cost;
  }

  private checkFormationCollisions(
    position: GridPosition,
    width: number,
    height: number
  ): number {
    let collisionCount = 0;

    // Check each cell in the formation
    for (let x = position.x; x <= position.x + width; x++) {
      for (let y = position.y; y <= position.y + height; y++) {
        const collisions = this.collisionSystem.findCollisions(
          { x, y },
          { width: 1, height: 1 }
        );
        collisionCount += collisions.length;
      }
    }

    return collisionCount;
  }

  private calculatePredictiveCollisionCost(position: GridPosition): number {
    let predictiveCost = 0;

    // Look ahead for potential collisions in expanding area
    for (let step = 1; step <= this.PREDICTIVE_LOOKAHEAD; step++) {
      // Check a larger area for each step to simulate future movement possibilities
      const searchDimensions = {
        width: 1 + step,
        height: 1 + step
      };

      const collisions = this.collisionSystem.findCollisions(
        {
          x: position.x - Math.floor(step / 2),
          y: position.y - Math.floor(step / 2)
        },
        searchDimensions
      );

      if (collisions.length > 0) {
        // Decrease impact of future collisions based on distance
        predictiveCost += (collisions.length * 0.2) / step;
      }
    }

    return predictiveCost;
  }

  private calculateHeuristic(
    start: GridPosition,
    end: GridPosition,
    category?: POICategory
  ): number {
    let base = Math.abs(start.x - end.x) + Math.abs(start.y - end.y);

    if (category) {
      // Adjust heuristic based on category preferences
      const rules = this.categoryRules[category];
      base *= rules.weightMultiplier;
    }

    return base;
  }

  private getWalkableNeighbors(
    position: GridPosition,
    characterId?: string,
    category?: POICategory,
    groupOptions?: {
      groupWidth: number;
      groupHeight: number;
      predictiveAvoidance: boolean;
      formationSpacing: number;
    }
  ): GridPosition[] {
    const neighbors: GridPosition[] = [];
    const directions = [
      { x: 0, y: -1 },  // North
      { x: 1, y: 0 },   // East
      { x: 0, y: 1 },   // South
      { x: -1, y: 0 },  // West
      { x: 1, y: -1 },  // Northeast
      { x: 1, y: 1 },   // Southeast
      { x: -1, y: 1 },  // Southwest
      { x: -1, y: -1 }  // Northwest
    ];

    for (const dir of directions) {
      const newPos = {
        x: position.x + dir.x,
        y: position.y + dir.y
      };

      const cell = this.gridManager.getCellAt(newPos);
      if (!cell) continue;

      if (category) {
        const rules = this.categoryRules[category];
        if (rules.avoidTypes.includes(cell.cellType)) continue;
      }

      // Check access control
      let building: Building | undefined | null = undefined;
      let room: Room | undefined | null = undefined;
      let door: Door | undefined | null = undefined;
      if (cell.buildingId) {
        building = this.gridManager.getBuildingById(cell.buildingId) as Building | undefined | null;
        if (characterId && building && !canCharacterAccessBuilding(characterId, building.metadata)) continue;
      }
      if (cell.roomId) {
        room = this.gridManager.getRoomById(cell.roomId) as Room | undefined | null;
        if (characterId && room && !canCharacterAccessRoom(characterId, room, building?.metadata)) continue;
      }
      if (cell.doorId) {
        door = this.gridManager.getDoorById(cell.doorId) as Door | undefined | null;
        if (characterId && door && !canCharacterAccessDoor(characterId, door, room || undefined, building?.metadata)) continue;
      }

      // Check if position is walkable for the entire group formation
      if (groupOptions) {
        const { groupWidth, groupHeight } = groupOptions;
        let formationWalkable = true;

        // Check each cell in the formation
        for (let x = newPos.x; x <= newPos.x + groupWidth && formationWalkable; x++) {
          for (let y = newPos.y; y <= newPos.y + groupHeight && formationWalkable; y++) {
            const formationCell = this.gridManager.getCellAt({ x, y });
            if (!formationCell || !formationCell.walkable) {
              formationWalkable = false;
            }
          }
        }

        if (!formationWalkable) continue;
      }

      // For single entity or if formation check passed
      if (cell.walkable) {
        neighbors.push(newPos);
      }
    }

    return neighbors;
  }

  private getCacheKey(
    start: GridPosition,
    end: GridPosition,
    category?: POICategory
  ): string {
    return `${start.x},${start.y}-${end.x},${end.y}${category ? `-${category}` : ''}`;
  }

  private getValidCachedPath(key: string): GridPosition[] | null {
    const cached = this.pathCache.get(key);
    if (!cached) return null;

    const age = Date.now() - cached.timestamp;
    if (age > this.CACHE_DURATION) {
      this.pathCache.delete(key);
      return null;
    }

    // Verify path is still valid
    for (const point of cached.path) {
      const cell = this.gridManager.getCellAt(point);
      if (!cell || !cell.walkable || cell.isOccupied) {
        this.pathCache.delete(key);
        return null;
      }
    }

    return cached.path;
  }

  private cleanCache(now: number = Date.now()): void {
    for (const [key, cache] of this.pathCache.entries()) {
      if (now - cache.timestamp > this.CACHE_DURATION) {
        this.pathCache.delete(key);
      }
    }
  }

  private getLowestFCostNode(nodes: PathfindingNode[]): PathfindingNode {
    let lowest = nodes[0];
    for (let i = 1; i < nodes.length; i++) {
      const fCost = nodes[i].gCost + nodes[i].hCost;
      const lowestFCost = lowest.gCost + lowest.hCost;
      if (fCost < lowestFCost || (fCost === lowestFCost && nodes[i].hCost < lowest.hCost)) {
        lowest = nodes[i];
      }
    }
    return lowest;
  }

  private reconstructPath(endNode: PathfindingNode): GridPosition[] {
    const path: GridPosition[] = [];
    let currentNode: PathfindingNode | undefined = endNode;

    while (currentNode) {
      path.unshift(currentNode.position);
      currentNode = currentNode.parent;
    }

    return path;
  }

  private removeFromArray(arr: PathfindingNode[], item: PathfindingNode): void {
    const index = arr.findIndex(node =>
      this.isSamePosition(node.position, item.position)
    );
    if (index !== -1) {
      arr.splice(index, 1);
    }
  }

  private isSamePosition(a: GridPosition, b: GridPosition): boolean {
    return a.x === b.x && a.y === b.y;
  }

  private positionToString(pos: GridPosition): string {
    return `${pos.x},${pos.y}`;
  }

  /**
   * Get the cost of moving to a node
   */
  private getNodeCost(node: PathfindingNode): number {
    const cell = this.gridManager.getCellAt(node.position);
    if (!cell) return Infinity;

    let cost = 1;

    // Add terrain costs
    cost += this.getTerrainCost(node);

    // Add collision costs
    const collisions = this.collisionSystem.findCollisions(
      node.position,
      { width: 1, height: 1 }
    );
    if (collisions.length > 0) {
      cost += collisions.length;
    }

    return cost;
  }

  /**
   * Register event listeners for building/room/door access control changes.
   * These should be called by the building/room/door systems when relevant state changes occur.
   */
  public onBuildingAccessChanged(buildingId: string, affectedArea: { min: GridPosition, max: GridPosition }) {
    // Invalidate pathfinding cache for the affected area
    this.invalidateCacheRegion(affectedArea);
  }

  public onRoomAccessChanged(roomId: string, affectedArea: { min: GridPosition, max: GridPosition }) {
    this.invalidateCacheRegion(affectedArea);
  }

  public onDoorAccessChanged(doorId: string, affectedArea: { min: GridPosition, max: GridPosition }) {
    this.invalidateCacheRegion(affectedArea);
  }

  /**
   * Invalidate pathfinding cache for a rectangular region (min/max inclusive)
   */
  private invalidateCacheRegion(region: { min: GridPosition, max: GridPosition }) {
    // For each cached path, if any node is within the region, invalidate the cache entry
    for (const [key, cache] of this.pathCache.entries()) {
      if (cache.path.some(pos =>
        pos.x >= region.min.x && pos.x <= region.max.x &&
        pos.y >= region.min.y && pos.y <= region.max.y
      )) {
        this.pathCache.delete(key);
      }
    }
  }
} 