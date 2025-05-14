import { DialogueEvent, DialogueChoice } from './types';

export class DialogueEventHandler {
  static handleEvent(event: DialogueEvent, callback: (event: DialogueEvent) => void): void {
    // TODO: Add type guard and error handling
    callback(event);
  }

  static handleChoice(choice: DialogueChoice, callback: (choice: DialogueChoice) => void): void {
    // TODO: Add type guard and error handling
    callback(choice);
  }
} 