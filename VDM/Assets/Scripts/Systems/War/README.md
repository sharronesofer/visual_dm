# Tension & War System (VDM)

## Overview
The Tension & War System manages faction conflicts, tension tracking, war simulation, and the resulting impact on resources, population, and world state. It is fully event-driven, modular, and designed for runtime-only Unity 2D projects.

## Architecture
- **WarManager**: Singleton MonoBehaviour coordinating all war and tension logic.
- **TensionTracker**: Tracks tension (0-100) between any two factions, supports modifiers and decay.
- **WarState**: Represents an active war, tracks exhaustion, events, and state.
- **ScriptableObjects**: Used for tension modifiers and war outcome templates for designer flexibility.
- **SerializableWarState**: Data structure for saving/loading all war and tension state.
- **TensionWarPanel**: UI panel for visualizing tensions and wars at runtime.

## Key Components
### WarManager
- Singleton, always present at runtime (initialized by GameLoader).
- Tracks all TensionTrackers and active WarStates.
- Exposes events:
  - `OnTensionChanged(string factionA, string factionB, float value)`
  - `OnWarStateChanged(WarState war, bool started)`
- Methods for starting/ending wars, simulating, and triggering battle events.

### TensionTracker
- Tracks tension between two factions.
- Supports runtime modifiers (ScriptableObjects implementing ITensionModifier).
- Decay logic and event-driven updates.

### WarState
- Tracks war exhaustion, events, and state.
- Holds a list of WarEvent objects for analytics and UI.
- Methods for simulating war, applying outcomes, and ending wars.

### ScriptableObjects
- **TensionModifierTemplate**: Defines how actions (trade, aggression, etc.) affect tension.
- **WarOutcomeTemplate**: Defines possible war outcomes, their probability, and effects.

### SerializableWarState
- Used for saving/loading all war and tension state.
- Includes lists of active wars, tensions, and recent events.

### TensionWarPanel (UI)
- Runtime UI for visualizing all faction tensions and active wars.
- Methods for updating tension and war lists.
- Uses runtime-generated UI (no scene references).

## Integration Points
- **Faction System**: Integrate with advanced faction logic for dynamic relationships.
- **POI State System**: WarManager can trigger POI state transitions (e.g., to Ruins) via POIStateManager.OnWarDamage().
- **Analytics**: Event hooks are present for future analytics integration.
- **GameLoader**: Ensures WarManager is always present at runtime.

## Event-Driven Design
- All major state changes (tension, war start/end, battle events) are event-driven.
- Other systems can subscribe to WarManager events for integration.

## Example Usage
```csharp
// Get or create a tension tracker
var tracker = WarManager.Instance.GetTensionTracker("FactionA", "FactionB");
tracker.ApplyEvent(+10f); // Increase tension

// Start a war
var war = WarManager.Instance.StartWar("FactionA", "FactionB");

// Trigger a battle event
WarManager.Instance.TriggerBattleEvent(war, someOutcomeTemplate);

// End a war
war.EndWar();
WarManager.Instance.EndWar(war);
```

## Extending the System
- Add new ScriptableObject templates for custom tension/war logic.
- Subscribe to WarManager events for analytics, UI, or world state changes.
- Integrate with POI, Faction, and Resource systems for deeper simulation.

## Best Practices
- All logic is runtime-only, no UnityEditor or scene dependencies.
- Use XML documentation for maintainability.
- Place all new code in the `VDM.Systems.War` namespace.

---
For questions or contributions, see the main project documentation or contact the system architect. 