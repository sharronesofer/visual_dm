# POI State Transition System

## Overview
The POI State Transition System enables Points of Interest (POIs) to dynamically change states (e.g., city, ruins, dungeon) based on population metrics and war damage. It is event-driven, designer-configurable, and fully runtime for Unity 2D projects.

## Architecture
- **POIStateManager**: Manages state transitions for a POI, tracks population, and triggers events.
- **PopulationMetricsTracker**: Tracks current/max population, change rates, and significant events.
- **POIStateTransitionRuleSet**: ScriptableObject for designer-configurable transition thresholds and rules.
- **POIStateIndicator**: MonoBehaviour for runtime visual feedback (color, label) on POI state.

## Configuration
- **Transition Rules**: Use POIStateTransitionRuleSet ScriptableObject to define population thresholds for each state transition (Normal→Declining, Declining→Abandoned, etc.), one-way transitions, and exemptions.
- **Manual Overrides**: Use POIStateManager public methods to set state manually or exempt POIs from automatic transitions.

## Event System
- **OnStateChanged**: `public event Action<POIState, POIState> OnStateChanged;` fires whenever a POI changes state.
- **Population Events**: PopulationMetricsTracker fires events for significant changes (e.g., disasters, migrations).
- **Integration**: Other systems (e.g., WarManager) can call `OnWarDamage(float severity)` to trigger state changes due to war.

## Visual Indicators
- **POIStateIndicator**: Attach at runtime to any POI GameObject. Uses SpriteRenderer color coding:
  - Normal: Green
  - Declining: Yellow
  - Abandoned: Orange
  - Ruins: Gray
  - Dungeon: Red
- **Floating Label**: TextMeshPro label above POI shows current state and population.
- **Threshold Warning**: (Optional) Can be extended to show warnings when near transition thresholds.

## Example Usage
```csharp
// Attach POIStateManager and POIStateIndicator at runtime
var poi = new GameObject("POI");
var stateManager = poi.AddComponent<POIStateManager>();
poi.AddComponent<POIStateIndicator>();

// Set population and trigger state evaluation
stateManager.SetPopulation(50);
stateManager.SetMaxPopulation(100);
stateManager.GetPopulationMetricsTracker().UpdateMetrics();

// Listen for state changes
stateManager.OnStateChanged += (oldState, newState) => Debug.Log($"State changed: {oldState?.Type} → {newState.Type}");

// Trigger war damage
stateManager.OnWarDamage(0.8f); // Likely transitions to Ruins
```

## Testing Scenarios
- Simulate population growth/decline and verify state transitions at correct thresholds.
- Trigger war damage and confirm correct state changes.
- Attach POIStateIndicator and verify color/label updates in real time.
- Test manual overrides and exemption logic.
- Use unit tests for PopulationMetricsTracker calculations and event triggers.

## Example Scene Setup
- Use GameLoader to spawn POIs with POIStateManager and POIStateIndicator at runtime.
- Simulate population changes and war events to test all transitions and visuals.

## Extension Points
- Add custom visual effects or icons for threshold warnings.
- Integrate with analytics by subscribing to OnStateChanged.
- Expand transition rules for narrative or gameplay needs.

---
For more details, see the code in `VDM/Assets/Scripts/POI/` and contact the system architect for advanced integration. 