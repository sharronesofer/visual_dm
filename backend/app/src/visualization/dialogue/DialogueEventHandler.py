from typing import Any


class DialogueEventHandler {
  static handleEvent(event: DialogueEvent, callback: (event: DialogueEvent) => void): void {
    callback(event)
  }
  static handleChoice(choice: DialogueChoice, callback: (choice: DialogueChoice) => void): void {
    callback(choice)
  }
} 