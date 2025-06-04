"""
Tension Configuration Repository Implementation

Repository implementation for loading tension configurations from JSON files.
Follows Development Bible standards for configuration management.
"""

from typing import Dict, Any, List
import json
from pathlib import Path

from backend.systems.tension.models.tension_state import (
    TensionConfig,
    ConflictTrigger,
    RevoltConfig,
    CalculationConstants
)
from backend.systems.tension.services.tension_business_service import TensionConfigRepository


class JSONTensionConfigRepository:
    """JSON-based implementation of TensionConfigRepository"""
    
    def __init__(self, config_dir: str = "data/systems/tension"):
        self.config_dir = Path(config_dir)
        self._cached_configs = {}
        self._load_all_configs()
    
    def get_location_config(self, region_id: str, poi_id: str) -> TensionConfig:
        """Get configuration for a location"""
        # Determine location type from region and POI identifiers
        location_type = self._determine_location_type(region_id, poi_id)
        
        location_configs = self._cached_configs.get('location_configs', {})
        
        # Use specific config or fall back to default
        config_data = location_configs.get(location_type, location_configs.get('default', {}))
        
        # Provide fallback defaults if config is missing
        default_config = {
            "base_tension": 0.2,
            "decay_rate": 0.05,
            "max_tension": 1.0,
            "min_tension": 0.1,
            "player_impact": 1.5,
            "npc_impact": 1.0,
            "environmental_impact": 0.5
        }
        
        # Merge with defaults
        final_config = {**default_config, **config_data}
        
        return TensionConfig(
            base_tension=final_config["base_tension"],
            decay_rate=final_config["decay_rate"],
            max_tension=final_config["max_tension"],
            min_tension=final_config["min_tension"],
            player_impact=final_config["player_impact"],
            npc_impact=final_config["npc_impact"],
            environmental_impact=final_config["environmental_impact"]
        )
    
    def _determine_location_type(self, region_id: str, poi_id: str) -> str:
        """Determine location type from region and POI identifiers"""
        # Check POI type mapping first
        poi_mapping = self._cached_configs.get('poi_type_mapping', {})
        if poi_id in poi_mapping:
            return poi_mapping[poi_id]
        
        # Simple heuristics for location type detection
        poi_id_lower = poi_id.lower()
        
        if "city" in poi_id_lower or "town" in poi_id_lower:
            return "city"
        elif "village" in poi_id_lower:
            return "village" 
        elif "dungeon" in poi_id_lower or "cave" in poi_id_lower:
            return "dungeon"
        elif "forest" in poi_id_lower:
            return "forest"
        elif "mountain" in poi_id_lower:
            return "mountain"
        elif "temple" in poi_id_lower or "shrine" in poi_id_lower:
            return "temple"
        elif "port" in poi_id_lower or "harbor" in poi_id_lower:
            return "port"
        elif "farm" in poi_id_lower:
            return "farm"
        elif "mine" in poi_id_lower:
            return "mine"
        else:
            return "default"
    
    def get_event_impact_config(self, event_type: str) -> Dict[str, Any]:
        """Get impact configuration for an event type"""
        event_impacts = self._cached_configs.get('event_impacts', {})
        
        # Use specific config or fall back to default
        config = event_impacts.get(event_type, event_impacts.get('default', {}))
        
        # Provide fallback defaults
        default_impact_config = {
            "base_impact": 0.1,
            "lethal_modifier": 0.2,
            "stealth_modifier": -0.05
        }
        
        return {**default_impact_config, **config}
    
    def get_calculation_constants(self) -> CalculationConstants:
        """Get calculation constants"""
        constants = self._cached_configs.get('calculation_constants', {})
        
        # Provide fallback defaults
        default_constants = {
            "high_tension_threshold": 0.7,
            "event_history_hours": 24,
            "modifier_expiration_check_hours": 1,
            "severity_thresholds": {
                "minor": 0.1,
                "moderate": 0.3,
                "major": 0.6,
                "extreme": 1.0
            },
            "revolt_probability": {
                "base_threshold": 0.5,
                "faction_modifier_per_faction": 0.1,
                "tension_multiplier": 2.0
            },
            "tension_limits": {
                "absolute_min": 0.0,
                "absolute_max": 1.0
            }
        }
        
        final_constants = {**default_constants, **constants}
        
        return CalculationConstants(
            high_tension_threshold=final_constants["high_tension_threshold"],
            event_history_hours=final_constants["event_history_hours"],
            modifier_expiration_check_hours=final_constants["modifier_expiration_check_hours"],
            severity_thresholds=final_constants["severity_thresholds"],
            revolt_probability=final_constants["revolt_probability"],
            tension_limits=final_constants["tension_limits"]
        )
    
    def get_conflict_triggers(self) -> List[ConflictTrigger]:
        """Get all conflict trigger configurations"""
        triggers_config = self._cached_configs.get('conflict_triggers', {})
        
        triggers = []
        for trigger_name, trigger_data in triggers_config.items():
            # Provide defaults for missing fields
            default_trigger = {
                "name": trigger_name,
                "tension_threshold": 0.8,
                "duration_hours": 48,
                "faction_requirements": {},
                "probability_modifier": 1.0
            }
            
            final_trigger = {**default_trigger, **trigger_data}
            final_trigger["name"] = trigger_name  # Ensure name matches key
            
            triggers.append(ConflictTrigger(
                name=final_trigger["name"],
                tension_threshold=final_trigger["tension_threshold"],
                duration_hours=final_trigger["duration_hours"],
                faction_requirements=final_trigger["faction_requirements"],
                probability_modifier=final_trigger["probability_modifier"]
            ))
        
        # Provide at least one default trigger if none configured
        if not triggers:
            triggers.append(ConflictTrigger(
                name="default_conflict",
                tension_threshold=0.8,
                duration_hours=48,
                faction_requirements={},
                probability_modifier=1.0
            ))
        
        return triggers
    
    def get_revolt_config(self) -> RevoltConfig:
        """Get revolt configuration"""
        revolt_config = self._cached_configs.get('revolt_config', {})
        
        # Provide fallback defaults
        default_revolt = {
            "base_probability_threshold": 0.5,
            "faction_influence_modifier": 0.1,
            "duration_range_hours": [24, 72],
            "casualty_multiplier": 1.0,
            "economic_impact_factor": 0.3
        }
        
        final_config = {**default_revolt, **revolt_config}
        
        return RevoltConfig(
            base_probability_threshold=final_config["base_probability_threshold"],
            faction_influence_modifier=final_config["faction_influence_modifier"],
            duration_range_hours=final_config["duration_range_hours"],
            casualty_multiplier=final_config["casualty_multiplier"],
            economic_impact_factor=final_config["economic_impact_factor"]
        )
    
    def _load_all_configs(self) -> None:
        """Load all configuration files"""
        config_files = [
            "location_configs.json",
            "event_impacts.json",
            "conflict_triggers.json",
            "calculation_constants.json",
            "revolt_config.json",
            "poi_type_mapping.json",
            "event_factory_defaults.json"
        ]
        
        for config_file in config_files:
            config_path = self.config_dir / config_file
            config_key = config_file.replace('.json', '')
            
            try:
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        self._cached_configs[config_key] = json.load(f)
                else:
                    # Create empty config if file doesn't exist
                    self._cached_configs[config_key] = {}
            except (json.JSONDecodeError, IOError):
                # Use empty config if file is corrupted or inaccessible
                self._cached_configs[config_key] = {}


class FallbackTensionConfigRepository:
    """Fallback configuration repository with hardcoded defaults"""
    
    def get_location_config(self, region_id: str, poi_id: str) -> TensionConfig:
        """Get default configuration for any location type"""
        return TensionConfig(
            base_tension=0.2,
            decay_rate=0.05,
            max_tension=1.0,
            min_tension=0.1,
            player_impact=1.5,
            npc_impact=1.0,
            environmental_impact=0.5
        )
    
    def get_event_impact_config(self, event_type: str) -> Dict[str, Any]:
        """Get default impact configuration"""
        return {
            "base_impact": 0.1,
            "lethal_modifier": 0.2,
            "stealth_modifier": -0.05
        }
    
    def get_calculation_constants(self) -> CalculationConstants:
        """Get default calculation constants"""
        return CalculationConstants(
            high_tension_threshold=0.7,
            event_history_hours=24,
            modifier_expiration_check_hours=1,
            severity_thresholds={"minor": 0.1, "moderate": 0.3, "major": 0.6, "extreme": 1.0},
            revolt_probability={"base_threshold": 0.5, "faction_modifier_per_faction": 0.1, "tension_multiplier": 2.0},
            tension_limits={"absolute_min": 0.0, "absolute_max": 1.0}
        )
    
    def get_conflict_triggers(self) -> List[ConflictTrigger]:
        """Get default conflict triggers"""
        return [
            ConflictTrigger(
                name="default_conflict",
                tension_threshold=0.8,
                duration_hours=48,
                faction_requirements={},
                probability_modifier=1.0
            )
        ]
    
    def get_revolt_config(self) -> RevoltConfig:
        """Get default revolt configuration"""
        return RevoltConfig(
            base_probability_threshold=0.5,
            faction_influence_modifier=0.1,
            duration_range_hours=[24, 72],
            casualty_multiplier=1.0,
            economic_impact_factor=0.3
        ) 