# Central Event Bus for Cross-System Scene Notifications

This module implements a central event/message bus architecture that enables automatic notifications and updates across all relevant systems (spatial, region, worldgen, analytics) when scenes load or unload.

## Architecture

The event system is composed of three main components:

1. **EventBus** - The core event bus implementation that handles subscription and event dispatching
2. **SceneEventSystem** - A higher-level wrapper for scene-specific events with additional capabilities
3. **SceneEventTypes** - Definition of all scene-related event types

## Usage

### Basic Usage

```typescript
// Import the required components
import { 
  SceneEventSystem, 
  SceneEventType, 
  DependencyType 
} from 'core/events';

// Get the SceneEventSystem singleton
const eventSystem = SceneEventSystem.getInstance();

// Subscribe to scene events
eventSystem.registerGlobalListener(
  SceneEventType.SCENE_LOADED,
  (event) => {
    console.log(`Scene ${event.sceneId} loaded!`);
    // Handle the event...
  }
);

// Emit a scene event
eventSystem.emitSceneEvent(
  SceneEventType.SCENE_LOADED,
  'my-scene-id',
  'SceneManager',
  { additional: 'data' }
);
```

### System Integration

To integrate a system with the event bus:

1. Register the system's dependencies
2. Register handlers for relevant events
3. React to events as needed

Example:

```typescript
// Register system dependency
eventSystem.registerSystemDependency(
  'MySystem',
  [DependencyType.SCENE_LIFECYCLE, DependencyType.SPATIAL]
);

// Register event handlers
eventSystem.registerGlobalListener(
  SceneEventType.SCENE_ACTIVATED,
  this.handleSceneActivated.bind(this)
);

// Handler implementation
private handleSceneActivated(event: ISceneEvent): void {
  const sceneId = event.sceneId;
  console.log(`MySystem: Scene ${sceneId} activated`);
  // Update system state, initialize scene-specific logic, etc.
}
```

See the complete example in `examples/SpatialIntegration.ts`.

### Scene-Specific Events

You can subscribe to events for specific scenes:

```typescript
// Register for events from a specific scene
eventSystem.registerSceneListener(
  'my-scene-id',
  SceneEventType.SCENE_OBJECT_ADDED,
  (event) => {
    console.log(`Object added to scene: ${event.data?.objectId}`);
  }
);
```

### Advanced Features

#### Priority-Based Execution

Set priority for event handlers:

```typescript
eventSystem.registerGlobalListener(
  SceneEventType.SCENE_LOADED,
  (event) => {
    console.log('This runs first!');
  },
  { priority: EventPriority.HIGH }
);
```

#### One-Time Handlers

Execute a handler only once:

```typescript
eventSystem.registerGlobalListener(
  SceneEventType.SCENE_LOADED,
  (event) => {
    console.log('This runs only once!');
  },
  { once: true }
);
```

#### Filtered Handlers

Only execute a handler if a condition is met:

```typescript
eventSystem.registerGlobalListener(
  SceneEventType.SCENE_LOADED,
  (event) => {
    console.log('Specific scene loaded!');
  },
  { 
    filter: (event) => event.sceneId === 'specific-scene-id'
  }
);
```

## Dependency Registration and Filtering (Advanced)

The event system now supports fine-grained dependency registration and event filtering using the `DependencyRegistry` and dependency-aware event delivery in the `EventBus`.

### Registering Dependencies

Systems can declare interest in specific scene elements or properties by registering dependencies:

```typescript
import { DependencyRegistry } from './DependencyRegistry';

const registry = DependencyRegistry.getInstance();

// Register interest in a specific scene
registry.registerDependency('MySystem', { type: 'scene', sceneId: 'scene-123' });

// Register interest in a specific object
registry.registerDependency('MySystem', { type: 'object', objectId: 'obj-456' });

// Register interest in a property of an object
registry.registerDependency('MySystem', { type: 'property', objectId: 'obj-456', property: 'position' });

// Register a custom filter
registry.registerDependency('MySystem', { type: 'custom', filter: (event) => event.data?.important === true });
```

### Dependency-Aware Event Delivery

When an event is emitted, the `EventBus` will deliver it only to handlers whose `subscriberId` matches a registered dependency (if any dependencies are registered for the event). If no dependencies are registered, all handlers receive the event as before.

#### Subscribing with a Subscriber ID

When subscribing to events, pass a `subscriberId` as the fourth argument to `EventBus.on`:

```typescript
import { EventBus } from './EventBus';
import { SceneEventType } from './SceneEventTypes';

EventBus.getInstance().on(
  SceneEventType.SCENE_OBJECT_ADDED,
  (event) => {
    // Handle the event
  },
  {}, // options
  'MySystem' // subscriberId
);
```

This ensures that the handler will only be called for events matching dependencies registered for 'MySystem'.

### Backward Compatibility

If no dependencies are registered for an event, all handlers are called as before. This allows gradual adoption of the dependency filtering mechanism.

## Available Event Types

See `SceneEventTypes.ts` for a complete list of available event types. The main categories are:

- Scene lifecycle events (`SCENE_PRE_LOAD`, `SCENE_LOADED`, etc.)
- Scene activation events (`SCENE_ACTIVATED`, `SCENE_DEACTIVATED`)
- Object-related events (`SCENE_OBJECT_ADDED`, `SCENE_OBJECT_REMOVED`)
- Memory management events (`MEMORY_WARNING`, `MEMORY_CRITICAL`)
- Region-related events (`REGION_ENTERED`, `REGION_EXITED`)
- Spatial system events (`COORDINATES_CHANGED`, `BOUNDARY_CROSSED`)
- Worldgen events (`TERRAIN_LOADED`, `TERRAIN_UNLOADED`, `BIOME_CHANGED`)

## Performance Considerations

- Event handling is asynchronous by default but can be forced to synchronous execution
- Event statistics are collected for monitoring and debugging
- The system has been designed with performance in mind, using efficient data structures

## Thread Safety

The event system is designed to be thread-safe, with appropriate locking mechanisms for critical sections when needed. However, it's primarily designed for the main thread model of operation.

## Configuration and Runtime Tuning

The event system supports comprehensive runtime configuration for advanced filtering, batching, error handling, logging, and monitoring. All configuration can be set via the EventBus and SceneEventSystem APIs.

### Configuration Options

| Option                | Description                                                      | Example Value |
|-----------------------|------------------------------------------------------------------|--------------|
| batchSize             | Number of events to batch before delivery                        | 10           |
| batchIntervalMs       | Time window (ms) for batching events                             | 50           |
| debounceIntervals     | Debounce interval per event type (ms)                            | { SCENE_LOADED: 100 } |
| throttleIntervals     | Throttle interval per event type (ms)                            | { SCENE_OBJECT_ADDED: 200 } |
| spatialFilters        | Spatial filter functions per event type                          | { REGION_ENTERED: (e) => e.regionId === 'r1' } |
| temporalFilters       | Temporal filter functions per event type                         | { SCENE_LOADED: (e) => e.timestamp % 2 === 0 } |
| enableBatching        | Enable/disable event batching                                    | true         |
| enableDebounce        | Enable/disable debouncing                                        | true         |
| enableThrottle        | Enable/disable throttling                                        | true         |
| logLevel              | Logging verbosity (ERROR, WARN, INFO, DEBUG)                     | 'INFO'       |
| circuitBreakerThreshold | Handler failure count before circuit breaker opens              | 5            |
| circuitBreakerTimeout | Time (ms) before circuit breaker half-opens                      | 60000        |
| retryPolicy           | Retry attempts and backoff for handlers                          | { handler: { maxAttempts: 3, backoff: 100 } } |
| replayBufferSize      | Number of recent events to keep for replay                       | 1000         |

#### Example: Setting Configuration

```typescript
import { EventBus, EventBusLogLevel } from './EventBus';

const bus = EventBus.getInstance();
bus.setConfig({
  batchSize: 20,
  debounceIntervals: { SCENE_LOADED: 100 },
  logLevel: EventBusLogLevel.DEBUG,
  circuitBreakerThreshold: 3,
  replayBufferSize: 500
});
bus.setLogLevel(EventBusLogLevel.INFO);

// Configure retry policy for a handler
bus.setRetryPolicy(myHandler, 3, 100); // 3 attempts, 100ms backoff
```

### Event Types and Payloads

| Event Type                | Payload Structure |
|---------------------------|------------------|
| SCENE_PRE_LOAD            | { sceneId, source, timestamp, metadata } |
| SCENE_LOADED              | { sceneId, source, timestamp, loadTime } |
| SCENE_UNLOADED            | { sceneId, source, timestamp, reason } |
| SCENE_ACTIVATED           | { sceneId, source, timestamp, changeSummary } |
| SCENE_OBJECT_ADDED        | { sceneId, source, timestamp, objectId, objectData } |
| SCENE_OBJECT_REMOVED      | { sceneId, source, timestamp, objectId, removalReason } |
| COORDINATES_CHANGED       | { sceneId, source, timestamp, objectId, previousTransform, newTransform } |
| BOUNDARY_CROSSED          | { sceneId, source, timestamp, objectId, previousTransform, newTransform } |
| REGION_ENTERED/EXITED     | { sceneId, source, timestamp, regionId } |
| TERRAIN_LOADED/UNLOADED   | { sceneId, source, timestamp, details } |
| BIOME_CHANGED             | { sceneId, source, timestamp, details } |

See `SceneEventTypes.ts` for full interface definitions.

### Integration Guide for New Systems

1. Register dependencies using `DependencyRegistry`.
2. Subscribe to events with `EventBus.on` or `SceneEventSystem.registerGlobalListener`.
3. Use configuration API to tune event delivery and error handling.
4. Implement robust error handling in your handlers.
5. Use metrics and logging for monitoring and debugging.

#### Example: Adding a New System

```typescript
import { DependencyRegistry } from './DependencyRegistry';
import { EventBus, SceneEventType } from './EventBus';

DependencyRegistry.getInstance().registerDependency('MySystem', { type: 'scene', sceneId: 'scene-123' });
EventBus.getInstance().on(SceneEventType.SCENE_LOADED, (event) => {
  // Handle scene loaded
}, {}, 'MySystem');
```

### Best Practices
- Use dependency registration to minimize unnecessary event delivery.
- Tune batch size and debounce/throttle intervals for your system's needs.
- Monitor metrics and adjust configuration as your workload changes.
- Use circuit breakers and retry policies to ensure system resilience.
- Document your event handlers and integration points.

### Diagrams

// (Insert sequence and architecture diagrams illustrating event flow and configuration points)

### Monitoring and Metrics

Use `EventBus.getMetrics()` to access real-time statistics:
- Event throughput
- Handler execution times
- Error rates
- Batched/dropped/filtered events

Integrate with your observability tools as needed.

### Event Replay

Replay recent events for debugging:
```typescript
EventBus.getInstance().replayEvents();
```

Filter replayed events:
```typescript
EventBus.getInstance().replayEvents(e => e.type === SceneEventType.SCENE_LOADED);
``` 