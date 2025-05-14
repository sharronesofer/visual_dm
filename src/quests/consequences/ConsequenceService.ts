import { PlayerAction, PlayerActionType, PlayerActionHistory, WorldStateChange, WorldState } from './types';
import { FactionService } from '../factions/FactionService';
import type { FactionType } from '../factions/types';

/**
 * Service for tracking and applying consequences of player actions, updating world state and faction relationships.
 */
export class ConsequenceService {
  private factionService: FactionService;
  private actionHistories: Map<string, PlayerAction[]> = new Map();
  // Optionally, add worldStateHandler for world state changes

  constructor(factionService: FactionService) {
    this.factionService = factionService;
  }

  /**
   * Apply a player action and its consequences.
   * Updates faction relationships, world state, and logs the action.
   */
  public applyAction(action: PlayerAction): void {
    this.recordAction(action);
    switch (action.actionType) {
      case 'QUEST_COMPLETION':
        if (action.factionId && action.targetFactionId && action.outcome === 'success') {
          // Example: improve relationship on quest success
          this.factionService.updateRelationship(action.factionId, action.targetFactionId, 10);
        }
        break;
      case 'QUEST_FAILURE':
        if (action.factionId && action.targetFactionId) {
          // Example: worsen relationship on quest failure
          this.factionService.updateRelationship(action.factionId, action.targetFactionId, -10);
        }
        break;
      case 'FACTION_INTERACTION':
        // Custom logic for faction interactions
        break;
      // Add more cases as needed
      default:
        break;
    }
    // Optionally: trigger follow-up events or world state changes
  }

  /**
   * Record a player action in the history log.
   */
  public recordAction(action: PlayerAction): void {
    if (!this.actionHistories.has(action.playerId)) {
      this.actionHistories.set(action.playerId, []);
    }
    this.actionHistories.get(action.playerId)!.push(action);
  }

  /**
   * Get the action history for a player.
   */
  public getHistory(playerId: string): PlayerAction[] {
    return this.actionHistories.get(playerId) || [];
  }

  /**
   * Trigger follow-up events based on player action history or world state.
   * (Stub for extensibility)
   */
  public triggerFollowUpEvents(playerId: string): void {
    // Example: if player has completed certain quests, unlock new quest/event
    const history = this.getHistory(playerId);
    // ...event logic here
  }

  /**
   * Update faction relationships based on quest outcomes or other triggers.
   */
  public updateFactionRelationships(factionId: FactionType, targetId: FactionType, change: number): void {
    this.factionService.updateRelationship(factionId, targetId, change);
  }
}

/**
 * # ConsequenceService API
 *
 * - applyAction(action: PlayerAction): void
 * - recordAction(action: PlayerAction): void
 * - getHistory(playerId: string): PlayerAction[]
 * - triggerFollowUpEvents(playerId: string): void
 * - updateFactionRelationships(factionId, targetId, change): void
 *
 * Designed for extensibility: add world state integration, event triggers, and more consequence types as needed.
 */ 