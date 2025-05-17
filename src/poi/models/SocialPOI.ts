import { BasePOI } from './BasePOI';
import { POIType, SocialSubtype, Coordinates, ThematicElements } from '../types/POITypes';
import { ReputationAuditLogger } from '../../systems/reputation/ReputationAuditLogger';

// Re-export the SocialSubtype enum
export { SocialSubtype };

interface NPC {
  id: string;
  name: string;
  role: 'merchant' | 'quest_giver' | 'trainer' | 'guard' | 'leader' | 'citizen';
  properties: {
    importance: number; // 1-10
    isAvailable: boolean;
    schedule?: {
      [timeOfDay: string]: string; // location or activity
    };
    relationships?: {
      [npcId: string]: number; // -100 to 100
    };
    inventory?: string[];
    [key: string]: unknown;
  };
}

interface Quest {
  id: string;
  title: string;
  type: 'fetch' | 'escort' | 'defend' | 'investigate' | 'diplomatic';
  properties: {
    difficulty: number;
    isAvailable: boolean;
    isComplete: boolean;
    requiredReputation?: number;
    rewards?: {
      reputation?: number;
      items?: string[];
      currency?: number;
    };
    [key: string]: unknown;
  };
}

interface Faction {
  id: string;
  name: string;
  properties: {
    playerReputation: number; // -100 to 100
    dominance: number; // 0-10, influence in the area
    relationships: {
      [factionId: string]: number; // -100 to 100
    };
    [key: string]: unknown;
  };
}

/**
 * Specialized POI class for social interaction locations
 */
export class SocialPOI extends BasePOI {
  private npcData: Map<string, NPC>;
  private questData: Map<string, Quest>;
  private factions: Map<string, Faction>;
  private economyLevel: number;
  private populationDensity: number;

  constructor(
    id: string,
    name: string,
    subtype: SocialSubtype,
    coordinates: Coordinates,
    thematicElements: ThematicElements
  ) {
    super(id, name, POIType.SOCIAL, subtype, coordinates, thematicElements);

    // Initialize social-specific properties
    this.npcData = new Map<string, NPC>();
    this.questData = new Map<string, Quest>();
    this.factions = new Map<string, Faction>();
    this.economyLevel = this.calculateInitialEconomyLevel();
    this.populationDensity = this.calculateInitialPopulation();

    // Set social-specific default values
    this.boundingBox = { width: 2, height: 2, depth: 2 }; // Social areas have standard size
    this.canExpand = true;

    // Add default expansion rules for social areas
    this.expansionRules = [
      {
        direction: 'north',
        conditions: ['!blocked', 'population_pressure'],
        probability: 0.4
      },
      {
        direction: 'south',
        conditions: ['!blocked', 'population_pressure'],
        probability: 0.4
      },
      {
        direction: 'east',
        conditions: ['!blocked', 'population_pressure'],
        probability: 0.4
      },
      {
        direction: 'west',
        conditions: ['!blocked', 'population_pressure'],
        probability: 0.4
      }
    ];

    // Initialize based on subtype
    this.initializeBySubtype(subtype);
  }

  // NPC management
  addNPC(npc: NPC): void {
    this.npcData.set(npc.id, npc);
    this.npcs.push(npc.id);
    this.features.push({
      id: npc.id,
      type: `npc_${npc.role}`,
      properties: npc.properties
    });
    this.trackChange('modification', `Added ${npc.role} NPC: ${npc.name}`);
  }

  removeNPC(npcId: string): boolean {
    const removed = this.npcData.delete(npcId);
    if (removed) {
      this.npcs = this.npcs.filter(id => id !== npcId);
      this.features = this.features.filter(f => f.id !== npcId);
      this.trackChange('modification', `Removed NPC: ${npcId}`);
    }
    return removed;
  }

  getNPC(npcId: string): NPC | undefined {
    return this.npcData.get(npcId);
  }

  updateNPCSchedule(npcId: string, timeOfDay: string, activity: string): boolean {
    const npc = this.npcData.get(npcId);
    if (npc) {
      if (!npc.properties.schedule) {
        npc.properties.schedule = {};
      }
      npc.properties.schedule[timeOfDay] = activity;
      this.trackChange('modification', `Updated schedule for NPC: ${npcId}`);
      return true;
    }
    return false;
  }

  // Quest management
  addQuest(quest: Quest): void {
    this.questData.set(quest.id, quest);
    this.quests.push(quest.id);
    this.features.push({
      id: quest.id,
      type: `quest_${quest.type}`,
      properties: quest.properties
    });
    this.trackChange('modification', `Added ${quest.type} quest: ${quest.title}`);
  }

  removeQuest(questId: string): boolean {
    const removed = this.questData.delete(questId);
    if (removed) {
      this.quests = this.quests.filter(id => id !== questId);
      this.features = this.features.filter(f => f.id !== questId);
      this.trackChange('modification', `Removed quest: ${questId}`);
    }
    return removed;
  }

  getQuest(questId: string): Quest | undefined {
    return this.questData.get(questId);
  }

  completeQuest(questId: string): boolean {
    const quest = this.questData.get(questId);
    if (quest && !quest.properties.isComplete) {
      quest.properties.isComplete = true;
      this.trackChange('modification', `Completed quest: ${questId}`);

      // Apply reputation changes if specified
      if (quest.properties.rewards?.reputation) {
        this.adjustFactionReputation(
          Object.keys(this.factions)[0], // Primary faction
          quest.properties.rewards.reputation
        );
      }
      return true;
    }
    return false;
  }

  // Faction management
  addFaction(faction: Faction): void {
    this.factions.set(faction.id, faction);
    this.features.push({
      id: faction.id,
      type: 'faction',
      properties: faction.properties
    });
    this.trackChange('modification', `Added faction: ${faction.name}`);
  }

  removeFaction(factionId: string): boolean {
    const removed = this.factions.delete(factionId);
    if (removed) {
      this.features = this.features.filter(f => f.id !== factionId);
      this.trackChange('modification', `Removed faction: ${factionId}`);
    }
    return removed;
  }

  getFaction(factionId: string): Faction | undefined {
    return this.factions.get(factionId);
  }

  adjustFactionReputation(factionId: string, change: number): boolean {
    const faction = this.factions.get(factionId);
    if (faction) {
      const oldReputation = faction.properties.playerReputation;
      faction.properties.playerReputation = Math.max(
        -100,
        Math.min(100, faction.properties.playerReputation + change)
      );
      this.trackChange('modification', `Adjusted faction reputation: ${factionId}`);
      // Audit log
      ReputationAuditLogger.log({
        timestamp: new Date().toISOString(),
        sourceSystem: 'SocialPOI',
        targetEntity: factionId,
        valueChange: faction.properties.playerReputation - oldReputation,
        context: `old: ${oldReputation}, new: ${faction.properties.playerReputation}, delta: ${change}`,
        callingSystem: 'SocialPOI.adjustFactionReputation'
      });
      return true;
    }
    return false;
  }

  // Economy and population metrics
  getEconomyLevel(): number {
    return this.economyLevel;
  }

  getPopulationDensity(): number {
    return this.populationDensity;
  }

  // Override serialize to include social-specific properties
  serialize(): Record<string, unknown> {
    return {
      ...super.serialize(),
      npcData: Array.from(this.npcData.entries()),
      questData: Array.from(this.questData.entries()),
      factions: Array.from(this.factions.entries()),
      economyLevel: this.economyLevel,
      populationDensity: this.populationDensity
    };
  }

  // Override deserialize to handle social-specific properties
  deserialize(data: Record<string, unknown>): void {
    super.deserialize(data);

    if (Array.isArray(data.npcData)) {
      this.npcData = new Map(data.npcData);
    }

    if (Array.isArray(data.questData)) {
      this.questData = new Map(data.questData);
    }

    if (Array.isArray(data.factions)) {
      this.factions = new Map(data.factions);
    }

    if (typeof data.economyLevel === 'number') {
      this.economyLevel = data.economyLevel;
    }

    if (typeof data.populationDensity === 'number') {
      this.populationDensity = data.populationDensity;
    }
  }

  // Override validateThematicCoherence to add social-specific validation
  validateThematicCoherence(): boolean {
    return super.validateThematicCoherence() && this.validateSocialTheme();
  }

  // Private helper methods
  private validateSocialTheme(): boolean {
    // Social areas should have appropriate characteristics
    return (
      this.validateNPCDistribution() &&
      this.validateQuestAvailability() &&
      this.validateFactionInfluence()
    );
  }

  private validateNPCDistribution(): boolean {
    // Check if NPC roles make sense for the area type
    const npcRoles = new Set(Array.from(this.npcData.values()).map(npc => npc.role));

    switch (this.subtype as SocialSubtype) {
      case SocialSubtype.MARKET:
        return npcRoles.has('merchant');
      case SocialSubtype.GUILD:
        return npcRoles.has('trainer') || npcRoles.has('leader');
      case SocialSubtype.CASTLE:
        return npcRoles.has('guard') && npcRoles.has('leader');
      default:
        return true;
    }
  }

  private validateQuestAvailability(): boolean {
    // Validate that quests are appropriate for the area
    for (const quest of this.questData.values()) {
      if (quest.properties.difficulty < 1 || quest.properties.difficulty > 10) {
        return false;
      }
    }
    return true;
  }

  private validateFactionInfluence(): boolean {
    // Ensure factions have valid influence levels
    for (const faction of this.factions.values()) {
      if (faction.properties.dominance < 0 || faction.properties.dominance > 10) {
        return false;
      }
    }
    return this.factions.size > 0;
  }

  private calculateInitialEconomyLevel(): number {
    // Base economy on thematic elements and subtype
    let baseEconomy = 5; // Default middle economy

    switch (this.subtype as SocialSubtype) {
      case SocialSubtype.MARKET:
      case SocialSubtype.GUILD:
        baseEconomy += 2;
        break;
      case SocialSubtype.CASTLE:
        baseEconomy += 3;
        break;
      case SocialSubtype.VILLAGE:
        baseEconomy -= 1;
        break;
      default:
        break;
    }

    return Math.min(10, Math.max(1, baseEconomy));
  }

  private calculateInitialPopulation(): number {
    // Base population on subtype and economy
    let basePopulation = this.economyLevel;

    switch (this.subtype as SocialSubtype) {
      case SocialSubtype.VILLAGE:
        basePopulation += 2;
        break;
      case SocialSubtype.MARKET:
        basePopulation += 4;
        break;
      case SocialSubtype.CASTLE:
        basePopulation += 5;
        break;
      default:
        break;
    }

    return Math.min(10, basePopulation);
  }

  private initializeBySubtype(subtype: SocialSubtype): void {
    switch (subtype) {
      case SocialSubtype.VILLAGE:
        this.boundingBox = { width: 3, height: 1, depth: 3 }; // Villages are spread out
        break;
      case SocialSubtype.MARKET:
        this.boundingBox = { width: 2, height: 1, depth: 2 }; // Markets are compact
        this.thematicElements.dangerLevel = Math.min(2, this.thematicElements.dangerLevel);
        break;
      case SocialSubtype.GUILD:
        this.boundingBox = { width: 2, height: 2, depth: 2 }; // Guilds are multi-story
        break;
      case SocialSubtype.CASTLE:
        this.boundingBox = { width: 4, height: 4, depth: 4 }; // Castles are large
        this.thematicElements.dangerLevel = Math.max(4, this.thematicElements.dangerLevel);
        break;
      default:
        break;
    }
  }
} 