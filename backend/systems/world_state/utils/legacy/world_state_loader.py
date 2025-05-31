"""
Utility to load predefined world state variables from JSON schema files.

DEPRECATED: This file uses non-canonical imports and is not used in the current codebase.
Consider removing or updating to use canonical backend.systems.world_state imports.
"""
import json
import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# DEPRECATED IMPORT - should use backend.systems.world_state.services instead
from backend.app.core.world_state.world_state_manager import (
    WorldStateManager,
    StateCategory,
    WorldRegion
)

logger = logging.getLogger(__name__)

class WorldStateLoader:
    """
    Loads predefined world state variables from JSON schema files.
    """
    
    def __init__(self, world_state_manager: WorldStateManager, schema_path: str = None):
        """
        Initialize the loader with a world state manager and optional schema path.
        
        Args:
            world_state_manager: The world state manager to populate
            schema_path: Path to the schema file (defaults to standard location)
        """
        self.world_state_manager = world_state_manager
        self.schema_path = schema_path or os.path.join(
            "backend", "data", "modding", "world_state_variables.json"
        )
        
    def load_schema(self) -> Dict[str, Any]:
        """
        Load the world state schema from the JSON file.
        
        Returns:
            The parsed schema as a dictionary
        """
        try:
            schema_file = Path(self.schema_path)
            
            if not schema_file.exists():
                logger.warning(f"World state schema file not found at: {self.schema_path}")
                return {}
                
            with open(schema_file, "r") as f:
                schema = json.load(f)
                
            logger.info(f"Loaded world state schema version {schema.get('schema_version', 'unknown')}")
            return schema
        except Exception as e:
            logger.error(f"Error loading world state schema: {str(e)}")
            return {}
            
    def initialize_default_state(self, categories: List[str] = None, regions: List[Tuple[str, str]] = None) -> None:
        """
        Initialize the world state with default values from the schema.
        
        Args:
            categories: Optional list of categories to initialize (all if None)
            regions: Optional list of (region_type, region_id) tuples to initialize (all if None)
        """
        schema = self.load_schema()
        if not schema or "variables" not in schema:
            logger.warning("No valid schema found, skipping default state initialization")
            return
            
        variables = schema.get("variables", {})
        initialized_count = 0
        
        # Process each category
        for category_name, category_data in variables.items():
            # Skip if categories filter is provided and this category is not in it
            if categories and category_name.upper() not in categories:
                continue
                
            try:
                category_enum = getattr(StateCategory, category_name.upper())
            except AttributeError:
                logger.warning(f"Skipping unknown category: {category_name}")
                continue
                
            # Process global variables
            if "global" in category_data:
                for var_key, var_data in category_data["global"].items():
                    self._initialize_variable(
                        var_key, var_data, category_enum, WorldRegion.GLOBAL, None, regions
                    )
                    initialized_count += 1
                    
            # Process region variables
            for region_type, region_vars in category_data.items():
                if region_type == "global":
                    continue  # Already handled
                    
                try:
                    region_enum = getattr(WorldRegion, region_type.upper())
                except AttributeError:
                    logger.warning(f"Skipping unknown region type: {region_type}")
                    continue
                    
                # For region variables, we need to initialize them for each relevant region ID
                # Here we would typically get the list of region IDs from a region service
                # For demonstration, we'll use placeholder IDs
                region_ids = self._get_region_ids(region_type)
                
                for region_id in region_ids:
                    # Skip if regions filter is provided and this region is not in it
                    if regions and (region_enum.name, region_id) not in regions:
                        continue
                        
                    for var_key, var_data in region_vars.items():
                        self._initialize_variable(
                            var_key, var_data, category_enum, region_enum, region_id, None
                        )
                        initialized_count += 1
                    
        logger.info(f"Initialized {initialized_count} default world state variables")
    
    def _initialize_variable(
        self, 
        key: str, 
        data: Dict[str, Any],
        category: StateCategory,
        region: WorldRegion,
        region_id: Optional[str],
        regions_filter: Optional[List[Tuple[str, str]]]
    ) -> None:
        """
        Initialize a single variable in the world state manager.
        
        Args:
            key: Variable key
            data: Variable data from schema
            category: State category
            region: World region
            region_id: Region ID (if applicable)
            regions_filter: Optional filter for regions
        """
        # Skip if this region is not in the filter
        if regions_filter and (region.name, region_id) not in regions_filter:
            return
            
        # Skip if the variable requires parameters (needs more context to initialize)
        if data.get("requires_parameters"):
            return
            
        # Set the default value from schema
        try:
            default_value = data.get("default")
            if default_value is not None:
                self.world_state_manager.set_state_variable(
                    key=key,
                    value=default_value,
                    category=category,
                    region=region,
                    region_id=region_id,
                    source="system_init"
                )
        except Exception as e:
            logger.error(f"Error initializing variable {key}: {str(e)}")
    
    def _get_region_ids(self, region_type: str) -> List[str]:
        """
        Get the list of region IDs for a specific region type.
        In a real implementation, this would query a game data service.
        
        Args:
            region_type: The type of region (e.g., "kingdom", "city")
            
        Returns:
            List of region IDs
        """
        # Placeholder implementation - in real code, this would query a service
        placeholder_regions = {
            "kingdom": ["alaria", "dornheim", "frost_reach"],
            "city": ["capital_city", "riverdale", "harbor_town", "mountain_keep"],
            "location": ["dark_forest", "ancient_ruins", "dragon_peak", "haunted_marsh"]
        }
        
        return placeholder_regions.get(region_type, [])

def initialize_world_state(world_state_manager: WorldStateManager) -> None:
    """
    Helper function to initialize the world state with defaults from schema.
    
    Args:
        world_state_manager: The world state manager to initialize
    """
    loader = WorldStateLoader(world_state_manager)
    loader.initialize_default_state() 
