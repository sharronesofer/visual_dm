from typing import Any, List, Union



class SpatialQueryOptions:
    center: Coordinates
    radius: float
    type?: POIType
    subType?: POISubtype
    maxResults?: float
class POIRelationship:
    parentId: Union[str, None]
    childIds: List[str]
    dependencies: List[str]
    dependents: List[str]
/**
 * Singleton manager class for handling POI lifecycle and relationships.
 * Responsible for:
 * - POI lifecycle management (creation, activation, deactivation, destruction)
 * - POI persistence (save/load state)
 * - Relationship tracking (parent-child, dependencies)
 * - Spatial queries and batching operations
 */
class POIManager extends TypedEventEmitter<POIEvents> {
  private static instance: \'POIManager\'
  private activePOIs: Map<string, IPOI>
  private relationships: Map<string, POIRelationship>
  private spatialIndex: Map<string, Coordinates>
  private factory: POIFactory
  private constructor() {
    super()
    this.activePOIs = new Map()
    this.relationships = new Map()
    this.spatialIndex = new Map()
    this.factory = POIFactory.getInstance()
  }
  /**
   * Get the singleton instance of POIManager
   */
  public static getInstance(): \'POIManager\' {
    if (!POIManager.instance) {
      POIManager.instance = new POIManager()
    }
    return POIManager.instance
  }
  /**
   * Create and register a new POI
   */
  public createPOI(
    type: POIType,
    subType: POISubtype,
    config: Any = {}
  ): IPOI {
    const poi = this.factory.createPOI(type, subType, config)
    try {
      if (!poi.validate()) {
        throw new Error(`Invalid POI configuration for type ${type} and subtype ${subType}`)
      }
      this.emit('poi:created', { poi })
      this.registerPOI(poi)
      return poi
    } catch (error) {
      this.emit('poi:error', { 
        type: 'validation',
        poiId: poi.id,
        error: error instanceof Error ? error : new Error('Unknown error during POI creation')
      })
      throw error
    }
  }
  /**
   * Register an existing POI with the manager
   */
  public registerPOI(poi: IPOI): void {
    try {
      if (this.activePOIs.has(poi.id)) {
        throw new Error(`POI with ID ${poi.id} is already registered`)
      }
      this.activePOIs.set(poi.id, poi)
      this.spatialIndex.set(poi.id, poi.getPosition())
      this.relationships.set(poi.id, {
        parentId: null,
        childIds: [],
        dependencies: [],
        dependents: []
      })
      this.emit('poi:registered', { poi })
    } catch (error) {
      this.emit('poi:error', {
        type: 'registration',
        poiId: poi.id,
        error: error instanceof Error ? error : new Error('Unknown error during POI registration')
      })
      throw error
    }
  }
  /**
   * Remove a POI from the manager
   */
  public deregisterPOI(poiId: str): bool {
    try {
      const poi = this.activePOIs.get(poiId)
      if (!poi) return false
      const relationship = this.relationships.get(poiId)
      if (relationship) {
        if (relationship.parentId) {
          const parentRel = this.relationships.get(relationship.parentId)
          if (parentRel) {
            parentRel.childIds = parentRel.childIds.filter(id => id !== poiId)
            this.emit('poi:parentRemoved', { 
              childId: poiId,
              previousParentId: relationship.parentId
            })
          }
        }
        for (const depId of relationship.dependencies) {
          const depRel = this.relationships.get(depId)
          if (depRel) {
            depRel.dependents = depRel.dependents.filter(id => id !== poiId)
            this.emit('poi:dependencyRemoved', {
              poiId,
              dependencyId: depId
            })
          }
        }
        for (const depId of relationship.dependents) {
          const depRel = this.relationships.get(depId)
          if (depRel) {
            depRel.dependencies = depRel.dependencies.filter(id => id !== poiId)
          }
        }
      }
      this.activePOIs.delete(poiId)
      this.spatialIndex.delete(poiId)
      this.relationships.delete(poiId)
      this.emit('poi:deregistered', { poiId })
      return true
    } catch (error) {
      this.emit('poi:error', {
        type: 'deregistration',
        poiId,
        error: error instanceof Error ? error : new Error('Unknown error during POI deregistration')
      })
      throw error
    }
  }
  /**
   * Find POIs within a radius of a point
   */
  public findPOIsInRadius(options: SpatialQueryOptions): IPOI[] {
    try {
      const results: List[IPOI] = []
      const maxResults = options.maxResults || Number.MAX_SAFE_INTEGER
      for (const [id, coords] of this.spatialIndex.entries()) {
        const distance = this.calculateDistance(options.center, coords)
        if (distance <= options.radius) {
          const poi = this.activePOIs.get(id)
          if (poi) {
            if (options.type && poi.type !== options.type) continue
            if (options.subType && poi.subtype !== options.subType) continue
            results.push(poi)
            if (results.length >= maxResults) break
          }
        }
      }
      this.emit('poi:searched', {
        center: options.center,
        radius: options.radius,
        type: options.type,
        subType: options.subType,
        results
      })
      return results
    } catch (error) {
      this.emit('poi:error', {
        type: 'query',
        error: error instanceof Error ? error : new Error('Unknown error during spatial query')
      })
      throw error
    }
  }
  /**
   * Handle POI modification events
   */
  public onPOIModified(poiId: str): void {
    const poi = this.activePOIs.get(poiId)
    if (!poi) return
    poi.stateTracking.lastModified = new Date()
    this.emit('poi:modified', { poiId, poi })
    this.savePOIState(poiId)
  }
  /**
   * Save POI state to persistent storage
   */
  private savePOIState(poiId: str): void {
    const poi = this.activePOIs.get(poiId)
    if (!poi) return
    const serializedState = poi.serialize()
    this.emit('poi:stateSaved', { poiId, state: serializedState })
  }
  /**
   * Update POI position and emit relevant events
   */
  public updatePOIPosition(poiId: str, newPosition: Coordinates): void {
    const poi = this.activePOIs.get(poiId)
    if (!poi) return
    const oldPosition = { ...poi.getPosition() }
    poi.setPosition(newPosition)
    this.spatialIndex.set(poiId, newPosition)
    this.emit('poi:moved', {
      poiId,
      oldPosition,
      newPosition
    })
    this.onPOIModified(poiId)
  }
  /**
   * Set parent-child relationship between POIs
   */
  public setParentPOI(childId: str, parentId: str): void {
    const childRel = this.relationships.get(childId)
    const parentRel = this.relationships.get(parentId)
    if (!childRel || !parentRel) return
    if (childRel.parentId) {
      const prevParentRel = this.relationships.get(childRel.parentId)
      if (prevParentRel) {
        prevParentRel.childIds = prevParentRel.childIds.filter(id => id !== childId)
        this.emit('poi:parentRemoved', {
          childId,
          previousParentId: childRel.parentId
        })
      }
    }
    childRel.parentId = parentId
    parentRel.childIds.push(childId)
    this.emit('poi:parentSet', {
      childId,
      parentId
    })
  }
  /**
   * Add a dependency relationship between POIs
   */
  public addDependency(poiId: str, dependencyId: str): void {
    const poiRel = this.relationships.get(poiId)
    const depRel = this.relationships.get(dependencyId)
    if (!poiRel || !depRel) return
    if (!poiRel.dependencies.includes(dependencyId)) {
      poiRel.dependencies.push(dependencyId)
      depRel.dependents.push(poiId)
      this.emit('poi:dependencyAdded', {
        poiId,
        dependencyId
      })
    }
  }
  /**
   * Remove a dependency relationship between POIs
   */
  public removeDependency(poiId: str, dependencyId: str): void {
    const poiRel = this.relationships.get(poiId)
    const depRel = this.relationships.get(dependencyId)
    if (!poiRel || !depRel) return
    poiRel.dependencies = poiRel.dependencies.filter(id => id !== dependencyId)
    depRel.dependents = depRel.dependents.filter(id => id !== poiId)
    this.emit('poi:dependencyRemoved', {
      poiId,
      dependencyId
    })
  }
  /**
   * Add a POI to the active POIs map
   */
  public addPOI(poi: IPOI): void {
    this.activePOIs.set(poi.id, poi)
  }
  /**
   * Get all active POIs
   */
  public getAllPOIs(): IPOI[] {
    return Array.from(this.activePOIs.values())
  }
  /**
   * Get POIs by type
   */
  public getPOIsByType(type: POIType): IPOI[] {
    return this.getAllPOIs().filter(poi => poi.type === type)
  }
  /**
   * Get POIs by subtype
   */
  public getPOIsBySubtype(subtype: POISubtype): IPOI[] {
    return this.getAllPOIs().filter(poi => poi.subtype === subtype)
  }
  private calculateDistance(a: Coordinates, b: Coordinates): float {
    const dx = a.x - b.x
    const dy = a.y - b.y
    const dz = a.z - b.z
    return Math.sqrt(dx * dx + dy * dy + dz * dz)
  }
} 