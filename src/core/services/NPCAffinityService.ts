import { NPCAffinity, RelationshipType } from '../types/npc/affinity';
import { NPCEventLoggingService } from './NPCEventLoggingService';

/**
 * Service for managing NPC-to-NPC affinity and relationship types.
 * Uses in-memory storage for demonstration/testing.
 */
export class NPCAffinityService {
  private static instance: NPCAffinityService;
  private affinities: Map<string, NPCAffinity> = new Map();

  private constructor() {}

  public static getInstance(): NPCAffinityService {
    if (!NPCAffinityService.instance) {
      NPCAffinityService.instance = new NPCAffinityService();
    }
    return NPCAffinityService.instance;
  }

  /**
   * Get or create an affinity record between two NPCs.
   */
  public getAffinity(npcId1: string, npcId2: string): NPCAffinity {
    const key = this.affinityKey(npcId1, npcId2);
    let affinity = this.affinities.get(key);
    if (!affinity) {
      affinity = {
        npcId1,
        npcId2,
        score: 0,
        lastInteraction: new Date(0),
        interactionCount: 0,
        relationship: RelationshipType.STRANGER,
      };
      this.affinities.set(key, affinity);
    }
    return affinity;
  }

  /**
   * Update affinity score and recalculate relationship type.
   */
  public updateAffinity(npcId1: string, npcId2: string, change: number, context?: Record<string, any>): NPCAffinity {
    const affinity = this.getAffinity(npcId1, npcId2);
    const before = { ...affinity };
    affinity.score += change;
    affinity.lastInteraction = new Date();
    affinity.interactionCount += 1;
    const prevRelationship = affinity.relationship;
    affinity.relationship = this.calculateRelationshipType(affinity.score);
    const after = { ...affinity };
    // Log affinity change
    NPCEventLoggingService.getInstance().logAffinityChange(
      npcId1,
      affinity,
      change,
      before,
      after,
      context
    );
    // Log relationship change if it occurred
    if (prevRelationship !== affinity.relationship) {
      NPCEventLoggingService.getInstance().logRelationshipChange(
        npcId1,
        prevRelationship,
        affinity.relationship,
        affinity,
        context
      );
    }
    return affinity;
  }

  /**
   * Get all affinity records for a specific NPC.
   */
  public getAllAffinitiesForNPC(npcId: string): NPCAffinity[] {
    return Array.from(this.affinities.values()).filter(
      a => a.npcId1 === npcId || a.npcId2 === npcId
    );
  }

  /**
   * Apply decay to all affinities over time (e.g., daily tick).
   */
  public decayAffinities(decayAmount = 1, context?: Record<string, any>): void {
    for (const affinity of this.affinities.values()) {
      const before = { ...affinity };
      affinity.score -= decayAmount;
      const prevRelationship = affinity.relationship;
      affinity.relationship = this.calculateRelationshipType(affinity.score);
      const after = { ...affinity };
      NPCEventLoggingService.getInstance().logAffinityChange(
        affinity.npcId1,
        affinity,
        -decayAmount,
        before,
        after,
        context
      );
      if (prevRelationship !== affinity.relationship) {
        NPCEventLoggingService.getInstance().logRelationshipChange(
          affinity.npcId1,
          prevRelationship,
          affinity.relationship,
          affinity,
          context
        );
      }
    }
  }

  /**
   * Helper: Calculate relationship type from score.
   */
  private calculateRelationshipType(score: number): RelationshipType {
    if (score >= 80) return RelationshipType.CLOSE_FRIEND;
    if (score >= 50) return RelationshipType.FRIEND;
    if (score >= 20) return RelationshipType.ACQUAINTANCE;
    if (score <= -60) return RelationshipType.ENEMY;
    if (score <= -30) return RelationshipType.RIVAL;
    return RelationshipType.STRANGER;
  }

  /**
   * Helper: Generate a unique key for an unordered NPC pair.
   */
  private affinityKey(npcId1: string, npcId2: string): string {
    return [npcId1, npcId2].sort().join('::');
  }

  /**
   * Process daily interactions between NPCs in the same POI.
   * @param npcsByPoi Map of POI ID to array of NPC IDs
   * @param options Optional: seed for deterministic testing
   * @returns Number of processed interactions
   */
  public processInteractions(
    npcsByPoi: Record<string, string[]>,
    options?: { seed?: number }
  ): number {
    let count = 0;
    const rng = options?.seed !== undefined ? this.seededRandom(options.seed) : Math.random;
    for (const npcIds of Object.values(npcsByPoi)) {
      for (let i = 0; i < npcIds.length; i++) {
        for (let j = i + 1; j < npcIds.length; j++) {
          if (rng() < 0.1) { // 10% chance
            // Random interaction type: -2 to +2 affinity change
            const change = Math.floor(rng() * 5) - 2;
            this.updateAffinity(npcIds[i], npcIds[j], change);
            count++;
          }
        }
      }
    }
    return count;
  }

  /**
   * Seeded random number generator for testability.
   */
  private seededRandom(seed: number): () => number {
    let s = seed % 2147483647;
    return () => {
      s = (s * 16807) % 2147483647;
      return (s - 1) / 2147483646;
    };
  }
} 