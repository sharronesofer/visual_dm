"""
World Template Manager - Infrastructure

Technical infrastructure for managing different world generation templates and configurations
that can be selected for different game scenarios. Handles file I/O and configuration loading.
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass

from backend.infrastructure.config_loaders import JsonConfigLoader


@dataclass
class WorldTemplate:
    """Template defining a specific world generation scenario."""
    name: str
    description: str
    continent_size_range: tuple
    island_count: int
    island_size_range: tuple
    biome_distribution: Dict[str, float]  # Biome preferences
    resource_abundance: float
    danger_level: float  # Overall world danger
    climate_variation: float
    special_features: List[str]  # Special world features


class WorldTemplateManager:
    """Technical infrastructure for managing world generation templates."""
    
    def __init__(self, template_path: Optional[str] = None):
        if template_path is None:
            # Point to the JSON file in data directory
            template_path = Path("data/systems/world_generation/world_templates.json")
        
        # Use the infrastructure JSON loader with default config
        self._config_loader = JsonConfigLoader(
            config_path=str(template_path),
            default_config=self._get_default_template_data()
        )
        
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, WorldTemplate]:
        """Load world templates from JSON file."""
        template_data = self._config_loader.load_config()
        return self._parse_templates(template_data)
    
    def _parse_templates(self, template_data: Dict) -> Dict[str, WorldTemplate]:
        """Parse template data from JSON into WorldTemplate objects."""
        templates = {}
        
        for template_name, data in template_data.items():
            template = WorldTemplate(
                name=data.get("name", template_name),
                description=data.get("description", ""),
                continent_size_range=tuple(data.get("continent_size_range", [80, 120])),
                island_count=data.get("island_count", 3),
                island_size_range=tuple(data.get("island_size_range", [5, 15])),
                biome_distribution=data.get("biome_distribution", {}),
                resource_abundance=data.get("resource_abundance", 0.5),
                danger_level=data.get("danger_level", 0.5),
                climate_variation=data.get("climate_variation", 0.7),
                special_features=data.get("special_features", [])
            )
            templates[template_name] = template
        
        return templates
    
    def _get_default_template_data(self) -> Dict[str, Any]:
        """Provide default world template data."""
        return {
            "standard_fantasy": {
                "name": "Standard Fantasy World",
                "description": "A balanced fantasy world with diverse biomes and moderate dangers",
                "continent_size_range": [80, 120],
                "island_count": 3,
                "island_size_range": [5, 15],
                "biome_distribution": {
                    "temperate_forest": 0.25,
                    "grassland": 0.20,
                    "mountains": 0.15,
                    "coastal": 0.15,
                    "desert": 0.10,
                    "swamp": 0.08,
                    "tundra": 0.07
                },
                "resource_abundance": 0.6,
                "danger_level": 0.5,
                "climate_variation": 0.7,
                "special_features": ["balanced_resources", "moderate_danger"]
            },
            "high_fantasy": {
                "name": "High Fantasy World",
                "description": "A magical world with mystical biomes and higher resource abundance",
                "continent_size_range": [100, 150],
                "island_count": 5,
                "island_size_range": [8, 20],
                "biome_distribution": {
                    "magical_forest": 0.20,
                    "temperate_forest": 0.20,
                    "mountains": 0.18,
                    "grassland": 0.15,
                    "coastal": 0.12,
                    "desert": 0.08,
                    "enchanted_grove": 0.07
                },
                "resource_abundance": 0.8,
                "danger_level": 0.6,
                "climate_variation": 0.8,
                "special_features": ["magical_nodes", "ancient_ruins", "ley_lines"]
            },
            "survival_world": {
                "name": "Survival World",
                "description": "A harsh world with scarce resources and high danger",
                "continent_size_range": [60, 90],
                "island_count": 2,
                "island_size_range": [3, 8],
                "biome_distribution": {
                    "desert": 0.25,
                    "tundra": 0.20,
                    "mountains": 0.20,
                    "swamp": 0.15,
                    "temperate_forest": 0.10,
                    "grassland": 0.10
                },
                "resource_abundance": 0.3,
                "danger_level": 0.8,
                "climate_variation": 0.9,
                "special_features": ["resource_scarcity", "extreme_weather", "dangerous_wildlife"]
            },
            "exploration_world": {
                "name": "Exploration World",
                "description": "A vast world designed for long-term exploration campaigns",
                "continent_size_range": [150, 200],
                "island_count": 8,
                "island_size_range": [10, 25],
                "biome_distribution": {
                    "temperate_forest": 0.18,
                    "grassland": 0.16,
                    "mountains": 0.14,
                    "coastal": 0.12,
                    "desert": 0.10,
                    "tundra": 0.10,
                    "swamp": 0.08,
                    "coniferous_forest": 0.08,
                    "prairie": 0.04
                },
                "resource_abundance": 0.7,
                "danger_level": 0.4,
                "climate_variation": 0.8,
                "special_features": ["vast_distances", "hidden_valleys", "lost_civilizations"]
            },
            "island_nations": {
                "name": "Island Nations",
                "description": "An archipelago world with many islands and maritime focus",
                "continent_size_range": [40, 60],
                "island_count": 12,
                "island_size_range": [3, 12],
                "biome_distribution": {
                    "coastal": 0.35,
                    "temperate_forest": 0.20,
                    "grassland": 0.15,
                    "mountains": 0.10,
                    "swamp": 0.10,
                    "desert": 0.05,
                    "volcanic": 0.05
                },
                "resource_abundance": 0.5,
                "danger_level": 0.5,
                "climate_variation": 0.6,
                "special_features": ["naval_travel", "trade_routes", "fishing_economy"]
            }
        }
    
    def get_template(self, template_name: str) -> Optional[WorldTemplate]:
        """Get a specific world template by name."""
        return self.templates.get(template_name)
    
    def list_templates(self) -> List[str]:
        """Get list of available template names."""
        return list(self.templates.keys())
    
    def get_template_descriptions(self) -> Dict[str, str]:
        """Get name and description of all templates."""
        return {name: template.description for name, template in self.templates.items()}
    
    def create_generation_config(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Create a WorldGenerationConfig dict from a template."""
        template = self.get_template(template_name)
        if not template:
            return None
        
        return {
            "main_continent_size": template.continent_size_range,
            "island_count": template.island_count,
            "island_size_range": template.island_size_range,
            "biome_diversity": len(template.biome_distribution) / 10.0,  # Normalize
            "resource_abundance": template.resource_abundance,
            "danger_progression": self._calculate_danger_progression(template.danger_level),
            "climate_variation": template.climate_variation,
            "special_features": template.special_features
        }
    
    def _calculate_danger_progression(self, danger_level: float) -> tuple:
        """Calculate danger progression tuple from overall danger level."""
        # Adjust safe/moderate/dangerous ratios based on danger level
        safe = max(0.1, 0.8 - danger_level)
        dangerous = min(0.8, danger_level)
        moderate = 1.0 - safe - dangerous
        return (safe, moderate, dangerous)
    
    def save_default_templates_file(self):
        """Save default template configuration to file."""
        self._config_loader.save_default_config()
    
    def reload_templates(self):
        """Force reload templates from file."""
        self._config_loader.reload_config()
        self.templates = self._load_templates() 