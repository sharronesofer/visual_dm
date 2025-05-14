import { NPCData } from './npc';
import { InteractionResult } from '../../systems/npc/InteractionSystem';

export interface EmotionalState {
  primary: string;
  intensity: number;
  secondary?: string[];
  triggers: {
    type: string;
    source: string;
    impact: number;
  }[];
  duration: number;
  timestamp: number;
}

export interface EmotionSystem {
  getCurrentEmotionalState(npcId: string): Promise<string>;
  updateEmotionalState(
    npcId: string,
    trigger: string,
    intensity: number,
    context?: any
  ): Promise<EmotionalState>;
  getEmotionalResponse(
    npcId: string,
    stimulus: string,
    intensity: number
  ): Promise<{
    response: string;
    intensity: number;
  }>;
  calculateEmotionalImpact(
    baseEmotion: string,
    personality: any,
    context: any
  ): Promise<number>;
} 