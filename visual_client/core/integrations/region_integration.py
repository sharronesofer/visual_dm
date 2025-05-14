"""
Region System integration with Scene Event System.

This module provides the glue code for connecting the region system
with scene management through the event-driven architecture.
"""

import logging
from typing import Dict, Any, Optional, List, Set
from ..events import SceneEventSystem, SceneEventType, SceneEvent, DependencyType

logger = logging.getLogger(__name__)

class RegionIntegration:
    """Integration between Region System and Scene Management."""
    
    def __init__(self, region_system=None):
        """Initialize the region integration.
        
        Args:
            region_system: The region system to integrate with
        """
        self.region_system = region_system
        self.event_system = SceneEventSystem.get_instance()
        self.active_scene = None
        self.active_regions: Dict[str, Set[str]] = {}  # scene_id -> set of region_ids
        
        # Register with scene event system
        self.register_event_handlers()
        
        logger.info("Region Integration initialized")
        
    def register_event_handlers(self) -> None:
        """Register handlers for scene events."""
        # Register system dependency
        self.event_system.register_system_dependency(
            "RegionSystem", 
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
            SceneEventType.REGION_ENTERED,
            self.handle_region_entered
        )
        
        self.event_system.register_global_listener(
            SceneEventType.REGION_EXITED,
            self.handle_region_exited
        )
        
        self.event_system.register_global_listener(
            SceneEventType.TERRAIN_LOADED,
            self.handle_terrain_loaded
        )
        
    def handle_scene_activated(self, event: SceneEvent) -> None:
        """Handle scene activation events.
        
        Args:
            event: Scene activated event
        """
        scene_id = event.scene_id
        self.active_scene = scene_id
        
        if scene_id not in self.active_regions:
            self.active_regions[scene_id] = set()
        
        if self.region_system is not None:
            try:
                logger.info(f"Activating region system for scene: {scene_id}")
                # Example: self.region_system.activate_scene(scene_id)
                
                # Initialize with starting region
                # Example: starting_region = self.region_system.get_starting_region(scene_id)
                # if starting_region:
                #     self.emit_region_entered(scene_id, starting_region, {"initial": True})
            except Exception as e:
                logger.error(f"Error activating region system for scene {scene_id}: {e}")
        
    def handle_scene_deactivated(self, event: SceneEvent) -> None:
        """Handle scene deactivation events.
        
        Args:
            event: Scene deactivated event
        """
        scene_id = event.scene_id
        
        if self.active_scene == scene_id:
            self.active_scene = None
            
        if self.region_system is not None:
            try:
                logger.info(f"Deactivating region system for scene: {scene_id}")
                # Example: self.region_system.deactivate_scene(scene_id)
                
                # Clear active regions
                if scene_id in self.active_regions:
                    self.active_regions[scene_id] = set()
            except Exception as e:
                logger.error(f"Error deactivating region system for scene {scene_id}: {e}")
    
    def handle_coordinates_changed(self, event: SceneEvent) -> None:
        """Handle coordinate change events.
        
        Args:
            event: Coordinates changed event
        """
        scene_id = event.scene_id
        coordinates = event.data.get("coordinates")
        
        if coordinates and self.region_system is not None:
            try:
                # Check if player/camera has entered a new region
                current_region = self.get_region_at_coordinates(scene_id, coordinates)
                
                if current_region:
                    # Check if this is a new region
                    if scene_id in self.active_regions:
                        if current_region not in self.active_regions[scene_id]:
                            # Entered a new region
                            self.emit_region_entered(scene_id, current_region, coordinates)
                            
                            # Check if we left any regions
                            old_regions = set(self.active_regions[scene_id])
                            for region_id in old_regions:
                                if not self.is_in_region(scene_id, coordinates, region_id):
                                    self.emit_region_exited(scene_id, region_id, coordinates)
                    else:
                        # First region in this scene
                        self.active_regions[scene_id] = set()
                        self.emit_region_entered(scene_id, current_region, coordinates)
            except Exception as e:
                logger.error(f"Error handling coordinate change: {e}")
    
    def handle_region_entered(self, event: SceneEvent) -> None:
        """Handle region entered events.
        
        Args:
            event: Region entered event
        """
        scene_id = event.scene_id
        region_id = event.data.get("region_id")
        coordinates = event.data.get("coordinates")
        
        if scene_id and region_id:
            logger.info(f"Region entered: {region_id} in scene {scene_id}")
            
            # Track active region
            if scene_id not in self.active_regions:
                self.active_regions[scene_id] = set()
            self.active_regions[scene_id].add(region_id)
            
            # Notify region system
            if self.region_system is not None:
                try:
                    # Example: self.region_system.on_region_entered(scene_id, region_id, coordinates)
                    pass
                except Exception as e:
                    logger.error(f"Error handling region entered: {e}")
    
    def handle_region_exited(self, event: SceneEvent) -> None:
        """Handle region exited events.
        
        Args:
            event: Region exited event
        """
        scene_id = event.scene_id
        region_id = event.data.get("region_id")
        coordinates = event.data.get("coordinates")
        
        if scene_id and region_id:
            logger.info(f"Region exited: {region_id} in scene {scene_id}")
            
            # Remove from active regions
            if scene_id in self.active_regions and region_id in self.active_regions[scene_id]:
                self.active_regions[scene_id].remove(region_id)
            
            # Notify region system
            if self.region_system is not None:
                try:
                    # Example: self.region_system.on_region_exited(scene_id, region_id, coordinates)
                    pass
                except Exception as e:
                    logger.error(f"Error handling region exited: {e}")
    
    def handle_terrain_loaded(self, event: SceneEvent) -> None:
        """Handle terrain loaded events.
        
        Args:
            event: Terrain loaded event
        """
        scene_id = event.scene_id
        region_id = event.data.get("region_id")
        
        if scene_id and region_id and self.region_system is not None:
            try:
                # Notify region system about newly loaded terrain
                # Example: self.region_system.on_terrain_loaded(scene_id, region_id)
                pass
            except Exception as e:
                logger.error(f"Error handling terrain loaded: {e}")
    
    def get_region_at_coordinates(self, scene_id: str, coordinates: Dict[str, float]) -> Optional[str]:
        """Get the region ID at the given coordinates.
        
        Args:
            scene_id: ID of the scene
            coordinates: The coordinates to check
            
        Returns:
            Optional[str]: Region ID or None if not in any region
        """
        # This would be implemented with actual region system logic
        # For now, return None as placeholder
        return None
    
    def is_in_region(self, scene_id: str, coordinates: Dict[str, float], region_id: str) -> bool:
        """Check if the coordinates are in the given region.
        
        Args:
            scene_id: ID of the scene
            coordinates: The coordinates to check
            region_id: ID of the region to check
            
        Returns:
            bool: True if coordinates are in the region
        """
        # This would be implemented with actual region system logic
        # For now, return False as placeholder
        return False
    
    def emit_region_entered(self, scene_id: str, region_id: str, coordinates: Dict[str, Any]) -> None:
        """Emit a region entered event.
        
        Args:
            scene_id: ID of the scene
            region_id: ID of the region entered
            coordinates: Coordinates where region was entered
        """
        self.event_system.emit_scene_event(
            SceneEventType.REGION_ENTERED,
            scene_id=scene_id,
            source="RegionSystem",
            data={
                "region_id": region_id,
                "coordinates": coordinates
            }
        )
    
    def emit_region_exited(self, scene_id: str, region_id: str, coordinates: Dict[str, Any]) -> None:
        """Emit a region exited event.
        
        Args:
            scene_id: ID of the scene
            region_id: ID of the region exited
            coordinates: Coordinates where region was exited
        """
        self.event_system.emit_scene_event(
            SceneEventType.REGION_EXITED,
            scene_id=scene_id,
            source="RegionSystem",
            data={
                "region_id": region_id,
                "coordinates": coordinates
            }
        )
    
    def get_active_regions(self, scene_id: Optional[str] = None) -> Dict[str, Set[str]]:
        """Get active regions.
        
        Args:
            scene_id: Optional scene ID to filter by
            
        Returns:
            Dict[str, Set[str]]: Dictionary of scene_id -> set of region_ids
        """
        if scene_id:
            if scene_id in self.active_regions:
                return {scene_id: self.active_regions[scene_id]}
            return {scene_id: set()}
        return dict(self.active_regions)
    
    def shutdown(self) -> None:
        """Shut down the region integration."""
        logger.info("Shutting down Region Integration")
        
        # Unregister system dependency
        self.event_system.unregister_system_dependency("RegionSystem") 