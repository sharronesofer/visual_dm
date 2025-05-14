from typing import Any, Dict


class EnhancedDialogueManager {
  private emotionSystem: EmotionSystem
  private memoryManager: MemoryManager
  private gptService: GPTServiceWrapper
  private errorHandler: LLMErrorHandler
  private logger: LoggerService
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
  }
  constructor(emotionSystem: EmotionSystem, memoryManager: MemoryManager) {
    this.emotionSystem = emotionSystem
    this.memoryManager = memoryManager
    this.gptService = GPTServiceWrapper.getInstance()
    this.errorHandler = LLMErrorHandler.getInstance()
    this.logger = LoggerService.getInstance()
    this.errorHandler.updateConfig({
      fallbackLibrary: Dict[str, Any]
    })
  }
  public async generateDialogue(
    npc: NPCData,
    context: InteractionContext
  ): Promise<DialogueResponse> {
    const emotionalState = await this.emotionSystem.getCurrentEmotionalState(npc.id)
    const relevantMemories = await this.memoryManager.getRelevantMemories(
      npc.id,
      context.type,
      context.targetId
    )
    let response: DialogueResponse
    try {
      switch (context.type) {
        case InteractionType.MENTORING:
          response = await this.generateMentoringDialogue(npc, context, emotionalState)
          break
        case InteractionType.CONFLICT_RESOLUTION:
          response = await this.generateConflictResolutionDialogue(npc, context, emotionalState)
          break
        case InteractionType.SOCIAL_BONDING:
          response = await this.generateSocialBondingDialogue(npc, context, emotionalState)
          break
        case InteractionType.INFORMATION_SHARING:
          response = await this.generateInformationSharingDialogue(npc, context, emotionalState)
          break
        case InteractionType.GROUP_DECISION:
          response = await this.generateGroupDecisionDialogue(npc, context, emotionalState)
          break
        default:
          response = await this.generateDefaultDialogue(npc, context, emotionalState)
      }
      response.tone = this.adjustToneForRelationship(
        response.tone,
        context.socialContext?.relationship || 0,
        npc.personality
      )
      return response
    } catch (error) {
      const errorContext: LLMErrorContext = {
        timestamp: Date.now(),
        characterId: npc.id,
        gameState: Dict[str, Any],
        errorDetails: error
      }
      const errorType = this.errorHandler.identifyErrorType(error as Error)
      this.errorHandler.logError(errorType, errorContext)
      return this.createFallbackResponse(npc, context.type, emotionalState)
    }
  }
  /**
   * Generate dialogue using GPT service with error handling
   */
  private async generateDialogueWithPrompt(
    npc: NPCData,
    prompt: str,
    contextType: str,
    emotionalState: str
  ): Promise<string> {
    try {
      return await this.gptService.generateText(prompt, {
        maxTokens: 200,
        temperature: 0.7,
        contextType,
        characterId: npc.id,
        gameState: Dict[str, Any]
      })
    } catch (error) {
      this.logger.error('Failed to generate dialogue even with error handling', { error, npcId: npc.id, contextType })
      return this.getFallbackDialogueText(contextType)
    }
  }
  /**
   * Create a fallback response when dialogue generation fails
   */
  private createFallbackResponse(
    npc: NPCData,
    contextType: str,
    emotionalState: str
  ): DialogueResponse {
    const message = this.getFallbackDialogueText(contextType)
    const tone = this.getFallbackTone(npc.personality, contextType)
    return {
      message,
      tone,
      emotionalState,
      subtext: 'Fallback response due to LLM error',
      followUp: this.getFallbackFollowUp(contextType)
    }
  }
  /**
   * Get appropriate fallback text based on context type
   */
  private getFallbackDialogueText(contextType: str): str {
    const contextKey = this.contextTypeToKey(contextType)
    const fallbacks = this.fallbackResponses[contextKey] || this.fallbackResponses.default
    const index = Math.floor(Math.random() * fallbacks.length)
    return fallbacks[index]
  }
  /**
   * Get appropriate fallback tone based on personality and context
   */
  private getFallbackTone(personality: NPCData['personality'], contextType: str): str {
    switch (this.contextTypeToKey(contextType)) {
      case 'mentoring':
        return 'patient and thoughtful'
      case 'conflict_resolution':
        return 'measured and diplomatic'
      case 'social_bonding':
        return 'warm and genuine'
      case 'information_sharing':
        return 'informative and careful'
      case 'group_decision':
        return 'collaborative and considerate'
      default:
        return 'neutral and composed'
    }
  }
  /**
   * Get follow-up options for fallback responses
   */
  private getFallbackFollowUp(contextType: str): string[] {
    switch (this.contextTypeToKey(contextType)) {
      case 'mentoring':
        return [
          'Would you like me to explain differently?',
          'Do you have any specific questions?',
          'Let me know if you need clarification.'
        ]
      case 'conflict_resolution':
        return [
          'What are your thoughts on this?',
          'How do you see the situation?',
          'What outcome would you prefer?'
        ]
      case 'social_bonding':
        return [
          'Tell me more about yourself.',
          'What brings you to these parts?',
          'What interests you most these days?'
        ]
      case 'information_sharing':
        return [
          'Is there something specific you want to know?',
          'What details are most important to you?',
          'How much do you already know about this?'
        ]
      case 'group_decision':
        return [
          'What option do you favor?',
          'How should we proceed?',
          'What factors seem most important to consider?'
        ]
      default:
        return [
          'What else would you like to discuss?',
          'Is there something specific on your mind?',
          'How can I assist you further?'
        ]
    }
  }
  /**
   * Convert InteractionType to a key used in our fallback map
   */
  private contextTypeToKey(contextType: str): str {
    const typeKey = contextType.toLowerCase().replace(/\s+/g, '_')
    if (Object.keys(this.fallbackResponses).includes(typeKey)) {
      return typeKey
    }
    return 'default'
  }
  /**
   * The following methods are enhanced versions of the original DialogueManager methods,
   * now using the GPTServiceWrapper for robust error handling
   */
  private async generateMentoringDialogue(
    npc: NPCData,
    context: InteractionContext,
    emotionalState: str
  ): Promise<DialogueResponse> {
    const { effectiveness = 0.5 } = context.data || {}
    const teachingStyle = this.getTeachingStyle(npc.personality)
    const prompt = `
      Generate a mentoring dialogue for an NPC named ${npc.name} who is a ${npc.type} with ${teachingStyle} teaching style.
      The NPC is currently in a ${emotionalState} emotional state.
      The teaching effectiveness is ${effectiveness > 0.7 ? 'high' : 'moderate to low'}.
      The dialogue should convey mentorship and guidance appropriate to the character.
      Response should be about 2-3 sentences long and in first person.
    `
    const message = await this.generateDialogueWithPrompt(npc, prompt, 'mentoring', emotionalState)
    const followUp = [
      'Would you like me to elaborate on any part?',
      'Let\'s practice this concept together.',
      'How does this align with your understanding?'
    ]
    const tone = effectiveness > 0.7 ? 'patient and encouraging' : 'methodical and supportive'
    return {
      message,
      tone,
      emotionalState,
      followUp,
      subtext: `Teaching effectiveness: ${effectiveness}`
    }
  }
  private async generateConflictResolutionDialogue(
    npc: NPCData,
    context: InteractionContext,
    emotionalState: str
  ): Promise<DialogueResponse> {
    const { resolutionChance = 0.5, conflict = 'unspecified dispute' } = context.data || {}
    const approach = this.getConflictResolutionApproach(npc.personality)
    const prompt = `
      Generate a conflict resolution dialogue for an NPC named ${npc.name} who is a ${npc.type} with a ${approach} approach to conflict.
      The NPC is currently in a ${emotionalState} emotional state.
      The conflict involves: "${conflict}"
      The chance of resolution is ${resolutionChance > 0.6 ? 'high' : 'uncertain'}.
      The dialogue should reflect their attempt to resolve the conflict.
      Response should be about 2-3 sentences long and in first person.
    `
    const message = await this.generateDialogueWithPrompt(npc, prompt, 'conflict_resolution', emotionalState)
    const followUp = resolutionChance > 0.6
      ? [
          'What are your thoughts on this approach?',
          'How can we make this work for you?',
          'Let\'s focus on our shared goals.'
        ]
      : [
          'What are your main concerns?',
          'Let\'s take a step back and reassess.',
          'Perhaps we can find some common ground.'
        ]
    const tone = resolutionChance > 0.6 ? 'diplomatic and constructive' : 'cautious but open'
    return {
      message,
      tone,
      emotionalState,
      followUp,
      subtext: `Conflict resolution approach: ${approach}`
    }
  }
  private async generateSocialBondingDialogue(
    npc: NPCData,
    context: InteractionContext,
    emotionalState: str
  ): Promise<DialogueResponse> {
    const { bondingScore = 0.5, activity = 'spending time together' } = context.data || {}
    const socialStyle = this.getSocialStyle(npc.personality)
    const prompt = `
      Generate a social bonding dialogue for an NPC named ${npc.name} who is a ${npc.type} with a ${socialStyle} social style.
      The NPC is currently in a ${emotionalState} emotional state.
      They have been ${activity} with the player.
      The bonding score is ${bondingScore > 0.7 ? 'high' : 'moderate to low'}.
      The dialogue should reflect their feelings about the social interaction.
      Response should be about 2-3 sentences long and in first person.
    `
    const message = await this.generateDialogueWithPrompt(npc, prompt, 'social_bonding', emotionalState)
    const followUp = bondingScore > 0.7
      ? [
          'We should do this again sometime.',
          'What other interests do we share?',
          'This has been really enjoyable.'
        ]
      : [
          'What are your thoughts on this?',
          'Perhaps we could try something different next time.',
          'Tell me more about your interests.'
        ]
    const tone = bondingScore > 0.7 ? 'warm and genuine' : 'polite and measured'
    return {
      message,
      tone,
      emotionalState,
      followUp,
      subtext: `Social bonding style: ${socialStyle}`
    }
  }
  private async generateInformationSharingDialogue(
    npc: NPCData,
    context: InteractionContext,
    emotionalState: str
  ): Promise<DialogueResponse> {
    const { sharingEffectiveness = 0.5, information = 'general knowledge' } = context.data || {}
    const trustLevel = context.socialContext?.relationship || 0
    const prompt = `
      Generate an information sharing dialogue for an NPC named ${npc.name} who is a ${npc.type} with trust level ${trustLevel}/100.
      The NPC is currently in a ${emotionalState} emotional state.
      The information to share is about: "${information}"
      The sharing effectiveness is ${sharingEffectiveness > 0.7 ? 'high' : 'moderate to low'}.
      The dialogue should convey information appropriate to the trust level.
      Response should be about 2-3 sentences long and in first person.
    `
    const message = await this.generateDialogueWithPrompt(npc, prompt, 'information_sharing', emotionalState)
    const followUp = sharingEffectiveness > 0.7
      ? [
          'Is there anything specific you want to know about this?',
          'I can elaborate if you\'re interested.',
          'What do you make of this information?'
        ]
      : [
          'I hope that helps somewhat.',
          'That\'s about all I know on the subject.',
          'Do you need any clarification?'
        ]
    const tone = sharingEffectiveness > 0.7 ? 'confidential and sincere' : 'cautious and reserved'
    return {
      message,
      tone,
      emotionalState,
      followUp,
      subtext: `Trust level: ${trustLevel}/100`
    }
  }
  private async generateGroupDecisionDialogue(
    npc: NPCData,
    context: InteractionContext,
    emotionalState: str
  ): Promise<DialogueResponse> {
    const { influenceScore = 0.5, decision = 'unspecified matter' } = context.data || {}
    const leadershipStyle = this.getLeadershipStyle(npc.personality)
    const prompt = `
      Generate a group decision dialogue for an NPC named ${npc.name} who is a ${npc.type} with a ${leadershipStyle} leadership style.
      The NPC is currently in a ${emotionalState} emotional state.
      The decision involves: "${decision}"
      The NPC's influence score is ${influenceScore > 0.7 ? 'high' : 'moderate to low'}.
      The dialogue should reflect their approach to group decision-making.
      Response should be about 2-3 sentences long and in first person.
    `
    const message = await this.generateDialogueWithPrompt(npc, prompt, 'group_decision', emotionalState)
    const followUp = influenceScore > 0.7
      ? [
          'What are your thoughts on this plan?',
          'Let\'s proceed if everyone agrees.',
          'Does anyone have concerns to address?'
        ]
      : [
          'What alternatives should we consider?',
          'I\'d like to hear everyone\'s perspective.',
          'We need to carefully weigh our options.'
        ]
    const tone = influenceScore > 0.7 ? 'confident and decisive' : 'thoughtful and inclusive'
    return {
      message,
      tone,
      emotionalState,
      followUp,
      subtext: `Leadership style: ${leadershipStyle}`
    }
  }
  private async generateDefaultDialogue(
    npc: NPCData,
    context: InteractionContext,
    emotionalState: str
  ): Promise<DialogueResponse> {
    const relationshipLevel = context.socialContext?.relationship || 0
    const prompt = `
      Generate a general dialogue for an NPC named ${npc.name} who is a ${npc.type}.
      The NPC is currently in a ${emotionalState} emotional state.
      The relationship level with the player is ${relationshipLevel}/100.
      Response should be about 2-3 sentences long, appropriate to the relationship level, and in first person.
    `
    const message = await this.generateDialogueWithPrompt(npc, prompt, 'default', emotionalState)
    const followUp = [
      'Is there something specific you needed?',
      'How can I assist you today?',
      'Was there anything else?'
    ]
    const tone = relationshipLevel > 70 ? 'friendly and open' : relationshipLevel > 30 ? 'neutral and polite' : 'distant and reserved'
    return {
      message,
      tone,
      emotionalState,
      followUp
    }
  }
  private getTeachingStyle(personality: NPCData['personality']): str {
    return personality.conscientiousness > 70 ? 'methodical' :
           personality.openness > 70 ? 'explorative' :
           personality.agreeableness > 70 ? 'supportive' :
           'pragmatic'
  }
  private getConflictResolutionApproach(personality: NPCData['personality']): str {
    return personality.agreeableness > 70 ? 'collaborative' :
           personality.extraversion > 70 ? 'direct' :
           personality.neuroticism > 70 ? 'cautious' :
           'analytical'
  }
  private getSocialStyle(personality: NPCData['personality']): str {
    return personality.extraversion > 70 ? 'outgoing' :
           personality.agreeableness > 70 ? 'warm' :
           personality.openness > 70 ? 'curious' :
           'reserved'
  }
  private getLeadershipStyle(personality: NPCData['personality']): str {
    return personality.conscientiousness > 70 ? 'organized' :
           personality.extraversion > 70 ? 'inspirational' :
           personality.agreeableness > 70 ? 'democratic' :
           'pragmatic'
  }
  private adjustToneForRelationship(
    baseTone: str,
    relationship: float,
    personality: NPCData['personality']
  ): str {
    if (relationship > 80) {
      return `${baseTone}, friendly and comfortable`
    } else if (relationship > 50) {
      return `${baseTone}, relaxed`
    } else if (relationship > 20) {
      return `${baseTone}, polite`
    } else {
      return `${baseTone}, formal`
    }
  }
} 