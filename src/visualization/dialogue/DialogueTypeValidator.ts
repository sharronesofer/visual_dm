import { DialogueEvent, DialogueChoice, DialogueState, isValidDialogueEvent, isValidDialogueChoice, validateDialogueState } from './types';

export class DialogueTypeValidator {
  static validateEvent(event: any): event is DialogueEvent {
    return isValidDialogueEvent(event);
  }

  static validateChoice(choice: any): choice is DialogueChoice {
    return isValidDialogueChoice(choice);
  }

  static validateState(state: any): state is DialogueState {
    return validateDialogueState(state);
  }
} 