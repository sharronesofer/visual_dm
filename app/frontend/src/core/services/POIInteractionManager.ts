import { v4 as uuidv4 } from 'uuid';
import {
  POI,
  POIInteraction,
  POIEntity,
  POIInteractionOption,
  POIRequirement,
  POIReward,
  POIFeedbackCallbacks,
  POIInteractionType,
  POIState,
  POIChunk,
  POIFeature,
  POIFeedback
} from '../types/poi';
import { usePoiStore } from '../store/core/poiStore';
import { NPCEventLoggingService } from './NPCEventLoggingService';
import { NPCInteraction } from '../types/npc/npc';

type FeedbackType = 'dialogue' | 'quest_accept' | 'quest_decline' | 'info_acknowledge';

interface DialogueOptions {
  text: string;
  action: () => void;
}

interface QuestInteractionParams {
  title: string;
  description: string;
  requirements: POIRequirement[];
  rewards: POIReward[];
  onAccept: () => void;
  onDecline: () => void;
}

/**
 * Manages POI interactions, including dialogue, quests, and information displays.
 * Handles interaction creation, feedback, and state management.
 */
class POIInteractionManager {
  private static instance: POIInteractionManager;
  private feedbackCallbacks: POIFeedbackCallbacks = {};

  private constructor() {}

  /**
   * Gets the singleton instance of POIInteractionManager
   * @returns The POIInteractionManager instance
   */
  public static getInstance(): POIInteractionManager {
    if (!POIInteractionManager.instance) {
      POIInteractionManager.instance = new POIInteractionManager();
    }
    return POIInteractionManager.instance;
  }

  /**
   * Sets callbacks for providing feedback during interactions
   * @param callbacks Object containing visual, audio, and haptic feedback callbacks
   */
  public setFeedbackCallbacks(callbacks: POIFeedbackCallbacks): void {
    this.feedbackCallbacks = {
      ...this.feedbackCallbacks,
      ...callbacks
    };
  }

  /**
   * Creates a dialogue interaction with an entity
   * @param entity The entity to create dialogue with
   * @param dialogueOptions Array of dialogue options with text and actions
   * @returns A dialogue interaction object
   */
  public createDialogueInteraction(
    entity: POIEntity,
    dialogueOptions: DialogueOptions[]
  ): POIInteraction {
    if (!entity.name) {
      throw new Error('Entity must have a name to create dialogue interaction');
    }

    return {
      id: uuidv4(),
      type: 'dialogue',
      title: `Speaking with ${entity.name}`,
      description: `${entity.name} is ready to talk.`,
      options: dialogueOptions.map(opt => ({
        id: uuidv4(),
        text: opt.text,
        action: () => {
          opt.action();
          this.provideFeedback('dialogue');
          // Log NPC interaction event
          const interaction: NPCInteraction = {
            timestamp: Date.now(),
            type: 'dialogue',
            targetId: entity.id,
            outcome: 'neutral', // Could be improved with actual outcome
          };
          NPCEventLoggingService.getInstance().logInteraction(
            entity.id,
            interaction,
            { entity, interactionType: 'dialogue' }
          );
        },
      })),
    };
  }

  /**
   * Creates a quest interaction with requirements and rewards
   * @param params Object containing quest parameters
   * @returns A quest interaction object
   */
  public createQuestInteraction(params: QuestInteractionParams): POIInteraction {
    const { title, description, requirements, rewards, onAccept, onDecline } = params;

    if (!title || !description) {
      throw new Error('Quest interaction must have a title and description');
    }

    return {
      id: uuidv4(),
      type: 'quest',
      title,
      description,
      requirements,
      options: [
        {
          id: uuidv4(),
          text: 'Accept Quest',
          action: () => {
            onAccept();
            this.provideFeedback('quest_accept');
            // Log NPC quest accept interaction
            const interaction: NPCInteraction = {
              timestamp: Date.now(),
              type: 'quest_accept',
              targetId: '', // Use empty string if no quest giver ID
              outcome: 'positive',
            };
            NPCEventLoggingService.getInstance().logInteraction(
              'system', // or quest giver ID if available
              interaction,
              { quest: { title, description, requirements, rewards }, interactionType: 'quest_accept' }
            );
          },
        },
        {
          id: uuidv4(),
          text: 'Decline',
          action: () => {
            onDecline();
            this.provideFeedback('quest_decline');
            // Log NPC quest decline interaction
            const interaction: NPCInteraction = {
              timestamp: Date.now(),
              type: 'quest_decline',
              targetId: '', // Use empty string if no quest giver ID
              outcome: 'negative',
            };
            NPCEventLoggingService.getInstance().logInteraction(
              'system', // or quest giver ID if available
              interaction,
              { quest: { title, description, requirements, rewards }, interactionType: 'quest_decline' }
            );
          },
        },
      ],
    };
  }

  /**
   * Creates an information interaction with optional acknowledgment
   * @param title The title of the information
   * @param description The information content
   * @param onAcknowledge Optional callback when information is acknowledged
   * @returns An info interaction object
   */
  public createInfoInteraction(
    title: string,
    description: string,
    onAcknowledge?: () => void
  ): POIInteraction {
    if (!title || !description) {
      throw new Error('Info interaction must have a title and description');
    }

    return {
      id: uuidv4(),
      type: 'info',
      title,
      description,
      options: onAcknowledge
        ? [
            {
              id: uuidv4(),
              text: 'Acknowledge',
              action: () => {
                onAcknowledge();
                this.provideFeedback('info_acknowledge');
              },
            },
          ]
        : undefined,
    };
  }

  /**
   * Generates interactions for a POI based on its entities and features
   * @param poi The POI to generate interactions for
   * @returns Array of generated interactions
   */
  public generateInteractionsForPOI(poi: POI): POIInteraction[] {
    if (!poi || !poi.id) {
      throw new Error('Invalid POI provided');
    }

    const interactions: POIInteraction[] = [];

    // Generate interactions for each entity in the POI
    if (poi.chunks) {
      Object.values(poi.chunks).forEach((chunk: POIChunk) => {
        if (chunk.entities) {
          Object.values(chunk.entities).forEach((entity: POIEntity) => {
            if (!entity || !entity.type) return;

            switch (entity.type.toLowerCase()) {
              case 'npc':
                interactions.push(
                  this.createDialogueInteraction(entity, [
                    {
                      text: 'Talk',
                      action: () => {
                        // Handle NPC dialogue
                        console.log(`Starting dialogue with ${entity.name}`);
                      },
                    },
                  ])
                );
                break;
              case 'quest_giver':
                interactions.push(
                  this.createQuestInteraction({
                    title: 'New Quest',
                    description: 'Would you like to accept this quest?',
                    requirements: [],
                    rewards: [],
                    onAccept: () => {
                      console.log(`Quest accepted from ${entity.name}`);
                    },
                    onDecline: () => {
                      console.log(`Quest declined from ${entity.name}`);
                    }
                  })
                );
                break;
              default:
                // Log unhandled entity types for debugging
                console.debug(`Unhandled entity type: ${entity.type}`);
                break;
            }
          });
        }
      });
    }

    // Generate interactions for POI features
    if (poi.features && Array.isArray(poi.features)) {
      poi.features.forEach((feature: POIFeature) => {
        if (!feature.type || !feature.properties) return;

        interactions.push(
          this.createInfoInteraction(
            feature.type,
            JSON.stringify(feature.properties),
            () => {
              console.log(`Feature ${feature.type} acknowledged`);
            }
          )
        );
      });
    }

    return interactions;
  }

  /**
   * Provides feedback based on the interaction type
   * @param type The type of feedback to provide
   */
  private provideFeedback(type: FeedbackType): void {
    if (!this.feedbackCallbacks) {
      console.warn('No feedback callbacks set');
      return;
    }

    switch (type) {
      case 'dialogue':
        this.feedbackCallbacks.audio?.('dialogue_complete');
        this.feedbackCallbacks.haptic?.('short');
        break;
      case 'quest_accept':
        this.feedbackCallbacks.visual?.('Quest accepted!');
        this.feedbackCallbacks.audio?.('quest_accept');
        this.feedbackCallbacks.haptic?.('medium');
        break;
      case 'quest_decline':
        this.feedbackCallbacks.audio?.('quest_decline');
        this.feedbackCallbacks.haptic?.('short');
        break;
      case 'info_acknowledge':
        this.feedbackCallbacks.audio?.('info_acknowledge');
        this.feedbackCallbacks.haptic?.('short');
        break;
      default:
        const _exhaustiveCheck: never = type;
        break;
    }
  }

  /**
   * Starts an interaction with a POI
   * @param poiId The ID of the POI to interact with
   * @throws Error if POI is not found
   */
  public startInteraction(poiId: string): void {
    if (!poiId) {
      throw new Error('POI ID is required');
    }

    const store = usePoiStore.getState();
    const poi = store.getPOI(poiId);

    if (!poi) {
      throw new Error(`POI with id ${poiId} not found`);
    }

    store.setCurrentPOI(poiId);
  }

  /**
   * Ends the current POI interaction
   */
  public endInteraction(): void {
    const store = usePoiStore.getState();
    store.setCurrentPOI(null);
  }

  /**
   * Updates a POI with new data
   * @param poiId The ID of the POI to update
   * @param updates Partial POI object with updates
   * @throws Error if POI is not found
   */
  public updatePOI(poiId: string, updates: Partial<POI>): void {
    if (!poiId) {
      throw new Error('POI ID is required');
    }

    const store = usePoiStore.getState();
    const poi = store.getPOI(poiId);

    if (!poi) {
      throw new Error(`POI with id ${poiId} not found`);
    }

    store.updatePOI(poiId, updates);
  }

  /**
   * Removes a POI from the store
   * @param poiId The ID of the POI to remove
   * @throws Error if POI is not found
   */
  public removePOI(poiId: string): void {
    if (!poiId) {
      throw new Error('POI ID is required');
    }

    const store = usePoiStore.getState();
    const poi = store.getPOI(poiId);

    if (!poi) {
      throw new Error(`POI with id ${poiId} not found`);
    }

    store.removePOI(poiId);
  }
}

export default POIInteractionManager;
