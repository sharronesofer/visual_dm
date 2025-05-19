# Combat System (Canonical)

This directory contains the canonical, modular, extensible combat system for Visual_DM, as specified in Development_Bible.md.

## Architecture
- **CombatManager**: Orchestrates combat state, turn queue, and effect pipeline. Entry point for all combat encounters.
- **TurnQueue**: Maintains and sorts combatants by initiative. Supports dynamic join/leave and reordering.
- **EffectPipeline**: Handles application, stacking, timing, and removal of combat effects. Integrates with turn system.
- **CombatEffect**: Abstract base for all effects (buffs, debuffs, statuses). Supports stacking, resistance, immunity, and custom timing.
- **EffectVisualizer**: Displays effect icons above combatants at runtime using SpriteRenderer and object pooling.
- **ObjectPool<T>**: Generic pooling for MonoBehaviour objects.
- **Combatant**: Concrete implementation of ICombatant (player, NPC, etc.).
- **ICombatant**: Interface for all combat participants.
- **CombatAction/CombatActionType**: Encapsulates actions (attack, defend, special, etc.) and their types.
- **ICombatActionHandler**: Interface for action handlers (attack, defend, special, etc.).

## Extension Points
- Add new effect types by subclassing `CombatEffect` and extending `EffectType`.
- Add new action types by implementing `ICombatActionHandler` and registering in your orchestrator.
- Use `EffectVisualizer` for runtime effect icons (assign icon prefab at runtime).
- Use `ObjectPool<T>` for all runtime-instantiated MonoBehaviours.

## Backend API Integration
- Python FastAPI backend in `/backend/` provides `/combat/state` GET/POST endpoints for combat state sync.
- Use Pydantic models for type safety and extensibility.
- Integrate with Unity via `UnityWebRequest` or Python client.

## Best Practices
- 100% runtime-generated: no UnityEditor code, no scene/prefab/tag dependencies.
- Entry point: `GameLoader.cs` in `Bootstrap.unity` scene.
- All combatants must implement `ICombatant`.
- Follow SOLID and DRY principles for all new code.
- Document new systems in this file and `/docs/systems/combat/`.

## References
- See `/docs/Development_Bible.md` and `/docs/CombatSystem_API.md` for full specifications and rationale. 