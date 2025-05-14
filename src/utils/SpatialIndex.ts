/**
 * Region interface for spatial indexing
 */
export interface Region {
  id: string;
  bbox: [number, number, number, number]; // [minX, minY, maxX, maxY]
}

/**
 * Grid-based spatial index for efficient region querying
 * Supports insertion, removal, update, and viewport queries
 */
export class GridSpatialIndex {
  private cellSize: number;
  private grid: Map<string, Set<string>> = new Map();
  private regions: Map<string, Region> = new Map();

  constructor(cellSize: number = 100) {
    this.cellSize = cellSize;
  }

  /**
   * Get all grid cell keys that a bounding box overlaps
   */
  private getCellsForBBox(bbox: [number, number, number, number]): string[] {
    const [minX, minY, maxX, maxY] = bbox;
    const cells: string[] = [];
    const startCellX = Math.floor(minX / this.cellSize);
    const startCellY = Math.floor(minY / this.cellSize);
    const endCellX = Math.floor(maxX / this.cellSize);
    const endCellY = Math.floor(maxY / this.cellSize);
    for (let x = startCellX; x <= endCellX; x++) {
      for (let y = startCellY; y <= endCellY; y++) {
        cells.push(`${x},${y}`);
      }
    }
    return cells;
  }

  /**
   * Insert a region into the spatial index
   */
  insert(region: Region): void {
    this.regions.set(region.id, region);
    const cells = this.getCellsForBBox(region.bbox);
    cells.forEach(cellKey => {
      if (!this.grid.has(cellKey)) {
        this.grid.set(cellKey, new Set());
      }
      this.grid.get(cellKey)!.add(region.id);
    });
  }

  /**
   * Remove a region by ID
   */
  remove(regionId: string): boolean {
    const region = this.regions.get(regionId);
    if (!region) return false;
    const cells = this.getCellsForBBox(region.bbox);
    cells.forEach(cellKey => {
      const cell = this.grid.get(cellKey);
      if (cell) {
        cell.delete(regionId);
        if (cell.size === 0) {
          this.grid.delete(cellKey);
        }
      }
    });
    this.regions.delete(regionId);
    return true;
  }

  /**
   * Query for region IDs that intersect a viewport rectangle
   */
  query(viewport: { minX: number; minY: number; maxX: number; maxY: number }): string[] {
    const cells = this.getCellsForBBox([
      viewport.minX,
      viewport.minY,
      viewport.maxX,
      viewport.maxY,
    ]);
    const resultSet = new Set<string>();
    cells.forEach(cellKey => {
      const cell = this.grid.get(cellKey);
      if (cell) {
        cell.forEach(regionId => {
          const region = this.regions.get(regionId)!;
          if (
            this.intersects(region.bbox, [
              viewport.minX,
              viewport.minY,
              viewport.maxX,
              viewport.maxY,
            ])
          ) {
            resultSet.add(regionId);
          }
        });
      }
    });
    return Array.from(resultSet);
  }

  /**
   * Update a region's bounding box
   */
  update(region: Region): boolean {
    if (!this.regions.has(region.id)) return false;
    this.remove(region.id);
    this.insert(region);
    return true;
  }

  /**
   * Check if two bounding boxes intersect (excluding touching at a single point/corner)
   */
  private intersects(
    bbox1: [number, number, number, number],
    bbox2: [number, number, number, number]
  ): boolean {
    // Use strict inequalities for non-overlapping cases
    return !(
      bbox1[2] <= bbox2[0] || // bbox1 is left of or just touching bbox2
      bbox1[0] >= bbox2[2] || // bbox1 is right of or just touching bbox2
      bbox1[3] <= bbox2[1] || // bbox1 is above or just touching bbox2
      bbox1[1] >= bbox2[3] // bbox1 is below or just touching bbox2
    );
  }
}

/**
 * Abstract interface for spatial index providers
 */
export interface SpatialIndexProvider {
  insert(region: Region): void;
  remove(regionId: string): boolean;
  update(region: Region): boolean;
  query(viewport: { minX: number; minY: number; maxX: number; maxY: number }): string[];
}

/**
 * Placeholder for a quadtree-based spatial index (for hierarchical culling)
 */
export class QuadtreeSpatialIndex implements SpatialIndexProvider {
  constructor(options: any = {}) {
    // TODO: Implement quadtree initialization with options (e.g., maxDepth, cellSize)
  }
  insert(region: Region): void {
    // TODO: Implement quadtree insert
  }
  remove(regionId: string): boolean {
    // TODO: Implement quadtree remove
    return false;
  }
  update(region: Region): boolean {
    // TODO: Implement quadtree update
    return false;
  }
  query(viewport: { minX: number; minY: number; maxX: number; maxY: number }): string[] {
    // TODO: Implement quadtree query
    return [];
  }
}

/**
 * Placeholder for an R-tree-based spatial index (for hierarchical culling)
 */
export class RTreeSpatialIndex implements SpatialIndexProvider {
  constructor(options: any = {}) {
    // TODO: Implement R-tree initialization with options (e.g., min/max entries)
  }
  insert(region: Region): void {
    // TODO: Implement R-tree insert
  }
  remove(regionId: string): boolean {
    // TODO: Implement R-tree remove
    return false;
  }
  update(region: Region): boolean {
    // TODO: Implement R-tree update
    return false;
  }
  query(viewport: { minX: number; minY: number; maxX: number; maxY: number }): string[] {
    // TODO: Implement R-tree query
    return [];
  }
}

/**
 * Factory function to create a spatial index provider
 * @param type The type of spatial index ('grid', 'quadtree', etc.)
 * @param options Options for the spatial index (e.g., cellSize)
 */
export function createSpatialIndex(type: string = 'grid', options: any = {}): SpatialIndexProvider {
  switch (type) {
    case 'quadtree':
      return new QuadtreeSpatialIndex(options);
    case 'rtree':
      return new RTreeSpatialIndex(options);
    case 'grid':
    default:
      return new GridSpatialIndex(options.cellSize || 100);
  }
}
