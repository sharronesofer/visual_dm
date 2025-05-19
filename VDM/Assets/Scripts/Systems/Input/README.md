# Input System: Action Buffering & Queuing

## Overview
This folder implements a comprehensive action buffering and queuing system for responsive combat and gameplay input in Unity (runtime-only, no prefabs or scene references).

### Components
- **InputBuffer.cs**: Circular buffer for input events, configurable window (15-500ms), input validation, debounce, and buffer clearing for game states.
- **ActionQueue.cs**: Priority-based queue for player/AI actions, supports validation, cancellation, priority adjustment, and expiration.
- **QueueVisualizer.cs**: Debug and player-facing UI for queue state, action priorities, and feedback (uses Unity UI at runtime).
- **ActionQueuePool.cs**: Object pooling for QueuedAction to reduce GC pressure in high-frequency scenarios.
- **QueuePerformanceMonitor.cs**: Logs queue processing times, supports profiling and adaptive processing.

## Usage
- Attach `InputBuffer` and `ActionQueue` to a runtime GameObject (e.g., via GameLoader.cs).
- Use `InputBuffer.AddInput()` to buffer player inputs; validate with `ValidateInput()`.
- Enqueue validated actions into `ActionQueue` with appropriate priority.
- Use `QueueVisualizer` for debug and player feedback; assign a Canvas at runtime.
- Monitor performance with `QueuePerformanceMonitor`.

## Integration
- Designed for runtime-only Unity 2D projects (SpriteRenderer, no MeshRenderer).
- No UnityEditor or scene references; all UI is generated at runtime.
- Integrate with animation, combat, and other systems via public APIs.
- Extend `GameContext` and `GameState` for richer contextual validation.

## Best Practices
- Use object pooling for high-frequency action creation.
- Adjust buffer window and queue capacity for your game's responsiveness needs.
- Use the debug panel during development; toggle off in production.
- Profile queue performance and tune for <16ms processing time.

## Extension
- Add new input types or priorities by extending enums.
- Integrate with analytics or telemetry for real-world performance data.
- Expand validation logic for more complex input/game state scenarios.

## Design Rationale and Best Practices
- For canonical Q&A, design rationale, and best practices, see docs/bible_qa.md.

---
For design rationale and Q&A, see `