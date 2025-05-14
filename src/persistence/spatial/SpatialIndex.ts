import RBush from 'rbush';
import { Building } from '../../types/buildings';
import { Logger } from '../../utils/logger';

/**
 * Spatial index entry type
 */
interface SpatialEntry {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
  buildingId: string;
  data?: Building;
}

/**
 * Search area bounds
 */
export interface SearchBounds {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
}

/**
 * Spatial index for efficient building location queries
 */
export class SpatialIndex {
  private index: RBush<SpatialEntry>;
  private logger: Logger;

  constructor() {
    this.index = new RBush<SpatialEntry>();
    this.logger = Logger.getInstance().child('SpatialIndex');
  }

  /**
   * Insert or update a building in the spatial index
   */
  public insert(building: Building): void {
    try {
      // Remove existing entry if any
      this.remove(building.id);

      // Calculate bounding box
      const bounds = this.calculateBuildingBounds(building);
      
      // Insert into index
      this.index.insert({
        ...bounds,
        buildingId: building.id,
        data: building
      });

      this.logger.debug('Building inserted into spatial index', { buildingId: building.id });
    } catch (error) {
      this.logger.error('Failed to insert building into spatial index:', { 
        buildingId: building.id,
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }

  /**
   * Remove a building from the spatial index
   */
  public remove(buildingId: string): void {
    try {
      const existing = this.index.all().find(entry => entry.buildingId === buildingId);
      if (existing) {
        this.index.remove(existing);
        this.logger.debug('Building removed from spatial index', { buildingId });
      }
    } catch (error) {
      this.logger.error('Failed to remove building from spatial index:', {
        buildingId,
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }

  /**
   * Search for buildings within bounds
   */
  public search(bounds: SearchBounds): Building[] {
    try {
      const results = this.index.search(bounds);
      return results.map(entry => entry.data!);
    } catch (error) {
      this.logger.error('Failed to search spatial index:', {
        bounds,
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }

  /**
   * Find nearest buildings to a point
   */
  public findNearest(x: number, y: number, k: number = 5): Building[] {
    try {
      // Create a small search box around the point
      const radius = 100; // Initial search radius
      const bounds = {
        minX: x - radius,
        minY: y - radius,
        maxX: x + radius,
        maxY: y + radius
      };

      // Get candidates
      let results = this.index.search(bounds);
      
      // Sort by distance
      results.sort((a, b) => {
        const distA = this.calculateDistance(x, y, a);
        const distB = this.calculateDistance(x, y, b);
        return distA - distB;
      });

      // Return k nearest
      return results.slice(0, k).map(entry => entry.data!);
    } catch (error) {
      this.logger.error('Failed to find nearest buildings:', {
        x,
        y,
        k,
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }

  /**
   * Calculate building bounds for indexing
   */
  private calculateBuildingBounds(building: Building): SearchBounds {
    const { position, dimensions } = building;
    return {
      minX: position.x - dimensions.width / 2,
      minY: position.y - dimensions.length / 2,
      maxX: position.x + dimensions.width / 2,
      maxY: position.y + dimensions.length / 2
    };
  }

  /**
   * Calculate distance from point to building center
   */
  private calculateDistance(x: number, y: number, entry: SpatialEntry): number {
    const centerX = (entry.minX + entry.maxX) / 2;
    const centerY = (entry.minY + entry.maxY) / 2;
    return Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2));
  }

  /**
   * Clear the spatial index
   */
  public clear(): void {
    try {
      this.index.clear();
      this.logger.debug('Spatial index cleared');
    } catch (error) {
      this.logger.error('Failed to clear spatial index:', {
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }

  /**
   * Get all buildings in the index
   */
  public getAll(): Building[] {
    try {
      return this.index.all().map(entry => entry.data!);
    } catch (error) {
      this.logger.error('Failed to get all buildings from spatial index:', {
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }

  /**
   * Bulk load buildings into the index
   */
  public bulkLoad(buildings: Building[]): void {
    try {
      const entries = buildings.map(building => ({
        ...this.calculateBuildingBounds(building),
        buildingId: building.id,
        data: building
      }));

      this.index.load(entries);
      this.logger.debug('Bulk loaded buildings into spatial index', { count: buildings.length });
    } catch (error) {
      this.logger.error('Failed to bulk load buildings into spatial index:', {
        count: buildings.length,
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }
} 