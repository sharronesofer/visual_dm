"""
Example usage of the events system.

This module demonstrates how to use the events system in both
synchronous and asynchronous code.
"""
import asyncio
import logging
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

# Import the event system components
from backend.systems.events import (
    EventDispatcher, EventBase, EventManager,
    SystemEvent, SystemEventType,
    MemoryEvent, MemoryEventType,
    logging_middleware, error_handling_middleware
)

# Example 1: Basic synchronous usage
def example_1_sync_usage():
    """Demonstrate basic synchronous event usage."""
    print("\n=== Example 1: Basic Synchronous Usage ===")
    
    # Get the event dispatcher
    dispatcher = EventDispatcher.get_instance()
    
    # Define a handler function
    def handle_system_event(event: SystemEvent) -> None:
        print(f"Received system event: {event.event_type} from {event.component}")
        print(f"Event details: {event.details}")
    
    # Subscribe to events
    dispatcher.subscribe(SystemEvent, handle_system_event)
    
    # Publish an event
    event = SystemEvent(
        event_type=SystemEventType.STARTUP.value,
        component="example_app",
        details={"version": "1.0.0", "environment": "development"}
    )
    
    results = dispatcher.publish_sync(event)
    print(f"Event dispatched, got {len(results)} results")
    
    # Unsubscribe when done
    dispatcher.unsubscribe(SystemEvent, handle_system_event)
    print("Handler unsubscribed")

# Example 2: Using EventManager
def example_2_event_manager():
    """Demonstrate using the EventManager utility."""
    print("\n=== Example 2: Using EventManager ===")
    
    # Create an event manager
    manager = EventManager()
    
    # Keep track of received events
    received_events: List[EventBase] = []
    
    # Define a handler
    def handle_memory_event(event: MemoryEvent) -> None:
        print(f"Received memory event: {event.event_type} for entity {event.entity_id}")
        received_events.append(event)
    
    # Subscribe to events with a priority
    manager.subscribe(MemoryEvent, handle_memory_event, priority=10)
    
    # Publish some events
    for i in range(3):
        event = MemoryEvent(
            event_type=MemoryEventType.CREATED.value,
            entity_id=f"npc_{i+1}",
            memory_id=f"memory_{i+1}",
            memory_type="observation",
            content=f"Test memory content {i+1}"
        )
        manager.publish(event)
    
    print(f"Received {len(received_events)} memory events")
    
    # Clean up
    manager.cleanup()
    print("Event manager cleaned up")

# Example 3: Using middleware
def example_3_middleware():
    """Demonstrate using middleware with the event system."""
    print("\n=== Example 3: Using Middleware ===")
    
    # Get the event dispatcher
    dispatcher = EventDispatcher.get_instance()
    
    # Add middleware (which would normally be done at startup)
    dispatcher.add_middleware(logging_middleware)
    dispatcher.add_middleware(error_handling_middleware)
    
    # Define a handler that might fail
    def risky_handler(event: SystemEvent) -> None:
        if event.event_type == SystemEventType.ERROR.value:
            print("Handler encountered an error!")
            raise ValueError("Simulated error")
        print(f"Successfully handled event: {event.event_type}")
    
    # Subscribe to events
    dispatcher.subscribe(SystemEvent, risky_handler)
    
    # Publish events - one will succeed, one will fail but be caught by middleware
    events = [
        SystemEvent(
            event_type=SystemEventType.INFO.value,
            component="example_app",
            details={"message": "This should succeed"}
        ),
        SystemEvent(
            event_type=SystemEventType.ERROR.value,
            component="example_app",
            details={"message": "This should trigger an error but be caught"}
        )
    ]
    
    for event in events:
        try:
            dispatcher.publish_sync(event)
            print("Event processing completed")
        except Exception as e:
            print(f"Event processing failed: {e}")
    
    # Clean up
    dispatcher.unsubscribe(SystemEvent, risky_handler)
    print("Handler unsubscribed")

# Example 4: Asynchronous event handling
async def example_4_async_events():
    """Demonstrate asynchronous event handling."""
    print("\n=== Example 4: Asynchronous Event Handling ===")
    
    # Get the event dispatcher
    dispatcher = EventDispatcher.get_instance()
    
    # Define an async handler
    async def async_handler(event: SystemEvent) -> str:
        print(f"Processing event: {event.event_type}...")
        # Simulate some async work
        await asyncio.sleep(0.5)
        print(f"Finished processing event: {event.event_type}")
        return f"Processed {event.event_type}"
    
    # Subscribe to events
    dispatcher.subscribe(SystemEvent, async_handler)
    
    # Publish an event asynchronously
    event = SystemEvent(
        event_type=SystemEventType.INFO.value,
        component="async_app",
        details={"async": True}
    )
    
    # Await the result
    results = await dispatcher.publish(event)
    print(f"Event dispatched, got results: {results}")
    
    # Clean up
    dispatcher.unsubscribe(SystemEvent, async_handler)
    print("Async handler unsubscribed")

# Run all examples
def run_examples():
    """Run all the examples."""
    # Reset the dispatcher between examples
    EventDispatcher._instance = None
    
    # Run synchronous examples
    example_1_sync_usage()
    example_2_event_manager()
    example_3_middleware()
    
    # Run async example
    asyncio.run(example_4_async_events())

if __name__ == "__main__":
    run_examples() 