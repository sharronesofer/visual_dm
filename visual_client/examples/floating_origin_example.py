"""
Example usage of the floating origin system in a game environment.
Demonstrates entity registration, position updates, and origin shifts.
"""

import time
import random
import math
import logging
from typing import List, Dict, Tuple, Any

from visual_client.core.utils.coordinates import GlobalCoord, LocalCoord
from visual_client.core.utils.floating_origin import FloatingOrigin, floating_origin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GameObject:
    """Simple game object with position for demonstration."""
    
    def __init__(self, entity_id: str, x: float, y: float, z: float = 0.0):
        """Initialize with position."""
        self.entity_id = entity_id
        self.position = (x, y, z)
        self.local_position = (x, y, z)  # Position relative to origin
        
    def get_position(self) -> GlobalCoord:
        """Get global position for floating origin system."""
        return GlobalCoord(*self.position)
    
    def set_position(self, dx: float, dy: float, dz: float) -> None:
        """Update position during origin shift."""
        x, y, z = self.position
        self.position = (x + dx, y + dy, z + dz)
        logger.debug(f"Entity {self.entity_id} shifted by ({dx:.2f}, {dy:.2f}, {dz:.2f})")
        
    def move_to(self, x: float, y: float, z: float = None) -> None:
        """Move object to a new global position."""
        if z is None:
            z = self.position[2]
        self.position = (x, y, z)
        
    def move_by(self, dx: float, dy: float, dz: float = 0.0) -> None:
        """Move object by a delta from current position."""
        x, y, z = self.position
        self.position = (x + dx, y + dy, z + dz)
        
    def update_local_position(self, origin_system) -> None:
        """Update local position based on current origin."""
        global_pos = GlobalCoord(*self.position)
        local_pos = origin_system.get_local_position(global_pos)
        self.local_position = (local_pos.x, local_pos.y, local_pos.z)
        
    def __str__(self) -> str:
        """String representation."""
        return f"{self.entity_id}: Global({self.position[0]:.2f}, {self.position[1]:.2f}, {self.position[2]:.2f}), Local({self.local_position[0]:.2f}, {self.local_position[1]:.2f}, {self.local_position[2]:.2f})"

class GameWorld:
    """Example game world using floating origin."""
    
    def __init__(self):
        """Initialize game world."""
        self.floating_origin = floating_origin
        self.floating_origin.enable_debug(True)
        self.entities: Dict[str, GameObject] = {}
        self.player = None
        
    def create_player(self, x: float, y: float, z: float = 0.0) -> GameObject:
        """Create player entity."""
        self.player = GameObject("player", x, y, z)
        self.register_entity(self.player)
        return self.player
    
    def create_entities(self, count: int, radius: float) -> List[GameObject]:
        """Create randomly positioned entities around origin."""
        entities = []
        for i in range(count):
            # Random position within radius
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, radius)
            x = distance * math.cos(angle)
            y = distance * math.sin(angle)
            z = random.uniform(-10, 10)
            
            entity = GameObject(f"entity_{i}", x, y, z)
            self.register_entity(entity)
            entities.append(entity)
            
        return entities
    
    def register_entity(self, entity: GameObject) -> None:
        """Register entity with floating origin system."""
        self.entities[entity.entity_id] = entity
        self.floating_origin.register_entity(
            entity.entity_id,
            entity.get_position,
            entity.set_position,
            group=entity.entity_id.split('_')[0]  # Group by prefix
        )
        
    def update_player_position(self, x: float, y: float, z: float = None) -> bool:
        """Update player position and trigger origin shift if needed."""
        if not self.player:
            raise ValueError("Player not created")
            
        self.player.move_to(x, y, z)
        
        # Update player position in floating origin system
        shift_performed = self.floating_origin.update_player_position(self.player.get_position())
        
        # Update local positions for rendering
        for entity in self.entities.values():
            entity.update_local_position(self.floating_origin)
            
        return shift_performed
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from floating origin system."""
        return self.floating_origin.get_metrics()
    
    def print_entity_status(self, max_entities: int = 5) -> None:
        """Print status of entities for debugging."""
        logger.info(f"Current origin: {self.floating_origin.coord_system.origin.get_origin()}")
        
        entities_to_print = list(self.entities.values())
        if len(entities_to_print) > max_entities:
            entities_to_print = [self.player] + random.sample(
                [e for e in entities_to_print if e.entity_id != "player"],
                min(max_entities - 1, len(entities_to_print) - 1)
            )
            
        for entity in entities_to_print:
            logger.info(str(entity))
            
        if len(self.entities) > max_entities:
            logger.info(f"... and {len(self.entities) - max_entities} more entities")
            
        group_info = self.floating_origin.get_entity_groups()
        logger.info(f"Entity groups: {group_info}")

def main():
    """Main example function."""
    logger.info("Starting floating origin example")
    
    # Create game world
    world = GameWorld()
    
    # Create player at origin
    player = world.create_player(0, 0, 0)
    logger.info(f"Created player: {player}")
    
    # Create some static entities
    entities = world.create_entities(100, 500)
    logger.info(f"Created {len(entities)} entities")
    
    # Simulate player movement in a spiral pattern
    logger.info("Simulating player movement...")
    
    for i in range(50):
        # Move in a spiral pattern
        angle = (i / 10) * 2 * math.pi
        distance = 200 + i * 50
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        z = i * 5
        
        # Update player position
        shift_performed = world.update_player_position(x, y, z)
        
        # Print status every 10 steps or when shift occurs
        if i % 10 == 0 or shift_performed:
            logger.info(f"Step {i}: Player at ({x:.2f}, {y:.2f}, {z:.2f}), Shift: {shift_performed}")
            world.print_entity_status()
        
        # Small delay for demonstration
        time.sleep(0.1)
    
    # Print final metrics
    metrics = world.get_metrics()
    logger.info(f"Floating origin metrics: {metrics}")
    logger.info(f"Total shifts: {metrics['shift_count']}")
    logger.info(f"Average shift time: {metrics['avg_shift_time']*1000:.2f}ms")
    
    # Print serialized state
    state = world.floating_origin.serialize_state()
    logger.info(f"Final state: {state}")
    
    logger.info("Floating origin example completed successfully")

if __name__ == "__main__":
    main() 