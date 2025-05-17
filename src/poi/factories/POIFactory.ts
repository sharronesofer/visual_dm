import { v4 as uuidv4 } from 'uuid';
import {
  POIType,
  POISubtype,
  DungeonSubtype,
  ExplorationSubtype,
  SocialSubtype,
  Coordinates,
  ThematicElements
} from '../types/POITypes';
import { IPOI } from '../interfaces/IPOI';
import { DungeonPOI } from '../models/DungeonPOI';
import { ExplorationPOI } from '../models/ExplorationPOI';
import { SocialPOI } from '../models/SocialPOI';
import { BasePOI } from '../models/BasePOI';

/**
 * Factory class for creating and managing POI instances.
 * Implements the Factory Method pattern with support for:
 * - Type-specific POI creation
 * - Deserialization from storage
 * - Validation of POI configurations
 * - Runtime POI type registration
 * - Template caching
 */
export class POIFactory {
  private static instance: POIFactory;
  private customFactories: Map<string, (data: any) => IPOI>;
  private templateCache: Map<string, IPOI>;

  private constructor() {
    this.customFactories = new Map();
    this.templateCache = new Map();
  }

  /**
   * Get the singleton instance of POIFactory
   */
  public static getInstance(): POIFactory {
    if (!POIFactory.instance) {
      POIFactory.instance = new POIFactory();
    }
    return POIFactory.instance;
  }

  /**
   * Create a new POI instance based on type and subtype
   */
  public createPOI(type: POIType.DUNGEON, subType: DungeonSubtype, config?: any): IPOI;
  public createPOI(type: POIType.EXPLORATION, subType: ExplorationSubtype, config?: any): IPOI;
  public createPOI(type: POIType.SOCIAL, subType: SocialSubtype, config?: any): IPOI;
  public createPOI(type: POIType, subType: POISubtype, config?: any): IPOI;
  public createPOI(
    type: POIType,
    subType: any,
    config: any = {}
  ): IPOI {
    const cacheKey = this.getCacheKey(type, subType, config);

    // Check template cache first
    if (this.templateCache.has(cacheKey)) {
      return this.clonePOI(this.templateCache.get(cacheKey)!);
    }

    // Check for custom factory
    const customKey = `${type}:${subType}`;
    if (this.customFactories.has(customKey)) {
      return this.customFactories.get(customKey)!(config);
    }

    // Use built-in factories
    let poi: IPOI;
    switch (type) {
      case POIType.DUNGEON:
        if (!(Object.values(DungeonSubtype) as string[]).includes(subType as string)) {
          throw new Error(`Invalid DungeonSubtype: ${subType}`);
        }
        poi = new DungeonPOI(
          config.id || uuidv4(),
          config.name || 'Dungeon',
          subType as DungeonSubtype,
          config.coordinates || { x: 0, y: 0, z: 0, level: 0 },
          config.thematicElements || { biome: '', climate: '', era: '', culture: '', dangerLevel: 1, lighting: 'dim', themes: [] }
        ) as unknown as IPOI;
        break;
      case POIType.EXPLORATION:
        if (!(Object.values(ExplorationSubtype) as string[]).includes(subType as string)) {
          throw new Error(`Invalid ExplorationSubtype: ${subType}`);
        }
        poi = new ExplorationPOI(
          config.id || uuidv4(),
          config.name || 'Exploration',
          subType as ExplorationSubtype,
          config.coordinates || { x: 0, y: 0, z: 0, level: 0 },
          config.thematicElements || { biome: '', climate: '', era: '', culture: '', dangerLevel: 1, lighting: 'dim', themes: [] }
        ) as unknown as IPOI;
        break;
      case POIType.SOCIAL:
        if (!(Object.values(SocialSubtype) as string[]).includes(subType as string)) {
          throw new Error(`Invalid SocialSubtype: ${subType}`);
        }
        poi = new SocialPOI(
          config.id || uuidv4(),
          config.name || 'Social',
          subType as SocialSubtype,
          config.coordinates || { x: 0, y: 0, z: 0, level: 0 },
          config.thematicElements || { biome: '', climate: '', era: '', culture: '', dangerLevel: 1, lighting: 'dim', themes: [] }
        ) as unknown as IPOI;
        break;
      default:
        throw new Error(`Unsupported POI type: ${type}`);
    }

    // Cache the template if appropriate
    if (this.shouldCacheTemplate(config)) {
      this.templateCache.set(cacheKey, this.clonePOI(poi));
    }

    return poi;
  }

  /**
   * Register a custom factory function for a specific POI type/subtype
   */
  public registerCustomFactory(
    type: POIType,
    subType: POISubtype,
    factory: (data: any) => IPOI
  ): void {
    const key = `${type}:${subType}`;
    this.customFactories.set(key, factory);
  }

  /**
   * Deserialize a POI from stored data
   */
  public deserializePOI(data: any): IPOI {
    if (!data.type || !data.subType) {
      throw new Error('Invalid POI data: missing type or subType');
    }

    // Validate the data structure
    this.validatePOIData(data);

    // Create POI instance
    const poi = this.createPOI(data.type as POIType, data.subType as POISubtype);

    // Load the data into the POI
    if (poi instanceof BasePOI) {
      poi.deserialize(data);
    } else {
      throw new Error('POI instance does not support deserialization');
    }

    return poi;
  }

  /**
   * Clear the template cache
   */
  public clearCache(): void {
    this.templateCache.clear();
  }

  /**
   * Remove a specific template from cache
   */
  public removeFromCache(type: POIType, subType: POISubtype, config: any = {}): void {
    const cacheKey = this.getCacheKey(type, subType, config);
    this.templateCache.delete(cacheKey);
  }

  /**
   * Validate POI configuration data
   */
  private validatePOIData(data: any): void {
    // Basic structure validation
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid POI data: must be an object');
    }

    // Type validation
    if (!Object.values(POIType).includes(data.type)) {
      throw new Error(`Invalid POI type: ${data.type}`);
    }

    // SubType validation based on type
    let validSubTypes: string[] = [];
    switch (data.type) {
      case POIType.DUNGEON:
        validSubTypes = Object.values(DungeonSubtype);
        break;
      case POIType.EXPLORATION:
        validSubTypes = Object.values(ExplorationSubtype);
        break;
      case POIType.SOCIAL:
        validSubTypes = Object.values(SocialSubtype);
        break;
    }

    if (!validSubTypes.includes(data.subType)) {
      throw new Error(`Invalid POI subType ${data.subType} for type ${data.type}`);
    }

    // Additional type-specific validation
    switch (data.type) {
      case POIType.DUNGEON:
        this.validateDungeonPOIData(data);
        break;
      case POIType.EXPLORATION:
        this.validateExplorationPOIData(data);
        break;
      case POIType.SOCIAL:
        this.validateSocialPOIData(data);
        break;
    }
  }

  /**
   * Type-specific validation for Dungeon POIs
   */
  private validateDungeonPOIData(data: any): void {
    // Add dungeon-specific validation logic
    if (data.dangerLevel && (typeof data.dangerLevel !== 'number' || data.dangerLevel < 0)) {
      throw new Error('Invalid dungeon danger level');
    }
  }

  /**
   * Type-specific validation for Exploration POIs
   */
  private validateExplorationPOIData(data: any): void {
    // Add exploration-specific validation logic
    if (data.resourceNodes && !Array.isArray(data.resourceNodes)) {
      throw new Error('Invalid resource nodes data');
    }
  }

  /**
   * Type-specific validation for Social POIs
   */
  private validateSocialPOIData(data: any): void {
    // Add social-specific validation logic
    if (data.npcIds && !Array.isArray(data.npcIds)) {
      throw new Error('Invalid NPC IDs data');
    }
  }

  /**
   * Generate a cache key for a POI template
   */
  private getCacheKey(type: POIType, subType: POISubtype, config: any): string {
    return `${type}:${subType}:${JSON.stringify(config)}`;
  }

  /**
   * Determine if a POI configuration should be cached as a template
   */
  private shouldCacheTemplate(config: any): boolean {
    // Add logic to determine if this configuration should be cached
    // For example, cache only configurations without runtime-specific data
    return !config.id && !config.coordinates;
  }

  /**
   * Create a deep clone of a POI instance
   */
  private clonePOI(poi: IPOI): IPOI {
    if (poi instanceof BasePOI) {
      const serialized = poi.serialize();
      return this.deserializePOI(serialized);
    }
    throw new Error('POI instance does not support cloning');
  }
} 