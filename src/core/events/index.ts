/**
 * Event system package for event-driven architecture.
 * 
 * This package provides a robust event system for communication between components,
 * with a focus on scene management integration.
 */

// Export event types
export { SceneEventType, type ISceneEvent } from './SceneEventTypes';

// Export base event bus
export {
    EventBus,
    EventPriority,
    type EventHandler,
    type EventSubscriptionOptions
} from './EventBus';

// Export scene event system
export {
    SceneEventSystem,
    DependencyType,
    createSceneEvent
} from './SceneEventSystem'; 