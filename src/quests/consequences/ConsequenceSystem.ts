import { QuestConsequence } from '../types';
import { ItemConsequenceHandler, PlayerInventory } from './ItemConsequenceHandler';
import { WorldStateHandler, WorldState } from './WorldStateHandler';
import { FactionType } from '../../core/interfaces/types/factions/faction';
import { WorldStateChangeCustomData } from './types';
import { ItemService } from '../../core/services/ItemService';

/**
 * Types of consequences that can occur
 */
export type ConsequenceType =
  | 'faction_reputation'
  | 'world_state'
  | 'npc_relationship'
  | 'environment'
  | 'quest_availability'
  | 'economy'
  | 'custom';

/**
 * Severity levels for consequences
 */
export type ConsequenceSeverity = 'minor' | 'moderate' | 'major' | 'critical';

/**
 * Represents a consequence trigger condition
 */
export interface ConsequenceTrigger {
  type: 'immediate' | 'delayed' | 'conditional';
  delay?: number; // Milliseconds for delayed triggers
  condition?: (state: WorldState) => boolean; // For conditional triggers
}

/**
 * Represents a single consequence
 */
export interface Consequence {
  id: string;
  type: ConsequenceType;
  severity: ConsequenceSeverity;
  description: string;
  trigger: ConsequenceTrigger;
  effects: Record<string, any>;
}

export type WorldStateChangeType =
  | 'QUEST_COMPLETION'
  | 'QUEST_FAILURE'
  | 'QUEST_CANCELLED'
  | 'FACTION_TENSION_CHANGE'
  | 'TENSION_DECREASE'
  | 'DIPLOMATIC_OPPORTUNITY'
  | 'RESOURCE_CHANGE'
  | 'TERRITORY_CHANGE';

export interface WorldStateChange {
  type: WorldStateChangeType;
  description: string;
  value: number;
  affectedFactions: FactionType[];
  location: string | null;
  customData?: WorldStateChangeCustomData;
}

export interface WorldStateChangeEvent {
  type: WorldStateChangeType;
  description: string;
  value: number;
  affectedFactions: FactionType[];
  location: string | null;
  timestamp: number;
  customData?: WorldStateChangeCustomData;
}

/**
 * Manages the tracking and application of quest consequences
 */
export class ConsequenceSystem {
  private itemHandler: ItemConsequenceHandler;

  constructor(
    private worldStateHandler: WorldStateHandler,
    private itemService: ItemService
  ) {
    this.itemHandler = new ItemConsequenceHandler(this.itemService);
  }

  /**
   * Process a consequence
   */
  async processConsequence(
    playerId: string,
    consequence: QuestConsequence
  ): Promise<void> {
    const worldState = this.worldStateHandler.getWorldState();

    switch (consequence.type) {
      case 'ITEM_REWARD':
        await this.itemHandler.handleItemReward(playerId, consequence, worldState as any);
        break;

      case 'ITEM_REMOVE':
        await this.itemHandler.handleItemRemoval(playerId, consequence, worldState as any);
        break;

      case 'WORLD_STATE':
        await this.worldStateHandler.handleWorldStateChange(consequence, worldState as any);
        break;

      default:
        throw new Error(`Unknown consequence type: ${consequence.type}`);
    }
  }

  /**
   * Process multiple consequences
   */
  async processConsequences(
    playerId: string,
    consequences: QuestConsequence[]
  ): Promise<void> {
    for (const consequence of consequences) {
      await this.processConsequence(playerId, consequence);
    }
  }

  /**
   * Update world state (check expired effects, etc.)
   */
  update(): void {
    // Cast to any to work around type mismatch between different WorldState definitions
    const worldState = this.worldStateHandler.getWorldState();
    this.worldStateHandler.update(worldState as any);
  }

  /**
   * Get the current world state
   */
  getWorldState(): any {
    return this.worldStateHandler.getWorldState();
  }

  /**
   * Get a player's inventory
   */
  getPlayerInventory(): any {
    return this.itemService.getPlayerInventory();
  }

  /**
   * Get state changes for a specific location
   */
  getLocationChanges(location: string): WorldStateChange[] {
    return this.worldStateHandler.getLocationChanges(location);
  }

  /**
   * Apply a consequence to the world state
   */
  applyConsequence(consequence: WorldStateChange): void {
    // Apply the consequence to the world state
    this.worldStateHandler.applyWorldStateChange(consequence);
  }

  /**
   * Apply a list of consequences to the world state
   */
  applyConsequences(consequences: WorldStateChange[]): void {
    consequences.forEach(consequence => {
      this.worldStateHandler.applyWorldStateChange(consequence);
    });
  }

  /**
   * Get all state changes
   */
  getAllStateChanges(): WorldStateChange[] {
    return this.worldStateHandler.getAllStateChanges();
  }

  /**
   * Handle item consequences
   */
  handleItemConsequences(playerId: string, consequences: any[]): void {
    this.itemHandler.handleConsequences(playerId, consequences);
  }
} 