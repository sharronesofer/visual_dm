# Unity Core Systems

This directory contains core systems for the Visual_DM Unity client, including the Event System implementation.

## Event System

### Key Files

- `EventBus.cs`: Core implementation of the EventBus with type safety, prioritization, and async support
- `EventSystem.cs`: Static utility class for simplified event usage
- `EventBusExtensions.cs`: Extension methods for integrating with ScriptableObject event channels

### Event Channels

The `EventChannels` directory contains ScriptableObject-based event channels for Unity-specific integration:

- `EventChannelBase.cs`: Base classes for all event channels
- `VoidEventChannel.cs`: For events with no parameters 
- `StringEventChannel.cs`: For string events
- `GameObjectEventChannel.cs`: For GameObject events
- `Vector3EventChannel.cs`: For position/direction events

### Usage

```csharp
using VisualDM.Core;

// Using the simplified API
EventSystem.Subscribe<MyEventType>(HandleEvent);
EventSystem.Publish(new MyEventType { /* data */ });

// Using the EventBus directly
EventBus.Instance.Subscribe<MyEventType>(HandleEvent);
EventBus.Instance.Publish(new MyEventType { /* data */ });
```

## Documentation

For complete documentation including examples and best practices, see:

- [Event System Documentation](/docs/event_system.md)
- [Unity Example](/UnityClient/Assets/Scripts/Examples/EventBusUsage.cs)
- [Unity Tests](/UnityClient/Assets/Scripts/Tests/Core/EventBusTests.cs) 