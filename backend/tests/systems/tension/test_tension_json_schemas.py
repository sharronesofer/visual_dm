"""
Tests for Tension System JSON Configuration Schemas

Tests that JSON configurations are properly structured and aligned
with the code expectations according to Development Bible standards.
"""

import pytest
import json
import os
from pathlib import Path
from typing import Dict, Any

from backend.systems.tension.models.tension_events import TensionEventType


class TestTensionJSONSchemas:
    """Test class for tension JSON configuration validation"""

    @pytest.fixture
    def tension_config_path(self):
        """Get path to tension configuration directory"""
        return Path(__file__).parent.parent.parent.parent / "data" / "systems" / "tension"

    @pytest.fixture
    def location_configs(self, tension_config_path):
        """Load location configurations JSON"""
        with open(tension_config_path / "location_configs.json", 'r') as f:
            return json.load(f)

    @pytest.fixture
    def event_impacts(self, tension_config_path):
        """Load event impacts JSON"""
        with open(tension_config_path / "event_impacts.json", 'r') as f:
            return json.load(f)

    @pytest.fixture
    def conflict_triggers(self, tension_config_path):
        """Load conflict triggers JSON"""
        with open(tension_config_path / "conflict_triggers.json", 'r') as f:
            return json.load(f)

    @pytest.fixture
    def calculation_constants(self, tension_config_path):
        """Load calculation constants JSON"""
        with open(tension_config_path / "calculation_constants.json", 'r') as f:
            return json.load(f)

    @pytest.fixture
    def revolt_config(self, tension_config_path):
        """Load revolt configuration JSON"""
        with open(tension_config_path / "revolt_config.json", 'r') as f:
            return json.load(f)

    @pytest.fixture
    def poi_type_mapping(self, tension_config_path):
        """Load POI type mapping JSON"""
        with open(tension_config_path / "poi_type_mapping.json", 'r') as f:
            return json.load(f)

    @pytest.fixture
    def event_factory_defaults(self, tension_config_path):
        """Load event factory defaults JSON"""
        with open(tension_config_path / "event_factory_defaults.json", 'r') as f:
            return json.load(f)

    def test_location_configs_structure(self, location_configs):
        """Test location_configs.json has correct structure matching TensionConfig"""
        # Should have default configuration
        assert "default" in location_configs
        
        # Each location should have required fields matching TensionConfig dataclass
        required_fields = [
            "base_tension", "decay_rate", "max_tension", "min_tension",
            "player_impact", "npc_impact", "environmental_impact"
        ]
        
        for location_type, config in location_configs.items():
            for field in required_fields:
                assert field in config, f"Missing {field} in {location_type} config"
                assert isinstance(config[field], (int, float)), f"{field} should be numeric in {location_type}"

    def test_location_configs_value_ranges(self, location_configs):
        """Test location configurations have sensible value ranges"""
        for location_type, config in location_configs.items():
            # Tension values should be between 0.0 and 1.0
            assert 0.0 <= config["base_tension"] <= 1.0, f"Invalid base_tension in {location_type}"
            assert 0.0 <= config["max_tension"] <= 1.0, f"Invalid max_tension in {location_type}"
            assert 0.0 <= config["min_tension"] <= 1.0, f"Invalid min_tension in {location_type}"
            
            # Min should be less than or equal to base, base should be less than or equal to max
            assert config["min_tension"] <= config["base_tension"], f"min_tension > base_tension in {location_type}"
            assert config["base_tension"] <= config["max_tension"], f"base_tension > max_tension in {location_type}"
            
            # Decay rate should be positive
            assert config["decay_rate"] > 0.0, f"Invalid decay_rate in {location_type}"
            
            # Impact multipliers should be positive
            assert config["player_impact"] > 0.0, f"Invalid player_impact in {location_type}"
            assert config["npc_impact"] > 0.0, f"Invalid npc_impact in {location_type}"
            assert config["environmental_impact"] > 0.0, f"Invalid environmental_impact in {location_type}"

    def test_event_impacts_structure(self, event_impacts):
        """Test event_impacts.json has correct structure"""
        # Should have configurations for core event types
        expected_events = [
            "player_combat", "player_death", "npc_death", "npc_arrival",
            "environmental_disaster", "magical_event", "economic_change", "political_change"
        ]
        
        for event_type in expected_events:
            assert event_type in event_impacts, f"Missing config for {event_type}"
            
            # Each event should have base_impact
            assert "base_impact" in event_impacts[event_type], f"Missing base_impact for {event_type}"
            assert isinstance(event_impacts[event_type]["base_impact"], (int, float)), f"base_impact should be numeric for {event_type}"

    def test_event_impacts_align_with_enum(self, event_impacts):
        """Test event impacts align with TensionEventType enum values"""
        # Get all enum values (convert to lowercase for comparison)
        enum_values = {event_type.value.lower() for event_type in TensionEventType}
        
        # Core events should be present and match enum structure
        core_mappings = {
            "player_combat": "player_combat",
            "npc_death": "npc_death",
            "environmental_disaster": "environmental_disaster",
            "political_change": "political_change"
        }
        
        for json_key, enum_key in core_mappings.items():
            assert json_key in event_impacts, f"Missing {json_key} in event_impacts.json"
            # Verify enum exists (this validates our TensionEventType enum is complete)
            assert enum_key in enum_values, f"TensionEventType missing {enum_key}"

    def test_conflict_triggers_structure(self, conflict_triggers):
        """Test conflict_triggers.json has correct structure matching ConflictTrigger"""
        required_fields = ["name", "tension_threshold", "duration_hours", "faction_requirements", "probability_modifier"]
        
        for trigger_name, trigger_config in conflict_triggers.items():
            for field in required_fields:
                assert field in trigger_config, f"Missing {field} in {trigger_name} trigger"
            
            # Validate specific field types
            assert isinstance(trigger_config["tension_threshold"], (int, float)), f"tension_threshold should be numeric in {trigger_name}"
            assert isinstance(trigger_config["duration_hours"], int), f"duration_hours should be integer in {trigger_name}"
            assert isinstance(trigger_config["faction_requirements"], dict), f"faction_requirements should be dict in {trigger_name}"
            assert isinstance(trigger_config["probability_modifier"], (int, float)), f"probability_modifier should be numeric in {trigger_name}"

    def test_conflict_triggers_value_ranges(self, conflict_triggers):
        """Test conflict triggers have sensible value ranges"""
        for trigger_name, trigger_config in conflict_triggers.items():
            # Tension threshold should be between 0.0 and 1.0
            assert 0.0 <= trigger_config["tension_threshold"] <= 1.0, f"Invalid tension_threshold in {trigger_name}"
            
            # Duration should be positive
            assert trigger_config["duration_hours"] > 0, f"Invalid duration_hours in {trigger_name}"
            
            # Probability modifier should be positive
            assert trigger_config["probability_modifier"] > 0.0, f"Invalid probability_modifier in {trigger_name}"

    def test_calculation_constants_structure(self, calculation_constants):
        """Test calculation_constants.json has correct structure matching CalculationConstants"""
        required_fields = [
            "high_tension_threshold", "event_history_hours", "modifier_expiration_check_hours",
            "severity_thresholds", "revolt_probability", "tension_limits"
        ]
        
        for field in required_fields:
            assert field in calculation_constants, f"Missing {field} in calculation_constants.json"

    def test_calculation_constants_severity_thresholds(self, calculation_constants):
        """Test severity thresholds are properly ordered"""
        thresholds = calculation_constants["severity_thresholds"]
        
        # Should have all severity levels
        expected_levels = ["minor", "moderate", "major", "extreme"]
        for level in expected_levels:
            assert level in thresholds, f"Missing {level} in severity_thresholds"
        
        # Should be in ascending order
        assert thresholds["minor"] < thresholds["moderate"], "Severity thresholds not properly ordered"
        assert thresholds["moderate"] < thresholds["major"], "Severity thresholds not properly ordered"
        assert thresholds["major"] < thresholds["extreme"], "Severity thresholds not properly ordered"

    def test_revolt_config_structure(self, revolt_config):
        """Test revolt_config.json has correct structure matching RevoltConfig"""
        required_fields = [
            "base_probability_threshold", "faction_influence_modifier",
            "duration_range_hours", "casualty_multiplier", "economic_impact_factor"
        ]
        
        for field in required_fields:
            assert field in revolt_config, f"Missing {field} in revolt_config.json"

    def test_revolt_config_duration_range(self, revolt_config):
        """Test revolt duration range is properly formatted"""
        duration_range = revolt_config["duration_range_hours"]
        
        # Should be an array/list with exactly 2 elements
        assert isinstance(duration_range, list), "duration_range_hours should be a list"
        assert len(duration_range) == 2, "duration_range_hours should have exactly 2 elements"
        
        # Both elements should be positive integers
        assert isinstance(duration_range[0], int), "duration_range min should be integer"
        assert isinstance(duration_range[1], int), "duration_range max should be integer"
        assert duration_range[0] > 0, "duration_range min should be positive"
        assert duration_range[1] > 0, "duration_range max should be positive"
        assert duration_range[0] <= duration_range[1], "duration_range min should be <= max"

    def test_poi_type_mapping_completeness(self, poi_type_mapping, location_configs):
        """Test POI type mapping covers all location types"""
        # All mapped location types should exist in location_configs
        for poi_type, location_type in poi_type_mapping.items():
            if poi_type != "default":  # Skip the default fallback
                assert location_type in location_configs, f"POI maps to unknown location type: {location_type}"

    def test_event_factory_defaults_structure(self, event_factory_defaults):
        """Test event factory defaults have correct structure"""
        # Should have configurations for major event types
        expected_factories = ["player_combat", "npc_death", "environmental_disaster", "political_change", "festival"]
        
        for factory_type in expected_factories:
            assert factory_type in event_factory_defaults, f"Missing factory config for {factory_type}"
            
            # Each factory should have base_impact
            config = event_factory_defaults[factory_type]
            assert "base_impact" in config or factory_type == "festival", f"Missing base_impact for {factory_type}"

    def test_json_files_exist(self, tension_config_path):
        """Test all required JSON files exist"""
        required_files = [
            "location_configs.json",
            "event_impacts.json", 
            "conflict_triggers.json",
            "calculation_constants.json",
            "revolt_config.json",
            "poi_type_mapping.json",
            "event_factory_defaults.json"
        ]
        
        for filename in required_files:
            file_path = tension_config_path / filename
            assert file_path.exists(), f"Missing required configuration file: {filename}"
            assert file_path.is_file(), f"Configuration path is not a file: {filename}"

    def test_json_files_valid_format(self, tension_config_path):
        """Test all JSON files are valid JSON format"""
        json_files = [
            "location_configs.json",
            "event_impacts.json", 
            "conflict_triggers.json",
            "calculation_constants.json",
            "revolt_config.json",
            "poi_type_mapping.json",
            "event_factory_defaults.json"
        ]
        
        for filename in json_files:
            file_path = tension_config_path / filename
            try:
                with open(file_path, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON in {filename}: {e}")

    def test_configuration_consistency(self, location_configs, poi_type_mapping):
        """Test configuration consistency across files"""
        # POI mappings should reference valid location configs
        for poi_type, location_type in poi_type_mapping.items():
            assert location_type in location_configs, f"POI {poi_type} maps to non-existent location {location_type}"
        
        # Default location should exist
        assert "default" in location_configs, "Missing default location configuration"

    def test_numeric_value_consistency(self, calculation_constants, location_configs):
        """Test numeric values are consistent across configurations"""
        # High tension threshold should be within valid tension range
        high_threshold = calculation_constants["high_tension_threshold"]
        assert 0.0 <= high_threshold <= 1.0, "high_tension_threshold outside valid range"
        
        # Should be achievable by some location types
        max_base_tension = max(config["base_tension"] for config in location_configs.values())
        assert high_threshold <= max_base_tension + 0.5, "high_tension_threshold may be unreachable"


class TestTensionJSONValidation:
    """Test validation logic for tension JSON configurations"""

    def test_location_config_field_validation(self):
        """Test validation of location configuration fields"""
        # Valid configuration
        valid_config = {
            "base_tension": 0.2,
            "decay_rate": 0.05,
            "max_tension": 1.0,
            "min_tension": 0.1,
            "player_impact": 1.5,
            "npc_impact": 1.0,
            "environmental_impact": 0.5
        }
        
        # This should pass validation (no exception)
        self._validate_location_config(valid_config)
        
        # Invalid configurations should fail
        invalid_configs = [
            # Missing required field
            {k: v for k, v in valid_config.items() if k != "base_tension"},
            # Invalid tension range
            {**valid_config, "base_tension": 1.5},
            # Min > Max
            {**valid_config, "min_tension": 0.8, "max_tension": 0.6},
            # Negative decay rate
            {**valid_config, "decay_rate": -0.1}
        ]
        
        for invalid_config in invalid_configs:
            with pytest.raises((ValueError, KeyError, AssertionError)):
                self._validate_location_config(invalid_config)

    def _validate_location_config(self, config: Dict[str, Any]) -> None:
        """Helper method to validate location configuration"""
        required_fields = [
            "base_tension", "decay_rate", "max_tension", "min_tension",
            "player_impact", "npc_impact", "environmental_impact"
        ]
        
        # Check required fields exist
        for field in required_fields:
            if field not in config:
                raise KeyError(f"Missing required field: {field}")
        
        # Check value ranges
        if not (0.0 <= config["base_tension"] <= 1.0):
            raise ValueError("base_tension must be between 0.0 and 1.0")
        
        if not (0.0 <= config["max_tension"] <= 1.0):
            raise ValueError("max_tension must be between 0.0 and 1.0")
        
        if not (0.0 <= config["min_tension"] <= 1.0):
            raise ValueError("min_tension must be between 0.0 and 1.0")
        
        if config["min_tension"] > config["base_tension"]:
            raise ValueError("min_tension cannot be greater than base_tension")
        
        if config["base_tension"] > config["max_tension"]:
            raise ValueError("base_tension cannot be greater than max_tension")
        
        if config["decay_rate"] <= 0.0:
            raise ValueError("decay_rate must be positive")
        
        # Check impact multipliers are positive
        for impact_field in ["player_impact", "npc_impact", "environmental_impact"]:
            if config[impact_field] <= 0.0:
                raise ValueError(f"{impact_field} must be positive") 