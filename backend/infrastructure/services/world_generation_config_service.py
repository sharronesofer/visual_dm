"""
World Generation Configuration Service - Infrastructure Implementation

Provides configuration data and validation for world generation system.
"""

import os
import json
from typing import Dict, Any, Optional, List

from backend.systems.world_generation.models import WorldGenerationConfig


class DefaultWorldGenerationConfigService:
    """Default implementation of WorldGenerationConfigService protocol"""
    
    def __init__(self):
        # Get the data path relative to the project root, not from the current file location
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.data_path = os.path.join(project_root, "data", "systems", "world_generation")
        self._biomes_cache = None
        self._templates_cache = None
        self._placement_rules_cache = None
        self._population_params_cache = None
    
    def get_biome_configuration(self, biome_type: str) -> Dict[str, Any]:
        """Get biome configuration data"""
        if self._biomes_cache is None:
            self._load_biomes_cache()
        
        return self._biomes_cache.get(biome_type, {})
    
    def get_world_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get world template configuration"""
        if self._templates_cache is None:
            self._load_templates_cache()
        
        return self._templates_cache.get(template_name)
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get list of available world templates"""
        if self._templates_cache is None:
            self._load_templates_cache()
        
        return [
            {
                'name': name,
                'description': template.get('description', f'Template: {name}'),
                'difficulty': template.get('difficulty', 'medium'),
                'biome_focus': template.get('biome_focus', []),
                'recommended_for': template.get('recommended_for', [])
            }
            for name, template in self._templates_cache.items()
        ]
    
    def validate_generation_config(self, config: WorldGenerationConfig) -> Dict[str, Any]:
        """Validate and process generation configuration"""
        validated = {}
        
        # Validate main continent size
        if hasattr(config, 'main_continent_size'):
            size = config.main_continent_size
            if isinstance(size, (list, tuple)) and len(size) == 2:
                validated['main_continent_size'] = (max(50, size[0]), min(200, size[1]))
            else:
                validated['main_continent_size'] = (80, 120)
        
        # Validate island count
        if hasattr(config, 'island_count'):
            validated['island_count'] = max(0, min(10, config.island_count))
        
        # Validate density values (0.0 to 1.0)
        density_fields = ['biome_diversity', 'resource_abundance', 'poi_density', 
                         'settlement_density', 'npc_density', 'faction_density', 
                         'trade_route_density']
        
        for field in density_fields:
            if hasattr(config, field):
                value = getattr(config, field)
                validated[field] = max(0.0, min(1.0, value))
        
        # Validate count fields
        count_fields = ['starting_factions', 'region_size']
        for field in count_fields:
            if hasattr(config, field):
                value = getattr(config, field)
                validated[field] = max(1, value)
        
        return validated
    
    def get_biome_placement_rules(self) -> Dict[str, Any]:
        """Get biome placement and adjacency rules"""
        if self._placement_rules_cache is None:
            self._load_placement_rules_cache()
        
        return self._placement_rules_cache
    
    def get_population_parameters(self) -> Dict[str, Any]:
        """Get population generation parameters"""
        if self._population_params_cache is None:
            self._load_population_params_cache()
        
        return self._population_params_cache
    
    def _load_biomes_cache(self):
        """Load biomes configuration from JSON"""
        try:
            biomes_file = os.path.join(self.data_path, "biomes.json")
            with open(biomes_file, 'r') as f:
                self._biomes_cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load biomes.json: {e}")
            self._biomes_cache = {}
    
    def _load_templates_cache(self):
        """Load world templates from JSON"""
        try:
            templates_file = os.path.join(self.data_path, "world_templates.json")
            with open(templates_file, 'r') as f:
                self._templates_cache = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load world_templates.json: {e}")
            self._templates_cache = {}
    
    def _load_placement_rules_cache(self):
        """Load biome placement rules from JSON"""
        try:
            # Load biome placement config
            placement_file = os.path.join(self.data_path, "biome_placement_config.json")
            with open(placement_file, 'r') as f:
                placement_config = json.load(f)
            
            # Load biomes for transition rules
            if self._biomes_cache is None:
                self._load_biomes_cache()
            
            # Build comprehensive placement rules
            self._placement_rules_cache = {
                'default_clustering_factor': placement_config.get('clustering', {}).get('default_clustering_factor', 0.5),
                'max_clustering_iterations': placement_config.get('clustering', {}).get('max_clustering_iterations', 3),
                'max_validation_iterations': placement_config.get('adjacency_validation', {}).get('max_validation_iterations', 5),
                'validation_enabled': placement_config.get('adjacency_validation', {}).get('validation_enabled', True),
                'environmental_weights': placement_config.get('biome_scoring', {}).get('environmental_weights', {
                    'temperature': 0.4,
                    'humidity': 0.4,
                    'elevation': 0.2
                }),
                'range_scoring': placement_config.get('biome_scoring', {}).get('range_scoring', {}),
                'biomes': self._biomes_cache,
                'biome_transitions': self._build_biome_transitions()
            }
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load biome placement config: {e}")
            self._placement_rules_cache = {
                'default_clustering_factor': 0.5,
                'max_clustering_iterations': 3,
                'max_validation_iterations': 5,
                'validation_enabled': True,
                'environmental_weights': {
                    'temperature': 0.4,
                    'humidity': 0.4,
                    'elevation': 0.2
                },
                'biomes': {},
                'biome_transitions': {}
            }
    
    def _load_population_params_cache(self):
        """Load population parameters from JSON"""
        try:
            population_file = os.path.join(self.data_path, "population_config.json")
            with open(population_file, 'r') as f:
                population_config = json.load(f)
            
            self._population_params_cache = population_config
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load population_config.json: {e}")
            # Fallback default values
            self._population_params_cache = {
                'base_populations': {
                    'temperate_forest': 800,
                    'grassland': 1200,
                    'mountains': 300,
                    'desert': 200,
                    'coastal': 1000,
                    'swamp': 400,
                    'tundra': 150,
                    'hills': 600
                }
            }
    
    def _build_biome_transitions(self) -> Dict[str, Dict[str, bool]]:
        """Build biome transition rules from biome adjacency data"""
        transitions = {}
        
        if not self._biomes_cache:
            return transitions
        
        for biome_name, biome_data in self._biomes_cache.items():
            transitions[biome_name] = {}
            adjacent_biomes = biome_data.get('adjacent_biomes', [])
            
            # Set allowed transitions
            for adjacent in adjacent_biomes:
                transitions[biome_name][adjacent] = True
            
            # Set forbidden transitions (not in adjacent list)
            for other_biome in self._biomes_cache.keys():
                if other_biome not in adjacent_biomes and other_biome != biome_name:
                    # Check transition difficulty to determine if it should be forbidden
                    difficulty = biome_data.get('transition_difficulty', 0.5)
                    if difficulty > 0.8:  # High difficulty = forbidden
                        transitions[biome_name][other_biome] = False
        
        return transitions 