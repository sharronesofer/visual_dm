"""
FogOfWar module for the Visual DM combat system.

This module implements a fog of war system for combat, managing visibility
and awareness between combatants. It calculates line of sight and determines
which entities are visible to each other based on terrain and distances.

Following the design principles from the Development Bible, this implementation:
1. Is entirely runtime-generated with no scene dependencies
2. Integrates with the combat area for line of sight calculations
3. Supports stealthy characters and awareness mechanics
4. Provides APIs for integrating with UI and other systems
"""

import logging
import math
from typing import Dict, List, Any, Optional, Tuple, Set, Union
import uuid
import time

from backend.infrastructure.utils.combat.combat_area import CombatArea, Position

# Set up logging
logger = logging.getLogger(__name__)

class VisibilityStatus:
    """Enum for visibility statuses."""
    VISIBLE = "visible"       # Fully visible
    PARTIALLY = "partially"   # Partially visible (e.g., behind partial cover)
    HIDDEN = "hidden"         # Hidden but known position
    UNAWARE = "unaware"       # Completely unaware of entity

class FogOfWar:
    """
    Manages visibility and awareness between entities in combat.
    
    This system tracks which entities can see each other, taking into account
    line of sight, stealth, and awareness mechanics.
    """
    
    def __init__(self, combat_area: CombatArea):
        """
        Initialize the fog of war system.
        
        Args:
            combat_area: The combat area instance to use for LOS calculations
        """
        self.combat_area = combat_area
        
        # Visibility map: entity_id -> {other_id: visibility_status}
        self.visibility_map: Dict[str, Dict[str, str]] = {}
        
        # Stealth/awareness data
        self.awareness: Dict[str, Dict[str, float]] = {}  # entity_id -> {other_id: awareness_level}
        self.stealth_values: Dict[str, float] = {}        # entity_id -> stealth_value
        self.detection_values: Dict[str, float] = {}      # entity_id -> detection_value
        
        # Line of sight cache for performance
        self.los_cache: Dict[Tuple[str, str], Tuple[bool, float]] = {}
        self.los_cache_time: Dict[Tuple[str, str], float] = {}
        self.los_cache_duration = 0.5  # Cache duration in seconds
        
        logger.info("FogOfWar system initialized")
    
    def update_entity(
        self,
        entity_id: str,
        stealth: Optional[float] = None,
        detection: Optional[float] = None,
        position: Optional[Position] = None
    ) -> None:
        """
        Update an entity's stealth, detection, or position.
        
        Args:
            entity_id: ID of the entity to update
            stealth: Stealth value (0-100)
            detection: Detection value (0-100)
            position: New position
        """
        # Update stealth if provided
        if stealth is not None:
            self.stealth_values[entity_id] = max(0, min(100, stealth))
        
        # Update detection if provided
        if detection is not None:
            self.detection_values[entity_id] = max(0, min(100, detection))
        
        # Update position (via combat area) if provided
        if position is not None and self.combat_area.get_entity_position(entity_id):
            self.combat_area.move_entity(entity_id, position)
        
        # Clear cached LOS for this entity
        self._clear_los_cache_for_entity(entity_id)
        
        # Set up visibility map entry if needed
        if entity_id not in self.visibility_map:
            self.visibility_map[entity_id] = {}
            
        # Set up awareness map entry if needed
        if entity_id not in self.awareness:
            self.awareness[entity_id] = {}
        
        logger.debug(f"Updated entity {entity_id} in fog of war")
    
    def _clear_los_cache_for_entity(self, entity_id: str) -> None:
        """
        Clear all LOS cache entries involving the given entity.
        
        Args:
            entity_id: ID of the entity
        """
        # Create a list of keys to remove (can't modify dict during iteration)
        keys_to_remove = [
            key for key in self.los_cache.keys()
            if entity_id in key
        ]
        
        # Remove keys from both cache dictionaries
        for key in keys_to_remove:
            if key in self.los_cache:
                del self.los_cache[key]
            if key in self.los_cache_time:
                del self.los_cache_time[key]
    
    def _get_los_data(
        self, 
        entity_id: str, 
        target_id: str
    ) -> Tuple[bool, float]:
        """
        Get line of sight data between two entities.
        
        Args:
            entity_id: ID of the viewer entity
            target_id: ID of the target entity
            
        Returns:
            Tuple of (has_los, distance)
        """
        # Check cache first
        cache_key = (entity_id, target_id)
        current_time = time.time()
        
        if cache_key in self.los_cache and cache_key in self.los_cache_time:
            cache_time = self.los_cache_time[cache_key]
            if current_time - cache_time <= self.los_cache_duration:
                return self.los_cache[cache_key]
        
        # Get positions
        entity_pos = self.combat_area.get_entity_position(entity_id)
        target_pos = self.combat_area.get_entity_position(target_id)
        
        if not entity_pos or not target_pos:
            return (False, float('inf'))
        
        # Calculate distance
        entity_x, entity_y, entity_z = entity_pos
        target_x, target_y, target_z = target_pos
        
        distance = math.sqrt(
            (target_x - entity_x) ** 2 +
            (target_z - entity_z) ** 2
        )
        
        # Check line of sight
        has_los = self.combat_area.is_line_of_sight_clear(entity_pos, target_pos)
        
        # Cache the result
        self.los_cache[cache_key] = (has_los, distance)
        self.los_cache_time[cache_key] = current_time
        
        return (has_los, distance)
    
    def update_awareness(
        self,
        observer_id: str,
        target_id: str,
        delta_awareness: float = 0.0
    ) -> float:
        """
        Update the awareness level between two entities.
        
        Args:
            observer_id: ID of the observing entity
            target_id: ID of the target entity
            delta_awareness: Change in awareness level
            
        Returns:
            New awareness level
        """
        # Create maps if needed
        if observer_id not in self.awareness:
            self.awareness[observer_id] = {}
            
        # Get current awareness
        current_awareness = self.awareness[observer_id].get(target_id, 0.0)
        
        # Update awareness
        new_awareness = max(0.0, min(100.0, current_awareness + delta_awareness))
        self.awareness[observer_id][target_id] = new_awareness
        
        return new_awareness
    
    def calculate_visibility(
        self,
        observer_id: str,
        target_id: str,
        recalculate: bool = False
    ) -> str:
        """
        Calculate visibility status of target from observer.
        
        Args:
            observer_id: ID of the observing entity
            target_id: ID of the target entity
            recalculate: Force recalculation instead of using cached value
            
        Returns:
            Visibility status (from VisibilityStatus)
        """
        # Return cached value if available and not forcing recalculation
        if not recalculate and observer_id in self.visibility_map:
            if target_id in self.visibility_map[observer_id]:
                return self.visibility_map[observer_id][target_id]
        
        # Check if entities are the same
        if observer_id == target_id:
            # An entity can always see itself
            visibility = VisibilityStatus.VISIBLE
            self._update_visibility(observer_id, target_id, visibility)
            return visibility
        
        # Get LOS and distance
        has_los, distance = self._get_los_data(observer_id, target_id)
        
        # Get stealth and detection values
        target_stealth = self.stealth_values.get(target_id, 0.0)
        observer_detection = self.detection_values.get(observer_id, 50.0)  # Default to average
        
        # Get awareness level
        awareness = self.awareness.get(observer_id, {}).get(target_id, 0.0)
        
        # Calculate base visibility
        if not has_los:
            # No line of sight
            if awareness >= 75.0:
                # High awareness means position is known even without LOS
                visibility = VisibilityStatus.HIDDEN
            else:
                visibility = VisibilityStatus.UNAWARE
        else:
            # Has line of sight, check stealth vs detection
            # Distance factor: reduces detection by 10 points per 5 units of distance
            distance_factor = max(0.0, 1.0 - (distance / 25.0))
            
            detection_chance = (observer_detection - target_stealth) * distance_factor
            detection_chance = max(0.0, detection_chance)
            
            # Apply awareness bonus
            detection_chance += awareness * 0.2  # Each 5 points of awareness adds 1 to detection
            
            if detection_chance >= 40.0:
                # Clear visibility
                visibility = VisibilityStatus.VISIBLE
            elif detection_chance >= 20.0:
                # Partial visibility
                visibility = VisibilityStatus.PARTIALLY
            elif awareness >= 50.0:
                # Known but barely visible
                visibility = VisibilityStatus.HIDDEN
            else:
                # Not detected
                visibility = VisibilityStatus.UNAWARE
        
        # Update visibility map
        self._update_visibility(observer_id, target_id, visibility)
        
        return visibility
    
    def _update_visibility(
        self,
        observer_id: str,
        target_id: str,
        visibility: str
    ) -> None:
        """
        Update visibility status in the map.
        
        Args:
            observer_id: ID of the observing entity
            target_id: ID of the target entity
            visibility: Visibility status
        """
        # Create maps if needed
        if observer_id not in self.visibility_map:
            self.visibility_map[observer_id] = {}
            
        # Update visibility
        self.visibility_map[observer_id][target_id] = visibility
    
    def get_visible_entities(
        self,
        observer_id: str,
        min_visibility: str = VisibilityStatus.PARTIALLY
    ) -> Dict[str, str]:
        """
        Get all entities visible to the observer.
        
        Args:
            observer_id: ID of the observing entity
            min_visibility: Minimum visibility level to include
            
        Returns:
            Dict mapping entity IDs to their visibility status
        """
        # Calculate visibility for all entities
        all_entities = list(self.combat_area.entity_positions.keys())
        
        # Set up visibility map if needed
        if observer_id not in self.visibility_map:
            self.visibility_map[observer_id] = {}
        
        # Calculate visibility for all entities
        for entity_id in all_entities:
            if entity_id != observer_id and entity_id not in self.visibility_map[observer_id]:
                self.calculate_visibility(observer_id, entity_id)
        
        # Filter by minimum visibility
        visible_entities = {}
        visibility_levels = [
            VisibilityStatus.VISIBLE,
            VisibilityStatus.PARTIALLY,
            VisibilityStatus.HIDDEN,
            VisibilityStatus.UNAWARE
        ]
        
        # Find the minimum index
        min_index = visibility_levels.index(min_visibility)
        
        # Get entities with visibility at or above minimum
        for entity_id, visibility in self.visibility_map[observer_id].items():
            if visibility_levels.index(visibility) <= min_index:
                visible_entities[entity_id] = visibility
        
        return visible_entities
    
    def update_all_visibility(self) -> None:
        """Update visibility for all entity pairs."""
        all_entities = list(self.combat_area.entity_positions.keys())
        
        for observer_id in all_entities:
            for target_id in all_entities:
                if observer_id != target_id:
                    self.calculate_visibility(observer_id, target_id, recalculate=True)
    
    def simulate_perception_check(
        self,
        observer_id: str,
        target_id: str,
        check_bonus: float = 0.0
    ) -> Tuple[bool, float]:
        """
        Simulate a perception check to detect a target.
        
        Args:
            observer_id: ID of the observing entity
            target_id: ID of the target entity
            check_bonus: Bonus to the check (positive or negative)
            
        Returns:
            Tuple of (success, margin)
        """
        # Get stealth and detection values
        target_stealth = self.stealth_values.get(target_id, 0.0)
        observer_detection = self.detection_values.get(observer_id, 50.0)
        
        # Get LOS and distance
        has_los, distance = self._get_los_data(observer_id, target_id)
        
        if not has_los:
            # No line of sight, perception check at disadvantage
            observer_detection *= 0.5
        
        # Apply distance penalty
        distance_factor = max(0.2, 1.0 - (distance / 15.0))
        effective_detection = observer_detection * distance_factor
        
        # Apply bonus
        effective_detection += check_bonus
        
        # Calculate check result
        difficulty = target_stealth
        margin = effective_detection - difficulty
        success = margin >= 0
        
        # Update awareness based on check outcome
        awareness_change = 0.0
        
        if success:
            # Successful check increases awareness
            awareness_change = 10.0 + max(0.0, margin / 2.0)
        else:
            # Failed check may still slightly increase awareness
            awareness_change = max(0.0, margin / 4.0)
        
        # Apply awareness change
        if awareness_change != 0.0:
            self.update_awareness(observer_id, target_id, awareness_change)
            
            # Recalculate visibility
            self.calculate_visibility(observer_id, target_id, recalculate=True)
        
        return (success, margin)
    
    def reset(self) -> None:
        """Reset the fog of war system."""
        self.visibility_map.clear()
        self.awareness.clear()
        self.stealth_values.clear()
        self.detection_values.clear()
        self.los_cache.clear()
        self.los_cache_time.clear()
        
        logger.info("FogOfWar system reset")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "visibility_map": self.visibility_map,
            "awareness": self.awareness,
            "stealth_values": self.stealth_values,
            "detection_values": self.detection_values
        }

# Create a factory function to get a fog of war instance
def create_fog_of_war(combat_area: CombatArea) -> FogOfWar:
    """
    Create and initialize a new fog of war system.
    
    Args:
        combat_area: Combat area to use for LOS calculations
        
    Returns:
        Initialized FogOfWar instance
    """
    return FogOfWar(combat_area) 