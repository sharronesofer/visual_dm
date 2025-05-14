import { NPCData } from '../../types/npc/npc';
import { InteractionResult } from './InteractionSystem';

export interface EmotionalState {
  primary: string;
  intensity: number;
  secondary?: string;
  duration?: number;
}

export class EmotionSystem {
  private readonly baseEmotions = [
    'happy',
    'angry',
    'sad',
    'afraid',
    'surprised',
    'disgusted',
    'neutral'
  ];

  constructor() {}

  public async processInteractionEmotion(
    npc: NPCData,
    result: InteractionResult
  ): Promise<string> {
    const emotionalState = await this.calculateEmotionalResponse(npc, result);
    return this.generateEmotionalResponse(emotionalState);
  }

  private async calculateEmotionalResponse(
    npc: NPCData,
    result: InteractionResult
  ): Promise<EmotionalState> {
    let primary = 'neutral';
    let intensity = 0.5;

    // Base emotional response on interaction success/failure
    if (result.success) {
      primary = 'happy';
      intensity = 0.7;
    } else {
      primary = 'angry';
      intensity = 0.6;
    }

    // Modify based on reputation change
    if (result.reputationChange) {
      if (result.reputationChange > 0.1) {
        primary = 'happy';
        intensity = Math.min(1, intensity + 0.2);
      } else if (result.reputationChange < -0.1) {
        primary = 'angry';
        intensity = Math.min(1, intensity + 0.2);
      }
    }

    // Modify based on NPC personality
    intensity = this.adjustIntensityForPersonality(npc, primary, intensity);

    return {
      primary,
      intensity,
      duration: this.calculateEmotionDuration(intensity)
    };
  }

  private adjustIntensityForPersonality(
    npc: NPCData,
    emotion: string,
    baseIntensity: number
  ): number {
    let intensity = baseIntensity;

    // Personality trait modifiers
    if (emotion === 'angry') {
      intensity *= (1 + npc.personality.aggressiveness * 0.5);
    } else if (emotion === 'happy') {
      intensity *= (1 + npc.personality.friendliness * 0.3);
    }

    // General personality effects
    if (npc.personality.cautiousness > 0.7) {
      intensity *= 0.8; // More reserved emotional responses
    }

    return Math.min(1, Math.max(0, intensity));
  }

  private calculateEmotionDuration(intensity: number): number {
    // Duration in milliseconds, based on intensity
    const baseTime = 5000; // 5 seconds base
    return Math.floor(baseTime * (1 + intensity));
  }

  private generateEmotionalResponse(state: EmotionalState): string {
    const intensityDescriptors = {
      low: ['slightly', 'mildly', 'somewhat'],
      medium: ['noticeably', 'visibly', 'clearly'],
      high: ['very', 'extremely', 'intensely']
    };

    let intensityLevel: keyof typeof intensityDescriptors;
    if (state.intensity < 0.4) intensityLevel = 'low';
    else if (state.intensity < 0.7) intensityLevel = 'medium';
    else intensityLevel = 'high';

    const descriptor = intensityDescriptors[intensityLevel][
      Math.floor(Math.random() * intensityDescriptors[intensityLevel].length)
    ];

    const emotionDescriptions = {
      happy: ['pleased', 'satisfied', 'content'],
      angry: ['upset', 'agitated', 'irritated'],
      sad: ['disappointed', 'disheartened', 'downcast'],
      afraid: ['nervous', 'anxious', 'worried'],
      surprised: ['startled', 'astonished', 'taken aback'],
      disgusted: ['repulsed', 'revolted', 'offended'],
      neutral: ['composed', 'reserved', 'indifferent']
    };

    const emotion = emotionDescriptions[state.primary as keyof typeof emotionDescriptions][
      Math.floor(Math.random() * emotionDescriptions[state.primary as keyof typeof emotionDescriptions].length)
    ];

    return `${descriptor} ${emotion}`;
  }
} 