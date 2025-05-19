# Combat\n\nThis folder contains all scripts related to the Combat domain.

## Action Response Time System
- See /docs/bible_qa.md for design rationale and requirements.
- The ActionRequest struct is defined in ActionRequest.cs and is used throughout the action pipeline, queue, and monitoring systems.
- Timing targets and configuration are managed via TimingConfiguration.cs and ActionPerformanceMonitor.cs.
- **ChainAction** is now a supported ActionType, with its own timing target and pipeline integration.

## Performance Monitoring & Dashboard
- ActionPerformanceMonitor.cs logs and analyzes action execution times.
- All action timings are now automatically captured via ActionPipeline integration.
- Use ExportPerformanceDataJson() to export data for developer dashboards.
- Warnings are logged if actions exceed timing targets.

## Input Handling, Queuing & Prioritization
- InputValidator.cs filters invalid or impossible action requests.
- PriorityResolver.cs determines which actions take precedence.
- ActionQueue (see Core/ActionQueue.cs) manages pending actions and supports input buffering.
- **Chain actions are enqueued as ActionType.ChainAction with context for the chain.**

## Modular Execution Pipeline
- ActionPipeline.cs and ActionResolutionPipeline.cs implement a modular, thread-safe pipeline (PreProcess, Execute, PostProcess).
- ActionPerformanceMonitor is integrated into ActionPipeline.cs for automatic timing of all actions.
- Extensible for new action types, effects, and feedback systems.
- **ChainActionExecutionStrategy** routes chain actions through the ChainActionSystem.

## Configuration & Extensibility
- TimingConfiguration.cs loads timing targets from StreamingAssets/ActionTimingConfig.json.
- Add new action types by extending ActionType enum and updating relevant systems.
- Adjust timing targets in the config file as needed for gameplay tuning.
- **ChainActionMs** is configurable for chain action timing.

## Integration & Feedback
- Integrate with animation, UI, and audio systems for synchronized feedback.
- Use event dispatchers and feedback coordinators for extensibility.
- Extension points are provided for future action types and feedback mechanisms.
- **Chain actions trigger feedback via SystemsManager and ChainActionUI.**

## Thread-Safety & Network Considerations
- ActionRequest and ActionQueue are designed for thread-safe operation.
- Frame-independent timing ensures consistent behavior across hardware.
- For multiplayer, implement network latency compensation in the action pipeline.

## Usage Example: Starting a Chain Action from Combat
```csharp
// Create a chain definition and context
var chainDef = new ChainDefinition { /* ... populate ... */ };
var owner = playerGameObject;
ChainActionSystem.Instance.StartChain(chainDef, owner);
// This will enqueue a ChainAction in the main ActionQueue, routed through the ActionPipeline.
```

## Design Rationale and Best Practices
- For canonical Q&A, design rationale, and best practices, see /docs/bible_qa.md.
