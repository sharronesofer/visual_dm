import { NPCData, StatisticalCrowdModel } from '../../core/interfaces/types/npc/npc';
import { InteractionResult } from './InteractionSystem';
import { ReputationAuditLogger } from '../reputation/ReputationAuditLogger';
import { eventBus } from '../../eventBus/EventBus';
import { PartyIntegrationEventType, PartyIntegrationEventPayload } from '../../interfaces/PartyIntegrationEvents';

export interface ReputationChange {
  value: number;
  reason: string;
  timestamp: number;
}

export class ReputationSystem {
  private reputationHistory: Map<string, ReputationChange[]>;

  constructor() {
    this.reputationHistory = new Map();
  }

  /**
   * Type guard to check if an object is a StatisticalCrowdModel
   */
  private isStatisticalCrowdModel(obj: any): obj is StatisticalCrowdModel {
    return obj && Array.isArray(obj.npcIds) && typeof obj.density === 'number';
  }

  /**
   * Computes a pooled reputation change for a statistical crowd model.
   * Uses average or sum of expected changes for the group.
   * @param crowd The statistical crowd model
   * @param targetId The target entity id
   * @param result Optional interaction result
   * @returns The computed reputation change for the crowd
   */
  public processCrowdReputation(
    crowd: StatisticalCrowdModel,
    targetId: string,
    result?: InteractionResult
  ): number {
    // Example: Use density as a proxy for impact, or average expected change
    // For now, just return density as the reputation change
    return crowd.density;
  }

  // Overload or type guard for processInteractionReputation
  public async processInteractionReputation(
    npcOrCrowd: NPCData | StatisticalCrowdModel,
    targetId: string,
    result: InteractionResult
  ): Promise<number> {
    if (this.isStatisticalCrowdModel(npcOrCrowd)) {
      return this.processCrowdReputation(npcOrCrowd, targetId, result);
    }
    try {
      // Calculate base reputation change
      let reputationChange = this.calculateBaseReputation(result);

      // Apply modifiers based on interaction type
      reputationChange = this.applyInteractionModifiers(reputationChange, result);

      // Record the change
      this.recordReputationChange(npcOrCrowd.id, targetId, reputationChange, result);

      // Audit log
      ReputationAuditLogger.log({
        timestamp: new Date().toISOString(),
        sourceSystem: 'ReputationSystem',
        targetEntity: `${npcOrCrowd.id}->${targetId}`,
        valueChange: reputationChange,
        context: JSON.stringify(result),
        callingSystem: 'ReputationSystem.processInteractionReputation'
      });

      return reputationChange;
    } catch (error) {
      console.error('Error processing reputation change:', error);
      return 0;
    }
  }

  private calculateBaseReputation(result: InteractionResult): number {
    let change = 0;

    // Base change from success/failure
    change += result.success ? 0.05 : -0.05;

    // Additional change from explicit reputation change
    // if (result.reputationChange) change += result.reputationChange; // TODO: Uncomment if property exists
    // if (result.economicImpact) change += result.economicImpact; // TODO: Uncomment if property exists
    // if (result.emotionalResponse) change += result.emotionalResponse; // TODO: Uncomment if property exists

    return change;
  }

  private applyInteractionModifiers(baseChange: number, result: InteractionResult): number {
    let finalChange = baseChange;

    // Modify based on economic impact
    // if (result.economicImpact) {
    //   const economicValue = result.economicImpact.value || 0;
    //   if (economicValue > 0) {
    //     finalChange *= 1.2; // Positive economic interactions boost reputation gain
    //   } else if (economicValue < 0) {
    //     finalChange *= 0.8; // Negative economic interactions reduce reputation gain
    //   }
    // }

    // Modify based on emotional response
    // if (result.emotionalResponse) {
    //   if (result.emotionalResponse.includes('happy') ||
    //     result.emotionalResponse.includes('pleased')) {
    //     finalChange *= 1.1;
    //   } else if (result.emotionalResponse.includes('angry') ||
    //     result.emotionalResponse.includes('upset')) {
    //     finalChange *= 0.9;
    //   }
    // }

    // Ensure change is within bounds
    return Math.max(-0.5, Math.min(0.5, finalChange));
  }

  private recordReputationChange(
    npcId: string,
    targetId: string,
    value: number,
    result: InteractionResult
  ): void {
    const key = `${npcId}:${targetId}`;
    if (!this.reputationHistory.has(key)) {
      this.reputationHistory.set(key, []);
    }

    const change: ReputationChange = {
      value,
      reason: this.generateChangeReason(result),
      timestamp: Date.now()
    };

    this.reputationHistory.get(key)?.push(change);

    // Audit log
    ReputationAuditLogger.log({
      timestamp: new Date().toISOString(),
      sourceSystem: 'ReputationSystem',
      targetEntity: `${npcId}->${targetId}`,
      valueChange: value,
      context: JSON.stringify(result),
      callingSystem: 'ReputationSystem.recordReputationChange'
    });
  }

  private generateChangeReason(result: InteractionResult): string {
    if (result.success) {
      return 'Successful interaction';
    } else {
      return 'Failed interaction';
    }
  }

  public getReputationHistory(npcId: string, targetId: string): ReputationChange[] {
    const key = `${npcId}:${targetId}`;
    return this.reputationHistory.get(key) || [];
  }

  public getAggregateReputation(npcId: string, targetId: string): number {
    const history = this.getReputationHistory(npcId, targetId);
    if (history.length === 0) return 0;

    // Calculate weighted average, giving more weight to recent interactions
    let totalWeight = 0;
    let weightedSum = 0;

    const now = Date.now();
    const dayInMs = 24 * 60 * 60 * 1000;

    history.forEach(change => {
      const daysAgo = (now - change.timestamp) / dayInMs;
      const weight = Math.max(0, 1 - (daysAgo / 30)); // Linear decay over 30 days

      weightedSum += change.value * weight;
      totalWeight += weight;
    });

    return totalWeight > 0 ? weightedSum / totalWeight : 0;
  }
}

// Singleton export
export const reputationSystem = new ReputationSystem();

// Subscribe to party integration events
// Decrease reputation for being kicked from a party
// Slightly increase reputation for joining a party
// (Assume processInteractionReputation is async and available)
eventBus.on(PartyIntegrationEventType.MEMBER_KICKED, async (payload: any) => {
  try {
    const { npc, party, result } = payload;
    await reputationSystem.processInteractionReputation(npc, party.id, result);
  } catch (error) {
    console.error('Error processing MEMBER_KICKED event in ReputationSystem:', error);
  }
});
eventBus.on(PartyIntegrationEventType.MEMBER_JOINED, async (payload: any) => {
  try {
    const { npc, party, result } = payload;
    await reputationSystem.processInteractionReputation(npc, party.id, result);
  } catch (error) {
    console.error('Error processing MEMBER_JOINED event in ReputationSystem:', error);
  }
});

// For testing: expose a method to clear reputation history
export function __clearReputationHistoryForTest() {
  reputationSystem['reputationHistory'].clear();
} 