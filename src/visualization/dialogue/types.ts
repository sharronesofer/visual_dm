// Dialogue system types and type guards

export enum Emotion {
  Neutral = 'neutral',
  Happy = 'happy',
  Sad = 'sad',
  Angry = 'angry',
  Surprised = 'surprised',
  // Add more as needed
}

export interface Speaker {
  id: string;
  name: string;
  portraitUrl?: string;
  emotion?: Emotion;
}

export interface DialogueChoice {
  id: string;
  text: string;
  nextEventId?: string;
  isAvailable?: boolean;
}

export interface DialogueEvent {
  id: string;
  speaker: Speaker;
  text: string;
  choices: DialogueChoice[];
  emotion?: Emotion;
  timestamp?: string;
  type: 'line' | 'choice' | 'end' | 'interruption';
}

export interface DialogueData {
  events: DialogueEvent[];
  initialEventId: string;
}

export interface DialogueState {
  currentEventId: string;
  history: DialogueEvent[];
  isActive: boolean;
}

// Type guards
export function isValidDialogueEvent(obj: any): obj is DialogueEvent {
  return !!(obj && typeof obj.id === 'string' && typeof obj.text === 'string' && Array.isArray(obj.choices));
}

export function isValidDialogueChoice(obj: any): obj is DialogueChoice {
  return !!(obj && typeof obj.id === 'string' && typeof obj.text === 'string');
}

export function validateDialogueState(state: any): state is DialogueState {
  return state && typeof state.currentEventId === 'string' && Array.isArray(state.history) && typeof state.isActive === 'boolean';
} 