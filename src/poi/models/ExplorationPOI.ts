import { BasePOI } from './BasePOI';
import { POIType, ExplorationSubtype, Coordinates, ThematicElements } from '../types/POITypes';

// Re-export the ExplorationSubtype enum
export { ExplorationSubtype };

interface ResourceNode {
  id: string;
  type: 'mineral' | 'herb' | 'artifact' | 'wildlife';
  properties: {
    rarity: number;
    quantity: number;
    respawnTime: number;
    lastHarvested?: number;
    isDepletable: boolean;
    [key: string]: unknown;
  };
}

interface Discovery {
  id: string;
  type: 'lore' | 'secret' | 'vista' | 'challenge';
  properties: {
    significance: number;
    isRevealed: boolean;
    requiresItem?: string;
    rewards?: string[];
    [key: string]: unknown;
  };
}

/**
 * Specialized POI class for exploration-type locations
 */
export class ExplorationPOI extends BasePOI {
  private resourceNodes: Map<string, ResourceNode>;
  private discoveries: Map<string, Discovery>;
  private explorationProgress: number;
  private environmentalChallenges: Set<string>;

  constructor(
    id: string,
    name: string,
    subtype: ExplorationSubtype,
    coordinates: Coordinates,
    thematicElements: ThematicElements
  ) {
    super(id, name, POIType.EXPLORATION, subtype, coordinates, thematicElements);
    
    // Initialize exploration-specific properties
    this.resourceNodes = new Map<string, ResourceNode>();
    this.discoveries = new Map<string, Discovery>();
    this.explorationProgress = 0;
    this.environmentalChallenges = new Set<string>();
    
    // Set exploration-specific default values
    this.boundingBox = { width: 3, height: 1, depth: 3 }; // Exploration areas are typically wide
    this.canExpand = true;
    
    // Add default expansion rules for exploration areas
    this.expansionRules = [
      {
        direction: 'north',
        conditions: ['!blocked', '!water_body'],
        probability: 0.6
      },
      {
        direction: 'south',
        conditions: ['!blocked', '!water_body'],
        probability: 0.6
      },
      {
        direction: 'east',
        conditions: ['!blocked', '!water_body'],
        probability: 0.6
      },
      {
        direction: 'west',
        conditions: ['!blocked', '!water_body'],
        probability: 0.6
      }
    ];

    // Initialize based on subtype
    this.initializeBySubtype(subtype);
  }

  // Resource node management
  addResourceNode(node: ResourceNode): void {
    this.resourceNodes.set(node.id, node);
    this.features.push({
      id: node.id,
      type: `resource_${node.type}`,
      properties: node.properties
    });
    this.trackChange('modification', `Added ${node.type} resource node: ${node.id}`);
  }

  removeResourceNode(nodeId: string): boolean {
    const removed = this.resourceNodes.delete(nodeId);
    if (removed) {
      this.features = this.features.filter(f => f.id !== nodeId);
      this.trackChange('modification', `Removed resource node: ${nodeId}`);
    }
    return removed;
  }

  getResourceNode(nodeId: string): ResourceNode | undefined {
    return this.resourceNodes.get(nodeId);
  }

  // Resource harvesting system
  harvestResource(nodeId: string): boolean {
    const node = this.resourceNodes.get(nodeId);
    if (node && node.properties.quantity > 0) {
      node.properties.quantity--;
      node.properties.lastHarvested = Date.now();
      this.trackChange('modification', `Harvested resource: ${nodeId}`);
      
      if (node.properties.quantity === 0 && node.properties.isDepletable) {
        this.removeResourceNode(nodeId);
      }
      return true;
    }
    return false;
  }

  // Discovery management
  addDiscovery(discovery: Discovery): void {
    this.discoveries.set(discovery.id, discovery);
    this.features.push({
      id: discovery.id,
      type: `discovery_${discovery.type}`,
      properties: discovery.properties
    });
    this.trackChange('modification', `Added ${discovery.type} discovery: ${discovery.id}`);
  }

  removeDiscovery(discoveryId: string): boolean {
    const removed = this.discoveries.delete(discoveryId);
    if (removed) {
      this.features = this.features.filter(f => f.id !== discoveryId);
      this.trackChange('modification', `Removed discovery: ${discoveryId}`);
    }
    return removed;
  }

  getDiscovery(discoveryId: string): Discovery | undefined {
    return this.discoveries.get(discoveryId);
  }

  // Discovery interaction
  revealDiscovery(discoveryId: string, requiredItem?: string): boolean {
    const discovery = this.discoveries.get(discoveryId);
    if (discovery && !discovery.properties.isRevealed) {
      if (discovery.properties.requiresItem && discovery.properties.requiresItem !== requiredItem) {
        return false;
      }
      discovery.properties.isRevealed = true;
      this.explorationProgress = this.calculateExplorationProgress();
      this.trackChange('modification', `Revealed discovery: ${discoveryId}`);
      return true;
    }
    return false;
  }

  // Environmental challenge management
  addEnvironmentalChallenge(challenge: string): void {
    this.environmentalChallenges.add(challenge);
    this.trackChange('modification', `Added environmental challenge: ${challenge}`);
  }

  removeEnvironmentalChallenge(challenge: string): boolean {
    const removed = this.environmentalChallenges.delete(challenge);
    if (removed) {
      this.trackChange('modification', `Removed environmental challenge: ${challenge}`);
    }
    return removed;
  }

  getEnvironmentalChallenges(): string[] {
    return Array.from(this.environmentalChallenges);
  }

  // Exploration progress
  getExplorationProgress(): number {
    return this.explorationProgress;
  }

  // Override serialize to include exploration-specific properties
  serialize(): Record<string, unknown> {
    return {
      ...super.serialize(),
      resourceNodes: Array.from(this.resourceNodes.entries()),
      discoveries: Array.from(this.discoveries.entries()),
      explorationProgress: this.explorationProgress,
      environmentalChallenges: Array.from(this.environmentalChallenges)
    };
  }

  // Override deserialize to handle exploration-specific properties
  deserialize(data: Record<string, unknown>): void {
    super.deserialize(data);
    
    if (Array.isArray(data.resourceNodes)) {
      this.resourceNodes = new Map(data.resourceNodes);
    }
    
    if (Array.isArray(data.discoveries)) {
      this.discoveries = new Map(data.discoveries);
    }
    
    if (typeof data.explorationProgress === 'number') {
      this.explorationProgress = data.explorationProgress;
    }
    
    if (Array.isArray(data.environmentalChallenges)) {
      this.environmentalChallenges = new Set(data.environmentalChallenges);
    }
  }

  // Override validateThematicCoherence to add exploration-specific validation
  validateThematicCoherence(): boolean {
    return super.validateThematicCoherence() && this.validateExplorationTheme();
  }

  // Private helper methods
  private validateExplorationTheme(): boolean {
    // Exploration areas should have appropriate features for their subtype
    return (
      this.validateResourceDistribution() &&
      this.validateDiscoveryPlacement() &&
      this.validateEnvironmentalChallenges()
    );
  }

  private validateResourceDistribution(): boolean {
    // Check if resource distribution makes sense for the area type
    const resourceTypes = new Set(Array.from(this.resourceNodes.values()).map(node => node.type));
    
    switch (this.subtype as ExplorationSubtype) {
      case ExplorationSubtype.WILDERNESS:
        return resourceTypes.has('herb') || resourceTypes.has('wildlife');
      case ExplorationSubtype.LANDMARK:
        return resourceTypes.has('artifact');
      case ExplorationSubtype.MOUNTAIN:
        return resourceTypes.has('mineral');
      default:
        return true;
    }
  }

  private validateDiscoveryPlacement(): boolean {
    // Validate that discoveries are appropriate for the area
    for (const discovery of this.discoveries.values()) {
      if (discovery.properties.significance < 1 || discovery.properties.significance > 10) {
        return false;
      }
    }
    return true;
  }

  private validateEnvironmentalChallenges(): boolean {
    // Ensure environmental challenges are appropriate for the subtype
    return this.environmentalChallenges.size > 0;
  }

  private calculateExplorationProgress(): number {
    const totalDiscoveries = this.discoveries.size;
    if (totalDiscoveries === 0) return 0;
    
    const revealedDiscoveries = Array.from(this.discoveries.values())
      .filter(d => d.properties.isRevealed).length;
    
    return (revealedDiscoveries / totalDiscoveries) * 100;
  }

  private initializeBySubtype(subtype: ExplorationSubtype): void {
    switch (subtype) {
      case ExplorationSubtype.WILDERNESS:
        this.boundingBox = { width: 4, height: 1, depth: 4 }; // Wilderness areas are larger
        this.addEnvironmentalChallenge('weather');
        this.addEnvironmentalChallenge('terrain');
        break;
      case ExplorationSubtype.LANDMARK:
        this.thematicElements.lighting = 'dim';
        this.addEnvironmentalChallenge('structural_integrity');
        break;
      case ExplorationSubtype.MOUNTAIN:
        this.thematicElements.lighting = 'dark';
        this.boundingBox.height = 2;
        this.addEnvironmentalChallenge('altitude');
        this.addEnvironmentalChallenge('weather');
        break;
      case ExplorationSubtype.GROVE:
        this.thematicElements.dangerLevel = Math.min(3, this.thematicElements.dangerLevel);
        this.addEnvironmentalChallenge('wildlife');
        break;
      default:
        break;
    }
  }
} 