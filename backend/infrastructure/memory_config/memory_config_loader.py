"""
Configuration Loader for Memory System
-------------------------------------

This module provides centralized loading and management of JSON configuration files
for the memory system, replacing hardcoded values with flexible, designer-friendly
configuration files.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MemoryConfigurationLoader:
    """
    Centralized configuration loader for the memory system.
    
    Loads and manages JSON configuration files for:
    - Memory categories
    - Behavioral responses
    - Trust calculation weights
    - Cross-system integration rules
    - Emotional trigger patterns
    """
    
    def __init__(self, config_directory: Optional[str] = None):
        """
        Initialize the configuration loader.
        
        Args:
            config_directory: Path to configuration directory. 
                            Defaults to data/systems/memory.
        """
        if config_directory is None:
            # Point to data directory instead of config directory
            project_root = Path(__file__).parent.parent.parent.parent
            config_directory = project_root / "data" / "systems" / "memory"
        
        self.config_dir = Path(config_directory)
        self._configs = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all configuration files."""
        config_files = {
            'memory_categories': 'memory_categories.json',
            'behavioral_responses': 'behavioral_responses.json',
            'trust_calculation': 'trust_calculation.json',
            'system_integration': 'system_integration.json',
            'emotional_triggers': 'emotional_triggers.json'
        }
        
        for config_name, filename in config_files.items():
            try:
                self._configs[config_name] = self._load_config_file(filename)
                logger.info(f"Loaded {config_name} configuration from {filename}")
            except Exception as e:
                logger.error(f"Failed to load {config_name} from {filename}: {e}")
                # Set empty config as fallback
                self._configs[config_name] = {}
    
    def _load_config_file(self, filename: str) -> Dict[str, Any]:
        """Load a specific configuration file."""
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            logger.warning(f"Configuration file {filename} not found at {config_path}")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filename}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            raise
    
    def reload_config(self, config_name: str = None):
        """
        Reload configuration files.
        
        Args:
            config_name: Specific config to reload, or None to reload all
        """
        if config_name:
            if config_name in self._configs:
                self._load_all_configs()
                logger.info(f"Reloaded {config_name} configuration")
            else:
                logger.warning(f"Unknown configuration: {config_name}")
        else:
            self._load_all_configs()
            logger.info("Reloaded all configurations")
    
    # Memory Categories Configuration
    def get_memory_category_config(self, category: str) -> Dict[str, Any]:
        """Get configuration for a specific memory category."""
        categories = self._configs.get('memory_categories', {}).get('memory_categories', {})
        return categories.get(category, {})
    
    def get_all_memory_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get all memory category configurations."""
        return self._configs.get('memory_categories', {}).get('memory_categories', {})
    
    # Behavioral Response Configuration
    def get_trauma_response(self, trauma_type: str) -> Dict[str, Any]:
        """Get configuration for a specific trauma response."""
        responses = self._configs.get('behavioral_responses', {}).get('trauma_responses', {})
        return responses.get(trauma_type, {})
    
    def get_achievement_response(self, achievement_type: str) -> Dict[str, Any]:
        """Get configuration for a specific achievement response."""
        responses = self._configs.get('behavioral_responses', {}).get('achievement_responses', {})
        return responses.get(achievement_type, {})
    
    def get_relationship_response(self, relationship_type: str) -> Dict[str, Any]:
        """Get configuration for a specific relationship response."""
        responses = self._configs.get('behavioral_responses', {}).get('relationship_responses', {})
        return responses.get(relationship_type, {})
    
    # Trust Calculation Configuration
    def get_trust_factors(self) -> Dict[str, Any]:
        """Get trust calculation factors."""
        return self._configs.get('trust_calculation', {}).get('trust_factors', {})
    
    def get_trust_interaction_weights(self) -> Dict[str, float]:
        """Get trust interaction weights."""
        return self.get_trust_factors().get('interaction_weights', {})
    
    def get_trust_temporal_factors(self) -> Dict[str, float]:
        """Get trust temporal factors."""
        return self.get_trust_factors().get('temporal_factors', {})
    
    def get_faction_bias_factors(self) -> Dict[str, Any]:
        """Get faction bias calculation factors."""
        return self._configs.get('trust_calculation', {}).get('faction_bias_factors', {})
    
    def get_risk_assessment_factors(self) -> Dict[str, Any]:
        """Get risk assessment calculation factors."""
        return self._configs.get('trust_calculation', {}).get('risk_assessment_factors', {})
    
    # System Integration Configuration
    def get_system_integration_config(self, system: str) -> Dict[str, Any]:
        """Get integration configuration for a specific system."""
        integration = self._configs.get('system_integration', {}).get('system_integration', {})
        return integration.get(system, {})
    
    def get_economy_integration_config(self) -> Dict[str, Any]:
        """Get economy system integration configuration."""
        return self.get_system_integration_config('economy')
    
    def get_combat_integration_config(self) -> Dict[str, Any]:
        """Get combat system integration configuration."""
        return self.get_system_integration_config('combat')
    
    def get_social_integration_config(self) -> Dict[str, Any]:
        """Get social system integration configuration."""
        return self.get_system_integration_config('social')
    
    def get_faction_integration_config(self) -> Dict[str, Any]:
        """Get faction system integration configuration."""
        return self.get_system_integration_config('faction')
    
    def get_memory_integration_config(self) -> Dict[str, Any]:
        """Get memory integration configuration."""
        return self._configs.get('system_integration', {}).get('memory_integration', {})
    
    # Emotional Triggers Configuration
    def get_trigger_patterns(self) -> Dict[str, list]:
        """Get all trigger patterns."""
        return self._configs.get('emotional_triggers', {}).get('trigger_patterns', {})
    
    def get_trigger_keywords(self, trigger_type: str) -> list:
        """Get keywords for a specific trigger type."""
        patterns = self.get_trigger_patterns()
        return patterns.get(trigger_type, [])
    
    def get_emotional_responses(self) -> Dict[str, Dict[str, Any]]:
        """Get emotional response configurations."""
        return self._configs.get('emotional_triggers', {}).get('emotional_responses', {})
    
    def get_emotional_response(self, emotion: str) -> Dict[str, Any]:
        """Get configuration for a specific emotional response."""
        responses = self.get_emotional_responses()
        return responses.get(emotion, {})
    
    def get_contextual_modifiers(self) -> Dict[str, Dict[str, Any]]:
        """Get contextual modifier configurations."""
        return self._configs.get('emotional_triggers', {}).get('contextual_modifiers', {})
    
    # Utility methods
    def get_config_value(self, config_path: str, default=None):
        """
        Get a configuration value using dot notation.
        
        Args:
            config_path: Dot-separated path to config value (e.g., 'trust_calculation.trust_factors.recency_weight')
            default: Default value if path not found
            
        Returns:
            Configuration value or default
        """
        try:
            parts = config_path.split('.')
            current = self._configs
            
            for part in parts:
                current = current[part]
            
            return current
        except (KeyError, TypeError):
            return default
    
    def validate_configurations(self) -> Dict[str, list]:
        """
        Validate all loaded configurations for common issues.
        
        Returns:
            Dictionary of validation warnings by config type
        """
        warnings = {}
        
        # Validate memory categories
        category_warnings = []
        categories = self.get_all_memory_categories()
        for cat_name, cat_config in categories.items():
            required_fields = ['default_importance', 'decay_modifier', 'is_permanent']
            for field in required_fields:
                if field not in cat_config:
                    category_warnings.append(f"Missing required field '{field}' in category '{cat_name}'")
            
            # Check value ranges
            importance = cat_config.get('default_importance', 0)
            if not 0 <= importance <= 1:
                category_warnings.append(f"Invalid importance {importance} in category '{cat_name}' (should be 0-1)")
        
        if category_warnings:
            warnings['memory_categories'] = category_warnings
        
        # Validate trust factors
        trust_warnings = []
        trust_factors = self.get_trust_factors()
        interaction_weights = trust_factors.get('interaction_weights', {})
        for weight_name, weight_value in interaction_weights.items():
            if not isinstance(weight_value, (int, float)):
                trust_warnings.append(f"Invalid weight type for '{weight_name}': {type(weight_value)}")
            elif not -1 <= weight_value <= 1:
                trust_warnings.append(f"Weight '{weight_name}' = {weight_value} outside recommended range [-1, 1]")
        
        if trust_warnings:
            warnings['trust_calculation'] = trust_warnings
        
        return warnings


# Global configuration loader instance
_config_loader = None


def get_memory_config() -> MemoryConfigurationLoader:
    """
    Get the global memory configuration loader instance.
    
    Returns:
        MemoryConfigurationLoader instance
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = MemoryConfigurationLoader()
    return _config_loader


def reload_memory_config():
    """Reload the global memory configuration."""
    global _config_loader
    if _config_loader:
        _config_loader.reload_config()
    else:
        _config_loader = MemoryConfigurationLoader() 