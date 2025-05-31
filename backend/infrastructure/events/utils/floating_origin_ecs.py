"""
Integration of the floating origin system with an entity component system (ECS).
Provides components and systems for floating origin support in ECS architecture.
"""

from typing import Dict, List, Set, Any, Optional, Callable
from dataclasses import dataclass, field
import logging

from backend.infrastructure.shared.utils.coordinates import GlobalCoord, LocalCoord
from backend.infrastructure.shared.utils.floating_origin import FloatingOrigin, floating_origin

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class TransformComponent:
    """
    Component for entity positioning and transformation.
    Stores both global and local coordinates.
    """
    global_x: float = 0.0
    global_y: float = 0.0
    global_z: float = 0.0
    local_x: float = 0.0
    local_y: float = 0.0
    local_z: float = 0.0
    rotation: float = 0.0
    scale: float = 1.0
    
    def get_global_position(self) -> GlobalCoord:
        """Get global position as GlobalCoord."""
        return GlobalCoord(self.global_x, self.global_y, self.global_z)
    
    def set_global_position(self, x: float, y: float, z: float) -> None:
        """Set global position directly."""
        self.global_x = x
        self.global_y = y
        self.global_z = z
    
    def get_local_position(self) -> LocalCoord:
        """Get local position as LocalCoord."""
        return LocalCoord(self.local_x, self.local_y, self.local_z)
    
    def set_local_position(self, x: float, y: float, z: float) -> None:
        """Set local position directly."""
        self.local_x = x
        self.local_y = y
        self.local_z = z
    
    def shift_position(self, dx: float, dy: float, dz: float) -> None:
        """Shift global position by delta (used during origin shifts)."""
        self.global_x += dx
        self.global_y += dy
        self.global_z += dz

@dataclass
class FloatingOriginComponent:
    """
    Component marking an entity as managed by the floating origin system.
    Attaching this component automatically registers the entity.
    """
    registered: bool = False
    group: str = "default"

@dataclass
class EntityComponentSystem:
    """
    Simple ECS implementation for floating origin integration example.
    In a real game, you would use a more sophisticated ECS framework.
    """
    entities: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    systems: List[Callable] = field(default_factory=list)
    floating_origin: FloatingOrigin = field(default_factory=lambda: floating_origin)
    
    def create_entity(self, entity_id: str) -> str:
        """Create an entity with the given ID."""
        if entity_id in self.entities:
            raise ValueError(f"Entity {entity_id} already exists")
        
        self.entities[entity_id] = {}
        return entity_id
    
    def add_component(self, entity_id: str, component_name: str, component: Any) -> None:
        """Add a component to an entity."""
        if entity_id not in self.entities:
            raise ValueError(f"Entity {entity_id} does not exist")
        
        self.entities[entity_id][component_name] = component
        
        # Special case for FloatingOriginComponent - auto-register with floating origin
        if component_name == "floating_origin" and isinstance(component, FloatingOriginComponent):
            self._register_with_floating_origin(entity_id, component)
    
    def get_component(self, entity_id: str, component_name: str) -> Any:
        """Get a component from an entity."""
        if entity_id not in self.entities:
            raise ValueError(f"Entity {entity_id} does not exist")
        
        return self.entities[entity_id].get(component_name)
    
    def has_component(self, entity_id: str, component_name: str) -> bool:
        """Check if an entity has a component."""
        if entity_id not in self.entities:
            return False
        
        return component_name in self.entities[entity_id]
    
    def get_entities_with_components(self, *component_names: str) -> List[str]:
        """Get all entities with the given components."""
        result = []
        for entity_id, components in self.entities.items():
            if all(c in components for c in component_names):
                result.append(entity_id)
        return result
    
    def remove_entity(self, entity_id: str) -> None:
        """Remove an entity and unregister from floating origin if needed."""
        if entity_id not in self.entities:
            return
        
        # Unregister from floating origin if registered
        if "floating_origin" in self.entities[entity_id]:
            fo_component = self.entities[entity_id]["floating_origin"]
            if fo_component.registered:
                self.floating_origin.unregister_entity(entity_id)
        
        del self.entities[entity_id]
    
    def add_system(self, system: Callable) -> None:
        """Add a system to the ECS."""
        self.systems.append(system)
    
    def update(self, dt: float) -> None:
        """Run all systems."""
        for system in self.systems:
            system(self, dt)
    
    def _register_with_floating_origin(self, entity_id: str, fo_component: FloatingOriginComponent) -> None:
        """Register an entity with the floating origin system."""
        # Skip if not all required components are present
        if not self.has_component(entity_id, "transform"):
            logger.warning(f"Entity {entity_id} needs a TransformComponent to register with FloatingOrigin")
            return
        
        # Get transform component
        transform = self.get_component(entity_id, "transform")
        
        # Skip if already registered
        if fo_component.registered:
            return
        
        # Register with floating origin
        self.floating_origin.register_entity(
            entity_id=entity_id,
            position_getter=transform.get_global_position,
            position_setter=transform.shift_position,
            group=fo_component.group
        )
        
        # Mark as registered
        fo_component.registered = True
        logger.debug(f"Entity {entity_id} registered with floating origin in group '{fo_component.group}'")

class FloatingOriginSystem:
    """
    System for handling floating origin in ECS.
    Updates local positions based on global positions and current origin.
    """
    
    @staticmethod
    def update(ecs: EntityComponentSystem, dt: float) -> None:
        """
        Update all entities with floating origin component.
        Updates local positions based on global positions.
        """
        # Find player entity (if any)
        player_entities = ecs.get_entities_with_components("transform", "floating_origin", "player")
        
        # Update player position and check for origin shift
        if player_entities:
            player_id = player_entities[0]
            player_transform = ecs.get_component(player_id, "transform")
            
            # Update floating origin with player position
            player_pos = player_transform.get_global_position()
            shift_occurred = ecs.floating_origin.update_player_position(player_pos)
            
            if shift_occurred:
                logger.info(f"Origin shifted to player position: {player_pos}")
        
        # Update local positions for all entities with transform component
        for entity_id in ecs.get_entities_with_components("transform"):
            transform = ecs.get_component(entity_id, "transform")
            
            # Update local position from global position
            global_pos = transform.get_global_position()
            local_pos = ecs.floating_origin.get_local_position(global_pos)
            
            transform.set_local_position(local_pos.x, local_pos.y, local_pos.z)

# Example usage function
def example_usage():
    """Example of how to use the floating origin ECS integration."""
    # Create ECS
    ecs = EntityComponentSystem()
    
    # Add floating origin system
    ecs.add_system(FloatingOriginSystem.update)
    
    # Create player entity
    player_id = ecs.create_entity("player")
    ecs.add_component(player_id, "transform", TransformComponent(global_x=0, global_y=0, global_z=0))
    ecs.add_component(player_id, "floating_origin", FloatingOriginComponent(group="player"))
    ecs.add_component(player_id, "player", {})  # Mark as player
    
    # Create some other entities
    for i in range(10):
        entity_id = ecs.create_entity(f"entity_{i}")
        ecs.add_component(entity_id, "transform", TransformComponent(
            global_x=i * 100, 
            global_y=i * 100, 
            global_z=0
        ))
        ecs.add_component(entity_id, "floating_origin", FloatingOriginComponent(group="npcs"))
    
    # Game loop
    for frame in range(10):
        # Move player
        player_transform = ecs.get_component(player_id, "transform")
        player_transform.set_global_position(
            frame * 200,  # Move far enough to trigger shifts
            frame * 200,
            0
        )
        
        # Update all systems
        ecs.update(0.016)  # 60 FPS
        
        # Log player position
        if frame % 3 == 0:
            logger.info(f"Frame {frame}: Player global={player_transform.get_global_position()}, local={player_transform.get_local_position()}")
    
    # Get floating origin metrics
    metrics = ecs.floating_origin.get_metrics()
    logger.info(f"Floating origin metrics: {metrics}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    example_usage() 