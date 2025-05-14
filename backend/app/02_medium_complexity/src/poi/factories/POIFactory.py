from typing import Any, List



  POIType,
  POISubtype,
  DungeonSubtype,
  ExplorationSubtype,
  SocialSubtype,
  Coordinates,
  ThematicElements
} from '../types/POITypes'
/**
 * Factory class for creating and managing POI instances.
 * Implements the Factory Method pattern with support for:
 * - Type-specific POI creation
 * - Deserialization from storage
 * - Validation of POI configurations
 * - Runtime POI type registration
 * - Template caching
 */
class POIFactory {
  private static instance: \'POIFactory\'
  private customFactories: Map<string, (data: Any) => IPOI>
  private templateCache: Map<string, IPOI>
  private constructor() {
    this.customFactories = new Map()
    this.templateCache = new Map()
  }
  /**
   * Get the singleton instance of POIFactory
   */
  public static getInstance(): \'POIFactory\' {
    if (!POIFactory.instance) {
      POIFactory.instance = new POIFactory()
    }
    return POIFactory.instance
  }
  /**
   * Create a new POI instance based on type and subtype
   */
  public createPOI(type: POIType, subType: POISubtype, config: Any = {}): IPOI {
    const cacheKey = this.getCacheKey(type, subType, config)
    if (this.templateCache.has(cacheKey)) {
      return this.clonePOI(this.templateCache.get(cacheKey)!)
    }
    const customKey = `${type}:${subType}`
    if (this.customFactories.has(customKey)) {
      return this.customFactories.get(customKey)!(config)
    }
    let poi: IPOI
    switch (type) {
      case POIType.DUNGEON:
        if (!Object.values(DungeonSubtype).includes(subType as DungeonSubtype)) {
          throw new Error(`Invalid dungeon subtype: ${subType}`)
        }
        poi = new DungeonPOI(subType as DungeonSubtype, config)
        break
      case POIType.EXPLORATION:
        if (!Object.values(ExplorationSubtype).includes(subType as ExplorationSubtype)) {
          throw new Error(`Invalid exploration subtype: ${subType}`)
        }
        poi = new ExplorationPOI(subType as ExplorationSubtype, config)
        break
      case POIType.SOCIAL:
        if (!Object.values(SocialSubtype).includes(subType as SocialSubtype)) {
          throw new Error(`Invalid social subtype: ${subType}`)
        }
        poi = new SocialPOI(subType as SocialSubtype, config)
        break
      default:
        throw new Error(`Unsupported POI type: ${type}`)
    }
    if (this.shouldCacheTemplate(config)) {
      this.templateCache.set(cacheKey, this.clonePOI(poi))
    }
    return poi
  }
  /**
   * Register a custom factory function for a specific POI type/subtype
   */
  public registerCustomFactory(
    type: POIType,
    subType: POISubtype,
    factory: (data: Any) => IPOI
  ): void {
    const key = `${type}:${subType}`
    this.customFactories.set(key, factory)
  }
  /**
   * Deserialize a POI from stored data
   */
  public deserializePOI(data: Any): IPOI {
    if (!data.type || !data.subType) {
      throw new Error('Invalid POI data: missing type or subType')
    }
    this.validatePOIData(data)
    const poi = this.createPOI(data.type as POIType, data.subType as POISubtype)
    if (poi instanceof BasePOI) {
      poi.deserialize(data)
    } else {
      throw new Error('POI instance does not support deserialization')
    }
    return poi
  }
  /**
   * Clear the template cache
   */
  public clearCache(): void {
    this.templateCache.clear()
  }
  /**
   * Remove a specific template from cache
   */
  public removeFromCache(type: POIType, subType: POISubtype, config: Any = {}): void {
    const cacheKey = this.getCacheKey(type, subType, config)
    this.templateCache.delete(cacheKey)
  }
  /**
   * Validate POI configuration data
   */
  private validatePOIData(data: Any): void {
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid POI data: must be an object')
    }
    if (!Object.values(POIType).includes(data.type)) {
      throw new Error(`Invalid POI type: ${data.type}`)
    }
    let validSubTypes: List[string] = []
    switch (data.type) {
      case POIType.DUNGEON:
        validSubTypes = Object.values(DungeonSubtype)
        break
      case POIType.EXPLORATION:
        validSubTypes = Object.values(ExplorationSubtype)
        break
      case POIType.SOCIAL:
        validSubTypes = Object.values(SocialSubtype)
        break
    }
    if (!validSubTypes.includes(data.subType)) {
      throw new Error(`Invalid POI subType ${data.subType} for type ${data.type}`)
    }
    switch (data.type) {
      case POIType.DUNGEON:
        this.validateDungeonPOIData(data)
        break
      case POIType.EXPLORATION:
        this.validateExplorationPOIData(data)
        break
      case POIType.SOCIAL:
        this.validateSocialPOIData(data)
        break
    }
  }
  /**
   * Type-specific validation for Dungeon POIs
   */
  private validateDungeonPOIData(data: Any): void {
    if (data.dangerLevel && (typeof data.dangerLevel !== 'number' || data.dangerLevel < 0)) {
      throw new Error('Invalid dungeon danger level')
    }
  }
  /**
   * Type-specific validation for Exploration POIs
   */
  private validateExplorationPOIData(data: Any): void {
    if (data.resourceNodes && !Array.isArray(data.resourceNodes)) {
      throw new Error('Invalid resource nodes data')
    }
  }
  /**
   * Type-specific validation for Social POIs
   */
  private validateSocialPOIData(data: Any): void {
    if (data.npcIds && !Array.isArray(data.npcIds)) {
      throw new Error('Invalid NPC IDs data')
    }
  }
  /**
   * Generate a cache key for a POI template
   */
  private getCacheKey(type: POIType, subType: POISubtype, config: Any): str {
    return `${type}:${subType}:${JSON.stringify(config)}`
  }
  /**
   * Determine if a POI configuration should be cached as a template
   */
  private shouldCacheTemplate(config: Any): bool {
    return !config.id && !config.coordinates
  }
  /**
   * Create a deep clone of a POI instance
   */
  private clonePOI(poi: IPOI): IPOI {
    if (poi instanceof BasePOI) {
      const serialized = poi.serialize()
      return this.deserializePOI(serialized)
    }
    throw new Error('POI instance does not support cloning')
  }
} 