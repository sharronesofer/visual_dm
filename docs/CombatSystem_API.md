# Combat System API Documentation

## Overview
The Combat System provides a modular, extensible framework for handling all combat-related logic in Visual_DM. It is designed for integration with the Action System, supports multiplayer/networked scenarios, and is built for performance and maintainability.

## Architecture
- **CombatStateManager**: Singleton managing global combat state, transitions, rollback, and conflict resolution.
- **Combatant**: Represents a participant in combat (player, NPC, etc.).
- **CombatAction**: Encapsulates a combat action (attack, defend, special, etc.).
- **CombatActionType**: Enum for action types.
- **ICombatActionHandler**: Interface for action handlers (attack, defend, special, etc.).
- **CombatActionHandlerRegistry**: Registry for action handlers by type.
- **CombatEffect**: Represents buffs, debuffs, damage, healing, etc.
- **CombatEffectPipeline**: Handles effect application, stacking, removal, and interruption.
- **CombatEventBus**: Publisher/subscriber event system for combat events.
- **CombatLogger**: Logging utility for combat events and errors.
- **CombatStateSnapshot**: Used for rollback and state history.

## Extension Points
- Implement new action types by creating classes that implement `ICombatActionHandler` and registering them in `CombatActionHandlerRegistry`.
- Add new effect types by extending `CombatEffect` and updating `CombatEffectPipeline`.
- Subscribe to combat events using `CombatEventBus` for integration with UI, audio, and other systems.

## Integration
- Designed for runtime-only Unity 2D projects (SpriteRenderer, no UnityEditor, no scene references).
- All state changes are thread-safe and support rollback for network/multiplayer scenarios.
- Follows narrative and mechanical rules as outlined in `bible_qa.md` (see that file for lore and gameplay constraints).

## Example Usage
```csharp
// Register an attack handler
var registry = new CombatActionHandlerRegistry();
registry.RegisterHandler(CombatActionType.Attack, new AttackActionHandler());

// Apply an action
var action = new CombatAction { ActionType = CombatActionType.Attack, Source = attacker, Target = defender };
var handler = registry.GetHandler(action.ActionType);
if (handler != null && handler.CanHandle(action))
    handler.Handle(action);
```

## See Also
- [bible_qa.md](bible_qa.md) for narrative and mechanical rules
- [Action System API](ActionSystem_API.md) for integration details 