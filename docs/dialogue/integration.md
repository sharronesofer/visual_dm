# Dialogue System Integration Guide

This document describes how to integrate the new GPT-driven dynamic dialogue system (with context management and caching) into existing game systems. It covers migration steps, new data flows, integration points, and usage examples.

## Overview
The new dialogue system replaces legacy branching dialogue with a dynamic, context-aware, GPT-driven approach. It leverages:
- **GPT Integration Layer** for generating responses
- **Context Management** for conversation history and context windowing
- **DialogueCache** for caching common responses and optimizing API usage
- **Redux-style State Management** for dialogue state
- **UI Components** for dynamic, asynchronous response handling

## Migration Steps
1. **Refactor the Interaction System**
   - Replace all calls to legacy dialogue logic with calls to the new dialogue generation service.
   - Ensure all triggers (e.g., quest, combat, NPC interaction) pass the correct context and character info.
   - Connect to context management and caching modules.

2. **Update UI Components**
   - Modify dialogue UI to handle asynchronous GPT calls (show loading, handle errors).
   - Display dynamically generated, context-aware responses.
   - Implement smooth transitions between dialogue states.

3. **Update State Management**
   - Ensure all dialogue state changes are dispatched as actions and stored in Redux-style state.
   - Update reducers/selectors for new dialogue data structures.
   - Add middleware for async dialogue generation and caching.

4. **Testing**
   - Write integration tests for the full dialogue flow (trigger → GPT → context → cache → UI).
   - Add regression tests to ensure no existing mechanics are broken.

## Data Flow Diagram
```
[Trigger/Event] → [Interaction System] → [Context Manager]
                                 ↓
                        [DialogueCache]
                                 ↓
                        [GPT Integration]
                                 ↓
                        [DialogueCache]
                                 ↓
                        [Redux State] → [UI]
```

## Integration Points
- **Interaction System:**
  - Calls `generate_dialogue(context, character)`
  - Uses `ConversationHistory` for context
  - Checks/sets cache via `DialogueCache`
- **UI:**
  - Subscribes to dialogue state
  - Shows loading indicators for async responses
  - Handles errors and retries
- **State Management:**
  - Actions: `DIALOGUE_REQUEST`, `DIALOGUE_SUCCESS`, `DIALOGUE_FAILURE`
  - Middleware: Handles async GPT/caching logic
  - Reducers: Store dialogue history, current response, error state

## Example Usage
```python
# In interaction_system.py
from dialogue.context_manager import ConversationHistory
from dialogue.cache import DialogueCache
from dialogue.gpt_service import generate_gpt_response

history = ConversationHistory()
cache = DialogueCache()

context = history.get_context_window(by_tokens=True)
cache_key = f"{character_id}:{context[-1].message if context else ''}"

response = cache.get(cache_key)
if not response:
    response = generate_gpt_response(context, character_id)
    cache.set(cache_key, response)
history.add_entry(character_id, response)
```

## UI Example (Pseudocode)
```js
// In dialogue_ui.js
onDialogueTrigger(context, character) {
  dispatch({ type: 'DIALOGUE_REQUEST' });
  api.getDialogueResponse(context, character)
    .then(response => dispatch({ type: 'DIALOGUE_SUCCESS', payload: response }))
    .catch(error => dispatch({ type: 'DIALOGUE_FAILURE', error }));
}
```

## Testing
- Use `tests/integration/test_dialogue_integration.py` for end-to-end tests
- Simulate triggers, check state, and verify UI updates

## Migration Checklist
- [ ] All legacy dialogue calls replaced
- [ ] UI updated for async responses
- [ ] State management updated
- [ ] Integration and regression tests passing

## Further Reading
- [docs/dialogue/context_manager.md](context_manager.md)
- [docs/dialogue/cache.md](cache.md) 