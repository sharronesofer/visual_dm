# Combat System API Documentation

## Overview
The Combat System provides a modular, extensible, and high-performance framework for handling all combat-related logic in the game. It integrates with the Action System, supports event-driven communication, and is designed for runtime-only Unity 2D projects.

## Main Components
- **CombatActionHandler**: Abstract base for all combat actions (attack, defend, special, etc.).
- **IActionProcessor**: Interface for action processing and resolution.
- **AttackActionHandler, DefendActionHandler, SpecialAbilityHandler**: Concrete action handlers.
- **CombatActionFactory**: Instantiates handlers based on action type.
- **CombatActionPriorityQueue**: Thread-safe priority queue for action resolution.
- **CombatResourceManager**: Manages cooldowns and resources (mana, stamina).
- **CombatActionValidator**: Validates if actions can be performed.
- **CombatStateManager**: Singleton for global combat state, transitions, and rollback.
- **IEffect, DamageEffect, HealEffect, StatusEffect**: Effect pipeline interfaces and implementations.
- **EffectProcessor**: Manages effect application, stacking, and duration.
- **EffectModifier**: Chain-of-responsibility for effect parameter modification.
- **CombatEventManager**: Event-driven publisher/subscriber system for combat events.
- **ObjectPool**: Generic thread-safe object pool for effects/events.
- **CombatStateDebugger**: Runtime tool for inspecting combat state.

## Extension Points
- **New Action Types**: Inherit from `CombatActionHandler` and implement custom logic.
- **New Effects**: Implement `IEffect` for new effect types (e.g., DoT, shield).
- **Event Types**: Extend `CombatEventType` and update event manager as needed.
- **Effect Modifiers**: Inherit from `EffectModifier` to add new effect modification logic.

## Integration Steps
1. **Action System**: All handlers implement `IActionProcessor` for seamless integration.
2. **Feedback System**: Use event hooks in `EffectProcessor` and `CombatEventManager` to trigger feedback.
3. **UI/Animation**: Subscribe to combat events for UI/animation updates.
4. **Networking**: Use `CombatEventManager` serialization for networked combat events.

## Usage Examples
### Creating a Custom Action Handler
```csharp
public class CustomActionHandler : CombatActionHandler
{
    public override void StartAction() { /* custom logic */ }
    public override void UpdateAction(float dt) { /* custom logic */ }
    public override void EndAction() { /* custom logic */ }
}
```

### Applying an Effect
```csharp
var effect = new DamageEffect(25f);
effectProcessor.ApplyEffect(effect, targetGameObject);
```

### Subscribing to Combat Events
```csharp
public class MyListener : ICombatEventListener
{
    public void OnCombatEvent(CombatEvent e) { /* handle event */ }
}
CombatEventManager.Instance.Subscribe(new MyListener(), CombatEventType.DamageDealt);
```

### Using Object Pool
```csharp
var pool = new ObjectPool<DamageEffect>(() => new DamageEffect(0));
var effect = pool.Get();
// ... use effect ...
pool.Return(effect);
```

## Thread Safety
All major components use locks or thread-safe collections. See code comments for critical sections.

## Debugging
Attach `CombatStateDebugger` to a GameObject to log combat state at runtime.

## Further Reading
- See XML documentation in code for API details.
- For integration with new systems, see the Integration Steps section above. 