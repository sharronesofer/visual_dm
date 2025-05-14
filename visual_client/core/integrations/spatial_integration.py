"""
Spatial System integration with Scene Event System.

This module provides the glue code for connecting the spatial system
with scene management through the event-driven architecture.
"""

import logging
from typing import Dict, Any, Optional, Set
from ..events import SceneEventSystem, SceneEventType, SceneEvent, DependencyType

logger = logging.getLogger(__name__)

class SpatialIntegration:
    """Integration between Spatial System and Scene Management."""
    
    def __init__(self, spatial_system=None):
        """Initialize the spatial integration.
        
        Args:
            spatial_system: The spatial system to integrate with
        """
        self.spatial_system = spatial_system
        self.event_system = SceneEventSystem.get_instance()
        self.active_scene = None
        self.tracked_boundaries: Set[str] = set()
        
        # Register with scene event system
        self.register_event_handlers()
        
        logger.info("Spatial Integration initialized")
        
    def register_event_handlers(self) -> None:
        """Register handlers for scene events."""
        # Register system dependency
        self.event_system.register_system_dependency(
            "SpatialSystem", 
            [DependencyType.SCENE_LIFECYCLE, DependencyType.SPATIAL]
        )
        
        # Register global listeners
        self.event_system.register_global_listener(
            SceneEventType.SCENE_ACTIVATED,
            self.handle_scene_activated
        )
        
        self.event_system.register_global_listener(
            SceneEventType.SCENE_DEACTIVATED,
            self.handle_scene_deactivated
        )
        
        self.event_system.register_global_listener(
            SceneEventType.COORDINATES_CHANGED,
            self.handle_coordinates_changed
        )
        
        self.event_system.register_global_listener(
            SceneEventType.BOUNDARY_CROSSED,
            self.handle_boundary_crossed
        )
        
    def handle_scene_activated(self, event: SceneEvent) -> None:
        """Handle scene activation events.
        
        Args:
            event: Scene activated event
        """
        scene_id = event.scene_id
        self.active_scene = scene_id
        
        if self.spatial_system is not None:
            try:
                logger.info(f"Activating spatial data for scene: {scene_id}")
                # Example: self.spatial_system.load_scene_data(scene_id)
            except Exception as e:
                logger.error(f"Error activating spatial data for scene {scene_id}: {e}")
        
    def handle_scene_deactivated(self, event: SceneEvent) -> None:
        """Handle scene deactivation events.
        
        Args:
            event: Scene deactivated event
        """
        scene_id = event.scene_id
        
        if self.active_scene == scene_id:
            self.active_scene = None
            
        if self.spatial_system is not None:
            try:
                logger.info(f"Deactivating spatial data for scene: {scene_id}")
                # Example: self.spatial_system.unload_scene_data(scene_id)
            except Exception as e:
                logger.error(f"Error deactivating spatial data for scene {scene_id}: {e}")
    
    def handle_coordinates_changed(self, event: SceneEvent) -> None:
        """Handle coordinate change events.
        
        Args:
            event: Coordinates changed event
        """
        scene_id = event.scene_id
        coordinates = event.data.get("coordinates")
        
        if coordinates and self.spatial_system is not None:
            try:
                # Example: self.spatial_system.update_coordinates(scene_id, coordinates)
                
                # Check if boundary was crossed
                boundaries = self.check_boundaries(coordinates)
                if boundaries:
                    for boundary in boundaries:
                        self.emit_boundary_crossed(scene_id, boundary, coordinates)
            except Exception as e:
                logger.error(f"Error handling coordinate change: {e}")
    
    def handle_boundary_crossed(self, event: SceneEvent) -> None:
        """Handle boundary crossed events.
        
        Args:
            event: Boundary crossed event
        """
        scene_id = event.scene_id
        boundary_id = event.data.get("boundary_id")
        coordinates = event.data.get("coordinates")
        
        if self.spatial_system is not None and boundary_id:
            try:
                logger.info(f"Boundary crossed: {boundary_id} in scene {scene_id}")
                # Example: self.spatial_system.handle_boundary_crossed(scene_id, boundary_id, coordinates)
            except Exception as e:
                logger.error(f"Error handling boundary crossed: {e}")
    
    def check_boundaries(self, coordinates: Dict[str, float]) -> Set[str]:
        """Check if the coordinates cross any boundaries.
        
        Args:
            coordinates: The coordinates to check
            
        Returns:
            Set[str]: Set of boundary IDs that were crossed
        """
        # This would be implemented with actual spatial checks
        # For now, return an empty set as placeholder
        return set()
        
    def emit_boundary_crossed(self, scene_id: str, boundary_id: str, coordinates: Dict[str, float]) -> None:
        """Emit a boundary crossed event.
        
        Args:
            scene_id: ID of the scene
            boundary_id: ID of the boundary crossed
            coordinates: Coordinates where boundary was crossed
        """
        self.event_system.emit_scene_event(
            SceneEventType.BOUNDARY_CROSSED,
            scene_id=scene_id,
            source="SpatialSystem",
            data={
                "boundary_id": boundary_id,
                "coordinates": coordinates
            }
        )
    
    def set_coordinates(self, scene_id: str, coordinates: Dict[str, float]) -> None:
        """Set coordinates in a scene and emit event.
        
        Args:
            scene_id: ID of the scene
            coordinates: New coordinates
        """
        if self.spatial_system is not None:
            # Example: self.spatial_system.set_coordinates(scene_id, coordinates)
            pass
            
        # Emit coordinates changed event
        self.event_system.emit_scene_event(
            SceneEventType.COORDINATES_CHANGED,
            scene_id=scene_id,
            source="SpatialSystem",
            data={"coordinates": coordinates}
        )
    
    def shutdown(self) -> None:
        """Shut down the spatial integration."""
        logger.info("Shutting down Spatial Integration")
        
        # Unregister system dependency
        self.event_system.unregister_system_dependency("SpatialSystem") 