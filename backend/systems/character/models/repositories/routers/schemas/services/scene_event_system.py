"""
Scene Event System for integration between Scene Management and related systems.

This system provides a specialized interface for scene-related events and manages
the integration between the Scene Manager and dependent systems like spatial, 
region, and worldgen systems.
"""

import logging
import threading
from typing import Dict, List, Set, Callable, Any, Optional, Union, TypeVar
from enum import Enum
from .event_bus import EventBus, EventPriority
from .scene_events import SceneEvent, SceneEventType, create_event

logger = logging.getLogger(__name__)

class DependencyType(Enum):
    """Types of dependencies a system can have on scenes."""
    ALL = "all"               # Dependent on all scene changes
    SCENE_LIFECYCLE = "scene" # Dependent on scene creation/activation/etc.
    ASSETS = "assets"         # Dependent on asset loading/unloading
    SPATIAL = "spatial"       # Dependent on scene spatial properties 
    WORLDGEN = "worldgen"     # Dependent on scene world generation
    MEMORY = "memory"         # Dependent on memory management events

class SceneEventSystem:
    """Manages event-driven integration between Scene Manager and other systems."""
    
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the SceneEventSystem.
        
        Returns:
            SceneEventSystem: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the scene event system (use get_instance() instead)."""
        self.event_bus = EventBus.get_instance()
        self.system_dependencies: Dict[str, Set[DependencyType]] = {}
        self.scene_listeners: Dict[str, Dict[SceneEventType, List[Callable]]] = {}
        self.global_listeners: Dict[SceneEventType, List[Callable]] = {}
        
        # Configuration
        self.config = {
            "log_events": True,
            "propagate_immediately": False,  # If True, bypass queue for critical events
            "max_queued_events": 1000,       # Maximum events to queue before dropping
        }
        
        logger.info("Scene Event System initialized")
        
    def register_system_dependency(
        self,
        system_id: str,
        dependency_types: Union[DependencyType, List[DependencyType]]
    ) -> None:
        """Register a system's dependencies on scene events.
        
        Args:
            system_id: Unique identifier for the dependent system
            dependency_types: Type(s) of dependencies this system has
        """
        if not isinstance(dependency_types, list):
            dependency_types = [dependency_types]
            
        if system_id not in self.system_dependencies:
            self.system_dependencies[system_id] = set()
            
        for dep_type in dependency_types:
            self.system_dependencies[system_id].add(dep_type)
            
        logger.debug(f"Registered system '{system_id}' with dependencies: {dependency_types}")
        
    def unregister_system_dependency(self, system_id: str) -> None:
        """Unregister a system's dependencies.
        
        Args:
            system_id: System identifier to unregister
        """
        if system_id in self.system_dependencies:
            del self.system_dependencies[system_id]
            logger.debug(f"Unregistered system '{system_id}'")
            
    def register_scene_listener(
        self,
        scene_id: str,
        event_type: SceneEventType,
        callback: Callable[[SceneEvent], None]
    ) -> None:
        """Register a listener for a specific scene and event type.
        
        Args:
            scene_id: Scene to listen for events from
            event_type: Type of event to listen for
            callback: Function to call when event occurs
        """
        if scene_id not in self.scene_listeners:
            self.scene_listeners[scene_id] = {}
            
        if event_type not in self.scene_listeners[scene_id]:
            self.scene_listeners[scene_id][event_type] = []
            
        self.scene_listeners[scene_id][event_type].append(callback)
        logger.debug(f"Registered listener for scene '{scene_id}', event {event_type}")
        
    def unregister_scene_listener(
        self,
        scene_id: str,
        event_type: SceneEventType,
        callback: Callable[[SceneEvent], None]
    ) -> bool:
        """Unregister a listener for a specific scene and event type.
        
        Args:
            scene_id: Scene ID
            event_type: Event type
            callback: Callback to remove
            
        Returns:
            bool: True if found and removed, False otherwise
        """
        if (scene_id not in self.scene_listeners or
            event_type not in self.scene_listeners[scene_id]):
            return False
            
        callbacks = self.scene_listeners[scene_id][event_type]
        if callback in callbacks:
            callbacks.remove(callback)
            logger.debug(f"Unregistered listener for scene '{scene_id}', event {event_type}")
            return True
            
        return False
        
    def register_global_listener(
        self,
        event_type: SceneEventType,
        callback: Callable[[SceneEvent], None]
    ) -> None:
        """Register a global listener for all scenes of a particular event type.
        
        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs
        """
        if event_type not in self.global_listeners:
            self.global_listeners[event_type] = []
            
        self.global_listeners[event_type].append(callback)
        logger.debug(f"Registered global listener for event {event_type}")
        
        # Hook up to event bus for this event type
        self._ensure_event_bus_subscription(event_type)
        
    def unregister_global_listener(
        self,
        event_type: SceneEventType,
        callback: Callable[[SceneEvent], None]
    ) -> bool:
        """Unregister a global listener.
        
        Args:
            event_type: Event type
            callback: Callback to remove
            
        Returns:
            bool: True if found and removed, False otherwise
        """
        if event_type not in self.global_listeners:
            return False
            
        if callback in self.global_listeners[event_type]:
            self.global_listeners[event_type].remove(callback)
            logger.debug(f"Unregistered global listener for event {event_type}")
            return True
            
        return False
    
    def _ensure_event_bus_subscription(self, event_type: SceneEventType) -> None:
        """Ensure we have an event bus subscription for this event type.
        
        This is called automatically when registering global listeners.
        
        Args:
            event_type: Event type to subscribe to
        """
        # Check if we already have subscribers for this event type
        if self.event_bus.get_subscriber_count(event_type) > 0:
            return
            
        # Subscribe to the event bus
        self.event_bus.subscribe(
            event_type,
            self._handle_event,
            priority=EventPriority.HIGH
        )
        
    def _handle_event(self, event: SceneEvent) -> None:
        """Handle an event from the event bus.
        
        This is the callback registered with the event bus.
        
        Args:
            event: Event to handle
        """
        try:
            event_type = event.type
            scene_id = event.scene_id
            
            # Log the event if configured
            if self.config["log_events"]:
                logger.debug(f"Handling event: {event}")
                
            # Call global listeners for this event type
            if event_type in self.global_listeners:
                for callback in self.global_listeners[event_type]:
                    try:
                        callback(event)
                    except Exception as e:
                        logger.error(f"Error in global event listener: {e}", exc_info=True)
                        
            # Call scene-specific listeners
            if scene_id and scene_id in self.scene_listeners:
                if event_type in self.scene_listeners[scene_id]:
                    for callback in self.scene_listeners[scene_id][event_type]:
                        try:
                            callback(event)
                        except Exception as e:
                            logger.error(f"Error in scene event listener: {e}", exc_info=True)
                            
        except Exception as e:
            logger.error(f"Error handling event: {e}", exc_info=True)
            
    def emit_scene_event(
        self,
        event_type: SceneEventType,
        scene_id: Optional[str] = None,
        source: str = "SceneManager",
        data: Optional[Dict[str, Any]] = None,
        immediate: Optional[bool] = None
    ) -> None:
        """Emit a scene event to all listeners.
        
        Args:
            event_type: Type of event from SceneEventType enum
            scene_id: Optional ID of the scene related to this event
            source: Component/system that generated this event
            data: Additional data to include with the event
            immediate: Override config to publish immediately if True
        """
        event = create_event(event_type, scene_id, source, data)
        
        # Determine if we should publish immediately
        should_publish_immediate = immediate
        if should_publish_immediate is None:
            should_publish_immediate = self.config["propagate_immediately"]
            
        # Publish the event
        if should_publish_immediate:
            self.event_bus.publish_immediate(event_type, event)
        else:
            self.event_bus.publish(event_type, event)
            
    def set_config(self, key: str, value: Any) -> None:
        """Update a configuration setting.
        
        Args:
            key: Configuration key
            value: New value
        """
        if key in self.config:
            self.config[key] = value
            logger.debug(f"Updated config: {key} = {value}")
        else:
            logger.warning(f"Unknown config key: {key}")
            
    def get_config(self, key: str) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key
            
        Returns:
            Any: Configuration value or None if not found
        """
        return self.config.get(key)
        
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about event processing.
        
        Returns:
            Dict[str, Any]: Event system statistics
        """
        stats = self.event_bus.get_stats()
        
        # Add our own stats
        stats.update({
            "system_dependencies": {
                system_id: [dep.value for dep in deps]
                for system_id, deps in self.system_dependencies.items()
            },
            "scene_listeners": {
                scene_id: {
                    event_type.name: len(callbacks)
                    for event_type, callbacks in scene_listeners.items()
                }
                for scene_id, scene_listeners in self.scene_listeners.items()
            },
            "global_listeners": {
                event_type.name: len(callbacks)
                for event_type, callbacks in self.global_listeners.items()
            }
        })
        
        return stats
        
    def clear_stats(self) -> None:
        """Clear event statistics."""
        self.event_bus.clear_stats()
        
    def shutdown(self) -> None:
        """Shut down the scene event system."""
        # Nothing additional to shut down here, but keep the method for future use
        logger.info("Scene Event System shut down") 
