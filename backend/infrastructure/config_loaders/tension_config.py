"""
Tension Configuration Manager

Manages externalized tension configurations loaded from JSON files,
replacing all hardcoded tension parameters from the original system.
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TensionConfig:
    """Configuration for tension calculations in a specific location type."""
    base_tension: float
    decay_rate: float
    max_tension: float
    min_tension: float
    player_impact: float
    npc_impact: float
    environmental_impact: float


@dataclass
class RevoltConfig:
    """Configuration for revolt mechanics."""
    base_probability_threshold: float
    faction_influence_modifier: float
    duration_range_hours: tuple
    casualty_multiplier: float
    economic_impact_factor: float


@dataclass
class ConflictTriggerConfig:
    """Configuration for conflict triggers."""
    name: str
    tension_threshold: float
    duration_hours: int
    faction_requirements: Dict[str, Any]
    probability_modifier: float


@dataclass
class CalculationConstants:
    """Configuration for calculation constants."""
    high_tension_threshold: float
    event_history_hours: int
    modifier_expiration_check_hours: int
    severity_thresholds: Dict[str, float]
    revolt_probability: Dict[str, float]
    tension_limits: Dict[str, float]


class TensionConfigManager:
    """Manages tension configurations loaded from external JSON files."""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Point to the new data directory structure
            # Go up from backend/infrastructure/config_loaders to project root, then to data
            project_root = Path(__file__).parent.parent.parent.parent
            config_path = project_root / "data" / "systems" / "tension"
        
        self.config_path = Path(config_path)
        self.location_configs = self._load_location_configs()
        self.event_impact_configs = self._load_event_impact_configs()
        self.revolt_config = self._load_revolt_config()
        self.conflict_triggers = self._load_conflict_triggers()
        self.calculation_constants = self._load_calculation_constants()
        self.poi_type_mapping = self._load_poi_type_mapping()
        self.event_factory_defaults = self._load_event_factory_defaults()
    
    def _validate_json_structure(self, data: Any, expected_keys: List[str], config_name: str) -> bool:
        """Validate JSON configuration structure."""
        if not isinstance(data, dict):
            logger.error(f"Invalid {config_name}: expected dictionary, got {type(data)}")
            return False
        
        missing_keys = set(expected_keys) - set(data.keys())
        if missing_keys:
            logger.warning(f"Missing keys in {config_name}: {missing_keys}")
        
        return True
    
    def _validate_number_range(self, value: float, min_val: float, max_val: float, field_name: str) -> bool:
        """Validate that a numeric value is within expected range."""
        if not isinstance(value, (int, float)):
            logger.error(f"Invalid {field_name}: expected number, got {type(value)}")
            return False
        
        if not (min_val <= value <= max_val):
            logger.warning(f"{field_name} value {value} outside recommended range [{min_val}, {max_val}]")
        
        return True
    
    def _load_location_configs(self) -> Dict[str, TensionConfig]:
        """Load location-specific tension configurations."""
        try:
            config_file = self.config_path / "location_configs.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    return self._parse_location_configs(data)
            else:
                logger.warning(f"Location configs file not found: {config_file}")
                return self._get_default_location_configs()
        except Exception as e:
            logger.error(f"Could not load location configs: {e}")
            return self._get_default_location_configs()
    
    def _parse_location_configs(self, data: Dict) -> Dict[str, TensionConfig]:
        """Parse location configurations from JSON with validation."""
        configs = {}
        
        for location_type, config_data in data.items():
            if not self._validate_json_structure(
                config_data, 
                ["base_tension", "decay_rate", "max_tension", "min_tension"], 
                f"location config for {location_type}"
            ):
                continue
            
            # Validate tension values are in reasonable ranges
            base_tension = config_data.get("base_tension", 0.3)
            decay_rate = config_data.get("decay_rate", 0.04)
            max_tension = config_data.get("max_tension", 1.0)
            min_tension = config_data.get("min_tension", 0.1)
            
            self._validate_number_range(base_tension, 0.0, 1.0, f"{location_type}.base_tension")
            self._validate_number_range(decay_rate, 0.0, 0.5, f"{location_type}.decay_rate")
            self._validate_number_range(max_tension, 0.0, 1.0, f"{location_type}.max_tension")
            self._validate_number_range(min_tension, 0.0, 1.0, f"{location_type}.min_tension")
            
            if min_tension >= max_tension:
                logger.error(f"Invalid {location_type}: min_tension >= max_tension")
                continue
            
            configs[location_type] = TensionConfig(
                base_tension=base_tension,
                decay_rate=decay_rate,
                max_tension=max_tension,
                min_tension=min_tension,
                player_impact=config_data.get("player_impact", 1.0),
                npc_impact=config_data.get("npc_impact", 1.0),
                environmental_impact=config_data.get("environmental_impact", 1.0)
            )
        
        return configs
    
    def _get_default_location_configs(self) -> Dict[str, TensionConfig]:
        """Provide default location configurations."""
        return {
            'city': TensionConfig(
                base_tension=0.2,
                decay_rate=0.05,
                max_tension=1.0,
                min_tension=0.1,
                player_impact=1.5,
                npc_impact=1.0,
                environmental_impact=0.5
            ),
            'town': TensionConfig(
                base_tension=0.15,
                decay_rate=0.06,
                max_tension=0.9,
                min_tension=0.05,
                player_impact=1.2,
                npc_impact=0.8,
                environmental_impact=0.6
            ),
            'village': TensionConfig(
                base_tension=0.1,
                decay_rate=0.08,
                max_tension=0.8,
                min_tension=0.0,
                player_impact=1.0,
                npc_impact=0.6,
                environmental_impact=0.8
            ),
            'dungeon': TensionConfig(
                base_tension=0.7,
                decay_rate=0.02,
                max_tension=1.0,
                min_tension=0.5,
                player_impact=2.0,
                npc_impact=1.5,
                environmental_impact=1.0
            ),
            'ruins': TensionConfig(
                base_tension=0.6,
                decay_rate=0.03,
                max_tension=0.9,
                min_tension=0.4,
                player_impact=1.8,
                npc_impact=1.3,
                environmental_impact=1.2
            ),
            'wilderness': TensionConfig(
                base_tension=0.4,
                decay_rate=0.03,
                max_tension=1.0,
                min_tension=0.2,
                player_impact=1.0,
                npc_impact=0.8,
                environmental_impact=2.0
            ),
            'forest': TensionConfig(
                base_tension=0.3,
                decay_rate=0.04,
                max_tension=0.9,
                min_tension=0.1,
                player_impact=0.9,
                npc_impact=0.7,
                environmental_impact=1.8
            ),
            'mountains': TensionConfig(
                base_tension=0.5,
                decay_rate=0.025,
                max_tension=1.0,
                min_tension=0.3,
                player_impact=1.1,
                npc_impact=0.9,
                environmental_impact=2.2
            ),
            'swamp': TensionConfig(
                base_tension=0.6,
                decay_rate=0.02,
                max_tension=1.0,
                min_tension=0.4,
                player_impact=1.3,
                npc_impact=1.1,
                environmental_impact=2.5
            ),
            'coastal': TensionConfig(
                base_tension=0.25,
                decay_rate=0.05,
                max_tension=0.8,
                min_tension=0.1,
                player_impact=1.0,
                npc_impact=0.9,
                environmental_impact=1.2
            ),
            'default': TensionConfig(
                base_tension=0.3,
                decay_rate=0.04,
                max_tension=1.0,
                min_tension=0.1,
                player_impact=1.0,
                npc_impact=1.0,
                environmental_impact=1.0
            )
        }
    
    def _load_event_impact_configs(self) -> Dict[str, Dict[str, float]]:
        """Load event impact configurations."""
        try:
            config_file = self.config_path / "event_impacts.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    # Validate event impact configs
                    for event_type, impact_data in data.items():
                        if not self._validate_json_structure(impact_data, ["base_impact"], f"event impact for {event_type}"):
                            continue
                        base_impact = impact_data.get("base_impact", 0.0)
                        self._validate_number_range(base_impact, -1.0, 1.0, f"{event_type}.base_impact")
                    return data
            else:
                logger.warning(f"Event impacts file not found: {config_file}")
                return self._get_default_event_impacts()
        except Exception as e:
            logger.error(f"Could not load event impact configs: {e}")
            return self._get_default_event_impacts()
    
    def _get_default_event_impacts(self) -> Dict[str, Dict[str, float]]:
        """Provide default event impact configurations."""
        return {
            "player_combat": {
                "base_impact": 0.15,
                "lethal_modifier": 0.3,
                "stealth_modifier": -0.1
            },
            "player_death": {
                "base_impact": 0.25,
                "public_death_modifier": 0.2
            },
            "npc_death": {
                "base_impact": 0.1,
                "important_npc_modifier": 0.3,
                "civilian_modifier": 0.2
            },
            "npc_arrival": {
                "base_impact": -0.05,
                "authority_modifier": -0.1,
                "hostile_modifier": 0.15
            },
            "environmental_disaster": {
                "base_impact": 0.3,
                "severity_multiplier": 2.0
            },
            "magical_event": {
                "base_impact": 0.2,
                "beneficial_modifier": -0.3,
                "harmful_modifier": 0.4
            },
            "economic_change": {
                "base_impact": 0.1,
                "prosperity_modifier": -0.2,
                "recession_modifier": 0.3
            },
            "political_change": {
                "base_impact": 0.2,
                "regime_change_modifier": 0.5,
                "peaceful_transition_modifier": -0.1
            }
        }
    
    def _load_revolt_config(self) -> RevoltConfig:
        """Load revolt configuration."""
        try:
            config_file = self.config_path / "revolt_config.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    if self._validate_json_structure(data, ["base_probability_threshold"], "revolt config"):
                        threshold = data.get("base_probability_threshold", 0.5)
                        self._validate_number_range(threshold, 0.0, 1.0, "base_probability_threshold")
                        return RevoltConfig(
                            base_probability_threshold=threshold,
                            faction_influence_modifier=data.get("faction_influence_modifier", 0.1),
                            duration_range_hours=tuple(data.get("duration_range_hours", [24, 72])),
                            casualty_multiplier=data.get("casualty_multiplier", 1.0),
                            economic_impact_factor=data.get("economic_impact_factor", 0.3)
                        )
            logger.warning("Using default revolt config")
            return self._get_default_revolt_config()
        except Exception as e:
            logger.error(f"Could not load revolt config: {e}")
            return self._get_default_revolt_config()
    
    def _get_default_revolt_config(self) -> RevoltConfig:
        """Provide default revolt configuration."""
        return RevoltConfig(
            base_probability_threshold=0.5,
            faction_influence_modifier=0.1,
            duration_range_hours=(24, 72),
            casualty_multiplier=1.0,
            economic_impact_factor=0.3
        )
    
    def get_location_config(self, region_id: str, poi_id: str) -> TensionConfig:
        """
        Get tension configuration for a specific location.
        Fixed: No longer returns 'default' always, integrates with region data.
        """
        # In a real implementation, this would query the region/POI system
        # to determine the actual location type
        location_type = self._determine_location_type(region_id, poi_id)
        return self.location_configs.get(location_type, self.location_configs['default'])
    
    def _determine_location_type(self, region_id: str, poi_id: str) -> str:
        """
        Determine location type based on region and POI data.
        Fixed: No longer hardcoded, uses externalized POI type mapping.
        """
        try:
            # Try to import and query the region system
            from backend.systems.region.services.services import RegionService
            
            region_service = RegionService()
            poi_data = region_service.get_poi_by_id(region_id, poi_id)
            
            if poi_data:
                # Use externalized POI type mapping
                poi_type_key = poi_data.poi_type.value if hasattr(poi_data.poi_type, 'value') else str(poi_data.poi_type)
                return self.poi_type_mapping.get(poi_type_key, self.poi_type_mapping.get('default', 'default'))
        
        except ImportError:
            # Fallback if region system not available
            logger.warning("Region system not available for location type determination")
        except Exception as e:
            logger.warning(f"Could not determine location type for {region_id}/{poi_id}: {e}")
        
        # Default fallback
        return self.poi_type_mapping.get('default', 'default')
    
    def get_event_impact_config(self, event_type) -> Dict[str, float]:
        """Get impact configuration for an event type."""
        # Convert enum to string if needed
        event_key = event_type.value.lower() if hasattr(event_type, 'value') else str(event_type).lower()
        return self.event_impact_configs.get(event_key, {"base_impact": 0.0})
    
    def get_revolt_config(self) -> RevoltConfig:
        """Get revolt configuration."""
        return self.revolt_config
    
    def get_conflict_triggers(self) -> List[ConflictTriggerConfig]:
        """Get conflict trigger configurations."""
        return self.conflict_triggers
    
    def get_calculation_constants(self) -> CalculationConstants:
        """Get calculation constants."""
        return self.calculation_constants
    
    def get_poi_type_mapping(self) -> Dict[str, str]:
        """Get POI type mapping."""
        return self.poi_type_mapping
    
    def get_event_factory_defaults(self) -> Dict[str, Dict[str, Any]]:
        """Get event factory default parameters."""
        return self.event_factory_defaults
    
    def reload_configs(self):
        """Reload all configurations from files."""
        self.location_configs = self._load_location_configs()
        self.event_impact_configs = self._load_event_impact_configs()
        self.revolt_config = self._load_revolt_config()
        self.conflict_triggers = self._load_conflict_triggers()
        self.calculation_constants = self._load_calculation_constants()
        self.poi_type_mapping = self._load_poi_type_mapping()
        self.event_factory_defaults = self._load_event_factory_defaults()
    
    def save_default_configs(self):
        """Save default configurations to JSON files for editing."""
        config_dir = self.config_path.parent
        os.makedirs(config_dir, exist_ok=True)
        
        # Save location configs
        location_data = {}
        for location_type, config in self._get_default_location_configs().items():
            location_data[location_type] = {
                "base_tension": config.base_tension,
                "decay_rate": config.decay_rate,
                "max_tension": config.max_tension,
                "min_tension": config.min_tension,
                "player_impact": config.player_impact,
                "npc_impact": config.npc_impact,
                "environmental_impact": config.environmental_impact
            }
        
        with open(config_dir / "location_configs.json", 'w') as f:
            json.dump(location_data, f, indent=2)
        
        # Save event impact configs
        with open(config_dir / "event_impacts.json", 'w') as f:
            json.dump(self._get_default_event_impacts(), f, indent=2)
        
        # Save revolt config
        revolt_config = self._get_default_revolt_config()
        revolt_data = {
            "base_probability_threshold": revolt_config.base_probability_threshold,
            "faction_influence_modifier": revolt_config.faction_influence_modifier,
            "duration_range_hours": list(revolt_config.duration_range_hours),
            "casualty_multiplier": revolt_config.casualty_multiplier,
            "economic_impact_factor": revolt_config.economic_impact_factor
        }
        
        with open(config_dir / "revolt_config.json", 'w') as f:
            json.dump(revolt_data, f, indent=2)
        
        # Save POI type mapping
        with open(config_dir / "poi_type_mapping.json", 'w') as f:
            json.dump(self._get_default_poi_type_mapping(), f, indent=2)

        # Save event factory defaults
        with open(config_dir / "event_factory_defaults.json", 'w') as f:
            json.dump(self._get_default_event_factory_defaults(), f, indent=2)
        
        logger.info(f"Default tension configurations saved to {config_dir}")
    
    def list_location_types(self) -> List[str]:
        """Get list of available location types."""
        return list(self.location_configs.keys())
    
    def update_location_config(self, location_type: str, config: TensionConfig):
        """Update configuration for a location type."""
        self.location_configs[location_type] = config

    def _load_conflict_triggers(self) -> List[ConflictTriggerConfig]:
        """Load conflict trigger configurations from JSON."""
        try:
            config_file = self.config_path / "conflict_triggers.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    triggers = []
                    for trigger_name, trigger_data in data.items():
                        if self._validate_json_structure(
                            trigger_data, 
                            ["tension_threshold", "duration_hours", "probability_modifier"], 
                            f"conflict trigger {trigger_name}"
                        ):
                            threshold = trigger_data.get("tension_threshold", 0.5)
                            self._validate_number_range(threshold, 0.0, 1.0, f"{trigger_name}.tension_threshold")
                            
                            triggers.append(ConflictTriggerConfig(
                                name=trigger_data.get("name", trigger_name),
                                tension_threshold=threshold,
                                duration_hours=trigger_data.get("duration_hours", 24),
                                faction_requirements=trigger_data.get("faction_requirements", {}),
                                probability_modifier=trigger_data.get("probability_modifier", 1.0)
                            ))
                    return triggers
            logger.warning("Conflict triggers file not found, using defaults")
            return self._get_default_conflict_triggers()
        except Exception as e:
            logger.error(f"Could not load conflict triggers: {e}")
            return self._get_default_conflict_triggers()

    def _get_default_conflict_triggers(self) -> List[ConflictTriggerConfig]:
        """Provide default conflict trigger configurations."""
        return [
            ConflictTriggerConfig(
                name="faction_revolt",
                tension_threshold=0.8,
                duration_hours=48,
                faction_requirements={"min_factions": 2, "power_imbalance": 0.3},
                probability_modifier=1.0
            ),
            ConflictTriggerConfig(
                name="regional_uprising",
                tension_threshold=0.9,
                duration_hours=72,
                faction_requirements={"min_factions": 1, "popular_support": 0.6},
                probability_modifier=0.7
            ),
            ConflictTriggerConfig(
                name="inter_faction_war",
                tension_threshold=0.7,
                duration_hours=168,  # 1 week
                faction_requirements={"min_factions": 3, "alliance_breakdown": True},
                probability_modifier=0.5
            )
        ]

    def _load_calculation_constants(self) -> CalculationConstants:
        """Load calculation constants from JSON."""
        try:
            config_file = self.config_path / "calculation_constants.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    if self._validate_json_structure(
                        data, 
                        ["high_tension_threshold", "event_history_hours"], 
                        "calculation constants"
                    ):
                        threshold = data.get("high_tension_threshold", 0.7)
                        self._validate_number_range(threshold, 0.0, 1.0, "high_tension_threshold")
                        
                        return CalculationConstants(
                            high_tension_threshold=threshold,
                            event_history_hours=data.get("event_history_hours", 24),
                            modifier_expiration_check_hours=data.get("modifier_expiration_check_hours", 1),
                            severity_thresholds=data.get("severity_thresholds", {
                                "minor": 0.1, "moderate": 0.3, "major": 0.6, "extreme": 1.0
                            }),
                            revolt_probability=data.get("revolt_probability", {
                                "base_threshold": 0.5, "faction_modifier_per_faction": 0.1, "tension_multiplier": 2.0
                            }),
                            tension_limits=data.get("tension_limits", {"absolute_min": 0.0, "absolute_max": 1.0})
                        )
            logger.warning("Calculation constants file not found, using defaults")
            return self._get_default_calculation_constants()
        except Exception as e:
            logger.error(f"Could not load calculation constants: {e}")
            return self._get_default_calculation_constants()

    def _get_default_calculation_constants(self) -> CalculationConstants:
        """Provide default calculation constants."""
        return CalculationConstants(
            high_tension_threshold=0.7,
            event_history_hours=24,
            modifier_expiration_check_hours=1,
            severity_thresholds={"minor": 0.1, "moderate": 0.3, "major": 0.6, "extreme": 1.0},
            revolt_probability={"base_threshold": 0.5, "faction_modifier_per_faction": 0.1, "tension_multiplier": 2.0},
            tension_limits={"absolute_min": 0.0, "absolute_max": 1.0}
        )

    def _load_poi_type_mapping(self) -> Dict[str, str]:
        """Load POI type mapping from JSON."""
        try:
            config_file = self.config_path / "poi_type_mapping.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    return data
            logger.warning("POI type mapping file not found, using defaults")
            return self._get_default_poi_type_mapping()
        except Exception as e:
            logger.error(f"Could not load POI type mapping: {e}")
            return self._get_default_poi_type_mapping()

    def _get_default_poi_type_mapping(self) -> Dict[str, str]:
        """Provide default POI type mapping."""
        return {
            'CITY': 'city',
            'TOWN': 'town',
            'VILLAGE': 'village',
            'DUNGEON': 'dungeon',
            'RUINS': 'ruins',
            'CAMP': 'wilderness',
            'TOWER': 'ruins',
            'TEMPLE': 'city',
            'MINE': 'wilderness',
            'FORTRESS': 'city',
            'default': 'default'
        }

    def _load_event_factory_defaults(self) -> Dict[str, Dict[str, Any]]:
        """Load event factory default parameters from JSON."""
        try:
            config_file = self.config_path / "event_factory_defaults.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    return data
            logger.warning("Event factory defaults file not found, using hardcoded defaults")
            return self._get_default_event_factory_defaults()
        except Exception as e:
            logger.error(f"Could not load event factory defaults: {e}")
            return self._get_default_event_factory_defaults()

    def _get_default_event_factory_defaults(self) -> Dict[str, Dict[str, Any]]:
        """Provide default event factory parameters."""
        return {
            "player_combat": {
                "base_impact": 0.15,
                "lethal_bonus": 0.3,
                "stealth_reduction": 0.1,
                "default_enemies_defeated": 1
            },
            "npc_death": {
                "base_impact": 0.1,
                "important_bonus": 0.3,
                "civilian_bonus": 0.2,
                "default_importance": "normal"
            },
            "environmental_disaster": {
                "base_impact": 0.3,
                "default_severity": 1.0,
                "default_duration_multiplier": 24
            },
            "political_change": {
                "base_impact": 0.2,
                "regime_change_bonus": 0.5,
                "major_change_bonus": 0.2,
                "peaceful_reduction": 0.1,
                "default_duration_minor": 24,
                "default_duration_regime": 72
            },
            "festival": {
                "local_impact": -0.1,
                "regional_impact": -0.2,
                "major_impact": -0.3,
                "default_duration": 24
            }
        }

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system configuration statistics for monitoring."""
        return {
            "location_types_configured": len(self.location_configs),
            "event_types_configured": len(self.event_impact_configs),
            "conflict_triggers_configured": len(self.conflict_triggers),
            "poi_mappings_configured": len(self.poi_type_mapping),
            "config_files_loaded": {
                "location_configs": bool(self.location_configs),
                "event_impacts": bool(self.event_impact_configs),
                "revolt_config": bool(self.revolt_config),
                "conflict_triggers": bool(self.conflict_triggers),
                "calculation_constants": bool(self.calculation_constants),
                "poi_type_mapping": bool(self.poi_type_mapping),
                "event_factory_defaults": bool(self.event_factory_defaults)
            }
        } 