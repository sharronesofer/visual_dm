# ChainActionSystem\n\nThis folder contains all scripts related to the ChainActionSystem domain.

## Integration with Action Response Time System & Combat
- Chain actions are now enqueued into the main ActionQueue as `ActionType.ChainAction`.
- The context for each chain action includes the `ChainDefinition` and `ChainContext`.
- The ActionPipeline uses a `ChainActionExecutionStrategy` to execute chain actions via the ChainActionSystem.
- Timing for chain actions is managed via `TimingConfiguration.ChainActionMs`.
- Feedback and UI are triggered via SystemsManager and ChainActionUI, with support for chain-specific events.

## Usage Example
```csharp
// Start a chain action (will enqueue in the main action queue):
ChainActionSystem.Instance.StartChain(chainDef, owner);
```

## Extension Points
- Add new IChainAction implementations for custom chain steps.
- Extend feedback/UI by subscribing to chain events (ChainStartedEvent, ChainEndedEvent, etc.).
- Tune timing and priority via TimingConfiguration and PriorityResolver.
