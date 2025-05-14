import { IPOI } from './types/IPOI';
import { POIFactory } from './factories/POIFactory';
import { POIType, POISubtype, Coordinates, ThematicElements } from './types/POITypes';

/**
 * Manages POI instances, their relationships, and persistence
 */
export class POIManager {
  private pois: Map<string, IPOI>;
  private activeRegion: { center: Coordinates; radius: number };

  constructor() {
    this.pois = new Map<string, IPOI>();
    this.activeRegion = {
      center: { x: 0, y: 0, z: 0, level: 0 },
      radius: 10
    };
  }

  /**
   * Create a new POI
   */
  createPOI(
    type: POIType,
    subtype: POISubtype,
    name: string,
    coordinates: Coordinates,
    thematicElements: ThematicElements
  ): IPOI {
    const poi = POIFactory.createPOI(type, subtype, name, coordinates, thematicElements);
    this.pois.set(poi.id, poi);
    this.updateAdjacentPOIs(poi);
    return poi;
  }

  /**
   * Get a POI by ID
   */
  getPOI(id: string): IPOI | undefined {
    return this.pois.get(id);
  }

  /**
   * Get all POIs
   */
  getAllPOIs(): IPOI[] {
    return Array.from(this.pois.values());
  }

  /**
   * Get POIs within the active region
   */
  getActivePOIs(): IPOI[] {
    return Array.from(this.pois.values()).filter(poi => 
      this.isInActiveRegion(poi.coordinates)
    );
  }

  /**
   * Set the active region center and radius
   */
  setActiveRegion(center: Coordinates, radius: number): void {
    this.activeRegion = { center, radius };
    this.updatePOIStates();
  }

  /**
   * Update POI states based on active region
   */
  private updatePOIStates(): void {
    for (const poi of this.pois.values()) {
      if (this.isInActiveRegion(poi.coordinates)) {
        poi.activate();
      } else {
        poi.deactivate();
      }
    }
  }

  /**
   * Check if coordinates are within the active region
   */
  private isInActiveRegion(coords: Coordinates): boolean {
    const distance = Math.sqrt(
      Math.pow(coords.x - this.activeRegion.center.x, 2) +
      Math.pow(coords.y - this.activeRegion.center.y, 2) +
      Math.pow(coords.z - this.activeRegion.center.z, 2)
    );
    return distance <= this.activeRegion.radius && coords.level === this.activeRegion.center.level;
  }

  /**
   * Update adjacent POIs for a given POI
   */
  private updateAdjacentPOIs(poi: IPOI): void {
    const adjacentPOIs: string[] = [];

    for (const otherPOI of this.pois.values()) {
      if (otherPOI.id === poi.id) continue;

      if (this.areAdjacent(poi.coordinates, otherPOI.coordinates)) {
        adjacentPOIs.push(otherPOI.id);
        if (!otherPOI.adjacentPOIs.includes(poi.id)) {
          otherPOI.adjacentPOIs.push(poi.id);
        }
      }
    }

    poi.adjacentPOIs = adjacentPOIs;
  }

  /**
   * Check if two sets of coordinates are adjacent
   */
  private areAdjacent(coords1: Coordinates, coords2: Coordinates): boolean {
    const maxDistance = 2; // Adjust based on your game's scale
    return (
      coords1.level === coords2.level &&
      Math.abs(coords1.x - coords2.x) <= maxDistance &&
      Math.abs(coords1.y - coords2.y) <= maxDistance &&
      Math.abs(coords1.z - coords2.z) <= maxDistance
    );
  }

  /**
   * Save POIs to storage
   */
  async save(): Promise<void> {
    const serializedPOIs = Array.from(this.pois.values()).map(poi => poi.serialize());
    // TODO: Implement actual storage mechanism (e.g., database, file system)
    console.log('Saving POIs:', serializedPOIs);
  }

  /**
   * Load POIs from storage
   */
  async load(): Promise<void> {
    // TODO: Implement actual storage mechanism
    const serializedPOIs: Record<string, unknown>[] = [];
    const loadedPOIs = POIFactory.fromSerializedArray(serializedPOIs);
    
    this.pois.clear();
    for (const poi of loadedPOIs) {
      this.pois.set(poi.id, poi);
    }
    
    // Update adjacent POIs after loading
    for (const poi of this.pois.values()) {
      this.updateAdjacentPOIs(poi);
    }
  }

  /**
   * Delete a POI by ID
   */
  deletePOI(id: string): boolean {
    const poi = this.pois.get(id);
    if (!poi) return false;

    // Remove this POI from adjacent POIs' lists
    for (const adjacentId of poi.adjacentPOIs) {
      const adjacentPOI = this.pois.get(adjacentId);
      if (adjacentPOI) {
        adjacentPOI.adjacentPOIs = adjacentPOI.adjacentPOIs.filter(id => id !== poi.id);
      }
    }

    return this.pois.delete(id);
  }
} 