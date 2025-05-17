# Decision Flowchart and Edge Case Handling for Progression-Based Interaction Availability

## Core Decision Flowchart (Text Format)

1. Player attempts interaction
2. System retrieves character progression data (with cache fallback)
3. System retrieves interaction definition and requirements
4. For each requirement:
   a. Evaluate requirement against progression data
   b. If requirement not met, add to missing requirements list
5. If all requirements met:
   a. Allow interaction
   b. Trigger UI feedback (unlocked state, notification)
6. If any requirements not met:
   a. Check for fallback interaction
   b. Display UI feedback (locked state, tooltip with missing requirements)
   c. If fallback exists, offer alternative interaction
7. Monitor for progression changes (level up, quest complete, etc.)
   a. Re-evaluate availability and update UI in real time

## Edge Case Handling

### Progression Resets
- Detection: Monitor for events that reduce progression (e.g., skill loss, quest regression)
- Handling: Immediately re-evaluate all affected interactions; lock those no longer available; notify player
- UX: Provide clear messaging for lost access ("You no longer meet the requirements for this interaction")

### Multiplayer Scenarios
- Detection: Identify shared or conflicting progression states (e.g., party-based progression)
- Handling: Define rules for shared vs. individual progression; resolve conflicts by majority, leader, or custom logic
- UX: Indicate which party member(s) meet requirements; gray out for those who do not

### Save Game Loading
- Detection: On load, validate progression data against current game state
- Handling: Recompute all interaction availabilities; handle missing/corrupt data with error recovery or safe defaults
- UX: Notify player if any interactions have changed state due to save/load

### Temporary Effects
- Detection: Track buffs/debuffs and their expiration
- Handling: Re-evaluate affected interactions on effect change; lock/unlock as needed
- UX: Animate or highlight changes in availability due to temporary effects

### Data Corruption/Missing Requirements
- Detection: Validate data integrity on access; catch exceptions
- Handling: Fallback to safe state (lock interaction, log error, prompt for revalidation)
- UX: Display error message or prompt for support if persistent

## Recommendations for Robustness
- Always revalidate on progression change, save/load, or multiplayer state update
- Use modular, testable functions for requirement evaluation
- Log all edge case events for QA and debugging
- Provide clear, actionable feedback to players for all state changes
- Design for graceful degradation: fallback interactions, safe defaults, and error recovery

This flowchart and edge case documentation ensure the progression-interaction system is robust, user-friendly, and maintainable under all gameplay scenarios.

---

## 1. Decision Flowchart: Interaction Availability

```mermaid
flowchart TD
    A[Start: Player attempts interaction] --> B{Is interaction defined?}
    B -- No --> Z1[Show error: Interaction not found]
    B -- Yes --> C{Are requirements defined?}
    C -- No --> Z2[Allow interaction (no gating)]
    C -- Yes --> D[Fetch CharacterProgression]
    D --> E{All requirements met?}
    E -- Yes --> F[Allow interaction]
    E -- No --> G[Block interaction]
    G --> H[Show UI: List missing requirements, suggest fallback]
    F --> I[Log interaction success]
    G --> J[Log interaction block]
    I & J --> K[End]
```

---

## 2. Edge Case Handling

### 2.1 Progression Resets
- **Scenario:** Player's progression is reset (e.g., prestige, rebirth, penalty)
- **Handling:**
  - Invalidate cached progression data
  - Re-evaluate all interaction availabilities
  - Notify player of changes in available interactions
  - Provide fallback or tutorial interactions if most content is locked

### 2.2 Multiplayer Scenarios
- **Scenario:** Multiple players interact with the same POI/building
- **Handling:**
  - Evaluate each player's progression independently
  - Synchronize shared state changes (e.g., POI evolution) across all clients
  - Lock/unlock interactions per player, not globally
  - Handle race conditions with optimistic concurrency or server arbitration

### 2.3 Save Game Loading
- **Scenario:** Player loads a save with outdated progression/interactions
- **Handling:**
  - Recompute interaction availability on load
  - Migrate or patch progression data if schema has changed
  - Warn player if some interactions are no longer valid

### 2.4 Temporary Effects
- **Scenario:** Buffs, debuffs, or story events temporarily alter progression
- **Handling:**
  - Re-evaluate interaction availability when effect is applied/removed
  - UI should indicate temporary nature of unlock/lock

### 2.5 Data Corruption or Inconsistency
- **Scenario:** Progression or interaction data is missing or corrupt
- **Handling:**
  - Fallback to safe defaults (lock interaction, show error)
  - Log error for diagnostics
  - Attempt automated data repair if possible

---

## 3. Graceful Degradation Recommendations
- Always provide clear UI feedback when an interaction is unavailable due to edge cases
- Offer fallback or tutorial interactions when most content is locked
- Log all edge case triggers for analytics and debugging
- Use server-side arbitration for multiplayer conflicts
- Regularly validate and migrate progression data to prevent schema drift

---

## 4. References
- `docs/progression_interaction_mapping.md`
- `docs/progression_interaction_data_api.md`
- `docs/progression_locked_interaction_ui.md` 