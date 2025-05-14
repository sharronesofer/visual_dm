from typing import Any, List, Union
from enum import Enum


class Emotion(Enum):
    Neutral = 'neutral'
    Happy = 'happy'
    Sad = 'sad'
    Angry = 'angry'
    Surprised = 'surprised'
class Speaker:
    id: str
    name: str
    portraitUrl?: str
    emotion?: \'Emotion\'
class DialogueChoice:
    id: str
    text: str
    nextEventId?: str
    isAvailable?: bool
class DialogueEvent:
    id: str
    speaker: \'Speaker\'
    text: str
    choices: List[DialogueChoice]
    emotion?: \'Emotion\'
    timestamp?: str
    type: Union['line', 'choice', 'end', 'interruption']
class DialogueData:
    events: List[DialogueEvent]
    initialEventId: str
class DialogueState:
    currentEventId: str
    history: List[DialogueEvent]
    isActive: bool
function isValidDialogueEvent(obj: Any): obj is DialogueEvent {
  return !!(obj && typeof obj.id === 'string' && typeof obj.text === 'string' && Array.isArray(obj.choices))
}
function isValidDialogueChoice(obj: Any): obj is DialogueChoice {
  return !!(obj && typeof obj.id === 'string' && typeof obj.text === 'string')
}
function validateDialogueState(state: Any): state is DialogueState {
  return state && typeof state.currentEventId === 'string' && Array.isArray(state.history) && typeof state.isActive === 'boolean'
} 