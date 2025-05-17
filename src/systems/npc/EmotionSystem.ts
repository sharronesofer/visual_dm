/**
 * Unified Emotion System
 *
 * Provides context-driven emotion evaluation for NPCs using the centralized emotion model and registry.
 *
 * Usage Example:
 *   const emotionSystem = new EmotionSystem();
 *   const emotion = emotionSystem.processInteractionEmotion(npc, result);
 *   const description = emotionSystem.describeEmotion(emotion);
 */
import { NPCData } from '../../core/interfaces/types/npc/npc';
import { InteractionResult } from './InteractionSystem';
import {
  EmotionDefinition,
  BasicEmotion,
  ComplexEmotion,
  EmotionRegistry,
  IEmotionContext
} from '../../models/EmotionDefinition';
import {
  EmotionMapper,
  MappingContext,
  EmotionMappingResult
} from '../../models/EmotionMapper';
import { StatisticalCrowdModel } from '../../core/interfaces/types/npc/npc';
import { eventBus } from '../../eventBus/EventBus';
import { PartyIntegrationEventType, PartyIntegrationEventPayload } from '../../interfaces/PartyIntegrationEvents';

/**
 * Context for emotion evaluation (can be extended as needed)
 */
export interface EmotionContext extends IEmotionContext {
  npc: NPCData;
  interactionResult?: InteractionResult;
}

/**
 * Main system for evaluating and generating NPC emotions.
 *
 * - Uses the unified emotion model and registry
 * - Integrates with EmotionMapper for bidirectional mapping
 * - Supports context-driven toggling and hierarchical emotions
 * - Ready for integration with mapping and performance systems
 *
 * Usage Example:
 *   const emotionSystem = new EmotionSystem();
 *   emotionSystem.loadMappingConfig(myConfig);
 *   const emotion = await emotionSystem.processInteractionEmotion(npc, result);
 *   const visual = emotionSystem.mapEmotionToVisual(emotion, { npc });
 *   const inferred = emotionSystem.mapVisualToEmotion(visual, { npc });
 */
export class EmotionSystem {
  private registry = EmotionRegistry.instance;
  private mapper: EmotionMapper;
  private mappingConfig: Record<string, any> = {};

  /**
   * Initializes the system, registers default emotions, and sets up the EmotionMapper.
   */
  constructor(mapper?: EmotionMapper) {
    this.mapper = mapper ?? new EmotionMapper();
    this.initializeDefaultEmotions();
    this.subscribeToMappingChanges();
  }

  /**
   * Registers a standard set of basic and complex emotions if not already present.
   */
  private initializeDefaultEmotions() {
    if (!this.registry.getEmotionByName('joy')) {
      this.registry.registerEmotion(new BasicEmotion('joy', 0.5, 1.0, 0.7, { performanceCritical: true }));
      this.registry.registerEmotion(new BasicEmotion('anger', 0.5, -1.0, 0.8, { performanceCritical: true }));
      this.registry.registerEmotion(new BasicEmotion('sadness', 0.5, -1.0, 0.3, { performanceCritical: false }));
      this.registry.registerEmotion(new BasicEmotion('fear', 0.5, -0.8, 0.9, { performanceCritical: false }));
      this.registry.registerEmotion(new BasicEmotion('disgust', 0.5, -0.9, 0.6, { performanceCritical: false }));
      this.registry.registerEmotion(new BasicEmotion('surprise', 0.5, 0.0, 1.0, { performanceCritical: false }));
      this.registry.registerEmotion(new BasicEmotion('neutral', 0.5, 0.0, 0.5, { performanceCritical: false }));
      // Example complex emotion: Jealousy (anger + fear)
      const anger = this.registry.getEmotionByName('anger')!;
      const fear = this.registry.getEmotionByName('fear')!;
      this.registry.registerEmotion(new ComplexEmotion('jealousy', 0.5, -0.7, 0.85, [anger, fear], { performanceCritical: false }));
    }
  }

  /**
   * Loads a mapping configuration for this NPC or system.
   * @param config The mapping configuration object
   */
  public loadMappingConfig(config: Record<string, any>) {
    this.mappingConfig = config;
    this.mapper.loadConfig(config);
  }

  /**
   * Subscribes to EmotionMapper change notifications to propagate updates.
   */
  private subscribeToMappingChanges() {
    this.mapper.subscribe('visual', ({ layer, emotion, representation, context }) => {
      // Example: propagate visual changes to UI or animation system
      // (Implement actual integration as needed)
      // console.log(`[EmotionSystem] Visual mapping changed:`, { emotion, representation, context });
    });
    this.mapper.subscribe('behavioral', ({ layer, emotion, representation, context }) => {
      // Example: propagate behavioral changes to AI/behavior system
      // (Implement actual integration as needed)
    });
    this.mapper.subscribe('internal', ({ layer, emotion, representation, context }) => {
      // Example: propagate internal state changes
      // (Implement actual integration as needed)
    });
  }

  /**
   * Type guard to check if an object is a StatisticalCrowdModel
   */
  private isStatisticalCrowdModel(obj: any): obj is StatisticalCrowdModel {
    return obj && Array.isArray(obj.npcIds) && typeof obj.density === 'number';
  }

  /**
   * Computes a pooled emotion for a statistical crowd model.
   * Uses dominant behaviors and average stats to infer a representative emotion.
   * @param crowd The statistical crowd model
   * @returns The computed EmotionDefinition for the crowd
   */
  public processCrowdEmotion(crowd: StatisticalCrowdModel): EmotionDefinition {
    // Example: Map dominant behavior to emotion, or use average stats
    const dominant = crowd.dominantBehaviors[0] || 'idle';
    let emotionName = 'neutral';
    switch (dominant) {
      case 'aggressive':
        emotionName = 'anger'; break;
      case 'happy':
      case 'cheering':
        emotionName = 'joy'; break;
      case 'fearful':
        emotionName = 'fear'; break;
      case 'sad':
        emotionName = 'sadness'; break;
      // Add more mappings as needed
      default:
        emotionName = 'neutral';
    }
    let base = this.registry.getEmotionByName(emotionName);
    if (!base) {
      // Fallback to a default neutral emotion if not found
      base = new BasicEmotion('neutral', 0.5, 0, 0.5, {});
    }
    // Use density or average stats to modulate intensity
    const intensity = Math.min(1, 0.5 + (crowd.density / 100));
    return new BasicEmotion(
      base.name,
      intensity,
      base.valence,
      base.arousal,
      base.metadata
    );
  }

  /**
   * Evaluates the NPC's emotional response to an interaction.
   * @param npcOrCrowd The NPC data or StatisticalCrowdModel
   * @param result The result of the interaction
   * @returns The evaluated EmotionDefinition instance
   */
  public async processInteractionEmotion(
    npcOrCrowd: NPCData | StatisticalCrowdModel,
    result?: InteractionResult
  ): Promise<EmotionDefinition> {
    if (this.isStatisticalCrowdModel(npcOrCrowd)) {
      return this.processCrowdEmotion(npcOrCrowd);
    }
    return this.calculateEmotionalResponse({ npc: npcOrCrowd as NPCData, interactionResult: result });
  }

  /**
   * Calculates the emotional response for a given context.
   * @param context The evaluation context (NPC, interaction, etc.)
   * @returns The selected EmotionDefinition instance
   */
  public calculateEmotionalResponse(
    context: EmotionContext
  ): EmotionDefinition {
    const { npc, interactionResult } = context;
    let emotion: EmotionDefinition = this.registry.getEmotionByName('neutral')!;
    let intensity = 0.5;

    if (interactionResult) {
      if (interactionResult.success) {
        emotion = this.registry.getEmotionByName('joy')!;
        intensity = 0.7;
      } else {
        emotion = this.registry.getEmotionByName('anger')!;
        intensity = 0.6;
      }
      // Reputation effect
      const repChange = interactionResult.outcome?.effects?.reputation ?? 0;
      if (repChange > 0.1) {
        emotion = this.registry.getEmotionByName('joy')!;
        intensity = Math.min(1, intensity + 0.2);
      } else if (repChange < -0.1) {
        emotion = this.registry.getEmotionByName('anger')!;
        intensity = Math.min(1, intensity + 0.2);
      }
    }

    // Personality trait modifiers
    intensity = this.adjustIntensityForPersonality(npc, emotion.name, intensity);

    // Return a new instance with updated intensity
    return new BasicEmotion(
      emotion.name,
      intensity,
      emotion.valence,
      emotion.arousal,
      emotion.metadata
    );
  }

  /**
   * Maps an internal emotion to a visual representation using EmotionMapper.
   * @param emotion The emotion instance
   * @param context The mapping context
   * @returns The visual representation (e.g., blend shapes, animation params)
   */
  public mapEmotionToVisual(
    emotion: EmotionDefinition,
    context: MappingContext
  ): any {
    return this.mapper.mapToRepresentation('visual', emotion, context)?.representation;
  }

  /**
   * Maps a visual representation back to an internal emotion using EmotionMapper.
   * @param visual The visual representation
   * @param context The mapping context
   * @returns The inferred EmotionDefinition or null
   */
  public mapVisualToEmotion(
    visual: any,
    context: MappingContext
  ): EmotionDefinition | null {
    return this.mapper.mapToEmotion('visual', visual, context);
  }

  /**
   * Maps an internal emotion to a behavioral representation using EmotionMapper.
   * @param emotion The emotion instance
   * @param context The mapping context
   * @returns The behavioral representation (e.g., voice, gesture)
   */
  public mapEmotionToBehavioral(
    emotion: EmotionDefinition,
    context: MappingContext
  ): any {
    return this.mapper.mapToRepresentation('behavioral', emotion, context)?.representation;
  }

  /**
   * Maps a behavioral representation back to an internal emotion using EmotionMapper.
   * @param behavioral The behavioral representation
   * @param context The mapping context
   * @returns The inferred EmotionDefinition or null
   */
  public mapBehavioralToEmotion(
    behavioral: any,
    context: MappingContext
  ): EmotionDefinition | null {
    return this.mapper.mapToEmotion('behavioral', behavioral, context);
  }

  /**
   * Adjusts emotion intensity based on NPC personality traits.
   * @param npc The NPC data
   * @param emotionName The emotion name
   * @param baseIntensity The base intensity
   * @returns The adjusted intensity
   */
  private adjustIntensityForPersonality(
    npc: NPCData,
    emotionName: string,
    baseIntensity: number
  ): number {
    let intensity = baseIntensity;
    if (emotionName === 'anger') {
      intensity *= (1 + (npc.personality.traits.get('aggressiveness') ?? 0) * 0.5);
    } else if (emotionName === 'joy') {
      intensity *= (1 + (npc.personality.traits.get('friendliness') ?? 0) * 0.3);
    }
    if ((npc.personality.traits.get('cautiousness') ?? 0) > 0.7) {
      intensity *= 0.8;
    }
    return Math.min(1, Math.max(0, intensity));
  }

  /**
   * Generates a human-readable description of an emotion for UI/logging.
   * @param emotion The emotion instance
   * @returns A string description (e.g., "noticeably joy")
   */
  public describeEmotion(emotion: EmotionDefinition): string {
    const intensity = emotion.intensity;
    let level: string;
    if (intensity < 0.4) level = 'slightly';
    else if (intensity < 0.7) level = 'noticeably';
    else level = 'intensely';
    return `${level} ${emotion.name}`;
  }
}

// Singleton export (add at the end of the file)
export const emotionSystem = new EmotionSystem();

// Subscribe to party integration events
// Trigger a 'loss' emotion for all members on PARTY_DISBANDED
eventBus.on(PartyIntegrationEventType.PARTY_DISBANDED, (payload: any) => {
  try {
    const { npc, member, result } = payload;
    emotionSystem.calculateEmotionalResponse({ npc, interactionResult: result });
    // Optionally, update the NPC's emotional state in the system here
  } catch (error) {
    console.error('Error processing PARTY_DISBANDED event in EmotionSystem:', error);
  }
}); 