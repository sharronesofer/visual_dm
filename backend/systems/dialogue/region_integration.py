"""
Region integration for the dialogue system.

This module provides functionality for connecting dialogue with geographic regions,
locations, and environmental context to create location-aware conversations.
"""

from typing import Dict, Any, List, Optional, Set
import logging

# Import region/location system components  
from backend.systems.regions.region_manager import RegionManager
from backend.systems.pois.poi_manager import POIManager

# Configure logger
logger = logging.getLogger(__name__)


class DialogueRegionIntegration:
    """
    Integration between dialogue and region/location systems.
    
    Enables dialogue to:
    - Reference regional characteristics and events
    - Provide location-specific conversation topics
    - Include environmental context in responses
    - Handle regional politics and conflicts
    """
    
    def __init__(self, region_manager=None, poi_manager=None):
        """
        Initialize the dialogue region integration.
        
        Args:
            region_manager: Optional region manager instance
            poi_manager: Optional POI manager instance
        """
        self.region_manager = region_manager or RegionManager.get_instance()
        self.poi_manager = poi_manager or POIManager.get_instance()
    
    def add_region_context_to_dialogue(
        self,
        context: Dict[str, Any],
        location_id: Optional[str] = None,
        region_id: Optional[str] = None,
        include_weather: bool = True,
        include_events: bool = True,
        include_politics: bool = True,
        include_economy: bool = True
    ) -> Dict[str, Any]:
        """
        Add regional and location information to dialogue context.
        
        Args:
            context: The existing dialogue context
            location_id: Optional specific location/POI ID
            region_id: Optional region ID (auto-detected from location if not provided)
            include_weather: Whether to include weather information
            include_events: Whether to include recent regional events
            include_politics: Whether to include political climate
            include_economy: Whether to include economic information
            
        Returns:
            Updated context with regional information added
        """
        # Create a copy of the context
        updated_context = dict(context)
        
        # Create region context if it doesn't exist
        if "region_context" not in updated_context:
            updated_context["region_context"] = {}
        
        region_context = updated_context["region_context"]
        
        # Determine region from location if not provided
        if not region_id and location_id:
            region_id = self._get_region_from_location(location_id)
        
        # Add location-specific context
        if location_id:
            location_data = self._get_location_context(location_id)
            if location_data:
                region_context["location"] = location_data
        
        # Add region-specific context
        if region_id:
            region_data = self._get_region_context(region_id)
            if region_data:
                region_context["region"] = region_data
                
                # Add optional context components
                if include_weather:
                    weather_data = self._get_weather_context(region_id, location_id)
                    if weather_data:
                        region_context["weather"] = weather_data
                
                if include_events:
                    events_data = self._get_recent_events_context(region_id)
                    if events_data:
                        region_context["recent_events"] = events_data
                
                if include_politics:
                    politics_data = self._get_political_context(region_id)
                    if politics_data:
                        region_context["politics"] = politics_data
                
                if include_economy:
                    economy_data = self._get_economic_context(region_id)
                    if economy_data:
                        region_context["economy"] = economy_data
        
        return updated_context
    
    def get_region_dialogue_topics(
        self,
        region_id: str,
        location_id: Optional[str] = None,
        character_perspective: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation topics relevant to the region and location.
        
        Args:
            region_id: ID of the region
            location_id: Optional specific location ID
            character_perspective: Optional character perspective filter
            
        Returns:
            List of region-relevant dialogue topics
        """
        topics = []
        
        try:
            # Get regional characteristics to discuss
            region_data = self._get_region_context(region_id)
            if region_data:
                # Regional features and landmarks
                if region_data.get("notable_features"):
                    topics.extend(self._get_feature_topics(region_data["notable_features"]))
                
                # Regional culture and customs
                if region_data.get("culture"):
                    topics.extend(self._get_culture_topics(region_data["culture"]))
                
                # Regional problems and challenges
                if region_data.get("challenges"):
                    topics.extend(self._get_challenge_topics(region_data["challenges"]))
            
            # Get location-specific topics
            if location_id:
                location_data = self._get_location_context(location_id)
                if location_data:
                    topics.extend(self._get_location_topics(location_data))
            
            # Get current events topics
            events = self._get_recent_events_context(region_id)
            if events:
                topics.extend(self._get_event_topics(events))
            
            # Filter by character perspective if provided
            if character_perspective:
                topics = self._filter_topics_by_perspective(topics, character_perspective)
            
        except Exception as e:
            logger.error(f"Error getting region dialogue topics for {region_id}: {e}")
        
        return topics[:10]  # Limit to 10 most relevant topics
    
    def get_location_atmosphere_description(
        self,
        location_id: str,
        time_of_day: Optional[str] = None,
        weather_condition: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate atmospheric description for dialogue based on location and conditions.
        
        Args:
            location_id: ID of the location
            time_of_day: Optional time of day context
            weather_condition: Optional weather context
            
        Returns:
            Atmospheric description string or None
        """
        try:
            location_data = self._get_location_context(location_id)
            if not location_data:
                return None
            
            # Base location description
            description_parts = []
            
            location_type = location_data.get("type", "area")
            location_name = location_data.get("name", "this place")
            
            # Add time-based atmospheric elements
            if time_of_day:
                time_atmosphere = self._get_time_atmosphere(location_type, time_of_day)
                if time_atmosphere:
                    description_parts.append(time_atmosphere)
            
            # Add weather-based atmospheric elements
            if weather_condition:
                weather_atmosphere = self._get_weather_atmosphere(location_type, weather_condition)
                if weather_atmosphere:
                    description_parts.append(weather_atmosphere)
            
            # Add location-specific atmosphere
            location_atmosphere = self._get_location_specific_atmosphere(location_data)
            if location_atmosphere:
                description_parts.append(location_atmosphere)
            
            # Combine into coherent description
            if description_parts:
                return " ".join(description_parts)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting atmosphere description for location {location_id}: {e}")
            return None
    
    def get_regional_character_responses(
        self,
        region_id: str,
        character_id: str,
        dialogue_context: Dict[str, Any]
    ) -> List[str]:
        """
        Get character responses that incorporate regional knowledge and perspective.
        
        Args:
            region_id: ID of the region
            character_id: ID of the character
            dialogue_context: Current dialogue context
            
        Returns:
            List of regionally-aware response options
        """
        responses = []
        
        try:
            # Get character's regional knowledge level
            regional_knowledge = self._get_character_regional_knowledge(character_id, region_id)
            
            # Get region-specific responses based on knowledge level
            if regional_knowledge == "native":
                responses.extend(self._get_native_responses(region_id))
            elif regional_knowledge == "familiar":
                responses.extend(self._get_familiar_responses(region_id))
            elif regional_knowledge == "visitor":
                responses.extend(self._get_visitor_responses(region_id))
            else:
                responses.extend(self._get_outsider_responses(region_id))
            
            # Add responses about current regional situation
            situation_responses = self._get_situational_responses(region_id, dialogue_context)
            responses.extend(situation_responses)
            
        except Exception as e:
            logger.error(f"Error getting regional character responses: {e}")
        
        return responses[:5]  # Limit to 5 most relevant responses
    
    def _get_region_from_location(self, location_id: str) -> Optional[str]:
        """Get region ID from a location ID."""
        try:
            location_data = self.poi_manager.get_poi(location_id)
            if location_data:
                return location_data.get("region_id")
            return None
        except Exception as e:
            logger.error(f"Error getting region from location {location_id}: {e}")
            return None
    
    def _get_location_context(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Get context information for a specific location."""
        try:
            location_data = self.poi_manager.get_poi(location_id)
            if location_data:
                return {
                    "id": location_id,
                    "name": location_data.get("name", "Unknown Location"),
                    "type": location_data.get("type", "area"),
                    "description": location_data.get("description", ""),
                    "notable_features": location_data.get("features", []),
                    "atmosphere": location_data.get("atmosphere", "neutral"),
                    "safety_level": location_data.get("safety_level", "safe"),
                    "population_density": location_data.get("population_density", "moderate"),
                    "accessibility": location_data.get("accessibility", "public")
                }
            return None
        except Exception as e:
            logger.error(f"Error getting location context for {location_id}: {e}")
            return None
    
    def _get_region_context(self, region_id: str) -> Optional[Dict[str, Any]]:
        """Get context information for a region."""
        try:
            region_data = self.region_manager.get_region(region_id)
            if region_data:
                return {
                    "id": region_id,
                    "name": region_data.get("name", "Unknown Region"),
                    "type": region_data.get("type", "area"),
                    "climate": region_data.get("climate", "temperate"),
                    "terrain": region_data.get("terrain", "mixed"),
                    "population": region_data.get("population", "moderate"),
                    "governance": region_data.get("governance", "autonomous"),
                    "notable_features": region_data.get("notable_features", []),
                    "culture": region_data.get("culture", {}),
                    "challenges": region_data.get("current_challenges", []),
                    "resources": region_data.get("resources", [])
                }
            return None
        except Exception as e:
            logger.error(f"Error getting region context for {region_id}: {e}")
            return None
    
    def _get_weather_context(self, region_id: str, location_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get current weather context for the region/location."""
        try:
            # This would integrate with weather system
            # For now, provide basic weather simulation
            weather_conditions = ["clear", "cloudy", "rainy", "stormy", "foggy", "windy"]
            import random
            
            current_weather = random.choice(weather_conditions)
            
            return {
                "condition": current_weather,
                "temperature": "moderate",
                "visibility": "good" if current_weather not in ["foggy", "stormy"] else "poor",
                "wind": "calm" if current_weather != "windy" else "strong",
                "description": self._get_weather_description(current_weather)
            }
        except Exception as e:
            logger.error(f"Error getting weather context: {e}")
            return None
    
    def _get_recent_events_context(self, region_id: str) -> List[Dict[str, Any]]:
        """Get recent events in the region."""
        try:
            # This would integrate with events/history system
            # For now, simulate some regional events
            sample_events = [
                {
                    "type": "economic",
                    "description": "Trade routes have been disrupted by recent conflicts",
                    "impact": "negative",
                    "timeframe": "recent"
                },
                {
                    "type": "social",
                    "description": "A harvest festival brought communities together",
                    "impact": "positive", 
                    "timeframe": "recent"
                },
                {
                    "type": "political",
                    "description": "New leadership has taken control of local governance",
                    "impact": "uncertain",
                    "timeframe": "current"
                }
            ]
            
            # Return subset based on region
            return sample_events[:2]  # Limit to 2 events
        except Exception as e:
            logger.error(f"Error getting recent events for region {region_id}: {e}")
            return []
    
    def _get_political_context(self, region_id: str) -> Optional[Dict[str, Any]]:
        """Get political climate context for the region."""
        try:
            region_data = self.region_manager.get_region(region_id)
            if region_data:
                return {
                    "governance_type": region_data.get("governance", "autonomous"),
                    "stability": region_data.get("political_stability", "stable"),
                    "key_figures": region_data.get("key_political_figures", []),
                    "recent_changes": region_data.get("recent_political_changes", []),
                    "tensions": region_data.get("political_tensions", [])
                }
            return None
        except Exception as e:
            logger.error(f"Error getting political context for region {region_id}: {e}")
            return None
    
    def _get_economic_context(self, region_id: str) -> Optional[Dict[str, Any]]:
        """Get economic context for the region."""
        try:
            region_data = self.region_manager.get_region(region_id)
            if region_data:
                return {
                    "primary_industries": region_data.get("primary_industries", []),
                    "trade_status": region_data.get("trade_status", "active"),
                    "economic_health": region_data.get("economic_health", "stable"),
                    "major_exports": region_data.get("major_exports", []),
                    "economic_challenges": region_data.get("economic_challenges", [])
                }
            return None
        except Exception as e:
            logger.error(f"Error getting economic context for region {region_id}: {e}")
            return None
    
    def _get_feature_topics(self, features: List[str]) -> List[Dict[str, Any]]:
        """Generate dialogue topics about regional features."""
        topics = []
        for feature in features[:3]:  # Limit to 3 features
            topics.append({
                "type": "regional_feature",
                "topic": f"Notable landmark: {feature}",
                "category": "location",
                "relevance": "high"
            })
        return topics
    
    def _get_culture_topics(self, culture_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate dialogue topics about regional culture."""
        topics = []
        
        if culture_data.get("traditions"):
            topics.append({
                "type": "cultural_tradition",
                "topic": "Local customs and traditions",
                "category": "culture",
                "relevance": "medium"
            })
        
        if culture_data.get("festivals"):
            topics.append({
                "type": "cultural_event",
                "topic": "Regional festivals and celebrations",
                "category": "culture",
                "relevance": "medium"
            })
        
        return topics
    
    def _get_challenge_topics(self, challenges: List[str]) -> List[Dict[str, Any]]:
        """Generate dialogue topics about regional challenges."""
        topics = []
        for challenge in challenges[:2]:  # Limit to 2 challenges
            topics.append({
                "type": "regional_problem",
                "topic": f"Current issue: {challenge}",
                "category": "problems",
                "relevance": "high"
            })
        return topics
    
    def _get_location_topics(self, location_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate dialogue topics specific to a location."""
        topics = []
        
        location_type = location_data.get("type", "area")
        location_name = location_data.get("name", "this place")
        
        topics.append({
            "type": "location_info",
            "topic": f"About {location_name}",
            "category": "location",
            "relevance": "high"
        })
        
        if location_data.get("notable_features"):
            topics.append({
                "type": "location_features",
                "topic": f"Interesting features of {location_name}",
                "category": "location", 
                "relevance": "medium"
            })
        
        return topics
    
    def _get_event_topics(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate dialogue topics about recent events."""
        topics = []
        for event in events:
            topics.append({
                "type": "recent_event",
                "topic": f"Recent {event['type']} developments",
                "category": "current_events",
                "relevance": "high",
                "event_data": event
            })
        return topics
    
    def _filter_topics_by_perspective(self, topics: List[Dict[str, Any]], perspective: str) -> List[Dict[str, Any]]:
        """Filter topics based on character perspective."""
        # This could be enhanced to filter topics based on character knowledge, interests, etc.
        # For now, return all topics
        return topics
    
    def _get_time_atmosphere(self, location_type: str, time_of_day: str) -> Optional[str]:
        """Get atmospheric description based on time of day."""
        time_descriptions = {
            "dawn": "The early morning light casts long shadows",
            "morning": "The area bustles with morning activity",
            "midday": "The sun is high overhead",
            "afternoon": "The day's activities are winding down",
            "evening": "The setting sun bathes everything in warm light",
            "night": "Darkness has settled over the area",
            "midnight": "The deep night brings an eerie quiet"
        }
        return time_descriptions.get(time_of_day)
    
    def _get_weather_atmosphere(self, location_type: str, weather_condition: str) -> Optional[str]:
        """Get atmospheric description based on weather."""
        weather_descriptions = {
            "clear": "under clear skies",
            "cloudy": "beneath overcast clouds",
            "rainy": "as rain falls steadily",
            "stormy": "while thunder rumbles overhead",
            "foggy": "through thick, obscuring fog",
            "windy": "with strong winds whipping around"
        }
        return weather_descriptions.get(weather_condition)
    
    def _get_location_specific_atmosphere(self, location_data: Dict[str, Any]) -> Optional[str]:
        """Get atmospheric description specific to the location."""
        atmosphere = location_data.get("atmosphere", "neutral")
        
        atmosphere_descriptions = {
            "peaceful": "A sense of tranquility pervades the area",
            "tense": "There's an underlying tension in the air",
            "bustling": "The place hums with constant activity",
            "eerie": "Something feels unsettling about this place",
            "sacred": "A reverent atmosphere surrounds the location",
            "dangerous": "An air of danger hangs over everything"
        }
        
        return atmosphere_descriptions.get(atmosphere)
    
    def _get_weather_description(self, condition: str) -> str:
        """Get descriptive text for weather condition."""
        descriptions = {
            "clear": "Clear skies with good visibility",
            "cloudy": "Overcast with clouds covering the sky",
            "rainy": "Steady rainfall dampening the ground",
            "stormy": "Thunderstorms with heavy rain and lightning",
            "foggy": "Thick fog reducing visibility",
            "windy": "Strong winds affecting movement"
        }
        return descriptions.get(condition, "Weather conditions are unremarkable")
    
    def _get_character_regional_knowledge(self, character_id: str, region_id: str) -> str:
        """Determine character's knowledge level about the region."""
        # This would integrate with character system to determine:
        # - Where character is from
        # - How long they've been in the region
        # - Their background and experience
        
        # For now, simulate knowledge levels
        knowledge_levels = ["native", "familiar", "visitor", "outsider"]
        import random
        return random.choice(knowledge_levels)
    
    def _get_native_responses(self, region_id: str) -> List[str]:
        """Get responses from a character native to the region."""
        return [
            "I've lived here all my life",
            "This region holds many memories for me",
            "I know these lands like the back of my hand"
        ]
    
    def _get_familiar_responses(self, region_id: str) -> List[str]:
        """Get responses from a character familiar with the region."""
        return [
            "I've spent considerable time in this region",
            "I know this area fairly well",
            "I've traveled through here many times"
        ]
    
    def _get_visitor_responses(self, region_id: str) -> List[str]:
        """Get responses from a visiting character."""
        return [
            "I'm still getting to know this region",
            "This area is quite different from where I come from",
            "I'm here on business, though I find the region interesting"
        ]
    
    def _get_outsider_responses(self, region_id: str) -> List[str]:
        """Get responses from an outsider character."""
        return [
            "I'm not from around here",
            "This region is foreign to me",
            "I'm still learning about local customs"
        ]
    
    def _get_situational_responses(self, region_id: str, dialogue_context: Dict[str, Any]) -> List[str]:
        """Get responses based on current regional situation."""
        responses = []
        
        # Check for regional events in context
        recent_events = dialogue_context.get("region_context", {}).get("recent_events", [])
        for event in recent_events:
            if event["impact"] == "negative":
                responses.append(f"These {event['type']} troubles have been concerning")
            elif event["impact"] == "positive":
                responses.append(f"The recent {event['type']} developments have been encouraging")
        
        return responses[:2]  # Limit to 2 situational responses
