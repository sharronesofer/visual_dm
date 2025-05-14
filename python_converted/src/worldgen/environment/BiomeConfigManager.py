#!/usr/bin/env python3
"""
BiomeConfigManager.py - Part of the World Generation System

Implements a configuration system for biome adjacency rules and transitions,
allowing designers to customize biome generation.
"""

import os
import json
from typing import Dict, List, Set, Optional, Any, Union, Tuple
import logging

from .BiomeTypes import BiomeType, BiomeClassification, BIOME_PARAMETERS, TRANSITION_BIOMES
from .BiomeAdjacencyMatrix import BiomeAdjacencyMatrix, BiomeAdjacencyRule, AdjacencyRuleType


class BiomeConfigManager:
    """
    Manages configuration for biome generation, including adjacency rules,
    transition properties, and custom overrides.
    """
    
    def __init__(self, config_directory: str = "config/biomes"):
        """
        Initialize the biome configuration manager
        
        Args:
            config_directory: Directory for configuration files
        """
        self.config_directory = config_directory
        self.logger = logging.getLogger("BiomeConfigManager")
        
        # Core configuration components
        self.adjacency_matrix = BiomeAdjacencyMatrix()
        self.custom_transitions: Dict[str, Dict] = {}
        self.region_overrides: Dict[str, Dict] = {}
        self.biome_parameters = BIOME_PARAMETERS.copy()
        
        # Ensure config directory exists
        os.makedirs(config_directory, exist_ok=True)
    
    def load_configuration(self) -> bool:
        """
        Load all configuration files from the config directory
        
        Returns:
            True if configuration loaded successfully, False otherwise
        """
        try:
            # Clear existing configuration
            self.custom_transitions = {}
            self.region_overrides = {}
            
            # Load adjacency matrix
            matrix_path = os.path.join(self.config_directory, "adjacency_matrix.json")
            if os.path.exists(matrix_path):
                self.adjacency_matrix = BiomeAdjacencyMatrix.load_from_file(matrix_path)
                self.logger.info(f"Loaded adjacency matrix from {matrix_path}")
            else:
                # Generate and save default matrix
                self.adjacency_matrix = BiomeAdjacencyMatrix()
                self.save_adjacency_matrix()
                self.logger.info(f"Created default adjacency matrix")
            
            # Load custom transitions
            transitions_path = os.path.join(self.config_directory, "custom_transitions.json")
            if os.path.exists(transitions_path):
                with open(transitions_path, 'r') as f:
                    self.custom_transitions = json.load(f)
                self.logger.info(f"Loaded custom transitions from {transitions_path}")
            
            # Load region overrides
            overrides_path = os.path.join(self.config_directory, "region_overrides.json")
            if os.path.exists(overrides_path):
                with open(overrides_path, 'r') as f:
                    self.region_overrides = json.load(f)
                self.logger.info(f"Loaded region overrides from {overrides_path}")
            
            # Load custom biome parameters if available
            params_path = os.path.join(self.config_directory, "biome_parameters.json")
            if os.path.exists(params_path):
                self._load_custom_biome_parameters(params_path)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            return False
    
    def save_configuration(self) -> bool:
        """
        Save all configuration to the config directory
        
        Returns:
            True if configuration saved successfully, False otherwise
        """
        try:
            # Save adjacency matrix
            self.save_adjacency_matrix()
            
            # Save custom transitions
            transitions_path = os.path.join(self.config_directory, "custom_transitions.json")
            with open(transitions_path, 'w') as f:
                json.dump(self.custom_transitions, f, indent=2)
                
            # Save region overrides
            overrides_path = os.path.join(self.config_directory, "region_overrides.json")
            with open(overrides_path, 'w') as f:
                json.dump(self.region_overrides, f, indent=2)
                
            # Save biome parameters
            self._save_biome_parameters()
                
            self.logger.info(f"Configuration saved to {self.config_directory}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            return False
    
    def save_adjacency_matrix(self) -> bool:
        """
        Save the current adjacency matrix to file
        
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            matrix_path = os.path.join(self.config_directory, "adjacency_matrix.json")
            self.adjacency_matrix.save_to_file(matrix_path)
            self.logger.info(f"Saved adjacency matrix to {matrix_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save adjacency matrix: {str(e)}")
            return False
    
    def set_biome_adjacency_rule(self, biome1: BiomeType, biome2: BiomeType,
                               rule_type: AdjacencyRuleType,
                               transition_biomes: Optional[List[BiomeType]] = None,
                               min_transition_width: int = 1) -> bool:
        """
        Define or override a biome adjacency rule
        
        Args:
            biome1: First biome
            biome2: Second biome
            rule_type: Rule type (compatible, incompatible, transition_needed)
            transition_biomes: List of biomes for transition
            min_transition_width: Minimum transition width
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.adjacency_matrix.override_rule(
                biome1=biome1,
                biome2=biome2,
                rule_type=rule_type,
                transition_biomes=transition_biomes,
                min_transition_width=min_transition_width
            )
            self.logger.info(f"Set adjacency rule for {biome1.value}-{biome2.value}: {rule_type.value}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set adjacency rule: {str(e)}")
            return False
    
    def set_custom_transition(self, region_id: str, biome1: BiomeType, biome2: BiomeType,
                             transition_biome: BiomeType, width: int = 1) -> bool:
        """
        Define a custom transition for a specific region
        
        Args:
            region_id: Unique identifier for the region
            biome1: First biome
            biome2: Second biome
            transition_biome: Biome to use for the transition
            width: Width of the transition zone
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Sort biomes to ensure consistent keys
            biome_key = '_'.join(sorted([biome1.value, biome2.value]))
            
            if region_id not in self.custom_transitions:
                self.custom_transitions[region_id] = {}
            
            self.custom_transitions[region_id][biome_key] = {
                "transition_biome": transition_biome.value,
                "width": width
            }
            
            self.logger.info(f"Set custom transition for region {region_id}, {biome1.value}-{biome2.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set custom transition: {str(e)}")
            return False
    
    def remove_custom_transition(self, region_id: str, biome1: BiomeType, biome2: BiomeType) -> bool:
        """
        Remove a custom transition for a specific region
        
        Args:
            region_id: Unique identifier for the region
            biome1: First biome
            biome2: Second biome
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Sort biomes to ensure consistent keys
            biome_key = '_'.join(sorted([biome1.value, biome2.value]))
            
            if region_id in self.custom_transitions and biome_key in self.custom_transitions[region_id]:
                del self.custom_transitions[region_id][biome_key]
                
                # Clean up empty dictionaries
                if not self.custom_transitions[region_id]:
                    del self.custom_transitions[region_id]
                    
                self.logger.info(f"Removed custom transition for region {region_id}, {biome1.value}-{biome2.value}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove custom transition: {str(e)}")
            return False
    
    def get_custom_transition(self, region_id: str, biome1: BiomeType, 
                             biome2: BiomeType) -> Optional[Dict]:
        """
        Get custom transition for a specific region and biome pair
        
        Args:
            region_id: Unique identifier for the region
            biome1: First biome
            biome2: Second biome
            
        Returns:
            Dictionary with transition configuration, or None if not found
        """
        # Sort biomes to ensure consistent keys
        biome_key = '_'.join(sorted([biome1.value, biome2.value]))
        
        if region_id in self.custom_transitions and biome_key in self.custom_transitions[region_id]:
            return self.custom_transitions[region_id][biome_key]
        
        return None
    
    def set_region_override(self, region_id: str, 
                           override_type: str, 
                           value: Any) -> bool:
        """
        Set a configuration override for a specific region
        
        Args:
            region_id: Unique identifier for the region
            override_type: Type of override (e.g., 'transitions_enabled', 'min_transition_width')
            value: Value for the override
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if region_id not in self.region_overrides:
                self.region_overrides[region_id] = {}
                
            self.region_overrides[region_id][override_type] = value
            self.logger.info(f"Set region override for {region_id}: {override_type}={value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set region override: {str(e)}")
            return False
    
    def remove_region_override(self, region_id: str, override_type: str) -> bool:
        """
        Remove a configuration override for a specific region
        
        Args:
            region_id: Unique identifier for the region
            override_type: Type of override to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if region_id in self.region_overrides and override_type in self.region_overrides[region_id]:
                del self.region_overrides[region_id][override_type]
                
                # Clean up empty dictionaries
                if not self.region_overrides[region_id]:
                    del self.region_overrides[region_id]
                    
                self.logger.info(f"Removed region override for {region_id}: {override_type}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove region override: {str(e)}")
            return False
    
    def get_region_override(self, region_id: str, override_type: str, default: Any = None) -> Any:
        """
        Get a configuration override for a specific region
        
        Args:
            region_id: Unique identifier for the region
            override_type: Type of override to get
            default: Default value if override not found
            
        Returns:
            Override value, or default if not found
        """
        if region_id in self.region_overrides and override_type in self.region_overrides[region_id]:
            return self.region_overrides[region_id][override_type]
        
        return default
    
    def get_biome_adjacency_matrix(self) -> BiomeAdjacencyMatrix:
        """
        Get the configured biome adjacency matrix
        
        Returns:
            The biome adjacency matrix
        """
        return self.adjacency_matrix
    
    def get_transition_biomes(self, biome1: BiomeType, biome2: BiomeType, 
                             region_id: Optional[str] = None) -> List[BiomeType]:
        """
        Get suitable transition biomes between two incompatible biomes,
        taking into account custom transitions if specified
        
        Args:
            biome1: First biome
            biome2: Second biome
            region_id: Optional region ID for custom transitions
            
        Returns:
            List of suitable transition biomes
        """
        # Check for custom transition if region ID is provided
        if region_id:
            custom = self.get_custom_transition(region_id, biome1, biome2)
            if custom and "transition_biome" in custom:
                try:
                    return [BiomeType(custom["transition_biome"])]
                except (ValueError, KeyError):
                    self.logger.warning(f"Invalid custom transition biome for {region_id}: {custom}")
        
        # Fall back to adjacency matrix
        return self.adjacency_matrix.get_transition_biomes(biome1, biome2)
    
    def get_transition_width(self, biome1: BiomeType, biome2: BiomeType, 
                           region_id: Optional[str] = None) -> int:
        """
        Get the transition width between two biomes, taking into account
        custom transitions and region overrides
        
        Args:
            biome1: First biome
            biome2: Second biome
            region_id: Optional region ID for custom settings
            
        Returns:
            Transition width in cells
        """
        # Check for region-wide override
        if region_id:
            global_width = self.get_region_override(region_id, "min_transition_width")
            if global_width is not None:
                return int(global_width)
                
            # Check for custom transition
            custom = self.get_custom_transition(region_id, biome1, biome2)
            if custom and "width" in custom:
                return int(custom["width"])
        
        # Fall back to adjacency matrix
        return self.adjacency_matrix.get_min_transition_width(biome1, biome2)
    
    def are_transitions_enabled(self, region_id: Optional[str] = None) -> bool:
        """
        Check if transitions are enabled for a specific region
        
        Args:
            region_id: Optional region ID
            
        Returns:
            True if transitions are enabled, False otherwise
        """
        if region_id:
            enabled = self.get_region_override(region_id, "transitions_enabled")
            if enabled is not None:
                return bool(enabled)
        
        # Default to enabled
        return True
    
    def export_configuration_template(self, output_path: str) -> bool:
        """
        Export a template configuration with comments for designers
        
        Args:
            output_path: Path to save the template
            
        Returns:
            True if successful, False otherwise
        """
        try:
            template = {
                "documentation": {
                    "description": "Biome Configuration Template",
                    "usage": "Edit this file to customize biome generation",
                    "notes": [
                        "This file is a template and can be modified by designers",
                        "Changes will be loaded when the game starts"
                    ]
                },
                "adjacency_rules_examples": [
                    {
                        "biome1": "desert",
                        "biome2": "tundra",
                        "rule_type": "transition_needed",
                        "transition_biomes": ["plains", "grassland", "shrubland"],
                        "min_transition_width": 3,
                        "comment": "Example of incompatible biomes requiring transition"
                    },
                    {
                        "biome1": "temperate_forest",
                        "biome2": "grassland",
                        "rule_type": "compatible",
                        "comment": "Example of compatible biomes"
                    }
                ],
                "custom_transitions_examples": {
                    "region_123": {
                        "desert_plains": {
                            "transition_biome": "shrubland",
                            "width": 2,
                            "comment": "Custom transition for desert-plains in region_123"
                        }
                    }
                },
                "region_overrides_examples": {
                    "region_456": {
                        "transitions_enabled": True,
                        "min_transition_width": 2,
                        "comment": "Global settings for region_456"
                    }
                },
                "available_biomes": [biome.value for biome in BiomeType],
                "transition_biomes": [biome.value for biome in TRANSITION_BIOMES]
            }
            
            with open(output_path, 'w') as f:
                json.dump(template, f, indent=2)
                
            self.logger.info(f"Exported configuration template to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export configuration template: {str(e)}")
            return False
    
    def _load_custom_biome_parameters(self, filepath: str) -> bool:
        """
        Load custom biome parameters from a JSON file
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                custom_params = json.load(f)
                
            for biome_name, params in custom_params.items():
                try:
                    biome = BiomeType(biome_name)
                    
                    # Update specific parameters while preserving the rest
                    original_params = self.biome_parameters[biome]
                    
                    # Update ranges if provided
                    if "temperature_range" in params:
                        original_params.temperature_range = tuple(params["temperature_range"])
                    if "moisture_range" in params:
                        original_params.moisture_range = tuple(params["moisture_range"])
                    if "elevation_range" in params:
                        original_params.elevation_range = tuple(params["elevation_range"])
                    
                    # Update other properties
                    for key in ["soil_fertility", "vegetation_density", "biodiversity", 
                               "base_color", "is_transition_biome", "transition_weight"]:
                        if key in params:
                            setattr(original_params, key, params[key])
                    
                    self.logger.info(f"Updated parameters for biome {biome_name}")
                    
                except ValueError:
                    self.logger.warning(f"Unknown biome in parameters file: {biome_name}")
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load custom biome parameters: {str(e)}")
            return False
    
    def _save_biome_parameters(self) -> bool:
        """
        Save current biome parameters to a JSON file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            params_path = os.path.join(self.config_directory, "biome_parameters.json")
            
            # Convert parameters to JSON-serializable format
            params_dict = {}
            for biome, params in self.biome_parameters.items():
                params_dict[biome.value] = {
                    "temperature_range": list(params.temperature_range),
                    "moisture_range": list(params.moisture_range),
                    "elevation_range": list(params.elevation_range),
                    "soil_fertility": params.soil_fertility,
                    "vegetation_density": params.vegetation_density,
                    "biodiversity": params.biodiversity,
                    "base_color": params.base_color,
                    "is_transition_biome": params.is_transition_biome,
                    "transition_weight": params.transition_weight
                }
            
            with open(params_path, 'w') as f:
                json.dump(params_dict, f, indent=2)
                
            self.logger.info(f"Saved biome parameters to {params_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save biome parameters: {str(e)}")
            return False 