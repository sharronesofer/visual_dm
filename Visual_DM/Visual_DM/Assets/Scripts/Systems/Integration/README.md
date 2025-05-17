# System Integration Framework for Quest System

## Overview
This framework enables the quest system to interact seamlessly with combat, inventory, market, character, and world systems using standardized protocols, state synchronization, and monitoring.

## Architecture
- **ServiceLocator**: Singleton for registering and retrieving system interfaces.
- **IntegrationEventBus**: Event-driven, type-safe message broker for async communication.
- **Interface Contracts**: `ICombatSystem`, `IInventorySystem`, `IMarketSystem`, `ICharacterSystem`, `IWorldSystem` define integration points.
- **Serialization**: `ISerializationUtility` and `JsonSerializationUtility` for cross-system data transfer.
- **Request/Response**: `IntegrationRequestBroker` for synchronous and callback-based operations.
- **StateSyncManager**: Observer-based state synchronization, snapshot, rollback, delta update, and conflict resolution.
- **Validation**: Input, schema, and transaction validation utilities.
- **Monitoring**: Logging, metrics, diagnostics, and alerting infrastructure.

## Interface Specifications

### ICombatSystem (example)
```csharp
public interface ICombatSystem
{
    void OnQuestEvent(QuestEventData eventData);
    CombatState GetCombatStateForQuest(string questId);
    void SyncCombatState(CombatState state);
}
```
- **OnQuestEvent**: Receives quest-related events for combat integration.
- **GetCombatStateForQuest**: Returns current combat state for a quest.
- **SyncCombatState**: Updates combat state from external system.

(Similar structure for IInventorySystem, IMarketSystem, ICharacterSystem, IWorldSystem)

## Example Usage

### Registering Systems
```csharp
ServiceLocator.Instance.Register<ICombatSystem>(combatSystemInstance);
ServiceLocator.Instance.Register<IInventorySystem>(inventorySystemInstance);
```

### Publishing and Subscribing to Events
```csharp
IntegrationEventBus.Instance.Subscribe<IntegrationMessage>(OnIntegrationMessage);
IntegrationEventBus.Instance.Publish(new IntegrationMessage { ... });
```

### State Synchronization
```csharp
var syncManager = new StateSyncManager<CombatState>();
syncManager.ConflictResolver = (current, incoming) => /* custom logic */;
syncManager.PreValidation = state => /* validation logic */;
syncManager.PostValidation = state => /* validation logic */;
syncManager.RegisterObserver(new CombatStateObserver());
syncManager.SetState(newState);
```

### Validation and Transactions
```csharp
IntegrationValidation.ValidateInput(input, validatorFunc);
using (var tx = new IntegrationTransaction(rollbackAction)) { /* ... */ tx.Commit(); }
```

### Monitoring and Diagnostics
```csharp
IntegrationLogger.Log("Integration started", LogLevel.Info, "Quest", "Combat", "Start", "Success");
IntegrationMetrics.Record("integration_latency", 123.4);
IntegrationAlerting.Alert("Integration failure", LogLevel.Critical, "Quest", "Inventory", "Sync");
IntegrationDiagnostics.Trace("Trade", "Item exchanged", "Market", "Inventory");
```

### World System Integration Example
```csharp
// In GameLoader.cs, after creating WorldManager:
ServiceLocator.Instance.Register<IWorldSystem>(worldManager);

// In WorldManager.cs:
// Implements IWorldSystem
// Subscribes to IntegrationEventBus for IntegrationMessage events
IntegrationEventBus.Instance.Subscribe<IntegrationMessage>(OnIntegrationMessage);
```

## Error Handling and Recovery
- All integration points should use try/catch and log errors using IntegrationLogger.
- Use IntegrationAlerting for critical failures.
- StateSyncManager supports rollback on validation or conflict errors.
- IntegrationRequestBroker and IntegrationEventBus provide retry logic for transient failures.

## Troubleshooting Guide
- **System not registered**: Ensure all systems are registered with ServiceLocator before use.
- **World system integration not working**: Ensure WorldManager implements IWorldSystem, is registered with ServiceLocator, and subscribes to IntegrationEventBus.
- **Event not delivered**: Check event bus subscriptions and log output for errors.
- **State not syncing**: Validate conflict resolver and validation hooks in StateSyncManager.
- **Performance issues**: Adjust IntegrationMetrics.SamplingRate and review logs for bottlenecks.
- **Alert not triggered**: Confirm IntegrationAlerting event handlers are set and thresholds are configured.

## Performance Considerations
- Use sampling for metrics to reduce overhead.
- Prefer async event-driven communication for decoupling.
- Minimize state transfer with delta updates.
- Use rollback and transaction patterns for error recovery.
- Monitor performance with IntegrationMetrics and adjust as needed.

## Best Practices
- Document all new integration points and workflows.
- Use observer and event-driven patterns for extensibility.
- Validate all data exchanges at system boundaries.
- Keep monitoring hooks lightweight for runtime performance.

## Sequence Diagrams
- Sequence diagrams for common workflows should be placed in `/docs/sequence_diagrams/` (to be created).
- Example: Quest triggers combat event → Combat system updates state → StateSyncManager notifies quest system.

## Integration Test Examples
- See `IntegrationEventBusTests.cs`, `IntegrationRequestBrokerTests.cs`, `StateSyncManagerTests.cs`, and `IntegrationMonitoringTests.cs` for example test cases and usage patterns.

## Transaction Safety, Atomicity, and Idempotency Patterns (Task #592)

### Overview
To prevent race conditions, duplication exploits, and ensure data integrity in all purchase, trade, and inventory change operations, the following patterns have been implemented:

- **Atomic Operations**: All inventory and economy modifications are wrapped in lock-protected critical sections to guarantee thread safety and atomicity.
- **Transaction Logging**: Every operation is logged using `IntegrationLogger` with a unique transaction ID, operation type, and status (Committed/RolledBack).
- **Idempotency Keys**: All externally-triggered inventory modifications (e.g., AddItem, RemoveItem) accept an optional idempotency key. Duplicate requests with the same key are ignored and logged as idempotent.
- **Rollback Mechanisms**: Where possible, operations are wrapped in `IntegrationTransaction` blocks to allow rollback on failure. For in-memory atomic operations, rollback is trivial, but the pattern is in place for future extension.
- **Timeouts and Error Handling**: All critical operations are wrapped in try/catch, and errors are logged and surfaced to the user/UI as appropriate.
- **Distributed Coordination**: IntegrationRequestBroker and IntegrationEventBus are used for distributed or cross-system operations, with retry and idempotency support.

### Implementation Locations
- `InventorySystem.cs`: All inventory modifications (AddItem, RemoveItem, SwapItems, Deserialize) are atomic, idempotent, and logged.
- `InventoryGiveTakeSystem.cs`: All loot/inventory changes use idempotency keys and transaction logging.
- `EconomySystem.cs`: All resource and trade modifications are atomic and logged.
- `IntegrationLogger`, `IntegrationTransaction`, `IntegrationRequestBroker`, and `IntegrationEventBus` provide the supporting infrastructure.

### Example Usage
```csharp
// Atomic, idempotent inventory add
inventory.AddItem(item, 1, idempotencyKey: "purchase_12345");

// Transaction logging
IntegrationLogger.Log($"[Inventory] AddItem txn={txnId} item={item.ID}", LogLevel.Info, ...);

// Distributed request with retry
requestBroker.SendRequestWithRetry(...);
```

### Best Practices
- Always generate a unique idempotency key for each external request (e.g., purchase, trade, loot).
- Log all critical operations with a unique transaction ID.
- Use lock-protected critical sections for all shared state modifications.
- Use IntegrationTransaction for rollback where possible.
- Surface errors to the user and log them for diagnostics. 