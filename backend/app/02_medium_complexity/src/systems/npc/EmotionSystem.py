from typing import Any



class EmotionalState:
    primary: str
    intensity: float
    secondary?: str
    duration?: float
class EmotionSystem {
  private readonly baseEmotions = [
    'happy',
    'angry',
    'sad',
    'afraid',
    'surprised',
    'disgusted',
    'neutral'
  ]
  constructor() {}
  public async processInteractionEmotion(
    npc: NPCData,
    result: InteractionResult
  ): Promise<string> {
    const emotionalState = await this.calculateEmotionalResponse(npc, result)
    return this.generateEmotionalResponse(emotionalState)
  }
  private async calculateEmotionalResponse(
    npc: NPCData,
    result: InteractionResult
  ): Promise<EmotionalState> {
    let primary = 'neutral'
    let intensity = 0.5
    if (result.success) {
      primary = 'happy'
      intensity = 0.7
    } else {
      primary = 'angry'
      intensity = 0.6
    }
    if (result.reputationChange) {
      if (result.reputationChange > 0.1) {
        primary = 'happy'
        intensity = Math.min(1, intensity + 0.2)
      } else if (result.reputationChange < -0.1) {
        primary = 'angry'
        intensity = Math.min(1, intensity + 0.2)
      }
    }
    intensity = this.adjustIntensityForPersonality(npc, primary, intensity)
    return {
      primary,
      intensity,
      duration: this.calculateEmotionDuration(intensity)
    }
  }
  private adjustIntensityForPersonality(
    npc: NPCData,
    emotion: str,
    baseIntensity: float
  ): float {
    let intensity = baseIntensity
    if (emotion === 'angry') {
      intensity *= (1 + npc.personality.aggressiveness * 0.5)
    } else if (emotion === 'happy') {
      intensity *= (1 + npc.personality.friendliness * 0.3)
    }
    if (npc.personality.cautiousness > 0.7) {
      intensity *= 0.8 
    }
    return Math.min(1, Math.max(0, intensity))
  }
  private calculateEmotionDuration(intensity: float): float {
    const baseTime = 5000 
    return Math.floor(baseTime * (1 + intensity))
  }
  private generateEmotionalResponse(state: EmotionalState): str {
    const intensityDescriptors = {
      low: ['slightly', 'mildly', 'somewhat'],
      medium: ['noticeably', 'visibly', 'clearly'],
      high: ['very', 'extremely', 'intensely']
    }
    let intensityLevel: keyof typeof intensityDescriptors
    if (state.intensity < 0.4) intensityLevel = 'low'
    else if (state.intensity < 0.7) intensityLevel = 'medium'
    else intensityLevel = 'high'
    const descriptor = intensityDescriptors[intensityLevel][
      Math.floor(Math.random() * intensityDescriptors[intensityLevel].length)
    ]
    const emotionDescriptions = {
      happy: ['pleased', 'satisfied', 'content'],
      angry: ['upset', 'agitated', 'irritated'],
      sad: ['disappointed', 'disheartened', 'downcast'],
      afraid: ['nervous', 'anxious', 'worried'],
      surprised: ['startled', 'astonished', 'taken aback'],
      disgusted: ['repulsed', 'revolted', 'offended'],
      neutral: ['composed', 'reserved', 'indifferent']
    }
    const emotion = emotionDescriptions[state.primary as keyof typeof emotionDescriptions][
      Math.floor(Math.random() * emotionDescriptions[state.primary as keyof typeof emotionDescriptions].length)
    ]
    return `${descriptor} ${emotion}`
  }
} 