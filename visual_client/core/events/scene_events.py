"""
Scene event system for integration between Scene Management and other systems.
"""

from enum import Enum, auto
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
import time
import logging

logger = logging.getLogger(__name__)

class SceneEventType(Enum):
    """Scene event types for integration with other systems."""
    # Scene lifecycle events
    SCENE_REGISTERED = auto()
    SCENE_UNREGISTERED = auto()
    SCENE_ACTIVATED = auto()
    SCENE_DEACTIVATED = auto()
    SCENE_PRELOADED = auto()
    
    # Asset-related events
    ASSET_REGISTERED = auto()
    ASSET_LOADED = auto()
    ASSET_UNLOADED = auto()
    ASSET_PRIORITY_CHANGED = auto()
    
    # Memory management events
    MEMORY_WARNING = auto()
    MEMORY_CRITICAL = auto()
    
    # Region-related events
    REGION_ENTERED = auto()
    REGION_EXITED = auto()
    
    # Spatial system events
    COORDINATES_CHANGED = auto()
    BOUNDARY_CROSSED = auto()
    
    # Worldgen events
    TERRAIN_LOADED = auto()
    TERRAIN_UNLOADED = auto()
    BIOME_CHANGED = auto()
    
    # Generic events
    SCENE_DATA_UPDATED = auto()
    SCENE_ERROR = auto()

@dataclass
class SceneEvent:
    """Event object for scene-related events."""
    type: SceneEventType
    scene_id: Optional[str] = None
    timestamp: float = None
    source: str = "SceneManager"
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.timestamp is None:
            self.timestamp = time.time()
            
        if self.data is None:
            self.data = {}
            
    def __str__(self) -> str:
        """String representation of the event."""
        return f"{self.type.name} - Scene: {self.scene_id} - Source: {self.source} - Time: {self.timestamp}"


def create_event(
    event_type: SceneEventType,
    scene_id: Optional[str] = None,
    source: str = "SceneManager",
    data: Optional[Dict[str, Any]] = None
) -> SceneEvent:
    """Create a scene event.
    
    Args:
        event_type: Type of event from SceneEventType enum
        scene_id: Optional ID of the scene related to this event
        source: Component/system that generated this event
        data: Additional data to include with the event
        
    Returns:
        SceneEvent: Populated event object
    """
    return SceneEvent(
        type=event_type,
        scene_id=scene_id,
        source=source,
        data=data or {}
    ) 

class SceneEventSystem:
    """
    Minimal event system for registering and dispatching scene events (singleton).
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SceneEventSystem, cls).__new__(cls)
            cls._instance._listeners = []
        return cls._instance

    def __init__(self):
        # Idempotent: do not reinitialize _listeners if already set
        if not hasattr(self, '_listeners'):
            self._listeners = []

    def register_listener(self, callback):
        self._listeners.append(callback)

    def dispatch(self, event: SceneEvent):
        for callback in self._listeners:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event listener: {e}")

    def emit_scene_event(self, event_type, scene_id=None, source="SceneManager", data=None):
        """Construct and dispatch a SceneEvent from arguments."""
        event = create_event(event_type, scene_id=scene_id, source=source, data=data)
        self.dispatch(event)

    @classmethod
    def get_instance(cls):
        return cls() 