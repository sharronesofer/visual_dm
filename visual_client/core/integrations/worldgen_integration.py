"""
World Generation System integration with Scene Event System.

This module provides the glue code for connecting the world generation system
with scene management through the event-driven architecture.
"""

import logging
from typing import Dict, Any, Optional, List
from ..events import SceneEventSystem, SceneEventType, SceneEvent, DependencyType

logger = logging.getLogger(__name__)

class WorldGenIntegration:
    """Integration between World Generation System and Scene Management."""
    
    def __init__(self, worldgen_system=None):
        """Initialize the world generation integration.
        
        Args:
            worldgen_system: The world generation system to integrate with
        """
        self.worldgen_system = worldgen_system
        self.event_system = SceneEventSystem.get_instance()
        self.active_scene = None
        self.loaded_regions: Dict[str, List[str]] = {}  # scene_id -> list of region_ids
        
        # Register with scene event system
        self.register_event_handlers()
        
        logger.info("WorldGen Integration initialized")
        
    def register_event_handlers(self) -> None:
        """Register handlers for scene events."""
        # Register system dependency
        self.event_system.register_system_dependency(
            "WorldGenSystem", 
            [DependencyType.SCENE_LIFECYCLE, DependencyType.WORLDGEN, DependencyType.SPATIAL]
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
        
        self.event_system.register_global_listener(
            SceneEventType.TERRAIN_LOADED,
            self.handle_terrain_loaded
        )
        
        self.event_system.register_global_listener(
            SceneEventType.TERRAIN_UNLOADED,
            self.handle_terrain_unloaded
        )
        
    def handle_scene_activated(self, event: SceneEvent) -> None:
        """Handle scene activation events.
        
        Args:
            event: Scene activated event
        """
        scene_id = event.scene_id
        self.active_scene = scene_id
        
        if scene_id not in self.loaded_regions:
            self.loaded_regions[scene_id] = []
        
        if self.worldgen_system is not None:
            try:
                logger.info(f"Initializing world generation for scene: {scene_id}")
                # Example: self.worldgen_system.initialize_scene(scene_id)
                
                # Load initial terrain around starting point
                # Example: regions = self.worldgen_system.load_initial_regions(scene_id)
                # self.loaded_regions[scene_id].extend(regions)
            except Exception as e:
                logger.error(f"Error initializing world generation for scene {scene_id}: {e}")
        
    def handle_scene_deactivated(self, event: SceneEvent) -> None:
        """Handle scene deactivation events.
        
        Args:
            event: Scene deactivated event
        """
        scene_id = event.scene_id
        
        if self.active_scene == scene_id:
            self.active_scene = None
            
        if self.worldgen_system is not None:
            try:
                logger.info(f"Saving world generation state for scene: {scene_id}")
                # Example: self.worldgen_system.save_state(scene_id)
                
                # Unload regions
                if scene_id in self.loaded_regions:
                    for region_id in self.loaded_regions[scene_id]:
                        self.unload_terrain(scene_id, region_id)
                    self.loaded_regions[scene_id] = []
            except Exception as e:
                logger.error(f"Error saving world generation state for scene {scene_id}: {e}")
    
    def handle_coordinates_changed(self, event: SceneEvent) -> None:
        """Handle coordinate change events.
        
        Args:
            event: Coordinates changed event
        """
        scene_id = event.scene_id
        coordinates = event.data.get("coordinates")
        
        if coordinates and self.worldgen_system is not None:
            try:
                # Check if new terrain needs to be loaded
                needed_regions = self.check_needed_regions(scene_id, coordinates)
                for region_id in needed_regions:
                    if scene_id in self.loaded_regions and region_id not in self.loaded_regions[scene_id]:
                        self.load_terrain(scene_id, region_id, coordinates)
                
                # Check if terrain can be unloaded
                if scene_id in self.loaded_regions:
                    far_regions = self.check_far_regions(scene_id, coordinates)
                    for region_id in far_regions:
                        if region_id in self.loaded_regions[scene_id]:
                            self.unload_terrain(scene_id, region_id)
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
        
        if self.worldgen_system is not None and boundary_id:
            try:
                # Check if this boundary crossing requires biome change
                biome_info = self.check_biome_change(scene_id, boundary_id, coordinates)
                if biome_info:
                    self.emit_biome_changed(scene_id, biome_info)
            except Exception as e:
                logger.error(f"Error handling boundary crossed: {e}")
    
    def handle_terrain_loaded(self, event: SceneEvent) -> None:
        """Handle terrain loaded events.
        
        Args:
            event: Terrain loaded event
        """
        scene_id = event.scene_id
        region_id = event.data.get("region_id")
        
        if scene_id and region_id:
            logger.info(f"Terrain loaded: {region_id} in scene {scene_id}")
            # Track loaded region
            if scene_id not in self.loaded_regions:
                self.loaded_regions[scene_id] = []
            if region_id not in self.loaded_regions[scene_id]:
                self.loaded_regions[scene_id].append(region_id)
    
    def handle_terrain_unloaded(self, event: SceneEvent) -> None:
        """Handle terrain unloaded events.
        
        Args:
            event: Terrain unloaded event
        """
        scene_id = event.scene_id
        region_id = event.data.get("region_id")
        
        if scene_id and region_id:
            logger.info(f"Terrain unloaded: {region_id} in scene {scene_id}")
            # Track unloaded region
            if scene_id in self.loaded_regions and region_id in self.loaded_regions[scene_id]:
                self.loaded_regions[scene_id].remove(region_id)
    
    def check_needed_regions(self, scene_id: str, coordinates: Dict[str, float]) -> List[str]:
        """Check which regions need to be loaded based on coordinates.
        
        Args:
            scene_id: ID of the scene
            coordinates: The current coordinates
            
        Returns:
            List[str]: List of region IDs that need to be loaded
        """
        # This would be implemented with actual world gen logic
        # For now, return an empty list as placeholder
        return []
    
    def check_far_regions(self, scene_id: str, coordinates: Dict[str, float]) -> List[str]:
        """Check which regions are too far and can be unloaded.
        
        Args:
            scene_id: ID of the scene
            coordinates: The current coordinates
            
        Returns:
            List[str]: List of region IDs that can be unloaded
        """
        # This would be implemented with actual world gen logic
        # For now, return an empty list as placeholder
        return []
    
    def check_biome_change(self, scene_id: str, boundary_id: str, coordinates: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Check if crossing this boundary results in a biome change.
        
        Args:
            scene_id: ID of the scene
            boundary_id: ID of the boundary crossed
            coordinates: Coordinates where boundary was crossed
            
        Returns:
            Optional[Dict[str, Any]]: Biome information or None if no change
        """
        # This would be implemented with actual world gen logic
        # For now, return None as placeholder
        return None
    
    def load_terrain(self, scene_id: str, region_id: str, coordinates: Dict[str, float]) -> None:
        """Load terrain for a region and emit event.
        
        Args:
            scene_id: ID of the scene
            region_id: ID of the region to load
            coordinates: Coordinates that triggered the load
        """
        if self.worldgen_system is not None:
            # Example: terrain_data = self.worldgen_system.load_region(scene_id, region_id)
            pass
            
        # Emit terrain loaded event
        self.event_system.emit_scene_event(
            SceneEventType.TERRAIN_LOADED,
            scene_id=scene_id,
            source="WorldGenSystem",
            data={
                "region_id": region_id,
                "coordinates": coordinates
            }
        )
    
    def unload_terrain(self, scene_id: str, region_id: str) -> None:
        """Unload terrain for a region and emit event.
        
        Args:
            scene_id: ID of the scene
            region_id: ID of the region to unload
        """
        if self.worldgen_system is not None:
            # Example: self.worldgen_system.unload_region(scene_id, region_id)
            pass
            
        # Emit terrain unloaded event
        self.event_system.emit_scene_event(
            SceneEventType.TERRAIN_UNLOADED,
            scene_id=scene_id,
            source="WorldGenSystem",
            data={"region_id": region_id}
        )
    
    def emit_biome_changed(self, scene_id: str, biome_info: Dict[str, Any]) -> None:
        """Emit a biome changed event.
        
        Args:
            scene_id: ID of the scene
            biome_info: Information about the new biome
        """
        self.event_system.emit_scene_event(
            SceneEventType.BIOME_CHANGED,
            scene_id=scene_id,
            source="WorldGenSystem",
            data=biome_info
        )
    
    def shutdown(self) -> None:
        """Shut down the world generation integration."""
        logger.info("Shutting down WorldGen Integration")
        
        # Unregister system dependency
        self.event_system.unregister_system_dependency("WorldGenSystem") 