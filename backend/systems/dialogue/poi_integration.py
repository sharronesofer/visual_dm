"""
POI (Points of Interest) integration for the dialogue system.

This module provides functionality for connecting dialogue with the POI system,
allowing dialogue to reference and be influenced by the state of locations and points
of interest (Normal, Declining, Abandoned, etc.)
"""

from typing import Dict, Any, List, Optional, Set
from uuid import UUID
import logging

# Import POI system components
from backend.systems.poi.services.services import PoiBusinessService, create_poi_business_service
from backend.infrastructure.systems.poi.models import PoiEntity, POIType, POIState
from backend.infrastructure.poi_repositories.poi_repository import PoiRepository
from backend.infrastructure.database import get_db_session
from sqlalchemy.orm import Session

# Configure logger
logger = logging.getLogger(__name__)


class POIManagerAdapter:
    """Adapter to provide POI manager functionality using the existing POI services"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or get_db_session()
        self.poi_service = create_poi_business_service(self.db_session)
        self.poi_repository = PoiRepository(self.db_session)
    
    @classmethod
    def get_instance(cls, db_session: Optional[Session] = None):
        """Get a singleton-like instance"""
        return cls(db_session)
    
    def get_poi(self, poi_id: str) -> Optional[Dict[str, Any]]:
        """Get POI by ID"""
        try:
            poi_uuid = UUID(poi_id)
            poi_entity = self.poi_repository.get(poi_uuid)
            if poi_entity:
                return poi_entity.to_dict()
        except (ValueError, Exception) as e:
            logger.error(f"Error getting POI {poi_id}: {e}")
        return None
    
    def get_nearby_pois(self, location_id: str, radius: float = 10.0) -> List[Dict[str, Any]]:
        """Get POIs near a location"""
        try:
            # First get the center POI
            center_poi = self.get_poi(location_id)
            if not center_poi:
                return []
            
            x = center_poi.get('location_x', 0)
            y = center_poi.get('location_y', 0)
            
            nearby_pois = self.poi_repository.get_nearby_pois(x, y, radius)
            return [poi.to_dict() for poi in nearby_pois]
        except Exception as e:
            logger.error(f"Error getting nearby POIs for {location_id}: {e}")
            return []
    
    def query_pois(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query POIs with filters"""
        try:
            # Extract search parameters
            name_pattern = query.get('name')
            poi_types = query.get('types', [])
            states = query.get('states', [])
            
            # Convert to enum types if needed
            poi_type_enums = []
            for poi_type in poi_types:
                try:
                    poi_type_enums.append(POIType(poi_type))
                except ValueError:
                    continue
            
            state_enums = []
            for state in states:
                try:
                    state_enums.append(POIState(state))
                except ValueError:
                    continue
            
            # Perform search
            pois, _ = self.poi_repository.search_advanced(
                name_pattern=name_pattern,
                poi_types=poi_type_enums if poi_type_enums else None,
                states=state_enums if state_enums else None,
                limit=query.get('limit', 100)
            )
            
            return [poi.to_dict() for poi in pois]
        except Exception as e:
            logger.error(f"Error querying POIs: {e}")
            return []


class SettlementManagerAdapter:
    """Adapter to provide settlement manager functionality using POI services"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or get_db_session()
        self.poi_repository = PoiRepository(self.db_session)
    
    @classmethod
    def get_instance(cls, db_session: Optional[Session] = None):
        """Get a singleton-like instance"""
        return cls(db_session)
    
    def get_settlement(self, settlement_id: str) -> Optional[Dict[str, Any]]:
        """Get settlement by ID (treating settlements as POIs)"""
        try:
            poi_uuid = UUID(settlement_id)
            poi_entity = self.poi_repository.get(poi_uuid)
            if poi_entity and poi_entity.poi_type in ['city', 'town', 'village', 'settlement']:
                return poi_entity.to_dict()
        except (ValueError, Exception) as e:
            logger.error(f"Error getting settlement {settlement_id}: {e}")
        return None
    
    def get_settlement_pois(self, settlement_id: str) -> List[Dict[str, Any]]:
        """Get POIs within a settlement"""
        try:
            # For now, return POIs near the settlement
            settlement = self.get_settlement(settlement_id)
            if not settlement:
                return []
            
            x = settlement.get('location_x', 0)
            y = settlement.get('location_y', 0)
            
            # Get POIs within a small radius of the settlement
            nearby_pois = self.poi_repository.get_nearby_pois(x, y, 5.0)
            return [poi.to_dict() for poi in nearby_pois if poi.id != UUID(settlement_id)]
        except Exception as e:
            logger.error(f"Error getting settlement POIs for {settlement_id}: {e}")
            return []


class DialoguePOIIntegration:
    """
    Integration between dialogue and POI systems.
    
    Allows dialogue to reference and be influenced by the state of
    locations and points of interest in the world.
    """
    
    def __init__(self, poi_manager=None, settlement_manager=None, db_session: Optional[Session] = None):
        """
        Initialize the dialogue POI integration.
        
        Args:
            poi_manager: Optional POI manager instance
            settlement_manager: Optional settlement manager instance
            db_session: Optional database session
        """
        self.db_session = db_session or get_db_session()
        self.poi_manager = poi_manager or POIManagerAdapter.get_instance(self.db_session)
        self.settlement_manager = settlement_manager or SettlementManagerAdapter.get_instance(self.db_session)
    
    def add_poi_context_to_dialogue(
        self,
        context: Dict[str, Any],
        location_id: str,
        include_nearby: bool = True,
        nearby_radius: float = 10.0,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Add POI information to dialogue context.
        
        Args:
            context: The existing dialogue context
            location_id: ID of the current location
            include_nearby: Whether to include nearby locations
            nearby_radius: Radius within which to include nearby locations
            include_details: Whether to include detailed POI information
            
        Returns:
            Updated context with POI information added
        """
        # Create a copy of the context
        updated_context = dict(context)
        
        # Create locations context if it doesn't exist
        if "locations" not in updated_context:
            updated_context["locations"] = {}
            
        # Get current location info
        location = self._get_location_info(location_id, include_details)
        
        if location:
            updated_context["locations"]["current"] = location
            
            # Add POI state reference
            poi_state = location.get("state", "normal")
            updated_context["locations"]["current_state"] = poi_state
            updated_context["locations"]["state_description"] = self._get_state_description(poi_state)
        
        # Add nearby locations if requested
        if include_nearby:
            nearby = self._get_nearby_locations(
                location_id=location_id,
                radius=nearby_radius,
                include_details=include_details
            )
            
            if nearby:
                updated_context["locations"]["nearby"] = nearby
                
        return updated_context
    
    def get_location_state_for_dialogue(
        self,
        location_id: str
    ) -> Dict[str, Any]:
        """
        Get information about a location's state for dialogue.
        
        Args:
            location_id: ID of the location
            
        Returns:
            Dictionary with location state information
        """
        try:
            # Get the location's state
            location = self.poi_manager.get_poi(location_id)
            
            if not location:
                logger.warning(f"Location not found: {location_id}")
                return {}
                
            state = location.get("state", "normal")
            
            # Get description and effects
            state_info = {
                "state": state,
                "description": self._get_state_description(state),
                "visible_effects": self._get_state_visible_effects(state),
                "duration": location.get("state_duration", 0),
                "severity": location.get("state_severity", 0)
            }
            
            return state_info
            
        except Exception as e:
            logger.error(f"Error getting location state for '{location_id}': {e}")
            return {"state": "unknown"}
    
    def get_settlement_dialogue_context(
        self,
        settlement_id: str,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Get dialogue context for a specific settlement.
        
        Args:
            settlement_id: ID of the settlement
            include_details: Whether to include detailed settlement information
            
        Returns:
            Settlement context for dialogue
        """
        try:
            # Get the settlement
            settlement = self.settlement_manager.get_settlement(settlement_id)
            
            if not settlement:
                logger.warning(f"Settlement not found: {settlement_id}")
                return {}
                
            # Basic settlement context
            settlement_context = {
                "id": settlement.get("id"),
                "name": settlement.get("name"),
                "type": settlement.get("type", "village"),
                "state": settlement.get("state", "normal"),
                "population": settlement.get("population", 0),
                "region": settlement.get("region"),
            }
            
            # Add details if requested
            if include_details:
                settlement_context.update({
                    "description": settlement.get("description", ""),
                    "notable_features": settlement.get("notable_features", []),
                    "prosperity": settlement.get("prosperity", "average"),
                    "primary_industry": settlement.get("primary_industry", ""),
                    "faction_control": settlement.get("faction_control", ""),
                    "state_description": self._get_state_description(
                        settlement.get("state", "normal")
                    )
                })
                
                # Add points of interest within settlement
                pois = self.settlement_manager.get_settlement_pois(settlement_id)
                if pois:
                    settlement_context["points_of_interest"] = [
                        {"id": poi.get("id"), "name": poi.get("name"), "type": poi.get("type")}
                        for poi in pois
                    ]
            
            return settlement_context
            
        except Exception as e:
            logger.error(f"Error getting settlement dialogue context for '{settlement_id}': {e}")
            return {}
    
    def get_poi_description_for_dialogue(
        self,
        poi_id: str,
        perspective: str = "visitor",
        time_of_day: Optional[str] = None
    ) -> str:
        """
        Get a narrative description of a POI suitable for dialogue.
        
        Args:
            poi_id: ID of the POI
            perspective: Perspective to describe from ('visitor', 'local', 'expert')
            time_of_day: Optional time of day for contextual description
            
        Returns:
            Narrative description of the POI
        """
        try:
            # Get the POI
            poi = self.poi_manager.get_poi(poi_id)
            
            if not poi:
                logger.warning(f"POI not found: {poi_id}")
                return "This location is unknown."
                
            # Basic description
            basic_desc = poi.get("description", "")
            
            # Get state-based description
            state = poi.get("state", "normal")
            state_desc = self._get_state_narrative(state)
            
            # Get time-based description
            time_desc = ""
            if time_of_day:
                time_desc = self._get_time_based_poi_description(poi_id, time_of_day)
            
            # Combine descriptions based on perspective
            if perspective == "visitor":
                return f"{basic_desc} {state_desc} {time_desc}".strip()
            elif perspective == "local":
                # Locals know more details
                local_details = poi.get("local_knowledge", "")
                return f"{basic_desc} {local_details} {state_desc} {time_desc}".strip()
            elif perspective == "expert":
                # Experts have historical knowledge
                history = poi.get("history", "")
                expert_details = poi.get("expert_knowledge", "")
                return f"{basic_desc} {history} {expert_details} {state_desc} {time_desc}".strip()
            else:
                return f"{basic_desc} {state_desc} {time_desc}".strip()
            
        except Exception as e:
            logger.error(f"Error getting POI description for '{poi_id}': {e}")
            return "Information about this location is unavailable."
    
    def get_relevant_pois_for_dialogue(
        self,
        character_id: str,
        topic: Optional[str] = None,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get POIs that are relevant to a character for dialogue topics.
        
        Args:
            character_id: ID of the character
            topic: Optional dialogue topic to filter relevant POIs
            limit: Maximum number of POIs to return
            
        Returns:
            List of relevant POIs for dialogue
        """
        try:
            # Get character information from a character system
            # This would need to be implemented with a character system integration
            character_info = self._get_character_info(character_id)
            
            home = character_info.get("home_location")
            occupation = character_info.get("occupation")
            interests = character_info.get("interests", [])
            faction = character_info.get("faction")
            
            # Query for relevant POIs
            # In a real implementation, this would use sophisticated relevance matching
            # For now, this is a simplified version
            query = {
                "character_home": home,
                "occupation_relevance": occupation,
                "interests": interests,
                "faction": faction,
                "topic": topic,
                "limit": limit
            }
            
            pois = self.poi_manager.query_pois(query)
            
            # Format for dialogue
            relevant_pois = []
            for poi in pois:
                relevant_poi = {
                    "id": poi.get("id"),
                    "name": poi.get("name"),
                    "type": poi.get("type"),
                    "state": poi.get("state", "normal"),
                    "relevance_reason": poi.get("relevance_reason", "")
                }
                relevant_pois.append(relevant_poi)
            
            return relevant_pois
            
        except Exception as e:
            logger.error(f"Error getting relevant POIs for character '{character_id}': {e}")
            return []
    
    def _get_location_info(
        self,
        location_id: str,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Get information about a location for dialogue context.
        
        Args:
            location_id: ID of the location
            include_details: Whether to include detailed location information
            
        Returns:
            Dictionary with location information
        """
        try:
            # Get the location
            location = self.poi_manager.get_poi(location_id)
            
            if not location:
                logger.warning(f"Location not found: {location_id}")
                return {}
                
            # Basic location info
            location_info = {
                "id": location.get("id"),
                "name": location.get("name"),
                "type": location.get("type"),
                "state": location.get("state", "normal")
            }
            
            # Add details if requested
            if include_details:
                location_info.update({
                    "description": location.get("description", ""),
                    "region": location.get("region", ""),
                    "faction_control": location.get("faction_control", ""),
                    "notable_features": location.get("notable_features", []),
                    "resources": location.get("resources", []),
                    "state_duration": location.get("state_duration", 0)
                })
            
            return location_info
            
        except Exception as e:
            logger.error(f"Error getting location info for '{location_id}': {e}")
            return {}
    
    def _get_nearby_locations(
        self,
        location_id: str,
        radius: float = 10.0,
        include_details: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get nearby locations for dialogue context.
        
        Args:
            location_id: ID of the current location
            radius: Radius within which to find nearby locations
            include_details: Whether to include detailed location information
            
        Returns:
            List of nearby locations
        """
        try:
            # Get nearby locations
            nearby = self.poi_manager.get_nearby_pois(
                poi_id=location_id,
                radius=radius
            )
            
            # Format for dialogue context
            formatted_nearby = []
            for poi in nearby:
                nearby_info = {
                    "id": poi.get("id"),
                    "name": poi.get("name"),
                    "type": poi.get("type"),
                    "state": poi.get("state", "normal"),
                    "distance": poi.get("distance", 0)
                }
                
                # Add details if requested
                if include_details:
                    nearby_info.update({
                        "description": poi.get("description", ""),
                        "region": poi.get("region", ""),
                        "faction_control": poi.get("faction_control", "")
                    })
                
                formatted_nearby.append(nearby_info)
            
            # Sort by distance
            formatted_nearby.sort(key=lambda x: x.get("distance", 0))
            
            return formatted_nearby
            
        except Exception as e:
            logger.error(f"Error getting nearby locations for '{location_id}': {e}")
            return []
    
    def _get_state_description(self, state: str) -> str:
        """
        Get a description for a POI state.
        
        Args:
            state: The POI state
            
        Returns:
            Description of the state
        """
        descriptions = {
            "normal": "The location is in its usual state with normal activity.",
            "declining": "The location shows signs of decline and decreased activity.",
            "abandoned": "The location appears to be abandoned, with little to no activity.",
            "ruined": "The location lies in ruins, severely damaged or decayed.",
            "flourishing": "The location is thriving with increased activity and prosperity.",
            "contested": "The location is contested, with signs of factional conflict.",
            "dangerous": "The location appears to be dangerous, posing risks to visitors.",
            "recovering": "The location shows signs of recovery from a previous decline."
        }
        
        return descriptions.get(state, "The location's state is unclear.")
    
    def _get_state_visible_effects(self, state: str) -> List[str]:
        """
        Get visible effects of a POI state.
        
        Args:
            state: The POI state
            
        Returns:
            List of visible effects
        """
        effects = {
            "normal": ["Regular traffic", "Maintained structures", "Active businesses"],
            "declining": ["Reduced traffic", "Some disrepair", "Businesses closing", "Increased crime"],
            "abandoned": ["No traffic", "Severe disrepair", "Closed businesses", "Possible squatters"],
            "ruined": ["Collapsed structures", "Overgrown vegetation", "Scavengers"],
            "flourishing": ["Heavy traffic", "New construction", "Thriving businesses", "Improved security"],
            "contested": ["Military presence", "Checkpoints", "Tension", "Propaganda"],
            "dangerous": ["Signs of violence", "Warning markers", "Criminal activity", "Hazards"],
            "recovering": ["Repair work", "Returning population", "Reopening businesses"]
        }
        
        return effects.get(state, ["Unknown effects"])
    
    def _get_state_narrative(self, state: str) -> str:
        """
        Get a narrative description of a POI state for dialogue.
        
        Args:
            state: The POI state
            
        Returns:
            Narrative description of the state
        """
        narratives = {
            "normal": "Everything seems to be functioning as expected.",
            "declining": "There's a sense of gradual decay here. Several buildings show signs of neglect, and there are fewer people around than one might expect.",
            "abandoned": "An eerie silence hangs in the air. The place is clearly abandoned, with no signs of recent human activity.",
            "ruined": "This place lies in ruins. The structures have largely collapsed, and nature is reclaiming what remains.",
            "flourishing": "There's a palpable energy here. New construction is underway, and the place bustles with activity and prosperity.",
            "contested": "Tension fills the air. Different factions vie for control, and their presence is evident in the guards, checkpoints, and competing symbols of authority.",
            "dangerous": "An atmosphere of danger permeates this location. Most sensible people avoid lingering here if they can help it.",
            "recovering": "Signs of renewal are visible amidst the lingering damage. People have begun returning, and repair work is underway."
        }
        
        return narratives.get(state, "")
    
    def _get_time_based_poi_description(
        self,
        poi_id: str,
        time_of_day: str
    ) -> str:
        """
        Get a time-specific description of a POI.
        
        Args:
            poi_id: ID of the POI
            time_of_day: Time of day ('morning', 'afternoon', 'evening', 'night')
            
        Returns:
            Time-specific POI description
        """
        try:
            # Get the POI
            poi = self.poi_manager.get_poi(poi_id)
            
            if not poi:
                return ""
                
            # Get time-specific descriptions if they exist
            time_descriptions = poi.get("time_descriptions", {})
            description = time_descriptions.get(time_of_day, "")
            
            if not description:
                # Generate a generic time-based description
                if time_of_day == "morning":
                    description = "The morning light casts long shadows across the area."
                elif time_of_day == "afternoon":
                    description = "The place is bathed in the full light of day."
                elif time_of_day == "evening":
                    description = "The warm hues of evening give the place a different character."
                elif time_of_day == "night":
                    description = "Darkness shrouds much of the area, with shadows concealing details."
            
            return description
            
        except Exception as e:
            logger.error(f"Error getting time-based description for POI '{poi_id}': {e}")
            return ""
    
    def _get_character_info(self, character_id: str) -> Dict[str, Any]:
        """
        Get character information for POI relevance.
        
        Args:
            character_id: ID of the character
            
        Returns:
            Character information
        """
        # This is a placeholder that would connect to a character system
        # In a real implementation, this would fetch actual character data
        
        # Placeholder data
        character_info = {
            "id": character_id,
            "home_location": None,
            "occupation": None,
            "interests": [],
            "faction": None
        }
        
        return character_info 