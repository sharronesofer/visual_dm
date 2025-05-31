"""
Floating origin system for large-scale world environments.
Shifts the world origin as the player moves to maintain coordinate precision.

This module provides the main API for floating origin management, including:
- Entity registration (with group and batch support)
- Origin shift logic and performance metrics
- Coordinate conversion utilities (global <-> local)
- Debug and performance monitoring tools
- Batch/group operations for efficient entity management

Usage:
    from backend.infrastructure.events.utils.floating_origin import FloatingOrigin, floating_origin
    # Register entities, update player position, monitor performance, etc.

See README_floating_origin.md for integration details.
"""

from typing import Tuple, Dict, Optional, List, Set, Any, Callable, Iterable
import math
import time
import logging
import json
from dataclasses import dataclass
from backend.infrastructure.events.utils.coordinates import GlobalCoord, LocalCoord, CoordinateSystem, coordinate_system

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class OriginShiftMetrics:
    """Tracks performance metrics for origin shifts."""
    shift_count: int = 0
    total_shift_time: float = 0.0
    avg_shift_time: float = 0.0
    max_shift_time: float = 0.0
    last_shift_time: float = 0.0
    total_entities_shifted: int = 0
    
    def record_shift(self, duration: float, entity_count: int) -> None:
        """Record metrics from a single origin shift operation."""
        self.shift_count += 1
        self.total_shift_time += duration
        self.last_shift_time = duration
        self.total_entities_shifted += entity_count
        
        # Update max and average times
        self.max_shift_time = max(self.max_shift_time, duration)
        self.avg_shift_time = self.total_shift_time / self.shift_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for serialization."""
        return {
            'shift_count': self.shift_count,
            'total_shift_time': self.total_shift_time,
            'avg_shift_time': self.avg_shift_time,
            'max_shift_time': self.max_shift_time,
            'last_shift_time': self.last_shift_time,
            'total_entities_shifted': self.total_entities_shifted
        }

class FloatingOrigin:
    """
    Main floating origin system that manages origin shifts and entity registration.
    Provides public API for the floating origin system.
    """
    
    def __init__(self, coord_system: Optional[CoordinateSystem] = None):
        """Initialize the floating origin system."""
        self.coord_system = coord_system or coordinate_system
        self.registered_entities = {}  # id -> entity info dict
        self.last_shift_time = 0
        self.debug_mode = False
        self.metrics = OriginShiftMetrics()
        self.entity_groups = {}  # group_name -> set of entity_ids
        
    def register_entity(self, entity_id: str, position_getter: Callable, 
                        position_setter: Callable, group: str = "default") -> None:
        """
        Register an entity to be updated during origin shifts.
        
        Args:
            entity_id: Unique ID for the entity
            position_getter: Function that returns entity's GlobalCoord
            position_setter: Function that takes (dx, dy, dz) and updates entity
            group: Optional group name for batch operations
        """
        self.registered_entities[entity_id] = {
            'id': entity_id,
            'get_position': position_getter,
            'set_position': position_setter,
            'group': group
        }
        
        # Add to entity group
        if group not in self.entity_groups:
            self.entity_groups[group] = set()
        self.entity_groups[group].add(entity_id)
        
    def unregister_entity(self, entity_id: str) -> None:
        """Remove an entity from the registration."""
        if entity_id in self.registered_entities:
            # Remove from group
            group = self.registered_entities[entity_id].get('group', 'default')
            if group in self.entity_groups and entity_id in self.entity_groups[group]:
                self.entity_groups[group].remove(entity_id)
                # Clean up empty groups
                if not self.entity_groups[group]:
                    del self.entity_groups[group]
            
            # Remove entity
            del self.registered_entities[entity_id]
    
    def update_player_position(self, player_pos: GlobalCoord) -> bool:
        """
        Update player position and check if an origin shift is needed.
        Returns True if a shift was performed.
        """
        # Check if shift is needed
        if self.coord_system.check_shift_needed(player_pos):
            self._perform_origin_shift(player_pos)
            return True
        return False
    
    def _perform_origin_shift(self, reference_pos: GlobalCoord) -> None:
        """
        Perform an origin shift using the reference position.
        Updates all registered entities.
        """
        start_time = time.time()
        
        # Get shift delta
        dx, dy, dz = self.coord_system.shift_origin(reference_pos)
        
        # Update all registered entities
        entity_count = 0
        errors = 0
        for entity_id, entity_info in self.registered_entities.items():
            try:
                # Apply delta to entity (negative because we're moving the world)
                entity_info['set_position'](-dx, -dy, -dz)
                entity_count += 1
            except Exception as e:
                errors += 1
                logger.error(f"Error updating entity {entity_id}: {e}")
        
        # Update statistics
        self.last_shift_time = time.time()
        shift_duration = self.last_shift_time - start_time
        
        # Record metrics
        self.metrics.record_shift(shift_duration, entity_count)
        
        if self.debug_mode:
            logger.info(f"Origin shift performed: ({dx:.2f}, {dy:.2f}, {dz:.2f})")
            logger.info(f"Shift took {shift_duration*1000:.2f}ms for {entity_count} entities (errors: {errors})")
            logger.info(f"Avg shift time: {self.metrics.avg_shift_time*1000:.2f}ms, Max: {self.metrics.max_shift_time*1000:.2f}ms")

    def get_global_position(self, local_pos: LocalCoord) -> GlobalCoord:
        """Convert local coordinates to global."""
        return self.coord_system.local_to_global(local_pos)
    
    def get_local_position(self, global_pos: GlobalCoord) -> LocalCoord:
        """Convert global coordinates to local."""
        return self.coord_system.global_to_local(global_pos)
    
    def enable_debug(self, enabled: bool = True) -> None:
        """Enable or disable debug logging."""
        self.debug_mode = enabled
    
    def get_metrics(self) -> Dict[str, Any]:
        """Return current performance metrics as a dictionary."""
        return self.metrics.to_dict()
    
    def batch_register_entities(self, entities: Iterable[Tuple[str, Callable, Callable]], 
                               group: str = "default") -> None:
        """
        Register multiple entities at once for better performance.
        
        Args:
            entities: Iterable of (entity_id, position_getter, position_setter) tuples
            group: Group name for all entities in this batch
        """
        for entity_id, position_getter, position_setter in entities:
            self.register_entity(entity_id, position_getter, position_setter, group)
    
    def unregister_group(self, group: str) -> int:
        """
        Unregister all entities in a group.
        
        Args:
            group: Group name to unregister
            
        Returns:
            Number of entities unregistered
        """
        if group not in self.entity_groups:
            return 0
        
        entity_ids = list(self.entity_groups[group])
        count = len(entity_ids)
        
        # Remove all entities in group
        for entity_id in entity_ids:
            del self.registered_entities[entity_id]
        
        # Clear group
        del self.entity_groups[group]
        return count
    
    def get_entity_groups(self) -> Dict[str, Set[str]]:
        """Return a dictionary of entity groups and their members."""
        return {group: set(members) for group, members in self.entity_groups.items()}
    
    def serialize_state(self) -> Dict[str, Any]:
        """
        Serialize the current state of the floating origin system.
        Useful for debugging and persistence.
        
        Returns:
            Dictionary containing the serialized state
        """
        return {
            'origin': {
                'x': self.coord_system.origin.global_x,
                'y': self.coord_system.origin.global_y,
                'z': self.coord_system.origin.global_z
            },
            'entity_count': len(self.registered_entities),
            'groups': self.get_entity_groups(),
            'metrics': self.metrics.to_dict(),
            'last_shift_time': self.last_shift_time,
            'shifts': self.coord_system.get_shift_history()
        }

# Create global instance for convenience
floating_origin = FloatingOrigin() 