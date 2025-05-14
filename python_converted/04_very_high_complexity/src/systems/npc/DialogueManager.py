from typing import Any, Dict, List



class DialogueResponse:
    message: str
    tone: str
    emotionalState: str
    subtext?: str
    followUp?: List[str]
class DialogueManager {
  private emotionSystem: EmotionSystem
  private memoryManager: MemoryManager
  constructor(emotionSystem: EmotionSystem, memoryManager: MemoryManager) {
    this.emotionSystem = emotionSystem
    this.memoryManager = memoryManager
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
    let response: \'DialogueResponse\'
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
  }
  private async generateMentoringDialogue(
    npc: NPCData,
    context: InteractionContext,
    emotionalState: str
  ): Promise<DialogueResponse> {
    const { effectiveness } = context.data
    const teachingStyle = this.getTeachingStyle(npc.personality)
    let message = ''
    let tone = ''
    let followUp: List[string] = []
    if (effectiveness > 0.7) {
      message = `${this.getEncouragement(teachingStyle)} Let me explain this concept clearly...`
      tone = 'patient and encouraging'
      followUp = [
        'Would you like me to elaborate on any part?',
        'Let\'s practice this concept together.',
        'How does this align with your understanding?'
      ]
    } else {
      message = `Let's approach this step by step...`
      tone = 'methodical and supportive'
      followUp = [
        'Tell me what part is unclear.',
        'Let\'s try a different approach.',
        'Perhaps we should review the basics first.'
      ]
    }
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
    const { resolutionChance, conflict } = context.data
    const approach = this.getConflictResolutionApproach(npc.personality)
    let message = ''
    let tone = ''
    let followUp: List[string] = []
    if (resolutionChance > 0.6) {
      message = `I believe we can find a solution that works for everyone...`
      tone = 'diplomatic and constructive'
      followUp = [
        'What are your thoughts on this approach?',
        'How can we make this work for you?',
        'Let\'s focus on our shared goals.'
      ]
    } else {
      message = `We need to address these concerns carefully...`
      tone = 'cautious but open'
      followUp = [
        'What are your main concerns?',
        'Let\'s take a step back and reassess.',
        'Perhaps we can find some common ground.'
      ]
    }
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
    const { bondingScore, activity } = context.data
    const socialStyle = this.getSocialStyle(npc.personality)
    let message = ''
    let tone = ''
    let followUp: List[string] = []
    if (bondingScore > 0.7) {
      message = `I've really enjoyed ${activity} with you. It's been wonderful...`
      tone = 'warm and genuine'
      followUp = [
        'We should do this again sometime.',
        'What other interests do we share?',
        'This has been really enjoyable.'
      ]
    } else {
      message = `This ${activity} has been interesting...`
      tone = 'polite and measured'
      followUp = [
        'What are your thoughts on this?',
        'Perhaps we could try something different next time.',
        'Tell me more about your interests.'
      ]
    }
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
    const { sharingEffectiveness, information } = context.data
    const trustLevel = context.socialContext?.relationship || 0
    let message = ''
    let tone = ''
    let followUp: List[string] = []
    if (sharingEffectiveness > 0.7) {
      message = `I trust you with this information...`
      tone = 'confidential and sincere'
      followUp = [
        'Please keep this between us.',
        'What are your thoughts on this?',
        'This could be important for both of us.'
      ]
    } else {
      message = `There's something you might want to know...`
      tone = 'cautious and reserved'
      followUp = [
        'I hope you understand the sensitivity of this.',
        'Let\'s keep this discreet.',
        'What do you make of this?'
      ]
    }
    return {
      message,
      tone,
      emotionalState,
      followUp,
      subtext: `Trust level: ${trustLevel}`
    }
  }
  private async generateGroupDecisionDialogue(
    npc: NPCData,
    context: InteractionContext,
    emotionalState: str
  ): Promise<DialogueResponse> {
    const { influenceScore, proposal } = context.data
    const leadershipStyle = this.getLeadershipStyle(npc.personality)
    let message = ''
    let tone = ''
    let followUp: List[string] = []
    if (influenceScore > 0.7) {
      message = `I believe this proposal offers significant benefits for the group...`
      tone = 'confident and persuasive'
      followUp = [
        'What are your thoughts on this approach?',
        'How can we make this work for everyone?',
        'Let\'s discuss the implementation details.'
      ]
    } else {
      message = `We should carefully consider all aspects of this proposal...`
      tone = 'thoughtful and inclusive'
      followUp = [
        'What concerns do you have?',
        'Are there alternatives we should consider?',
        'Let\'s hear everyone\'s perspective.'
      ]
    }
    return {
      message,
      tone,
      emotionalState,
      followUp,
      subtext: `Leadership style: ${leadershipStyle}`
    }
  }
  private getTeachingStyle(personality: NPCData['personality']): str {
    if (personality.empathy > 0.7) return 'nurturing'
    if (personality.intelligence > 0.7) return 'analytical'
    if (personality.charisma > 0.7) return 'inspiring'
    return 'practical'
  }
  private getConflictResolutionApproach(personality: NPCData['personality']): str {
    if (personality.diplomacy > 0.7) return 'mediator'
    if (personality.assertiveness > 0.7) return 'direct'
    if (personality.empathy > 0.7) return 'empathetic'
    return 'pragmatic'
  }
  private getSocialStyle(personality: NPCData['personality']): str {
    if (personality.extraversion > 0.7) return 'outgoing'
    if (personality.empathy > 0.7) return 'supportive'
    if (personality.charisma > 0.7) return 'charming'
    return 'reserved'
  }
  private getLeadershipStyle(personality: NPCData['personality']): str {
    if (personality.leadership > 0.7) return 'authoritative'
    if (personality.empathy > 0.7) return 'democratic'
    if (personality.intelligence > 0.7) return 'strategic'
    return 'collaborative'
  }
  private getEncouragement(style: str): str {
    const encouragements = {
      nurturing: "You're doing great! ",
      analytical: "Let's examine this systematically. ",
      inspiring: "I believe you can master this! ",
      practical: "Here's how we'll approach this. "
    }
    return encouragements[style as keyof typeof encouragements] || "Let's continue. "
  }
  private adjustToneForRelationship(
    baseTone: str,
    relationship: float,
    personality: NPCData['personality']
  ): str {
    if (relationship > 0.8) {
      return personality.friendliness > 0.7 ? 'warm and familiar' : 'respectful and friendly'
    } else if (relationship > 0.5) {
      return personality.friendliness > 0.7 ? 'friendly and open' : 'polite and professional'
    } else if (relationship > 0.2) {
      return personality.cautiousness > 0.7 ? 'reserved and formal' : 'neutral and professional'
    } else {
      return personality.aggressiveness > 0.7 ? 'distant and guarded' : 'formal and detached'
    }
  }
  private async generateDefaultDialogue(
    npc: NPCData,
    context: InteractionContext,
    emotionalState: str
  ): Promise<DialogueResponse> {
    return {
      message: 'I acknowledge your presence.',
      tone: 'neutral',
      emotionalState,
      followUp: ['How may I assist you?']
    }
  }
  public async generateNegotiationResponse(npc: NPCData, offerQuality: float): Promise<string> {
    const baseResponses = {
      excellent: [
        "That's a very generous offer!",
        "I'd be foolish to refuse such terms.",
        "You drive a fair bargain."
      ],
      good: [
        "That seems reasonable.",
        "I can work with those terms.",
        "A fair offer, indeed."
      ],
      fair: [
        "Hmm, I was hoping for a bit more.",
        "Could you sweeten the deal?",
        "Let's discuss this further."
      ],
      poor: [
        "That's far below what I'd accept.",
        "You'll need to do better than that.",
        "I'm afraid that won't work for me."
      ]
    }
    let responsePool
    if (offerQuality >= 0.9) responsePool = baseResponses.excellent
    else if (offerQuality >= 0.7) responsePool = baseResponses.good
    else if (offerQuality >= 0.5) responsePool = baseResponses.fair
    else responsePool = baseResponses.poor
    return responsePool[Math.floor(Math.random() * responsePool.length)]
  }
  public async generateDeceptionResponse(npc: NPCData, detected: bool): Promise<string> {
    const responses = {
      detected: [
        "You're not being truthful with me...",
        "I can tell you're lying.",
        "Do you take me for a fool?"
      ],
      undetected: [
        "I see...",
        "That makes sense.",
        "I understand completely."
      ]
    }
    const responsePool = detected ? responses.detected : responses.undetected
    return responsePool[Math.floor(Math.random() * responsePool.length)]
  }
  public async generateCooperationRejection(npc: NPCData): Promise<string> {
    const responses = [
      "I don't think we can work together right now.",
      "Our goals are too different.",
      "Perhaps another time.",
      "I need to focus on my own priorities."
    ]
    return responses[Math.floor(Math.random() * responses.length)]
  }
  public async generateCooperationAgreement(npc: NPCData, benefits: Any): Promise<string> {
    const responses = [
      "I think we can help each other.",
      "Working together would benefit us both.",
      "Let's combine our efforts.",
      "I'm willing to cooperate with you."
    ]
    return responses[Math.floor(Math.random() * responses.length)]
  }
  public async generateCompetitionResponse(
    npc: NPCData,
    response: Dict[str, Any]
  ): Promise<string> {
    const responses = {
      accepted: Dict[str, Any],
      rejected: [
        "I have no interest in competing with you.",
        "Find someone else for your challenge.",
        "This isn't worth my time."
      ]
    }
    if (!response.accepted) {
      return responses.rejected[Math.floor(Math.random() * responses.rejected.length)]
    }
    const intensityPool = responses.accepted[response.intensity as keyof typeof responses.accepted]
    return intensityPool[Math.floor(Math.random() * intensityPool.length)]
  }
} 