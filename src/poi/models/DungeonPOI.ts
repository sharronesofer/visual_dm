import { BasePOI } from './BasePOI';
import { POIType, DungeonSubtype, Coordinates, ThematicElements } from '../types/POITypes';

// Re-export the DungeonSubtype enum
export { DungeonSubtype };

interface DungeonFeature {
  id: string;
  type: 'trap' | 'treasure' | 'monster_spawn' | 'puzzle';
  properties: {
    difficulty: number;
    isActive: boolean;
    isDiscovered: boolean;
    rewards?: string[];
    [key: string]: unknown;
  };
}

/**
 * Specialized POI class for dungeon-type locations
 */
export class DungeonPOI extends BasePOI {
  private dungeonFeatures: Map<string, DungeonFeature>;
  private difficultyRating: number;
  private treasureValue: number;

  constructor(
    id: string,
    name: string,
    subtype: DungeonSubtype,
    coordinates: Coordinates,
    thematicElements: ThematicElements
  ) {
    super(id, name, POIType.DUNGEON, subtype, coordinates, thematicElements);
    
    // Initialize dungeon-specific properties
    this.dungeonFeatures = new Map<string, DungeonFeature>();
    this.difficultyRating = this.calculateInitialDifficulty();
    this.treasureValue = 0;
    
    // Set dungeon-specific default values
    this.boundingBox = { width: 2, height: 2, depth: 2 }; // Dungeons are typically larger
    this.canExpand = true; // Dungeons can always expand
    
    // Add default expansion rules for dungeons
    this.expansionRules = [
      {
        direction: 'down',
        conditions: ['!water_level', '!lava_level'],
        probability: 0.7
      },
      {
        direction: 'north',
        conditions: ['!blocked'],
        probability: 0.5
      },
      {
        direction: 'south',
        conditions: ['!blocked'],
        probability: 0.5
      },
      {
        direction: 'east',
        conditions: ['!blocked'],
        probability: 0.5
      },
      {
        direction: 'west',
        conditions: ['!blocked'],
        probability: 0.5
      }
    ];

    // Initialize based on subtype
    this.initializeBySubtype(subtype);
  }

  // Dungeon-specific feature management
  addFeature(feature: DungeonFeature): void {
    this.dungeonFeatures.set(feature.id, feature);
    this.features.push({
      id: feature.id,
      type: feature.type,
      properties: feature.properties
    });
    this.recalculateDifficulty();
    this.trackChange('modification', `Added ${feature.type} feature: ${feature.id}`);
  }

  removeFeature(featureId: string): boolean {
    const removed = this.dungeonFeatures.delete(featureId);
    if (removed) {
      this.features = this.features.filter(f => f.id !== featureId);
      this.recalculateDifficulty();
      this.trackChange('modification', `Removed feature: ${featureId}`);
    }
    return removed;
  }

  getFeature(featureId: string): DungeonFeature | undefined {
    return this.dungeonFeatures.get(featureId);
  }

  // Dungeon state management
  activateFeature(featureId: string): boolean {
    const feature = this.dungeonFeatures.get(featureId);
    if (feature) {
      feature.properties.isActive = true;
      this.trackChange('modification', `Activated feature: ${featureId}`);
      return true;
    }
    return false;
  }

  deactivateFeature(featureId: string): boolean {
    const feature = this.dungeonFeatures.get(featureId);
    if (feature) {
      feature.properties.isActive = false;
      this.trackChange('modification', `Deactivated feature: ${featureId}`);
      return true;
    }
    return false;
  }

  discoverFeature(featureId: string): boolean {
    const feature = this.dungeonFeatures.get(featureId);
    if (feature && !feature.properties.isDiscovered) {
      feature.properties.isDiscovered = true;
      this.trackChange('modification', `Discovered feature: ${featureId}`);
      return true;
    }
    return false;
  }

  // Dungeon metrics
  getDifficultyRating(): number {
    return this.difficultyRating;
  }

  getTreasureValue(): number {
    return this.treasureValue;
  }

  // Override serialize to include dungeon-specific properties
  serialize(): Record<string, unknown> {
    return {
      ...super.serialize(),
      dungeonFeatures: Array.from(this.dungeonFeatures.entries()),
      difficultyRating: this.difficultyRating,
      treasureValue: this.treasureValue
    };
  }

  // Override deserialize to handle dungeon-specific properties
  deserialize(data: Record<string, unknown>): void {
    super.deserialize(data);
    
    if (Array.isArray(data.dungeonFeatures)) {
      this.dungeonFeatures = new Map(data.dungeonFeatures);
    }
    
    if (typeof data.difficultyRating === 'number') {
      this.difficultyRating = data.difficultyRating;
    }
    
    if (typeof data.treasureValue === 'number') {
      this.treasureValue = data.treasureValue;
    }
  }

  // Override validateThematicCoherence to add dungeon-specific validation
  validateThematicCoherence(): boolean {
    return super.validateThematicCoherence() && this.validateDungeonTheme();
  }

  // Private helper methods
  private validateDungeonTheme(): boolean {
    // Dungeons should have appropriate danger level and lighting
    return (
      this.thematicElements.dangerLevel >= 3 && // Dungeons should be at least moderately dangerous
      this.thematicElements.lighting !== 'bright' && // Dungeons shouldn't be brightly lit
      this.validateDungeonFeatures()
    );
  }

  private validateDungeonFeatures(): boolean {
    // Validate that all features are properly configured
    for (const feature of this.dungeonFeatures.values()) {
      if (
        typeof feature.properties.difficulty !== 'number' ||
        typeof feature.properties.isActive !== 'boolean' ||
        typeof feature.properties.isDiscovered !== 'boolean'
      ) {
        return false;
      }
    }
    return true;
  }

  private calculateInitialDifficulty(): number {
    // Base difficulty on thematic elements and subtype
    let baseDifficulty = this.thematicElements.dangerLevel;
    
    switch (this.subtype as DungeonSubtype) {
      case DungeonSubtype.FORTRESS:
      case DungeonSubtype.TEMPLE:
        baseDifficulty += 2;
        break;
      case DungeonSubtype.CRYPT:
        baseDifficulty += 3;
        break;
      default:
        break;
    }
    
    return Math.min(10, baseDifficulty);
  }

  private recalculateDifficulty(): void {
    let maxFeatureDifficulty = 0;
    let activeFeatures = 0;
    
    for (const feature of this.dungeonFeatures.values()) {
      if (feature.properties.isActive) {
        activeFeatures++;
        maxFeatureDifficulty = Math.max(maxFeatureDifficulty, feature.properties.difficulty);
      }
    }
    
    // Adjust difficulty based on active features and their difficulty
    const featureImpact = (maxFeatureDifficulty * activeFeatures) / 10;
    this.difficultyRating = Math.min(10, this.calculateInitialDifficulty() + featureImpact);
  }

  private initializeBySubtype(subtype: DungeonSubtype): void {
    switch (subtype) {
      case DungeonSubtype.TEMPLE:
        this.thematicElements.lighting = 'dim';
        this.boundingBox.height = 3; // Temples are taller
        break;
      case DungeonSubtype.MINE:
        this.expansionRules?.push({
          direction: 'down',
          conditions: ['!flooded'],
          probability: 0.9
        });
        break;
      case DungeonSubtype.CRYPT:
        this.thematicElements.lighting = 'dark';
        this.thematicElements.dangerLevel = Math.max(6, this.thematicElements.dangerLevel);
        break;
      case DungeonSubtype.FORTRESS:
        this.boundingBox = { width: 3, height: 3, depth: 3 }; // Fortresses are larger
        break;
      default:
        break;
    }
  }
} 