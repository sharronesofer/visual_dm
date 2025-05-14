import { InteractionResult } from '../../systems/npc/InteractionSystem';

export interface ReputationChange {
  value: number;
  reason: string;
  timestamp: number;
}

export interface ReputationSystem {
  processInteractionReputation(
    npcId: string,
    targetId: string,
    result: InteractionResult
  ): Promise<number>;
  calculateBaseReputation(result: InteractionResult): number;
  applyInteractionModifiers(baseChange: number, result: InteractionResult): number;
  recordReputationChange(
    npcId: string,
    targetId: string,
    value: number,
    result: InteractionResult
  ): void;
  generateChangeReason(result: InteractionResult): string;
  getReputationHistory(npcId: string, targetId: string): ReputationChange[];
  getAggregateReputation(npcId: string, targetId: string): number;
  updateReputation(
    npcId: string,
    change: number,
    context: any
  ): Promise<void>;
  getReputation(
    npcId: string,
    groupId?: string
  ): Promise<number>;
  calculateReputationChange(
    baseChange: number,
    context: any
  ): number;
  decayReputation(
    npcId: string,
    timePassed: number
  ): Promise<void>;
  getReputationHistory(
    npcId: string,
    timeRange: {
      start: number;
      end: number;
    }
  ): Promise<{
    timestamp: number;
    change: number;
    reason: string;
  }[]>;
} 