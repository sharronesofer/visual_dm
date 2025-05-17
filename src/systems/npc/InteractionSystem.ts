import { NPCData } from '../../core/interfaces/types/npc/npc';
import { DialogueManager, DialogueResponse } from './DialogueManager';
import { EmotionSystem } from './EmotionSystem';
import { ReputationSystem } from './ReputationSystem';
import { MemoryManager } from './MemoryManager';
import { GroupFormationSystem } from './GroupFormationSystem';
import { EconomicAgentSystem } from '../economy/EconomicAgentSystem';
import { NPCEventLoggingService } from '../../core/services/NPCEventLoggingService';
import { MemoryEventType } from '../../core/interfaces/types/npc/memory';
import { DialogueConfigurationManager } from '../../dialogue/config/DialogueConfigurationManager';
import { ConversationContextManager } from '../../dialogue/ConversationContextManager';
import { useInteractionDispatch } from '../../store/core/interactionStore';
import { eventBus } from '../../eventBus/EventBus';
import { InteractionIntegrationEventType, InteractionIntegrationEventPayload } from '../../interfaces/InteractionIntegrationEvents';
import { PartyIntegrationEventType, PartyIntegrationEventPayload } from '../../interfaces/PartyIntegrationEvents';

export enum InteractionType {
  DIALOGUE = 'dialogue',
  TRADE = 'trade',
  MENTORING = 'mentoring',
  CONFLICT_RESOLUTION = 'conflict_resolution',
  SOCIAL_BONDING = 'social_bonding',
  INFORMATION_SHARING = 'information_sharing',
  GROUP_DECISION = 'group_decision',
  NEGOTIATION = 'negotiation',
  DECEPTION = 'deception',
  COOPERATION = 'cooperation',
  COMPETITION = 'competition'
}

export interface InteractionContext {
  npcId: string;
  targetId: string;
  type: InteractionType;
  subtype?: string;
  data?: any;
  location?: string;
  time?: number;
  witnesses?: string[];
  socialContext?: {
    relationship: number;
    groupContext?: {
      groupId: string;
      role: string;
    };
    reputationImpact: number;
    emotionalContext: {
      mood: string;
      intensity: number;
    };
  };
  economicContext?: {
    marketConditions: {
      supply: number;
      demand: number;
    };
    resourceValues: {
      [key: string]: number;
    };
    tradeHistory?: {
      success: number;
      total: number;
    };
  };
}

export interface InteractionResult {
  success: boolean;
  type: InteractionType;
  participants: string[];
  outcome: {
    description: string;
    effects: {
      relationship?: number;
      reputation?: number;
      resources?: {
        type: string;
        amount: number;
      }[];
      emotions?: {
        npcId: string;
        emotion: string;
        intensity: number;
      }[];
      memories?: {
        npcId: string;
        memoryId: string;
      }[];
    };
  };
  context: InteractionContext;
  timestamp: number;
}

export class InteractionSystem {
  private dialogueManager: DialogueManager;
  private emotionSystem: EmotionSystem;
  private reputationSystem: ReputationSystem;
  private memoryManager: MemoryManager;
  private groupSystem: GroupFormationSystem;
  private economicSystem: EconomicAgentSystem;
  private configManager: DialogueConfigurationManager;
  private contextManager: ConversationContextManager;
  private dispatch: Function;

  /**
   * @param dialogueManager DialogueManager or EnhancedDialogueManager instance
   * @param configManager DialogueConfigurationManager instance
   * @param contextManager ConversationContextManager instance
   * @param ...otherDeps Other system dependencies
   */
  constructor(
    dialogueManager: DialogueManager,
    emotionSystem: EmotionSystem,
    reputationSystem: ReputationSystem,
    memoryManager: MemoryManager,
    groupSystem: GroupFormationSystem,
    economicSystem: EconomicAgentSystem,
    configManager: DialogueConfigurationManager,
    contextManager: ConversationContextManager,
    dispatch?: Function
  ) {
    this.dialogueManager = dialogueManager;
    this.emotionSystem = emotionSystem;
    this.reputationSystem = reputationSystem;
    this.memoryManager = memoryManager;
    this.groupSystem = groupSystem;
    this.economicSystem = economicSystem;
    this.configManager = configManager;
    this.contextManager = contextManager;
    this.dispatch = dispatch ?? useInteractionDispatch();
    this.setupPartyIntegrationListeners();
  }

  private setupPartyIntegrationListeners() {
    eventBus.on(PartyIntegrationEventType.PARTY_DISBANDED, (payload: PartyIntegrationEventPayload) => {
      try {
        this.updateMoraleOnPartyDisbanded(payload.partyId);
      } catch (error) {
        console.error('Error updating morale on PARTY_DISBANDED:', error);
      }
    });
    eventBus.on(PartyIntegrationEventType.MEMBER_JOINED, (payload: PartyIntegrationEventPayload) => {
      try {
        this.updateMoraleOnMemberJoined(payload.partyId, payload.memberId);
      } catch (error) {
        console.error('Error updating morale on MEMBER_JOINED:', error);
      }
    });
    eventBus.on(PartyIntegrationEventType.MEMBER_KICKED, (payload: PartyIntegrationEventPayload) => {
      try {
        this.updateMoraleOnMemberKicked(payload.partyId, payload.memberId);
      } catch (error) {
        console.error('Error updating morale on MEMBER_KICKED:', error);
      }
    });
    // Add more handlers as needed for other party events
  }

  // --- Morale/Loyalty Tracking System Integration ---
  // In-memory stubs for demonstration; replace with real persistence as needed
  private npcMorale: Map<string, number> = new Map();
  private npcLoyalty: Map<string, number> = new Map();

  private updateMoraleOnPartyDisbanded(partyId: string) {
    // Fetch all members of the party (stub: assume we have a way to get member IDs)
    const memberIds = this.getPartyMemberIds(partyId);
    memberIds.forEach(npcId => {
      const oldMorale = this.npcMorale.get(npcId) ?? 50;
      const newMorale = Math.max(0, oldMorale - 20); // Arbitrary morale drop
      this.npcMorale.set(npcId, newMorale);
      console.log(`Morale for NPC ${npcId} after party disbanded: ${oldMorale} -> ${newMorale}`);
    });
  }

  private updateMoraleOnMemberJoined(partyId: string, memberId?: string) {
    if (!memberId) return;
    const oldMorale = this.npcMorale.get(memberId) ?? 50;
    const newMorale = Math.min(100, oldMorale + 10); // Arbitrary morale boost
    this.npcMorale.set(memberId, newMorale);
    const oldLoyalty = this.npcLoyalty.get(memberId) ?? 50;
    const newLoyalty = Math.min(100, oldLoyalty + 5); // Slight loyalty boost
    this.npcLoyalty.set(memberId, newLoyalty);
    console.log(`Morale for NPC ${memberId} after joining party: ${oldMorale} -> ${newMorale}`);
    console.log(`Loyalty for NPC ${memberId} after joining party: ${oldLoyalty} -> ${newLoyalty}`);
  }

  private updateMoraleOnMemberKicked(partyId: string, memberId?: string) {
    if (!memberId) return;
    const oldMorale = this.npcMorale.get(memberId) ?? 50;
    const newMorale = Math.max(0, oldMorale - 30); // Larger morale drop
    this.npcMorale.set(memberId, newMorale);
    const oldLoyalty = this.npcLoyalty.get(memberId) ?? 50;
    const newLoyalty = Math.max(0, oldLoyalty - 15); // Loyalty penalty
    this.npcLoyalty.set(memberId, newLoyalty);
    console.log(`Morale for NPC ${memberId} after being kicked: ${oldMorale} -> ${newMorale}`);
    console.log(`Loyalty for NPC ${memberId} after being kicked: ${oldLoyalty} -> ${newLoyalty}`);
  }

  // Stub: Replace with actual party member lookup
  private getPartyMemberIds(partyId: string): string[] {
    // In a real implementation, fetch from party system
    // For now, return an empty array
    return [];
  }

  /**
   * Process an interaction and update UI state via Redux/Zustand
   */
  public async processInteraction(
    initiator: NPCData,
    target: NPCData,
    context: InteractionContext
  ): Promise<InteractionResult> {
    // Emit interaction started event
    eventBus.emit(InteractionIntegrationEventType.INTERACTION_STARTED, {
      initiatorId: initiator.id,
      targetId: target.id,
      interactionType: context.type,
      timestamp: Date.now(),
    } as InteractionIntegrationEventPayload);

    // Calculate emotional state for initiator and target (stub: use calculateEmotionalResponse)
    const initiatorEmotion = this.emotionSystem.calculateEmotionalResponse({
      npc: initiator,
      interactionResult: { success: true, type: context.type, participants: [initiator.id, target.id], outcome: { description: '', effects: {} }, context, timestamp: Date.now() }
    });
    const targetEmotion = this.emotionSystem.calculateEmotionalResponse({
      npc: target,
      interactionResult: { success: true, type: context.type, participants: [initiator.id, target.id], outcome: { description: '', effects: {} }, context, timestamp: Date.now() }
    });

    // Get relevant memories (stub: use queryMemories)
    const relevantMemories = await this.memoryManager.queryMemories(initiator.id, { type: context.type, participants: [target.id] });

    // Process interaction based on type
    let result: InteractionResult;
    switch (context.type) {
      case InteractionType.MENTORING:
        result = await this.processMentoring(initiator, target, context);
        break;
      case InteractionType.CONFLICT_RESOLUTION:
        result = await this.processConflictResolution(initiator, target, context);
        break;
      case InteractionType.SOCIAL_BONDING:
        result = await this.processSocialBonding(initiator, target, context);
        break;
      case InteractionType.INFORMATION_SHARING:
        result = await this.processInformationSharing(initiator, target, context);
        break;
      case InteractionType.GROUP_DECISION:
        result = await this.processGroupDecision(initiator, target, context);
        break;
      case InteractionType.NEGOTIATION:
        result = await this.processNegotiation(initiator, target, context);
        break;
      case InteractionType.DECEPTION:
        result = await this.processDeception(initiator, target, context);
        break;
      case InteractionType.COOPERATION:
        result = await this.processCooperation(initiator, target, context);
        break;
      case InteractionType.COMPETITION:
        result = await this.processCompetition(initiator, target, context);
        break;
      default:
        result = await this.processDefaultInteraction(initiator, target, context);
    }

    // At the end, emit interaction completed event
    eventBus.emit(InteractionIntegrationEventType.INTERACTION_COMPLETED, {
      initiatorId: initiator.id,
      targetId: target.id,
      interactionType: context.type,
      result,
      timestamp: Date.now(),
    } as InteractionIntegrationEventPayload);

    // Update memories for both participants
    await this.createInteractionMemories(result);

    // TODO: Implement updateEmotionalStates if needed
    // await this.updateEmotionalStates(result);

    // TODO: Implement updateReputations if needed
    // await this.updateReputations(result);

    // Log interaction for both initiator and target
    const loggingService = NPCEventLoggingService.getInstance();
    loggingService.logInteraction(initiator.id, {
      timestamp: result.timestamp,
      type: context.type,
      targetId: target.id,
      outcome: result.success ? 'positive' : 'negative',
    }, {
      context,
      result,
      role: 'initiator',
    });
    loggingService.logInteraction(target.id, {
      timestamp: result.timestamp,
      type: context.type,
      targetId: initiator.id,
      outcome: result.success ? 'positive' : 'negative',
    }, {
      context,
      result,
      role: 'target',
    });

    // Dispatch dialogue event to UI state
    if (result && result.outcome && result.outcome.description) {
      // Get rich dialogue metadata from DialogueManager
      const dialogue = await this.dialogueManager.generateDialogue(initiator, context);
      await this.dispatch({
        type: 'UPDATE_STATE',
        payload: {
          lastDialogue: {
            message: dialogue.message,
            participants: result.participants,
            context: result.context,
            timestamp: result.timestamp,
            cacheStatus: dialogue.cacheStatus,
            gptMetadata: dialogue.gptMetadata,
            error: dialogue.error,
            contextSnapshot: dialogue.contextSnapshot,
            cacheAnalytics: dialogue.cacheAnalytics
          },
          isLoading: false,
        },
      });
    }

    return result;
  }

  private async processMentoring(
    mentor: NPCData,
    student: NPCData,
    context: InteractionContext
  ): Promise<InteractionResult> {
    const effectiveness = this.calculateMentoringEffectiveness(mentor, student);
    const dialogue = await this.dialogueManager.generateDialogue(mentor, {
      ...context,
      data: { effectiveness }
    });

    return {
      success: effectiveness > 0.5,
      type: InteractionType.MENTORING,
      participants: [mentor.id, student.id],
      outcome: {
        description: dialogue.message,
        effects: {
          relationship: effectiveness * 0.2,
          reputation: effectiveness * 0.1,
          emotions: [
            {
              npcId: mentor.id,
              emotion: effectiveness > 0.7 ? 'satisfied' : 'frustrated',
              intensity: effectiveness
            },
            {
              npcId: student.id,
              emotion: effectiveness > 0.7 ? 'grateful' : 'discouraged',
              intensity: effectiveness
            }
          ]
        }
      },
      context,
      timestamp: Date.now()
    };
  }

  private async processConflictResolution(
    initiator: NPCData,
    target: NPCData,
    context: InteractionContext
  ): Promise<InteractionResult> {
    const resolutionChance = this.calculateResolutionChance(initiator, target, context);
    const dialogue = await this.dialogueManager.generateDialogue(initiator, {
      ...context,
      data: { resolutionChance }
    });

    return {
      success: resolutionChance > 0.6,
      type: InteractionType.CONFLICT_RESOLUTION,
      participants: [initiator.id, target.id],
      outcome: {
        description: dialogue.message,
        effects: {
          relationship: resolutionChance > 0.6 ? 0.3 : -0.2,
          reputation: resolutionChance > 0.6 ? 0.2 : -0.1,
          emotions: [
            {
              npcId: initiator.id,
              emotion: resolutionChance > 0.6 ? 'relieved' : 'tense',
              intensity: Math.abs(resolutionChance - 0.5) * 2
            },
            {
              npcId: target.id,
              emotion: resolutionChance > 0.6 ? 'agreeable' : 'resistant',
              intensity: Math.abs(resolutionChance - 0.5) * 2
            }
          ]
        }
      },
      context,
      timestamp: Date.now()
    };
  }

  private async processSocialBonding(
    initiator: NPCData,
    target: NPCData,
    context: InteractionContext
  ): Promise<InteractionResult> {
    const bondingScore = this.calculateBondingScore(initiator, target, context);
    const dialogue = await this.dialogueManager.generateDialogue(initiator, {
      ...context,
      data: { bondingScore }
    });

    return {
      success: bondingScore > 0.5,
      type: InteractionType.SOCIAL_BONDING,
      participants: [initiator.id, target.id],
      outcome: {
        description: dialogue.message,
        effects: {
          relationship: bondingScore * 0.3,
          reputation: bondingScore * 0.1,
          emotions: [
            {
              npcId: initiator.id,
              emotion: bondingScore > 0.7 ? 'happy' : 'neutral',
              intensity: bondingScore
            },
            {
              npcId: target.id,
              emotion: bondingScore > 0.7 ? 'friendly' : 'indifferent',
              intensity: bondingScore
            }
          ]
        }
      },
      context,
      timestamp: Date.now()
    };
  }

  private async processInformationSharing(
    initiator: NPCData,
    target: NPCData,
    context: InteractionContext
  ): Promise<InteractionResult> {
    const sharingEffectiveness = this.calculateSharingEffectiveness(initiator, target, context);
    const dialogue = await this.dialogueManager.generateDialogue(initiator, {
      ...context,
      data: { sharingEffectiveness }
    });

    return {
      success: sharingEffectiveness > 0.5,
      type: InteractionType.INFORMATION_SHARING,
      participants: [initiator.id, target.id],
      outcome: {
        description: dialogue.message,
        effects: {
          relationship: sharingEffectiveness * 0.2,
          reputation: sharingEffectiveness * 0.15,
          emotions: [
            {
              npcId: initiator.id,
              emotion: sharingEffectiveness > 0.7 ? 'trusting' : 'cautious',
              intensity: sharingEffectiveness
            },
            {
              npcId: target.id,
              emotion: sharingEffectiveness > 0.7 ? 'interested' : 'skeptical',
              intensity: sharingEffectiveness
            }
          ]
        }
      },
      context,
      timestamp: Date.now()
    };
  }

  private async processGroupDecision(
    initiator: NPCData,
    target: NPCData,
    context: InteractionContext
  ): Promise<InteractionResult> {
    const influenceScore = this.calculateInfluenceScore(initiator, target, context);
    const dialogue = await this.dialogueManager.generateDialogue(initiator, {
      ...context,
      data: { influenceScore }
    });

    return {
      success: influenceScore > 0.6,
      type: InteractionType.GROUP_DECISION,
      participants: [initiator.id, target.id],
      outcome: {
        description: dialogue.message,
        effects: {
          relationship: influenceScore * 0.1,
          reputation: influenceScore * 0.2,
          emotions: [
            {
              npcId: initiator.id,
              emotion: influenceScore > 0.7 ? 'confident' : 'uncertain',
              intensity: influenceScore
            },
            {
              npcId: target.id,
              emotion: influenceScore > 0.7 ? 'receptive' : 'resistant',
              intensity: influenceScore
            }
          ]
        }
      },
      context,
      timestamp: Date.now()
    };
  }

  private async processNegotiation(
    initiator: NPCData,
    target: NPCData,
    context: InteractionContext
  ): Promise<InteractionResult> {
    // Implementation for negotiation interaction
    return this.processDefaultInteraction(initiator, target, context);
  }

  private async processDeception(
    initiator: NPCData,
    target: NPCData,
    context: InteractionContext
  ): Promise<InteractionResult> {
    // Implementation for deception interaction
    return this.processDefaultInteraction(initiator, target, context);
  }

  private async processCooperation(
    initiator: NPCData,
    target: NPCData,
    context: InteractionContext
  ): Promise<InteractionResult> {
    // Implementation for cooperation interaction
    return this.processDefaultInteraction(initiator, target, context);
  }

  private async processCompetition(
    initiator: NPCData,
    target: NPCData,
    context: InteractionContext
  ): Promise<InteractionResult> {
    // Implementation for competition interaction
    return this.processDefaultInteraction(initiator, target, context);
  }

  private async processDefaultInteraction(
    initiator: NPCData,
    target: NPCData,
    context: InteractionContext
  ): Promise<InteractionResult> {
    return {
      success: true,
      type: context.type,
      participants: [initiator.id, target.id],
      outcome: {
        description: 'Default interaction occurred',
        effects: {
          relationship: 0,
          reputation: 0,
          emotions: [
            {
              npcId: initiator.id,
              emotion: 'neutral',
              intensity: 0.5
            },
            {
              npcId: target.id,
              emotion: 'neutral',
              intensity: 0.5
            }
          ]
        }
      },
      context,
      timestamp: Date.now()
    };
  }

  private calculateMentoringEffectiveness(mentor: NPCData, student: NPCData): number {
    return (
      (mentor.stats.intelligence * 0.3 +
        mentor.stats.wisdom * 0.3 +
        mentor.stats.charisma * 0.2 +
        (mentor.personality.traits.get('empathy') ?? 0) * 0.2) /
      2
    );
  }

  private calculateResolutionChance(
    initiator: NPCData,
    target: NPCData,
    context: InteractionContext
  ): number {
    return (
      ((initiator.personality.traits.get('diplomacy') ?? 0) * 0.3 +
        (initiator.personality.traits.get('empathy') ?? 0) * 0.3 +
        (target.personality.traits.get('openness') ?? 0) * 0.2 +
        (context.socialContext?.relationship || 0) * 0.2) /
      2
    );
  }

  private calculateBondingScore(
    initiator: NPCData,
    target: NPCData,
    context: InteractionContext
  ): number {
    return (
      ((initiator.personality.traits.get('friendliness') ?? 0) * 0.3 +
        (initiator.personality.traits.get('empathy') ?? 0) * 0.2 +
        (target.personality.traits.get('openness') ?? 0) * 0.2 +
        (context.socialContext?.relationship || 0) * 0.3) /
      2
    );
  }

  private calculateSharingEffectiveness(
    initiator: NPCData,
    target: NPCData,
    context: InteractionContext
  ): number {
    return (
      (initiator.stats.charisma * 0.3 +
        (initiator.personality.traits.get('trustworthiness') ?? 0) * 0.3 +
        (target.personality.traits.get('openness') ?? 0) * 0.2 +
        (context.socialContext?.relationship || 0) * 0.2) /
      2
    );
  }

  private calculateInfluenceScore(
    initiator: NPCData,
    target: NPCData,
    context: InteractionContext
  ): number {
    return (
      ((initiator.personality.traits.get('leadership') ?? 0) * 0.3 +
        initiator.stats.charisma * 0.3 +
        (target.personality.traits.get('conformity') ?? 0) * 0.2 +
        (context.socialContext?.relationship || 0) * 0.2) /
      2
    );
  }

  private async createInteractionMemories(result: InteractionResult): Promise<void> {
    const baseMemory = {
      type: MemoryEventType.INTERACTION,
      time: result.timestamp,
      participants: result.participants,
      location: result.context.location || 'unknown',
      details: {
        eventType: result.type,
        description: result.outcome.description,
        outcome: result.success ? 'success' : 'failure',
        emotionalImpact: 0,
        importance: 0
      },
      relationships: [],
      tags: [result.type],
      associatedMemories: [],
      recallCount: 0,
      decayRate: 0.1
    };

    // Create memories for all participants
    for (const participantId of result.participants) {
      const emotionalImpact =
        result.outcome.effects.emotions?.find((e) => e.npcId === participantId)?.intensity || 0;

      const memory = {
        ...baseMemory,
        details: {
          ...baseMemory.details,
          emotionalImpact,
          importance: this.calculateMemoryImportance(result, emotionalImpact)
        },
        relationships: result.participants
          .filter((id) => id !== participantId)
          .map((id) => ({
            npcId: id,
            impact: result.outcome.effects.relationship || 0,
            type: result.type
          }))
      };

      await this.memoryManager.addMemory(participantId, memory);
    }
  }

  private calculateMemoryImportance(result: InteractionResult, emotionalImpact: number): number {
    const baseImportance = 0.5;
    const emotionalWeight = 0.3;
    const successWeight = 0.2;
    const reputationWeight = 0.3;
    const relationshipWeight = 0.2;

    return (
      baseImportance +
      emotionalImpact * emotionalWeight +
      (result.success ? successWeight : 0) +
      Math.abs(result.outcome.effects.reputation || 0) * reputationWeight +
      Math.abs(result.outcome.effects.relationship || 0) * relationshipWeight
    );
  }
}

// --- Performance Metrics Integration Stub ---
// See docs/performance/interaction_system_targets.md for required metrics and targets.
// TODO: Integrate real-time metrics logging for: active interactions, response times, memory/CPU usage, bandwidth, error rates.
export function logInteractionSystemMetrics(metrics: any) {
  // Placeholder: send metrics to monitoring dashboard or log to file
  // Example: metrics = { active: 42, latency: 15, memory: 1.2, cpu: 5, bandwidth: 8, errors: 0 }
} 