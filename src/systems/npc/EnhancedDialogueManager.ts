import { NPCData } from '../../types/npc/npc';
import { InteractionContext, InteractionType } from './InteractionSystem';
import { EmotionSystem } from './EmotionSystem';
import { MemoryManager } from '../memory/MemoryManager';
import { DialogueResponse } from '../../types/npc/DialogueManager';
import { GPTServiceWrapper } from '../../core/services/GPTServiceWrapper';
import { LLMErrorHandler, LLMErrorType, LLMErrorContext } from '../../core/services/LLMErrorHandler';
import { LoggerService } from '../../core/services/LoggerService';
import { DialogueConfigurationManager } from '../../dialogue/config/DialogueConfigurationManager';

export class EnhancedDialogueManager {
  private emotionSystem: EmotionSystem;
  private memoryManager: MemoryManager;
  private gptService: GPTServiceWrapper;
  private errorHandler: LLMErrorHandler;
  private logger: LoggerService;
  private configManager: DialogueConfigurationManager;

  // Pre-defined fallback responses for different dialogue types
  private fallbackResponses: Record<string, string[]> = {
    'mentoring': [
      "Let me consider how best to explain this...",
      "There's an important principle here I want to make sure I convey clearly.",
      "Let's approach this systematically so it's easier to understand.",
      "This is something that takes practice to master, but I'll guide you through it.",
      "The fundamentals here are quite important to grasp first."
    ],
    'conflict_resolution': [
      "Let's take a step back and look at this objectively.",
      "I think we should focus on finding common ground here.",
      "There might be a way to resolve this that works for everyone.",
      "I understand this is a difficult situation, but I believe we can work through it.",
      "Let's consider what's most important here and focus on that."
    ],
    'social_bonding': [
      "I've enjoyed our time together.",
      "It's good to share moments like these.",
      "I find these conversations quite meaningful.",
      "There's something special about connecting with others, isn't there?",
      "I appreciate your company and our discussions."
    ],
    'information_sharing': [
      "Let me gather my thoughts on that matter...",
      "That's an interesting question that requires careful consideration.",
      "I have some knowledge on that topic, but let me organize my thoughts.",
      "There are several aspects to consider here.",
      "I want to make sure I give you accurate information about that."
    ],
    'group_decision': [
      "We should consider all perspectives before deciding.",
      "It's important we reach a consensus that works for the group.",
      "Let's weigh our options carefully before proceeding.",
      "I think we need to evaluate the risks and benefits together.",
      "Each of us brings valuable insights to this decision."
    ],
    'default': [
      "I need a moment to gather my thoughts.",
      "Let me consider how to respond to that.",
      "That's an interesting point to consider.",
      "I'm reflecting on what you've said.",
      "I appreciate your patience as I think about this."
    ]
  };

  constructor(emotionSystem: EmotionSystem, memoryManager: MemoryManager, configManager: DialogueConfigurationManager) {
    this.emotionSystem = emotionSystem;
    this.memoryManager = memoryManager;
    this.gptService = GPTServiceWrapper.getInstance();
    this.errorHandler = LLMErrorHandler.getInstance();
    this.logger = LoggerService.getInstance();
    this.configManager = configManager;

    // Update the error handler with our dialogue-specific fallbacks
    this.errorHandler.updateConfig({
      fallbackLibrary: {
        'mentoring': this.fallbackResponses.mentoring,
        'conflict_resolution': this.fallbackResponses.conflict_resolution,
        'social_bonding': this.fallbackResponses.social_bonding,
        'information_sharing': this.fallbackResponses.information_sharing,
        'group_decision': this.fallbackResponses.group_decision,
        'default': this.fallbackResponses.default
      }
    });
  }

  public async generateDialogue(
    npc: NPCData,
    context: InteractionContext
  ): Promise<DialogueResponse> {
    // Use scenario-based prompt template if available
    const scenario = context.type?.toLowerCase() || 'default';
    let promptTemplate = this.configManager.getPromptTemplate(scenario) || this.configManager.getPromptTemplate('default') || '';
    // Replace template variables
    const prompt = promptTemplate
      .replace(/{{npcName}}/g, npc.name)
      .replace(/{{npcRole}}/g, (npc.groupAffiliations?.[0]?.role || 'npc'));

    // Get emotional state for dialogue tone
    const emotionalState = await this.emotionSystem.getCurrentEmotionalState(npc.id);

    // Get relevant memories for context
    const relevantMemories = await this.memoryManager.getRelevantMemories(
      npc.id,
      context.type,
      context.targetId
    );

    let response: DialogueResponse;

    try {
      // Generate dialogue using config
      const response = await this.gptService.generateCompletion(prompt, [], this.configManager.getConfig());

      // Adjust tone based on relationship and personality
      response.tone = this.adjustToneForRelationship(
        response.tone,
        context.socialContext?.relationship || 0,
        npc.personality
      );

      return response;
    } catch (error) {
      // Log the error with our centralized error handler
      const errorContext: LLMErrorContext = {
        timestamp: Date.now(),
        characterId: npc.id,
        gameState: {
          interactionType: context.type,
          emotionalState,
          socialContext: context.socialContext
        },
        errorDetails: error
      };

      const errorType = this.errorHandler.identifyErrorType(error as Error);
      this.errorHandler.logError(errorType, errorContext);

      // Create a fallback response
      return this.createFallbackResponse(npc, context.type, emotionalState);
    }
  }

  /**
   * Create a fallback response when dialogue generation fails
   */
  private createFallbackResponse(
    npc: NPCData,
    contextType: string,
    emotionalState: string
  ): DialogueResponse {
    const message = this.getFallbackDialogueText(contextType);
    const tone = this.getFallbackTone(npc.personality, contextType);

    return {
      message,
      tone,
      emotionalState,
      subtext: 'Fallback response due to LLM error',
      followUp: this.getFallbackFollowUp(contextType)
    };
  }

  /**
   * Get appropriate fallback text based on context type
   */
  private getFallbackDialogueText(contextType: string): string {
    const contextKey = this.contextTypeToKey(contextType);
    const fallbacks = this.fallbackResponses[contextKey] || this.fallbackResponses.default;
    const index = Math.floor(Math.random() * fallbacks.length);
    return fallbacks[index];
  }

  /**
   * Get appropriate fallback tone based on personality and context
   */
  private getFallbackTone(personality: NPCData['personality'], contextType: string): string {
    switch (this.contextTypeToKey(contextType)) {
      case 'mentoring':
        return 'patient and thoughtful';
      case 'conflict_resolution':
        return 'measured and diplomatic';
      case 'social_bonding':
        return 'warm and genuine';
      case 'information_sharing':
        return 'informative and careful';
      case 'group_decision':
        return 'collaborative and considerate';
      default:
        return 'neutral and composed';
    }
  }

  /**
   * Get follow-up options for fallback responses
   */
  private getFallbackFollowUp(contextType: string): string[] {
    switch (this.contextTypeToKey(contextType)) {
      case 'mentoring':
        return [
          'Would you like me to explain differently?',
          'Do you have any specific questions?',
          'Let me know if you need clarification.'
        ];
      case 'conflict_resolution':
        return [
          'What are your thoughts on this?',
          'How do you see the situation?',
          'What outcome would you prefer?'
        ];
      case 'social_bonding':
        return [
          'Tell me more about yourself.',
          'What brings you to these parts?',
          'What interests you most these days?'
        ];
      case 'information_sharing':
        return [
          'Is there something specific you want to know?',
          'What details are most important to you?',
          'How much do you already know about this?'
        ];
      case 'group_decision':
        return [
          'What option do you favor?',
          'How should we proceed?',
          'What factors seem most important to consider?'
        ];
      default:
        return [
          'What else would you like to discuss?',
          'Is there something specific on your mind?',
          'How can I assist you further?'
        ];
    }
  }

  /**
   * Convert InteractionType to a key used in our fallback map
   */
  private contextTypeToKey(contextType: string): string {
    const typeKey = contextType.toLowerCase().replace(/\s+/g, '_');
    if (Object.keys(this.fallbackResponses).includes(typeKey)) {
      return typeKey;
    }
    return 'default';
  }

  // The following utility methods are from the original DialogueManager

  private getTeachingStyle(personality: NPCData['personality']): string {
    // Simple mapping of personality traits to teaching styles
    return personality.conscientiousness > 70 ? 'methodical' :
      personality.openness > 70 ? 'explorative' :
        personality.agreeableness > 70 ? 'supportive' :
          'pragmatic';
  }

  private getConflictResolutionApproach(personality: NPCData['personality']): string {
    // Simple mapping of personality traits to conflict resolution approaches
    return personality.agreeableness > 70 ? 'collaborative' :
      personality.extraversion > 70 ? 'direct' :
        personality.neuroticism > 70 ? 'cautious' :
          'analytical';
  }

  private getSocialStyle(personality: NPCData['personality']): string {
    // Simple mapping of personality traits to social styles
    return personality.extraversion > 70 ? 'outgoing' :
      personality.agreeableness > 70 ? 'warm' :
        personality.openness > 70 ? 'curious' :
          'reserved';
  }

  private getLeadershipStyle(personality: NPCData['personality']): string {
    // Simple mapping of personality traits to leadership styles
    return personality.conscientiousness > 70 ? 'organized' :
      personality.extraversion > 70 ? 'inspirational' :
        personality.agreeableness > 70 ? 'democratic' :
          'pragmatic';
  }

  private adjustToneForRelationship(
    baseTone: string,
    relationship: number,
    personality: NPCData['personality']
  ): string {
    if (relationship > 80) {
      return `${baseTone}, friendly and comfortable`;
    } else if (relationship > 50) {
      return `${baseTone}, relaxed`;
    } else if (relationship > 20) {
      return `${baseTone}, polite`;
    } else {
      return `${baseTone}, formal`;
    }
  }
} 