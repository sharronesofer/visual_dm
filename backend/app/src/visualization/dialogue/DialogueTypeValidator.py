from typing import Any


class DialogueTypeValidator {
  static validateEvent(event: Any): event is DialogueEvent {
    return isValidDialogueEvent(event)
  }
  static validateChoice(choice: Any): choice is DialogueChoice {
    return isValidDialogueChoice(choice)
  }
  static validateState(state: Any): state is DialogueState {
    return validateDialogueState(state)
  }
} 