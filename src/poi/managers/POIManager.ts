import { TypedEventEmitter } from '../../utils/TypedEventEmitter';
import { v4 as uuidv4 } from 'uuid';
import { IPOI } from '../interfaces/IPOI';
import { POIFactory } from '../factories/POIFactory';
import { POIType, POISubtype, Coordinates } from '../types/POITypes';
import { POIEvents } from '../types/POIEvents';
import { EventBus } from '../../core/interfaces/types/events';

interface SpatialQueryOptions {
  center: Coordinates;
  radius: number;
  type?: POIType;
  subType?: POISubtype;
  maxResults?: number;
}

interface POIRelationship {
  parentId: string | null;
  childIds: string[];
  dependencies: string[];
  dependents: string[];
}

/**
 * Singleton manager class for handling POI lifecycle and relationships.
 * Responsible for:
 * - POI lifecycle management (creation, activation, deactivation, destruction)
 * - POI persistence (save/load state)
 * - Relationship tracking (parent-child, dependencies)
 * - Spatial queries and batching operations
 */
export class POIManager extends TypedEventEmitter<POIEvents> {
  private static instance: POIManager;
  private activePOIs: Map<string, IPOI>;
  private relationships: Map<string, POIRelationship>;
  private spatialIndex: Map<string, Coordinates>;
  private factory: POIFactory;
  private deregisteredPOIs: Set<string> = new Set();
  private lastCaptor: Map<string, string> = new Map();

  private constructor() {
    super();
    this.activePOIs = new Map();
    this.relationships = new Map();
    this.spatialIndex = new Map();
    this.factory = POIFactory.getInstance();
  }

  /**
   * Get the singleton instance of POIManager
   */
  public static getInstance(): POIManager {
    if (!POIManager.instance) {
      POIManager.instance = new POIManager();
    }
    return POIManager.instance;
  }

  /**
   * Create and register a new POI
   */
  public createPOI(
    type: POIType,
    subType: POISubtype,
    config: any = {}
  ): IPOI {
    const poi = this.factory.createPOI(type, subType, config);

    try {
      if (!poi.validate()) {
        throw new Error(`Invalid POI configuration for type ${type} and subtype ${subType}`);
      }

      this.emit('poi:created', { poi });
      this.registerPOI(poi);
      return poi;
    } catch (error) {
      this.emit('poi:error', {
        type: 'validation',
        poiId: poi.id,
        error: error instanceof Error ? error : new Error('Unknown error during POI creation')
      });
      throw error;
    }
  }

  /**
   * Register a POI with the manager
   * @param poi - The POI to register
   */
  public registerPOI(poi: IPOI): void {
    try {
      if (this.activePOIs.has(poi.id)) {
        throw new Error(`POI with ID ${poi.id} is already registered`);
      }

      this.activePOIs.set(poi.id, poi);
      this.spatialIndex.set(poi.id, poi.getPosition());
      this.relationships.set(poi.id, {
        parentId: null,
        childIds: [],
        dependencies: [],
        dependents: []
      });

      this.emit('poi:registered', { poi });
    } catch (error) {
      this.emit('poi:error', {
        type: 'registration',
        poiId: poi.id,
        error: error instanceof Error ? error : new Error('Unknown error during POI registration')
      });
      throw error;
    }
  }

  /**
   * Retrieve a POI by ID
   * @param poiId - The ID of the POI
   * @returns The POI instance or undefined
   */
  public getPOI(poiId: string): IPOI | undefined {
    return this.activePOIs.get(poiId);
  }

  /**
   * Capture a POI (ownership/control change)
   * Idempotent: Only emits if captor is different from current owner.
   * Atomic: All state changes are performed before event emission.
   * @param poiId - The ID of the POI
   * @param captorId - The ID of the new owner
   * @param previousOwnerId - The ID of the previous owner (optional)
   * @returns True if capture event was emitted, false otherwise
   */
  public capturePOI(poiId: string, captorId: string, previousOwnerId?: string): boolean {
    try {
      const poi = this.activePOIs.get(poiId);
      if (!poi) return false;
      if (this.lastCaptor.get(poiId) === captorId) return false;
      this.lastCaptor.set(poiId, captorId);
      // Ownership logic (update properties, etc.) can be added here
      // Idempotency: Only emit if captor is different from current owner
      if ((poi as any).ownerId && (poi as any).ownerId === captorId) {
        return false;
      }
      (poi as any).ownerId = captorId;
      // Emit capture event (versioned)
      this.emit('poi:captured', {
        poiId,
        poi,
        captorId,
        previousOwnerId,
        timestamp: Date.now(),
        version: 1
      });
      return true;
    } catch (error) {
      this.emit('poi:error', {
        type: 'capture',
        poiId,
        error: error instanceof Error ? error : new Error('Unknown error during POI capture')
      });
      throw error;
    }
  }

  /**
   * Deregister (destroy) a POI
   * Idempotent: Only emits if POI is still present.
   * Atomic: All state changes are performed before event emission.
   * @param poiId - The ID of the POI
   * @param reason - Reason for destruction
   * @returns True if destroyed event was emitted, false otherwise
   */
  public deregisterPOI(poiId: string, reason: string = 'removed'): boolean {
    try {
      if (this.deregisteredPOIs.has(poiId)) return false;
      const poi = this.activePOIs.get(poiId);
      if (!poi) return false;

      // Clean up relationships
      const relationship = this.relationships.get(poiId);
      if (relationship) {
        // Remove from parent's children list
        if (relationship.parentId) {
          const parentRel = this.relationships.get(relationship.parentId);
          if (parentRel) {
            parentRel.childIds = parentRel.childIds.filter(id => id !== poiId);
            this.emit('poi:parentRemoved', {
              childId: poiId,
              previousParentId: relationship.parentId
            });
          }
        }

        // Update dependencies
        for (const depId of relationship.dependencies) {
          const depRel = this.relationships.get(depId);
          if (depRel) {
            depRel.dependents = depRel.dependents.filter(id => id !== poiId);
            this.emit('poi:dependencyRemoved', {
              poiId,
              dependencyId: depId
            });
          }
        }

        // Update dependents
        for (const depId of relationship.dependents) {
          const depRel = this.relationships.get(depId);
          if (depRel) {
            depRel.dependencies = depRel.dependencies.filter(id => id !== poiId);
          }
        }
      }

      this.activePOIs.delete(poiId);
      this.spatialIndex.delete(poiId);
      this.relationships.delete(poiId);

      this.deregisteredPOIs.add(poiId);
      this.emit('poi:deregistered', { poiId });
      // Emit destruction event (versioned) only if POI was present and not already deregistered
      this.emit('poi:destroyed', {
        poiId,
        poi,
        reason,
        timestamp: Date.now(),
        version: 1
      });
      return true;
    } catch (error) {
      this.emit('poi:error', {
        type: 'deregistration',
        poiId,
        error: error instanceof Error ? error : new Error('Unknown error during POI deregistration')
      });
      throw error;
    }
  }

  /**
   * Find POIs within a radius of a point
   */
  public findPOIsInRadius(options: SpatialQueryOptions): IPOI[] {
    try {
      const results: IPOI[] = [];
      const maxResults = options.maxResults || Number.MAX_SAFE_INTEGER;

      for (const [id, coords] of this.spatialIndex.entries()) {
        const distance = this.calculateDistance(options.center, coords);
        if (distance <= options.radius) {
          const poi = this.activePOIs.get(id);
          if (poi) {
            if (options.type && poi.type !== options.type) continue;
            if (options.subType && poi.subtype !== options.subType) continue;
            results.push(poi);
            if (results.length >= maxResults) break;
          }
        }
      }

      this.emit('poi:searched', {
        center: options.center,
        radius: options.radius,
        type: options.type,
        subType: options.subType,
        results
      });

      return results;
    } catch (error) {
      this.emit('poi:error', {
        type: 'query',
        error: error instanceof Error ? error : new Error('Unknown error during spatial query')
      });
      throw error;
    }
  }

  /**
   * Handle POI modification events
   */
  public onPOIModified(poiId: string): void {
    const poi = this.activePOIs.get(poiId);
    if (!poi) return;

    // Update last modified timestamp
    poi.stateTracking.lastModified = new Date();

    // Emit modification event
    this.emit('poi:modified', { poiId, poi });

    // Save changes
    this.savePOIState(poiId);
  }

  /**
   * Save POI state to persistent storage
   */
  private savePOIState(poiId: string): void {
    const poi = this.activePOIs.get(poiId);
    if (!poi) return;

    // Serialize POI state
    const serializedState = poi.serialize();

    // Emit save event with serialized state
    this.emit('poi:stateSaved', { poiId, state: serializedState });
  }

  /**
   * Update POI position and emit relevant events
   */
  public updatePOIPosition(poiId: string, newPosition: Coordinates): void {
    const poi = this.activePOIs.get(poiId);
    if (!poi) return;

    const oldPosition = { ...poi.getPosition() };
    poi.setPosition(newPosition);
    this.spatialIndex.set(poiId, newPosition);

    this.emit('poi:moved', {
      poiId,
      oldPosition,
      newPosition
    });

    this.onPOIModified(poiId);
  }

  /**
   * Set parent-child relationship between POIs
   */
  public setParentPOI(childId: string, parentId: string): void {
    const childRel = this.relationships.get(childId);
    const parentRel = this.relationships.get(parentId);

    if (!childRel || !parentRel) return;

    // Remove from previous parent if exists
    if (childRel.parentId) {
      const prevParentRel = this.relationships.get(childRel.parentId);
      if (prevParentRel) {
        prevParentRel.childIds = prevParentRel.childIds.filter(id => id !== childId);
        this.emit('poi:parentRemoved', {
          childId,
          previousParentId: childRel.parentId
        });
      }
    }

    // Set new parent
    childRel.parentId = parentId;
    parentRel.childIds.push(childId);

    this.emit('poi:parentSet', {
      childId,
      parentId
    });
  }

  /**
   * Add a dependency relationship between POIs
   */
  public addDependency(poiId: string, dependencyId: string): void {
    const poiRel = this.relationships.get(poiId);
    const depRel = this.relationships.get(dependencyId);

    if (!poiRel || !depRel) return;

    if (!poiRel.dependencies.includes(dependencyId)) {
      poiRel.dependencies.push(dependencyId);
      depRel.dependents.push(poiId);

      this.emit('poi:dependencyAdded', {
        poiId,
        dependencyId
      });
    }
  }

  /**
   * Remove a dependency relationship between POIs
   */
  public removeDependency(poiId: string, dependencyId: string): void {
    const poiRel = this.relationships.get(poiId);
    const depRel = this.relationships.get(dependencyId);

    if (!poiRel || !depRel) return;

    poiRel.dependencies = poiRel.dependencies.filter(id => id !== dependencyId);
    depRel.dependents = depRel.dependents.filter(id => id !== poiId);

    this.emit('poi:dependencyRemoved', {
      poiId,
      dependencyId
    });
  }

  /**
   * Add a POI to the active POIs map
   */
  public addPOI(poi: IPOI): void {
    this.activePOIs.set(poi.id, poi);
  }

  /**
   * Get all active POIs
   */
  public getAllPOIs(): IPOI[] {
    return Array.from(this.activePOIs.values());
  }

  /**
   * Get POIs by type
   */
  public getPOIsByType(type: POIType): IPOI[] {
    return this.getAllPOIs().filter(poi => poi.type === type);
  }

  /**
   * Get POIs by subtype
   */
  public getPOIsBySubtype(subtype: POISubtype): IPOI[] {
    return this.getAllPOIs().filter(poi => poi.subtype === subtype);
  }

  private calculateDistance(a: Coordinates, b: Coordinates): number {
    const dx = a.x - b.x;
    const dy = a.y - b.y;
    const dz = a.z - b.z;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }

  /**
   * Override emit to also forward POI events to the global EventBus
   */
  public emit<E extends keyof POIEvents>(event: E, payload: POIEvents[E]): boolean {
    // Emit locally (for POIManager listeners)
    const localResult = super.emit(event, payload);
    // Forward to global EventBus (for cross-system integration)
    EventBus.getInstance().emit(event as string, payload as any);
    return localResult;
  }
} 