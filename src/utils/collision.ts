import { GridManager } from './grid';
import { GridPosition, GridDimensions, CellType } from '../types/grid';

interface QuadTreeBounds {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface QuadTreeNode {
  bounds: QuadTreeBounds;
  objects: string[];
  nodes: QuadTreeNode[];
  level: number;
}

export class CollisionSystem {
  private gridManager: GridManager;
  private quadTree: QuadTreeNode;
  private readonly MAX_OBJECTS = 10;
  private readonly MAX_LEVELS = 5;

  constructor(gridManager: GridManager) {
    this.gridManager = gridManager;
    const grid = gridManager.getGrid();
    
    this.quadTree = {
      bounds: {
        x: 0,
        y: 0,
        width: grid.dimensions.width,
        height: grid.dimensions.height
      },
      objects: [],
      nodes: [],
      level: 0
    };
  }

  public clear(): void {
    this.quadTree.objects = [];
    this.quadTree.nodes = [];
  }

  public insert(objectId: string, position: GridPosition, dimensions: GridDimensions): void {
    const bounds = {
      x: position.x,
      y: position.y,
      width: dimensions.width,
      height: dimensions.height
    };

    this.insertIntoNode(this.quadTree, objectId, bounds);
  }

  public remove(objectId: string, position: GridPosition, dimensions: GridDimensions): void {
    const bounds = {
      x: position.x,
      y: position.y,
      width: dimensions.width,
      height: dimensions.height
    };

    this.removeFromNode(this.quadTree, objectId, bounds);
  }

  public update(objectId: string, oldPos: GridPosition, newPos: GridPosition, dimensions: GridDimensions): void {
    this.remove(objectId, oldPos, dimensions);
    this.insert(objectId, newPos, dimensions);
  }

  public findCollisions(position: GridPosition, dimensions: GridDimensions): string[] {
    const bounds = {
      x: position.x,
      y: position.y,
      width: dimensions.width,
      height: dimensions.height
    };

    const potentialCollisions = this.queryNode(this.quadTree, bounds);
    return potentialCollisions.filter(id => this.checkDetailedCollision(id, bounds));
  }

  public findValidPosition(
    objectId: string,
    position: GridPosition,
    dimensions: GridDimensions,
    maxAttempts: number = 10
  ): GridPosition | null {
    // Try original position first
    if (this.isPositionValid(position, dimensions, objectId)) {
      return position;
    }

    // Try positions in expanding spiral pattern
    const spiralOffsets = this.generateSpiralOffsets(maxAttempts);
    for (const offset of spiralOffsets) {
      const newPos = {
        x: position.x + offset.x,
        y: position.y + offset.y
      };

      if (this.isPositionValid(newPos, dimensions, objectId)) {
        return newPos;
      }
    }

    return null;
  }

  private insertIntoNode(node: QuadTreeNode, objectId: string, bounds: QuadTreeBounds): void {
    // If node has subnodes, insert into appropriate subnode
    if (node.nodes.length > 0) {
      const index = this.getNodeIndex(node, bounds);
      if (index !== -1) {
        this.insertIntoNode(node.nodes[index], objectId, bounds);
        return;
      }
    }

    // Add object to this node
    node.objects.push(objectId);

    // Split if needed
    if (
      node.objects.length > this.MAX_OBJECTS &&
      node.level < this.MAX_LEVELS
    ) {
      if (node.nodes.length === 0) {
        this.split(node);
      }

      // Redistribute existing objects
      let i = 0;
      while (i < node.objects.length) {
        const currentId = node.objects[i];
        const currentBounds = this.getBoundsForObject(currentId);
        const index = this.getNodeIndex(node, currentBounds);

        if (index !== -1) {
          const movedId = node.objects.splice(i, 1)[0];
          this.insertIntoNode(node.nodes[index], movedId, currentBounds);
        } else {
          i++;
        }
      }
    }
  }

  private removeFromNode(node: QuadTreeNode, objectId: string, bounds: QuadTreeBounds): void {
    // If node has subnodes, try to remove from appropriate subnode
    if (node.nodes.length > 0) {
      const index = this.getNodeIndex(node, bounds);
      if (index !== -1) {
        this.removeFromNode(node.nodes[index], objectId, bounds);
        return;
      }
    }

    // Remove object from this node
    const index = node.objects.indexOf(objectId);
    if (index !== -1) {
      node.objects.splice(index, 1);
    }
  }

  private queryNode(node: QuadTreeNode, bounds: QuadTreeBounds): string[] {
    const result: string[] = [];
    
    // Get index for bounds
    const index = this.getNodeIndex(node, bounds);

    // Add objects from this node
    result.push(...node.objects);

    // If node has subnodes and bounds fits in a subnode, add from that subnode
    if (node.nodes.length > 0) {
      if (index !== -1) {
        result.push(...this.queryNode(node.nodes[index], bounds));
      } else {
        // Bounds overlaps multiple nodes, check all
        for (const subnode of node.nodes) {
          if (this.boundsOverlap(bounds, subnode.bounds)) {
            result.push(...this.queryNode(subnode, bounds));
          }
        }
      }
    }

    return result;
  }

  private split(node: QuadTreeNode): void {
    const subWidth = node.bounds.width / 2;
    const subHeight = node.bounds.height / 2;
    const x = node.bounds.x;
    const y = node.bounds.y;
    const level = node.level + 1;

    node.nodes = [
      // Top right
      {
        bounds: { x: x + subWidth, y, width: subWidth, height: subHeight },
        objects: [],
        nodes: [],
        level
      },
      // Top left
      {
        bounds: { x, y, width: subWidth, height: subHeight },
        objects: [],
        nodes: [],
        level
      },
      // Bottom left
      {
        bounds: { x, y: y + subHeight, width: subWidth, height: subHeight },
        objects: [],
        nodes: [],
        level
      },
      // Bottom right
      {
        bounds: { x: x + subWidth, y: y + subHeight, width: subWidth, height: subHeight },
        objects: [],
        nodes: [],
        level
      }
    ];
  }

  private getNodeIndex(node: QuadTreeNode, bounds: QuadTreeBounds): number {
    const verticalMidpoint = node.bounds.x + (node.bounds.width / 2);
    const horizontalMidpoint = node.bounds.y + (node.bounds.height / 2);

    const fitsTop = bounds.y < horizontalMidpoint && bounds.y + bounds.height < horizontalMidpoint;
    const fitsBottom = bounds.y > horizontalMidpoint;
    const fitsLeft = bounds.x < verticalMidpoint && bounds.x + bounds.width < verticalMidpoint;
    const fitsRight = bounds.x > verticalMidpoint;

    if (fitsTop && fitsRight) return 0;
    if (fitsTop && fitsLeft) return 1;
    if (fitsBottom && fitsLeft) return 2;
    if (fitsBottom && fitsRight) return 3;

    return -1;
  }

  private boundsOverlap(a: QuadTreeBounds, b: QuadTreeBounds): boolean {
    return !(
      a.x + a.width <= b.x ||
      b.x + b.width <= a.x ||
      a.y + a.height <= b.y ||
      b.y + b.height <= a.y
    );
  }

  private getBoundsForObject(objectId: string): QuadTreeBounds {
    const position = this.gridManager.getGrid().buildings.get(objectId);
    if (!position) {
      throw new Error(`Object ${objectId} not found in grid`);
    }

    return {
      x: position.x,
      y: position.y,
      width: 1, // Default size
      height: 1
    };
  }

  private checkDetailedCollision(objectId: string, bounds: QuadTreeBounds): boolean {
    const objectBounds = this.getBoundsForObject(objectId);
    return this.boundsOverlap(bounds, objectBounds);
  }

  private isPositionValid(
    position: GridPosition,
    dimensions: GridDimensions,
    excludeId?: string
  ): boolean {
    // Check grid bounds
    if (!this.gridManager.isValidPosition(position)) return false;
    if (
      !this.gridManager.isValidPosition({
        x: position.x + dimensions.width - 1,
        y: position.y + dimensions.height - 1
      })
    ) {
      return false;
    }

    // Check terrain and occupancy
    for (let y = position.y; y < position.y + dimensions.height; y++) {
      for (let x = position.x; x < position.x + dimensions.width; x++) {
        const cell = this.gridManager.getCellAt({ x, y });
        if (!cell) return false;
        if (cell.isOccupied && cell.buildingId !== excludeId) return false;
        if (cell.cellType === CellType.WALL || cell.cellType === CellType.BLOCKED) {
          return false;
        }
      }
    }

    // Check collisions with other objects
    const collisions = this.findCollisions(position, dimensions);
    return collisions.length === 0 || (excludeId && collisions.length === 1 && collisions[0] === excludeId);
  }

  private generateSpiralOffsets(maxAttempts: number): GridPosition[] {
    const offsets: GridPosition[] = [];
    let x = 0;
    let y = 0;
    let dx = 0;
    let dy = -1;

    for (let i = 0; i < maxAttempts; i++) {
      offsets.push({ x, y });

      if (x === y || (x < 0 && x === -y) || (x > 0 && x === 1 - y)) {
        const temp = dx;
        dx = -dy;
        dy = temp;
      }

      x += dx;
      y += dy;
    }

    return offsets;
  }
} 