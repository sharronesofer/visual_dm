from typing import Any, Dict



  isValidDialogueEvent,
  isValidDialogueChoice,
  validateDialogueState,
  DialogueEvent,
  DialogueChoice,
  DialogueState,
  Emotion
} from '../types'
describe('Dialogue Type Guards', () => {
  test('isValidDialogueEvent validates DialogueEvent objects', () => {
    const validEvent: DialogueEvent = {
      id: 'event1',
      speaker: Dict[str, Any],
      text: 'Hello world',
      choices: [
        { id: 'choice1', text: 'Option 1' }
      ],
      emotion: Emotion.Happy,
      type: 'line'
    }
    expect(isValidDialogueEvent(validEvent)).toBe(true)
    expect(isValidDialogueEvent({ id: 'event1', text: 'Missing fields' })).toBe(false)
    expect(isValidDialogueEvent(null)).toBe(false)
  })
  test('isValidDialogueChoice validates DialogueChoice objects', () => {
    const validChoice: DialogueChoice = { id: 'choice1', text: 'Option 1' }
    expect(isValidDialogueChoice(validChoice)).toBe(true)
    expect(isValidDialogueChoice({ id: 'choice1' })).toBe(false)
    expect(isValidDialogueChoice(null)).toBe(false)
  })
})
describe('DialogueState Validation', () => {
  test('validateDialogueState validates complete states', () => {
    const validState: DialogueState = {
      currentEventId: 'event1',
      history: [],
      isActive: true
    }
    expect(validateDialogueState(validState)).toBe(true)
  })
  test('validateDialogueState fails on invalid state', () => {
    const invalidState = {
      currentEventId: 123,
      history: 'not-an-array',
      isActive: 'yes'
    }
    expect(validateDialogueState(invalidState)).toBe(false)
  })
}) 