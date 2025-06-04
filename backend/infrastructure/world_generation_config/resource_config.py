"""
Resource Configuration Manager - Infrastructure

Technical infrastructure for managing resource type definitions and validation
for the world generation system. Handles file I/O and configuration loading.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path

from backend.infrastructure.config_loaders import JsonConfigLoader


class ResourceConfigManager:
    """Technical infrastructure for managing resource configuration loaded from JSON files."""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Point to the JSON file in data directory
            config_path = Path("data/systems/world_generation/resource_types.json")
        
        # Use the infrastructure JSON loader with default config
        self._config_loader = JsonConfigLoader(
            config_path=str(config_path),
            default_config=self._get_default_config()
        )
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Provide default configuration as fallback."""
        return {
            "resource_types": {
                "timber": {"name": "Timber", "category": "raw_material", "rarity": "common", "trade_value": 1.0},
                "stone": {"name": "Stone", "category": "raw_material", "rarity": "common", "trade_value": 0.8},
                "iron": {"name": "Iron Ore", "category": "metal", "rarity": "common", "trade_value": 2.0},
                "fresh_water": {"name": "Fresh Water", "category": "vital_resource", "rarity": "common", "trade_value": 0.3}
            },
            "rarity_multipliers": {
                "common": 1.0, "uncommon": 1.5, "rare": 3.0, "very_rare": 8.0, "legendary": 20.0
            }
        }
    
    def get_resource_types(self) -> Dict[str, Dict[str, Any]]:
        """Get all resource type definitions."""
        return self._config_loader.get_config_value("resource_types", {})
    
    def get_resource_type(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific resource type."""
        return self.get_resource_types().get(resource_id)
    
    def get_resource_name(self, resource_id: str) -> str:
        """Get the display name for a resource type."""
        resource = self.get_resource_type(resource_id)
        return resource.get("name", resource_id.title()) if resource else resource_id.title()
    
    def get_resource_category(self, resource_id: str) -> str:
        """Get the category for a resource type."""
        resource = self.get_resource_type(resource_id)
        return resource.get("category", "unknown") if resource else "unknown"
    
    def get_resource_rarity(self, resource_id: str) -> str:
        """Get the rarity for a resource type."""
        resource = self.get_resource_type(resource_id)
        return resource.get("rarity", "common") if resource else "common"
    
    def get_resource_trade_value(self, resource_id: str) -> float:
        """Get the base trade value for a resource type."""
        resource = self.get_resource_type(resource_id)
        return resource.get("trade_value", 1.0) if resource else 1.0
    
    def get_rarity_multiplier(self, rarity: str) -> float:
        """Get the trade value multiplier for a rarity level."""
        multipliers = self._config_loader.get_config_value("rarity_multipliers", {})
        return multipliers.get(rarity, 1.0)
    
    def get_effective_trade_value(self, resource_id: str) -> float:
        """Get the effective trade value including rarity modifier."""
        base_value = self.get_resource_trade_value(resource_id)
        rarity = self.get_resource_rarity(resource_id)
        multiplier = self.get_rarity_multiplier(rarity)
        return base_value * multiplier
    
    def get_resources_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Get all resources of a specific category."""
        all_resources = self.get_resource_types()
        return {
            resource_id: resource_data 
            for resource_id, resource_data in all_resources.items()
            if resource_data.get("category") == category
        }
    
    def get_resources_by_rarity(self, rarity: str) -> Dict[str, Dict[str, Any]]:
        """Get all resources of a specific rarity level."""
        all_resources = self.get_resource_types()
        return {
            resource_id: resource_data 
            for resource_id, resource_data in all_resources.items()
            if resource_data.get("rarity") == rarity
        }
    
    def validate_resource_id(self, resource_id: str) -> bool:
        """Check if a resource ID is valid."""
        return resource_id in self.get_resource_types()
    
    def get_valid_resource_ids(self) -> List[str]:
        """Get list of all valid resource IDs."""
        return list(self.get_resource_types().keys())
    
    def get_category_descriptions(self) -> Dict[str, str]:
        """Get descriptions for all resource categories."""
        return self._config_loader.get_config_value("category_descriptions", {}) 