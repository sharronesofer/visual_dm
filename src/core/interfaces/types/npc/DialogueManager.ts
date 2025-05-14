import { NPCData } from './npc';
import { InteractionContext } from '../../systems/npc/InteractionSystem';

export interface DialogueResponse {
  message: string;
  tone: string;
  emotionalState: string;
  subtext?: string;
  followUp?: string[];
}

export interface DialogueManager {
  generateDialogue(
    npc: any,
    context: any
  ): Promise<DialogueResponse>;
  
  generateResponse(
    npc: any,
    input: string,
    context: any
  ): Promise<DialogueResponse>;
  
  generateEmotionalResponse(
    npc: any,
    emotion: string,
    intensity: number,
    context: any
  ): Promise<DialogueResponse>;
  
  generateNegotiationResponse(
    npc: any,
    offerQuality: number,
    context: any
  ): Promise<DialogueResponse>;
  
  generateDeceptionResponse(
    npc: any,
    detected: boolean,
    context: any
  ): Promise<DialogueResponse>;
  
  generateCooperationResponse(
    npc: any,
    proposal: any,
    context: any
  ): Promise<DialogueResponse>;
  
  generateCompetitionResponse(
    npc: any,
    challenge: any,
    context: any
  ): Promise<DialogueResponse>;
} 