"""
Service layer for POI operations.
Provides higher-level business logic for creating, updating, and managing POIs.
"""

from typing import List, Optional, Dict, Any, Tuple
from uuid import uuid4
from datetime import datetime

from .models import PointOfInterest, POIState, POIType
from .schemas import POICreationSchema

class POIService:
    """
    Service for managing Point of Interest (POI) operations.
    
    Provides methods for creating, updating, retrieving, and managing POIs.
    """
    
    @staticmethod
    def create_poi(poi_data: POICreationSchema) -> PointOfInterest:
        """
        Create a new POI from the provided data.
        
        Args:
            poi_data: The POI creation data
            
        Returns:
            The newly created POI
        """
        # Create base POI from schema
        poi = PointOfInterest(
            id=str(uuid4()),
            name=poi_data.name,
            description=poi_data.description or f"{poi_data.name} - a {poi_data.poi_type}",
            region_id=poi_data.region_id,
            position=poi_data.position,
            poi_type=poi_data.poi_type,
            tags=poi_data.tags,
            claimed_region_hex_ids=poi_data.claimed_region_hex_ids,
            population=poi_data.population,
            max_population=poi_data.max_population,
            current_state=poi_data.current_state,
            faction_id=poi_data.faction_id,
            level=poi_data.level or 1
        )
        
        return poi
    
    @staticmethod
    def update_poi(poi: PointOfInterest, updates: Dict[str, Any]) -> PointOfInterest:
        """
        Update a POI with the provided changes.
        
        Args:
            poi: The POI to update
            updates: Dictionary of field:value pairs to update
            
        Returns:
            The updated POI
        """
        # Handle population changes specially as they may trigger state changes
        if 'population' in updates:
            POIStateService.update_population(poi, updates['population'])
            # Remove from updates to prevent double application
            del updates['population']
            
        # Handle state transitions specially
        if 'current_state' in updates:
            POIStateService.transition_state(poi, updates['current_state'])
            # Remove from updates to prevent double application
            del updates['current_state']
            
        # Apply remaining updates
        for field, value in updates.items():
            if hasattr(poi, field):
                setattr(poi, field, value)
                
        # Update timestamp
        poi.update_timestamp()
        
        return poi
    
    @staticmethod
    def attach_npcs_to_poi(poi: PointOfInterest, npc_ids: List[str]) -> PointOfInterest:
        """
        Attach NPCs to a POI.
        
        Args:
            poi: The POI to update
            npc_ids: List of NPC IDs to attach
            
        Returns:
            The updated POI
        """
        for npc_id in npc_ids:
            poi.add_npc(npc_id)
        return poi
    
    @staticmethod
    def check_state_transition(poi: PointOfInterest, damage_level: float = 0.0) -> Optional[str]:
        """
        Check if a POI should transition to a new state based on damage or other factors.
        
        Args:
            poi: The POI to check
            damage_level: Optional damage level (0.0-1.0) that might trigger state changes
            
        Returns:
            New state if a transition should occur, None otherwise
        """
        # Delegate to POIStateService for evaluation
        return POIStateService.evaluate_state(poi, damage_level)
    
    @staticmethod
    def calculate_resource_production(poi: PointOfInterest) -> Dict[str, float]:
        """
        Calculate resource production for a POI based on its type, state, population, etc.
        
        Args:
            poi: The POI to calculate for
            
        Returns:
            Dictionary of resource:amount pairs representing production per time unit
        """
        # Base production dictionary
        production = {}
        
        # Base on POI type
        if poi.poi_type == POIType.CITY or poi.poi_type == POIType.TOWN:
            production["gold"] = 10.0 * (poi.population / 100)
            production["food"] = 5.0 * (poi.population / 100)
        elif poi.poi_type == POIType.FARM:
            production["food"] = 20.0 * (poi.population / 10)
        elif poi.poi_type == POIType.MINE:
            production["ore"] = 15.0 * (poi.population / 10)
        
        # Adjust for state
        if poi.current_state == POIState.DECLINING:
            for resource in production:
                production[resource] *= 0.7
        elif poi.current_state == POIState.ABANDONED or poi.current_state == POIState.RUINS:
            for resource in production:
                production[resource] = 0
        
        return production
    
    @staticmethod
    def get_claimed_area(poi: PointOfInterest) -> List[Dict[str, int]]:
        """
        Get the area claimed by this POI in region hex coordinates.
        
        Args:
            poi: The POI to get claimed area for
            
        Returns:
            List of coordinate dictionaries representing the claimed hexes
        """
        # For now just convert the list of hex_ids to coordinates
        # In a real implementation, this would work with actual hex grid coordinates
        claimed_coords = []
        for hex_id in poi.claimed_region_hex_ids:
            # Parse hex_id to get coordinates - this is a placeholder
            # Assuming format like "hex_x_y"
            parts = hex_id.split("_")
            if len(parts) >= 3:
                try:
                    x, y = int(parts[-2]), int(parts[-1])
                    claimed_coords.append({"x": x, "y": y})
                except (ValueError, IndexError):
                    # Skip invalid hex IDs
                    pass
        
        return claimed_coords

    @staticmethod
    def generate_poi_tilemap(poi: PointOfInterest) -> Dict[str, Any]:
        """
        Generate a complete tilemap for a POI including structure and enrichment.
        
        Args:
            poi: The POI to generate a tilemap for
            
        Returns:
            Dictionary with the rendered tilemap data
        """
        from .tilemap_service import TilemapService
        
        # Generate the basic room structure
        rooms = TilemapService.generate_tilemap(poi)
        
        # Enrich the tilemap with objects, monsters, etc.
        enrichment = TilemapService.enrich_tilemap(poi, rooms)
        
        # Render the final tilemap data for client consumption
        rendered_tilemap = TilemapService.render_tilemap(rooms, enrichment)
        
        return rendered_tilemap

    @staticmethod
    def calculate_distance_between_pois(poi1: PointOfInterest, poi2: PointOfInterest) -> float:
        """
        Calculate the distance between two POIs.
        
        Args:
            poi1: First POI
            poi2: Second POI
            
        Returns:
            Distance in arbitrary units (grid cells)
        """
        from .utils import calculate_poi_distance
        return calculate_poi_distance(poi1, poi2)
        
    @staticmethod
    def find_nearby_pois(poi: PointOfInterest, all_pois: List[PointOfInterest], max_distance: float = 30.0) -> List[PointOfInterest]:
        """
        Find POIs within a certain distance of the given POI.
        
        Args:
            poi: The center POI
            all_pois: List of all POIs to search
            max_distance: Maximum distance to consider a POI nearby
            
        Returns:
            List of nearby POIs (excluding the center POI)
        """
        from .utils import calculate_poi_distance
        
        nearby = []
        for other_poi in all_pois:
            # Skip self
            if other_poi.id == poi.id:
                continue
                
            # Calculate distance
            distance = calculate_poi_distance(poi, other_poi)
            
            # Add if within range
            if distance <= max_distance:
                nearby.append(other_poi)
                
        return nearby

class POIStateService:
    """
    Service for managing POI state transitions and state-related operations.
    
    Provides methods for checking, evaluating, and transitioning POI states.
    """
    
    @staticmethod
    def get_state_info(poi: PointOfInterest) -> Dict[str, Any]:
        """
        Get detailed information about a POI's current state.
        
        Args:
            poi: The POI to get state information for
            
        Returns:
            Dictionary with state details including:
            - state_name: Current state name
            - can_interact: Whether the POI can be interacted with
            - population_status: Description of population status
            - resource_status: Description of resource status
            - danger_level: Numeric danger level (0-10)
        """
        # Base state info
        state_info = {
            "state_name": poi.current_state,
            "can_interact": True,
            "population_status": "Normal",
            "resource_status": "Normal",
            "danger_level": 0,
        }
        
        # Adjust based on state
        if poi.current_state == POIState.NORMAL:
            pass  # Default values are fine
        elif poi.current_state == POIState.DECLINING:
            state_info["population_status"] = "Declining"
            state_info["resource_status"] = "Limited"
            state_info["danger_level"] = 2
        elif poi.current_state == POIState.ABANDONED:
            state_info["can_interact"] = False
            state_info["population_status"] = "Abandoned"
            state_info["resource_status"] = "Depleted"
            state_info["danger_level"] = 4
        elif poi.current_state == POIState.RUINS:
            state_info["can_interact"] = False
            state_info["population_status"] = "None"
            state_info["resource_status"] = "Ruins"
            state_info["danger_level"] = 6
        elif poi.current_state == POIState.DUNGEON:
            state_info["can_interact"] = False
            state_info["population_status"] = "Monsters"
            state_info["resource_status"] = "Unknown"
            state_info["danger_level"] = 8
        elif poi.current_state == POIState.REPOPULATING:
            state_info["population_status"] = "Returning"
            state_info["resource_status"] = "Recovering"
            state_info["danger_level"] = 3
        elif poi.current_state == POIState.SPECIAL:
            # Special states require additional context
            # Use metadata if available
            if "special_state" in poi.metadata:
                special = poi.metadata["special_state"]
                state_info["state_name"] = special.get("name", "Special")
                state_info["can_interact"] = special.get("can_interact", True)
                state_info["population_status"] = special.get("population_status", "Special")
                state_info["resource_status"] = special.get("resource_status", "Special")
                state_info["danger_level"] = special.get("danger_level", 5)
        
        return state_info
    
    @staticmethod
    def update_population(poi: PointOfInterest, new_population: int) -> PointOfInterest:
        """
        Update the POI's population and potentially change state.
        
        Args:
            poi: The POI to update
            new_population: The new population value
            
        Returns:
            Updated POI object
        """
        old_population = poi.population
        poi.population = new_population
        poi.updated_at = datetime.utcnow()
        
        # If population has changed significantly, we might need to change state
        if new_population == 0 and old_population > 0:
            poi.current_state = POIState.ABANDONED
        elif new_population > 0 and old_population == 0:
            poi.current_state = POIState.REPOPULATING
        elif new_population < old_population * 0.5 and poi.current_state == POIState.NORMAL:
            poi.current_state = POIState.DECLINING
        elif new_population > old_population * 1.5 and poi.current_state == POIState.DECLINING:
            poi.current_state = POIState.NORMAL
            
        return poi
    
    @staticmethod
    def transition_state(poi: PointOfInterest, new_state: str) -> PointOfInterest:
        """
        Transition the POI to a new state.
        
        Args:
            poi: The POI to update
            new_state: The new state value
            
        Returns:
            Updated POI object
        """
        poi.current_state = new_state
        poi.updated_at = datetime.utcnow()
        
        # Additional logic based on state transition
        if new_state == POIState.RUINS or new_state == POIState.DUNGEON:
            # For ruins and dungeons, reset population
            poi.population = 0
            
        return poi
    
    @staticmethod
    def evaluate_state(poi: PointOfInterest, damage_level: float = 0.0) -> Optional[str]:
        """
        Evaluate if a POI should transition to a new state based on current conditions.
        
        Args:
            poi: The POI to evaluate
            damage_level: Optional damage level (0.0-1.0) that might trigger state changes
            
        Returns:
            New state if a transition should occur, None otherwise
        """
        # Handle damage-based transitions first (e.g., from war)
        if damage_level > 0.8:
            return POIState.RUINS
        elif damage_level > 0.5 and poi.current_state != POIState.RUINS:
            return POIState.ABANDONED
            
        # Population-based transitions
        if poi.population == 0 and poi.current_state not in [POIState.RUINS, POIState.DUNGEON, POIState.ABANDONED]:
            return POIState.ABANDONED
        elif poi.population > 0 and poi.current_state == POIState.ABANDONED:
            return POIState.REPOPULATING
        elif poi.population < (poi.max_population or 100) * 0.3 and poi.current_state == POIState.NORMAL:
            return POIState.DECLINING
        elif poi.population > (poi.max_population or 100) * 0.7 and poi.current_state == POIState.DECLINING:
            return POIState.NORMAL
            
        # No state change needed
        return None
    
    @staticmethod
    def apply_war_damage(poi: PointOfInterest, damage_severity: float) -> PointOfInterest:
        """
        Apply war damage to a POI and update its state accordingly.
        
        Args:
            poi: The POI to damage
            damage_severity: Damage severity (0.0-1.0)
            
        Returns:
            Updated POI object
        """
        # Update population based on damage
        if damage_severity > 0.3:
            population_loss = int(poi.population * damage_severity)
            new_population = max(0, poi.population - population_loss)
            POIStateService.update_population(poi, new_population)
        
        # Check for state transition
        new_state = POIStateService.evaluate_state(poi, damage_severity)
        if new_state:
            POIStateService.transition_state(poi, new_state)
            
        # Update metadata
        if "war_damage" not in poi.metadata:
            poi.metadata["war_damage"] = []
            
        poi.metadata["war_damage"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "severity": damage_severity,
            "population_before": poi.population + population_loss if 'population_loss' in locals() else poi.population,
            "population_after": poi.population,
            "state_change": new_state is not None
        })
            
        return poi 