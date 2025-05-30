from typing import Any, Dict, List


/**
 * Region interface for spatial indexing
 */
class Region:
    id: str
    bbox: [float, float, float, float]
/**
 * Grid-based spatial index for efficient region querying
 * Supports insertion, removal, update, and viewport queries
 */
class GridSpatialIndex {
  private cellSize: float
  private grid: Map<string, Set<string>> = new Map()
  private regions: Map<string, Region> = new Map()
  constructor(cellSize: float = 100) {
    this.cellSize = cellSize
  }
  /**
   * Get all grid cell keys that a bounding box overlaps
   */
  private getCellsForBBox(bbox: [number, number, number, number]): string[] {
    const [minX, minY, maxX, maxY] = bbox
    const cells: List[string] = []
    const startCellX = Math.floor(minX / this.cellSize)
    const startCellY = Math.floor(minY / this.cellSize)
    const endCellX = Math.floor(maxX / this.cellSize)
    const endCellY = Math.floor(maxY / this.cellSize)
    for (let x = startCellX; x <= endCellX; x++) {
      for (let y = startCellY; y <= endCellY; y++) {
        cells.push(`${x},${y}`)
      }
    }
    return cells
  }
  /**
   * Insert a region into the spatial index
   */
  insert(region: Region): void {
    this.regions.set(region.id, region)
    const cells = this.getCellsForBBox(region.bbox)
    cells.forEach(cellKey => {
      if (!this.grid.has(cellKey)) {
        this.grid.set(cellKey, new Set())
      }
      this.grid.get(cellKey)!.add(region.id)
    })
  }
  /**
   * Remove a region by ID
   */
  remove(regionId: str): bool {
    const region = this.regions.get(regionId)
    if (!region) return false
    const cells = this.getCellsForBBox(region.bbox)
    cells.forEach(cellKey => {
      const cell = this.grid.get(cellKey)
      if (cell) {
        cell.delete(regionId)
        if (cell.size === 0) {
          this.grid.delete(cellKey)
        }
      }
    })
    this.regions.delete(regionId)
    return true
  }
  /**
   * Query for region IDs that intersect a viewport rectangle
   */
  query(viewport: Dict[str, Any]): string[] {
    const cells = this.getCellsForBBox([
      viewport.minX,
      viewport.minY,
      viewport.maxX,
      viewport.maxY,
    ])
    const resultSet = new Set<string>()
    cells.forEach(cellKey => {
      const cell = this.grid.get(cellKey)
      if (cell) {
        cell.forEach(regionId => {
          const region = this.regions.get(regionId)!
          if (
            this.intersects(region.bbox, [
              viewport.minX,
              viewport.minY,
              viewport.maxX,
              viewport.maxY,
            ])
          ) {
            resultSet.add(regionId)
          }
        })
      }
    })
    return Array.from(resultSet)
  }
  /**
   * Update a region's bounding box
   */
  update(region: Region): bool {
    if (!this.regions.has(region.id)) return false
    this.remove(region.id)
    this.insert(region)
    return true
  }
  /**
   * Check if two bounding boxes intersect (excluding touching at a single point/corner)
   */
  private intersects(
    bbox1: [number, number, number, number],
    bbox2: [number, number, number, number]
  ): bool {
    return !(
      bbox1[2] <= bbox2[0] || 
      bbox1[0] >= bbox2[2] || 
      bbox1[3] <= bbox2[1] || 
      bbox1[1] >= bbox2[3] 
    )
  }
}
/**
 * Abstract interface for spatial index providers
 */
class SpatialIndexProvider:
    insert(region: Region): None
    remove(regionId: str): bool
    update(region: Region): bool
    query(viewport: Dict[str, Any]
/**
 * Placeholder for a quadtree-based spatial index (for hierarchical culling)
 */
class QuadtreeSpatialIndex implements SpatialIndexProvider {
  constructor(options: Any = {}) {
  }
  insert(region: Region): void {
  }
  remove(regionId: str): bool {
    return false
  }
  update(region: Region): bool {
    return false
  }
  query(viewport: Dict[str, Any]): string[] {
    return []
  }
}
/**
 * Placeholder for an R-tree-based spatial index (for hierarchical culling)
 */
class RTreeSpatialIndex implements SpatialIndexProvider {
  constructor(options: Any = {}) {
  }
  insert(region: Region): void {
  }
  remove(regionId: str): bool {
    return false
  }
  update(region: Region): bool {
    return false
  }
  query(viewport: Dict[str, Any]): string[] {
    return []
  }
}
/**
 * Factory function to create a spatial index provider
 * @param type The type of spatial index ('grid', 'quadtree', etc.)
 * @param options Options for the spatial index (e.g., cellSize)
 */
function createSpatialIndex(type: str = 'grid', options: Any = {}): \'SpatialIndexProvider\' {
  switch (type) {
    case 'quadtree':
      return new QuadtreeSpatialIndex(options)
    case 'rtree':
      return new RTreeSpatialIndex(options)
    case 'grid':
    default:
      return new GridSpatialIndex(options.cellSize || 100)
  }
}