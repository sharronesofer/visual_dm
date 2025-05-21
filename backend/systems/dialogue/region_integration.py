"""
Region system integration for the dialogue system.

This module provides functionality for connecting dialogue with the Region systems,
allowing dialogue to reference and be influenced by regional information such as
biomes, environmental characteristics, and region-specific factors.
"""

from typing import Dict, Any, List, Optional, Set
import logging

# Import region system components
from backend.systems.regions.region_manager import RegionManager
from backend.systems.regions.biome_manager import BiomeManager

# Configure logger
logger = logging.getLogger(__name__)


class DialogueRegionIntegration:
    """
    Integration between dialogue and region systems.
    
    Allows dialogue to reference and be influenced by regional information,
    such as biomes, terrain, resources, and environmental characteristics.
    """
    
    def __init__(self, region_manager=None, biome_manager=None):
        """
        Initialize the dialogue region integration.
        
        Args:
            region_manager: Optional region manager instance
            biome_manager: Optional biome manager instance
        """
        self.region_manager = region_manager or RegionManager.get_instance()
        self.biome_manager = biome_manager or BiomeManager.get_instance()
    
    def add_region_context_to_dialogue(
        self,
        context: Dict[str, Any],
        region_id: str,
        include_biome: bool = True,
        include_resources: bool = True,
        include_adjacents: bool = True,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Add region information to dialogue context.
        
        Args:
            context: The existing dialogue context
            region_id: ID of the region
            include_biome: Whether to include biome information
            include_resources: Whether to include resource information
            include_adjacents: Whether to include adjacent regions
            include_details: Whether to include detailed region information
            
        Returns:
            Updated context with region information added
        """
        # Create a copy of the context
        updated_context = dict(context)
        
        # Create region context if it doesn't exist
        if "region" not in updated_context:
            updated_context["region"] = {}
            
        # Get region info
        region = self._get_region_info(region_id, include_details)
        
        if region:
            updated_context["region"]["current"] = region
            
            # Add biome information if requested
            if include_biome and "biome" in region:
                biome_id = region.get("biome")
                biome_info = self._get_biome_info(biome_id)
                
                if biome_info:
                    updated_context["region"]["biome"] = biome_info
            
            # Add resource information if requested
            if include_resources:
                resources = self._get_region_resources(region_id)
                
                if resources:
                    updated_context["region"]["resources"] = resources
                    
            # Add adjacent regions if requested
            if include_adjacents:
                adjacents = self._get_adjacent_regions(region_id)
                
                if adjacents:
                    updated_context["region"]["adjacent_regions"] = adjacents
        
        return updated_context
    
    def get_region_description_for_dialogue(
        self,
        region_id: str,
        perspective: str = "visitor",
        season: Optional[str] = None,
        weather: Optional[str] = None
    ) -> str:
        """
        Get a narrative description of a region suitable for dialogue.
        
        Args:
            region_id: ID of the region
            perspective: Perspective to describe from ('visitor', 'native', 'scholar')
            season: Optional season for contextual description
            weather: Optional weather for contextual description
            
        Returns:
            Narrative description of the region
        """
        try:
            # Get the region
            region = self.region_manager.get_region(region_id)
            
            if not region:
                logger.warning(f"Region not found: {region_id}")
                return "This region is unknown."
                
            # Basic description
            name = region.get("name", "")
            basic_desc = region.get("description", "")
            
            # Get biome description
            biome_id = region.get("biome")
            biome_desc = ""
            
            if biome_id:
                biome = self.biome_manager.get_biome(biome_id)
                if biome:
                    biome_desc = biome.get("description", "")
            
            # Get seasonal description
            season_desc = ""
            if season:
                season_desc = self._get_seasonal_region_description(region_id, season)
            
            # Get weather description
            weather_desc = ""
            if weather:
                weather_desc = self._get_weather_region_description(region_id, weather)
            
            # Combine descriptions based on perspective
            if perspective == "visitor":
                return f"The region of {name} is {basic_desc} {biome_desc} {season_desc} {weather_desc}".strip()
            elif perspective == "native":
                # Natives know more details
                native_details = region.get("native_knowledge", "")
                return f"The region of {name}, your home, is {basic_desc} {native_details} {biome_desc} {season_desc} {weather_desc}".strip()
            elif perspective == "scholar":
                # Scholars have historical and analytical knowledge
                history = region.get("history", "")
                scholarly_details = region.get("scholarly_knowledge", "")
                return f"The region known as {name} is {basic_desc} {scholarly_details} Historically, {history} {biome_desc} {season_desc} {weather_desc}".strip()
            else:
                return f"The region of {name} is {basic_desc} {biome_desc} {season_desc} {weather_desc}".strip()
            
        except Exception as e:
            logger.error(f"Error getting region description for '{region_id}': {e}")
            return "Information about this region is unavailable."
    
    def get_region_context_by_location(
        self,
        location_id: str
    ) -> Dict[str, Any]:
        """
        Get region information based on a location.
        
        Args:
            location_id: ID of the location
            
        Returns:
            Region context for the location
        """
        try:
            # Get the region for this location
            region_id = self._get_region_for_location(location_id)
            
            if not region_id:
                logger.warning(f"No region found for location: {location_id}")
                return {}
                
            # Get region info
            region = self._get_region_info(region_id, include_details=True)
            
            if not region:
                return {}
                
            # Get biome info
            biome_context = {}
            biome_id = region.get("biome")
            
            if biome_id:
                biome = self._get_biome_info(biome_id)
                if biome:
                    biome_context = biome
            
            # Format context
            context = {
                "region": region,
                "biome": biome_context
            }
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting region context for location '{location_id}': {e}")
            return {}
    
    def get_biome_dialogue_references(
        self,
        biome_id: str,
        reference_type: str = "general",
        season: Optional[str] = None
    ) -> List[str]:
        """
        Get biome-specific references for dialogue.
        
        Args:
            biome_id: ID of the biome
            reference_type: Type of references ('general', 'flora', 'fauna', 'terrain', 'weather')
            season: Optional season for seasonal references
            
        Returns:
            List of biome-specific dialogue references
        """
        try:
            # Get the biome
            biome = self.biome_manager.get_biome(biome_id)
            
            if not biome:
                logger.warning(f"Biome not found: {biome_id}")
                return []
                
            # Get references based on type
            references = []
            
            if reference_type == "general":
                references = biome.get("dialogue_references", [])
            elif reference_type == "flora":
                flora = biome.get("flora", [])
                references = [f"{plant}" for plant in flora]
            elif reference_type == "fauna":
                fauna = biome.get("fauna", [])
                references = [f"{animal}" for animal in fauna]
            elif reference_type == "terrain":
                terrain_features = biome.get("terrain_features", [])
                references = [f"{feature}" for feature in terrain_features]
            elif reference_type == "weather":
                weather_patterns = biome.get("common_weather", [])
                references = [f"{pattern}" for pattern in weather_patterns]
            
            # Add seasonal references if requested
            if season:
                seasonal_refs = biome.get("seasonal_references", {}).get(season, [])
                references.extend(seasonal_refs)
            
            return references
            
        except Exception as e:
            logger.error(f"Error getting biome dialogue references for '{biome_id}': {e}")
            return []
    
    def get_region_comparison(
        self,
        region1_id: str,
        region2_id: str
    ) -> Dict[str, Any]:
        """
        Get comparison between two regions for dialogue.
        
        Args:
            region1_id: ID of the first region
            region2_id: ID of the second region
            
        Returns:
            Dictionary with region comparison information
        """
        try:
            # Get the regions
            region1 = self.region_manager.get_region(region1_id)
            region2 = self.region_manager.get_region(region2_id)
            
            if not region1 or not region2:
                logger.warning(f"One or both regions not found: {region1_id}, {region2_id}")
                return {}
                
            # Get biomes
            biome1_id = region1.get("biome")
            biome2_id = region2.get("biome")
            
            biome1 = self.biome_manager.get_biome(biome1_id) if biome1_id else None
            biome2 = self.biome_manager.get_biome(biome2_id) if biome2_id else None
            
            # Compare basic attributes
            comparison = {
                "region1": {
                    "id": region1_id,
                    "name": region1.get("name", ""),
                    "biome": biome1.get("name", "") if biome1 else ""
                },
                "region2": {
                    "id": region2_id,
                    "name": region2.get("name", ""),
                    "biome": biome2.get("name", "") if biome2 else ""
                },
                "differences": [],
                "similarities": []
            }
            
            # Compare climates
            if region1.get("climate") == region2.get("climate"):
                comparison["similarities"].append(f"Both regions have a {region1.get('climate', '')} climate")
            else:
                comparison["differences"].append(f"{region1.get('name')} has a {region1.get('climate', '')} climate, while {region2.get('name')} has a {region2.get('climate', '')} climate")
            
            # Compare terrain
            if region1.get("terrain") == region2.get("terrain"):
                comparison["similarities"].append(f"Both regions feature {region1.get('terrain', '')} terrain")
            else:
                comparison["differences"].append(f"{region1.get('name')} features {region1.get('terrain', '')} terrain, while {region2.get('name')} features {region2.get('terrain', '')} terrain")
            
            # Compare resources
            resources1 = set(region1.get("resources", []))
            resources2 = set(region2.get("resources", []))
            
            common_resources = resources1.intersection(resources2)
            if common_resources:
                comparison["similarities"].append(f"Both regions are rich in {', '.join(common_resources)}")
            
            unique_resources1 = resources1 - resources2
            if unique_resources1:
                comparison["differences"].append(f"{region1.get('name')} has {', '.join(unique_resources1)}, which {region2.get('name')} lacks")
            
            unique_resources2 = resources2 - resources1
            if unique_resources2:
                comparison["differences"].append(f"{region2.get('name')} has {', '.join(unique_resources2)}, which {region1.get('name')} lacks")
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error getting region comparison for '{region1_id}' and '{region2_id}': {e}")
            return {}
    
    def _get_region_info(
        self,
        region_id: str,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Get information about a region for dialogue context.
        
        Args:
            region_id: ID of the region
            include_details: Whether to include detailed region information
            
        Returns:
            Dictionary with region information
        """
        try:
            # Get the region
            region = self.region_manager.get_region(region_id)
            
            if not region:
                logger.warning(f"Region not found: {region_id}")
                return {}
                
            # Basic region info
            region_info = {
                "id": region.get("id"),
                "name": region.get("name"),
                "biome": region.get("biome"),
                "climate": region.get("climate")
            }
            
            # Add details if requested
            if include_details:
                region_info.update({
                    "description": region.get("description", ""),
                    "terrain": region.get("terrain", ""),
                    "population": region.get("population", 0),
                    "faction_control": region.get("faction_control", ""),
                    "stability": region.get("stability", "stable"),
                    "danger_level": region.get("danger_level", "low"),
                    "notable_landmarks": region.get("notable_landmarks", [])
                })
            
            return region_info
            
        except Exception as e:
            logger.error(f"Error getting region info for '{region_id}': {e}")
            return {}
    
    def _get_biome_info(
        self, 
        biome_id: str
    ) -> Dict[str, Any]:
        """
        Get information about a biome for dialogue context.
        
        Args:
            biome_id: ID of the biome
            
        Returns:
            Dictionary with biome information
        """
        try:
            # Get the biome
            biome = self.biome_manager.get_biome(biome_id)
            
            if not biome:
                logger.warning(f"Biome not found: {biome_id}")
                return {}
                
            # Format for dialogue
            biome_info = {
                "id": biome.get("id"),
                "name": biome.get("name"),
                "description": biome.get("description", ""),
                "climate": biome.get("climate", ""),
                "flora": biome.get("flora", []),
                "fauna": biome.get("fauna", []),
                "terrain_features": biome.get("terrain_features", []),
                "common_weather": biome.get("common_weather", []),
                "seasonal_changes": biome.get("seasonal_changes", {})
            }
            
            return biome_info
            
        except Exception as e:
            logger.error(f"Error getting biome info for '{biome_id}': {e}")
            return {}
    
    def _get_region_resources(
        self, 
        region_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get resources in a region for dialogue context.
        
        Args:
            region_id: ID of the region
            
        Returns:
            List of resources in the region
        """
        try:
            # Get the region
            region = self.region_manager.get_region(region_id)
            
            if not region:
                return []
                
            # Get resource information
            raw_resources = region.get("resources", [])
            
            # Format for dialogue
            formatted_resources = []
            for resource in raw_resources:
                # In a real implementation, you would fetch detailed resource info
                resource_info = {
                    "name": resource,
                    "abundance": region.get("resource_abundance", {}).get(resource, "common"),
                    "importance": region.get("resource_importance", {}).get(resource, "low")
                }
                formatted_resources.append(resource_info)
            
            return formatted_resources
            
        except Exception as e:
            logger.error(f"Error getting region resources for '{region_id}': {e}")
            return []
    
    def _get_adjacent_regions(
        self, 
        region_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get adjacent regions for dialogue context.
        
        Args:
            region_id: ID of the region
            
        Returns:
            List of adjacent regions
        """
        try:
            # Get adjacent regions
            adjacents = self.region_manager.get_adjacent_regions(region_id)
            
            # Format for dialogue
            formatted_adjacents = []
            for adjacent in adjacents:
                adjacent_info = {
                    "id": adjacent.get("id"),
                    "name": adjacent.get("name"),
                    "direction": adjacent.get("direction", "unknown"),
                    "border_type": adjacent.get("border_type", "natural"),
                    "relationship": adjacent.get("relationship", "neutral")
                }
                formatted_adjacents.append(adjacent_info)
            
            return formatted_adjacents
            
        except Exception as e:
            logger.error(f"Error getting adjacent regions for '{region_id}': {e}")
            return []
    
    def _get_seasonal_region_description(
        self, 
        region_id: str, 
        season: str
    ) -> str:
        """
        Get season-specific description of a region.
        
        Args:
            region_id: ID of the region
            season: Season ('spring', 'summer', 'autumn', 'winter')
            
        Returns:
            Season-specific region description
        """
        try:
            # Get the region
            region = self.region_manager.get_region(region_id)
            
            if not region:
                return ""
                
            # Get seasonal descriptions if they exist
            seasonal_descriptions = region.get("seasonal_descriptions", {})
            description = seasonal_descriptions.get(season, "")
            
            if not description:
                # Get biome's seasonal changes as fallback
                biome_id = region.get("biome")
                if biome_id:
                    biome = self.biome_manager.get_biome(biome_id)
                    if biome:
                        seasonal_changes = biome.get("seasonal_changes", {})
                        biome_season_desc = seasonal_changes.get(season, "")
                        
                        if biome_season_desc:
                            description = f"During {season}, {biome_season_desc}"
            
            return description
            
        except Exception as e:
            logger.error(f"Error getting seasonal description for region '{region_id}': {e}")
            return ""
    
    def _get_weather_region_description(
        self, 
        region_id: str, 
        weather: str
    ) -> str:
        """
        Get weather-specific description of a region.
        
        Args:
            region_id: ID of the region
            weather: Weather condition (e.g., 'rain', 'snow', 'clear')
            
        Returns:
            Weather-specific region description
        """
        try:
            # Get the region
            region = self.region_manager.get_region(region_id)
            
            if not region:
                return ""
                
            # Get weather descriptions if they exist
            weather_descriptions = region.get("weather_descriptions", {})
            description = weather_descriptions.get(weather, "")
            
            if not description:
                # Get biome's weather information as fallback
                biome_id = region.get("biome")
                if biome_id:
                    biome = self.biome_manager.get_biome(biome_id)
                    if biome:
                        weather_effects = biome.get("weather_effects", {})
                        biome_weather_desc = weather_effects.get(weather, "")
                        
                        if biome_weather_desc:
                            description = f"During {weather} conditions, {biome_weather_desc}"
            
            return description
            
        except Exception as e:
            logger.error(f"Error getting weather description for region '{region_id}': {e}")
            return ""
    
    def _get_region_for_location(
        self, 
        location_id: str
    ) -> Optional[str]:
        """
        Get the region ID for a location.
        
        Args:
            location_id: ID of the location
            
        Returns:
            ID of the region containing the location
        """
        # This would connect to a location/POI system to determine the region
        # In a real implementation, you'd have a proper lookup mechanism
        
        # Placeholder implementation
        try:
            # This is a simplified version that assumes the location data
            # contains a "region_id" field
            from backend.systems.poi.poi_manager import POIManager
            
            poi_manager = POIManager.get_instance()
            location = poi_manager.get_poi(location_id)
            
            if location:
                return location.get("region_id")
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting region for location '{location_id}': {e}")
            return None 