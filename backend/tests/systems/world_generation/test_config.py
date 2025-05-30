from backend.systems.shared.config import ComponentConfig
from backend.systems.shared.config import PipelineConfig
from backend.systems.shared.config import ComponentConfig
from backend.systems.shared.config import PipelineConfig
from backend.systems.shared.config import ComponentConfig
from backend.systems.shared.config import PipelineConfig
from backend.systems.shared.config import ComponentConfig
from backend.systems.shared.config import PipelineConfig
from backend.systems.shared.config import ComponentConfig
from backend.systems.shared.config import PipelineConfig
from backend.systems.shared.config import ComponentConfig
from backend.systems.shared.config import PipelineConfig
from typing import Type
"""
Tests for the world generation configuration system.
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, mock_open

from backend.systems.world_generation.config import (
    ConfigScope,
    ParameterType,
    ParameterDefinition,
    ComponentConfig,
    PhaseConfig,
    PipelineConfig,
    create_default_pipeline_config,
)


class TestConfigScope:
    """Test the ConfigScope enum."""

    def test_config_scope_values(self):
        """Test that ConfigScope has the expected values."""
        assert ConfigScope.GLOBAL.value == "global"
        assert ConfigScope.PHASE.value == "phase"
        assert ConfigScope.COMPONENT.value == "component"


class TestParameterType:
    """Test the ParameterType enum."""

    def test_parameter_type_values(self):
        """Test that ParameterType has the expected values."""
        assert ParameterType.STRING.value == "string"
        assert ParameterType.INTEGER.value == "integer"
        assert ParameterType.FLOAT.value == "float"
        assert ParameterType.BOOLEAN.value == "boolean"
        assert ParameterType.ENUM.value == "enum"
        assert ParameterType.LIST.value == "list"
        assert ParameterType.DICT.value == "dict"
        assert ParameterType.CUSTOM.value == "custom"


class TestParameterDefinition:
    """Test the ParameterDefinition class."""

    def test_parameter_definition_creation(self):
        """Test creating a parameter definition."""
        param_def = ParameterDefinition(
            name="test_param",
            type=ParameterType.STRING,
            default_value="default",
            description="A test parameter",
            required=True,
        )
        
        assert param_def.name == "test_param"
        assert param_def.type == ParameterType.STRING
        assert param_def.default_value == "default"
        assert param_def.description == "A test parameter"
        assert param_def.required is True

    def test_validate_string_parameter(self):
        """Test validating string parameters."""
        param_def = ParameterDefinition(name="test", type=ParameterType.STRING)
        
        # Valid string
        assert param_def.validate("hello") == "hello"
        
        # Invalid type
        with pytest.raises(ValueError, match="must be a string"):
            param_def.validate(123)

    def test_validate_integer_parameter(self):
        """Test validating integer parameters."""
        param_def = ParameterDefinition(
            name="test", 
            type=ParameterType.INTEGER,
            min_value=0,
            max_value=100
        )
        
        # Valid integer
        assert param_def.validate(50) == 50
        
        # Invalid type (bool is subclass of int but should be rejected)
        with pytest.raises(ValueError, match="must be an integer"):
            param_def.validate(True)
            
        # Invalid type (float)
        with pytest.raises(ValueError, match="must be an integer"):
            param_def.validate(50.5)
            
        # Below minimum
        with pytest.raises(ValueError, match="must be >= 0"):
            param_def.validate(-1)
            
        # Above maximum
        with pytest.raises(ValueError, match="must be <= 100"):
            param_def.validate(101)

    def test_validate_float_parameter(self):
        """Test validating float parameters."""
        param_def = ParameterDefinition(
            name="test",
            type=ParameterType.FLOAT,
            min_value=0.0,
            max_value=1.0
        )
        
        # Valid float
        assert param_def.validate(0.5) == 0.5
        
        # Valid integer (should be accepted for float)
        assert param_def.validate(1) == 1
        
        # Invalid type (bool)
        with pytest.raises(ValueError, match="must be a number"):
            param_def.validate(True)
            
        # Below minimum
        with pytest.raises(ValueError, match="must be >= 0.0"):
            param_def.validate(-0.1)
            
        # Above maximum
        with pytest.raises(ValueError, match="must be <= 1.0"):
            param_def.validate(1.1)

    def test_validate_boolean_parameter(self):
        """Test validating boolean parameters."""
        param_def = ParameterDefinition(name="test", type=ParameterType.BOOLEAN)
        
        # Valid boolean
        assert param_def.validate(True) is True
        assert param_def.validate(False) is False
        
        # Invalid type
        with pytest.raises(ValueError, match="must be a boolean"):
            param_def.validate("true")

    def test_validate_enum_parameter(self):
        """Test validating enum parameters."""
        param_def = ParameterDefinition(
            name="test",
            type=ParameterType.ENUM,
            allowed_values=["option1", "option2", "option3"]
        )
        
        # Valid enum value
        assert param_def.validate("option1") == "option1"
        
        # Invalid enum value
        with pytest.raises(ValueError, match="must be one of: option1, option2, option3"): pass
            param_def.validate("invalid_option")

    def test_validate_list_parameter(self):
        """Test validating list parameters."""
        param_def = ParameterDefinition(
            name="test",
            type=ParameterType.LIST,
            list_item_type=ParameterType.INTEGER,
            min_value=0,
            max_value=10
        )
        
        # Valid list
        assert param_def.validate([1, 2, 3]) == [1, 2, 3]
        
        # Invalid type
        with pytest.raises(ValueError, match="must be a list"):
            param_def.validate("not a list")
            
        # Invalid list item
        with pytest.raises(ValueError, match="must be an integer"):
            param_def.validate([1, "invalid", 3])

    def test_validate_dict_parameter(self):
        """Test validating dict parameters."""
        param_def = ParameterDefinition(name="test", type=ParameterType.DICT)
        
        # Valid dict
        test_dict = {"key": "value"}
        assert param_def.validate(test_dict) == test_dict
        
        # Invalid type
        with pytest.raises(ValueError, match="must be a dictionary"):
            param_def.validate("not a dict")

    def test_validate_custom_parameter(self):
        """Test validating custom parameters."""
        def custom_validator(value):
            if not isinstance(value, str) or len(value) < 3:
                raise ValueError("Must be a string with at least 3 characters")
            return value.upper()
        
        param_def = ParameterDefinition(
            name="test",
            type=ParameterType.CUSTOM,
            custom_validator=custom_validator
        )
        
        # Valid custom value
        assert param_def.validate("hello") == "HELLO"
        
        # Invalid custom value
        with pytest.raises(ValueError, match="failed custom validation"):
            param_def.validate("hi")

    def test_validate_required_parameter(self):
        """Test validating required parameters."""
        param_def = ParameterDefinition(
            name="test",
            type=ParameterType.STRING,
            required=True
        )
        
        # Missing required parameter
        with pytest.raises(ValueError, match="is required but missing"):
            param_def.validate(None)

    def test_validate_optional_parameter_with_default(self):
        """Test validating optional parameters with defaults."""
        param_def = ParameterDefinition(
            name="test",
            type=ParameterType.STRING,
            default_value="default_value",
            required=False
        )
        
        # Missing optional parameter should return default
        assert param_def.validate(None) == "default_value"


class TestComponentConfig:
    """Test the ComponentConfig class."""

    def test_component_config_creation(self):
        """Test creating a component configuration."""
        config = ComponentConfig(
            component_name="test_component",
            enabled=True,
            parameters={"param1": "value1"}
        )
        
        assert config.component_name == "test_component"
        assert config.enabled is True
        assert config.parameters == {"param1": "value1"}

    def test_component_config_to_dict(self):
        """Test converting component config to dictionary."""
        config = ComponentConfig(
            component_name="test_component",
            enabled=False,
            parameters={"param1": "value1", "param2": 42}
        )
        
        expected = {
            "component_name": "test_component",
            "enabled": False,
            "parameters": {"param1": "value1", "param2": 42}
        }
        
        assert config.to_dict() == expected

    def test_component_config_from_dict(self):
        """Test creating component config from dictionary."""
        data = {
            "component_name": "test_component",
            "enabled": False,
            "parameters": {"param1": "value1"}
        }
        
        config = ComponentConfig.from_dict(data)
        
        assert config.component_name == "test_component"
        assert config.enabled is False
        assert config.parameters == {"param1": "value1"}

    def test_component_config_from_dict_defaults(self):
        """Test creating component config from dictionary with defaults."""
        data = {"component_name": "test_component"}
        
        config = ComponentConfig.from_dict(data)
        
        assert config.component_name == "test_component"
        assert config.enabled is True  # Default
        assert config.parameters == {}  # Default


class TestPhaseConfig:
    """Test the PhaseConfig class."""

    def test_phase_config_creation(self):
        """Test creating a phase configuration."""
        component = ComponentConfig("test_component")
        config = PhaseConfig(
            phase_name="test_phase",
            enabled=True,
            components=[component],
            parameters={"param1": "value1"}
        )
        
        assert config.phase_name == "test_phase"
        assert config.enabled is True
        assert len(config.components) == 1
        assert config.components[0] == component
        assert config.parameters == {"param1": "value1"}

    def test_phase_config_to_dict(self):
        """Test converting phase config to dictionary."""
        component = ComponentConfig("test_component", enabled=False)
        config = PhaseConfig(
            phase_name="test_phase",
            enabled=False,
            components=[component],
            parameters={"param1": "value1"}
        )
        
        result = config.to_dict()
        
        assert result["phase_name"] == "test_phase"
        assert result["enabled"] is False
        assert len(result["components"]) == 1
        assert result["components"][0]["component_name"] == "test_component"
        assert result["parameters"] == {"param1": "value1"}

    def test_phase_config_from_dict(self):
        """Test creating phase config from dictionary."""
        data = {
            "phase_name": "test_phase",
            "enabled": False,
            "components": [
                {"component_name": "comp1", "enabled": True},
                {"component_name": "comp2", "enabled": False}
            ],
            "parameters": {"param1": "value1"}
        }
        
        config = PhaseConfig.from_dict(data)
        
        assert config.phase_name == "test_phase"
        assert config.enabled is False
        assert len(config.components) == 2
        assert config.components[0].component_name == "comp1"
        assert config.components[1].component_name == "comp2"
        assert config.parameters == {"param1": "value1"}

    def test_add_component(self):
        """Test adding a component to phase config."""
        config = PhaseConfig("test_phase")
        component = ComponentConfig("test_component")
        
        config.add_component(component)
        
        assert len(config.components) == 1
        assert config.components[0] == component

    def test_add_component_replace_existing(self):
        """Test adding a component that replaces an existing one."""
        config = PhaseConfig("test_phase")
        component1 = ComponentConfig("test_component", enabled=True)
        component2 = ComponentConfig("test_component", enabled=False)
        
        config.add_component(component1)
        config.add_component(component2)  # Should replace component1
        
        assert len(config.components) == 1
        assert config.components[0].enabled is False

    def test_get_component(self):
        """Test getting a component from phase config."""
        component = ComponentConfig("test_component")
        config = PhaseConfig("test_phase", components=[component])
        
        result = config.get_component("test_component")
        assert result == component
        
        result = config.get_component("nonexistent")
        assert result is None

    def test_remove_component(self):
        """Test removing a component from phase config."""
        component = ComponentConfig("test_component")
        config = PhaseConfig("test_phase", components=[component])
        
        # Remove existing component
        result = config.remove_component("test_component")
        assert result is True
        assert len(config.components) == 0
        
        # Try to remove nonexistent component
        result = config.remove_component("nonexistent")
        assert result is False


class TestPipelineConfig:
    """Test the PipelineConfig class."""

    def test_pipeline_config_creation(self):
        """Test creating a pipeline configuration."""
        config = PipelineConfig()
        
        assert config.global_parameters == {}
        assert config.phases == {}  # phases is a dict, not a list
        assert config.parameter_definitions == {}

    def test_pipeline_config_with_seed_data(self):
        """Test creating pipeline config with seed data."""
        seed_data = {
            "generation": {
                "pipeline": {
                    "global_parameters": {
                        "size": "medium",
                        "difficulty": "normal"
                    }
                }
            }
        }
        
        config = PipelineConfig(seed_data)
        
        # Should have extracted some global parameters
        assert "size" in config.global_parameters
        assert "difficulty" in config.global_parameters

    def test_add_parameter_definition(self):
        """Test adding parameter definitions."""
        config = PipelineConfig()
        param_def = ParameterDefinition("test_param", ParameterType.STRING)
        
        config.add_parameter_definition(param_def)
        
        assert "test_param" in config.parameter_definitions
        assert config.parameter_definitions["test_param"] == param_def

    def test_set_global_parameter(self):
        """Test setting global parameters."""
        config = PipelineConfig()
        
        config.set_global_parameter("test_param", "test_value")
        
        assert config.global_parameters["test_param"] == "test_value"

    def test_set_global_parameter_with_validation(self):
        """Test setting global parameters with validation."""
        config = PipelineConfig()
        param_def = ParameterDefinition(
            "test_param", 
            ParameterType.INTEGER,
            min_value=0,
            max_value=100
        )
        config.add_parameter_definition(param_def)
        
        # Valid value
        config.set_global_parameter("test_param", 50)
        assert config.global_parameters["test_param"] == 50
        
        # Invalid value
        with pytest.raises(ValueError):
            config.set_global_parameter("test_param", 150)

    def test_get_global_parameter(self):
        """Test getting global parameters."""
        config = PipelineConfig()
        config.global_parameters["test_param"] = "test_value"
        
        assert config.get_global_parameter("test_param") == "test_value"
        assert config.get_global_parameter("nonexistent", "default") == "default"

    def test_add_phase(self):
        """Test adding phases."""
        config = PipelineConfig()
        phase = PhaseConfig("test_phase")
        
        config.add_phase(phase)
        
        assert len(config.phases) == 1
        assert config.phases["test_phase"] == phase

    def test_add_phase_replace_existing(self):
        """Test adding a phase that replaces an existing one."""
        config = PipelineConfig()
        phase1 = PhaseConfig("test_phase", enabled=True)
        phase2 = PhaseConfig("test_phase", enabled=False)
        
        config.add_phase(phase1)
        config.add_phase(phase2)  # Should replace phase1
        
        assert len(config.phases) == 1
        assert config.phases["test_phase"].enabled is False

    def test_get_phase(self):
        """Test getting phases."""
        config = PipelineConfig()
        phase = PhaseConfig("test_phase")
        config.add_phase(phase)
        
        result = config.get_phase("test_phase")
        assert result == phase
        
        result = config.get_phase("nonexistent")
        assert result is None

    def test_remove_phase(self):
        """Test removing phases."""
        config = PipelineConfig()
        phase = PhaseConfig("test_phase")
        config.add_phase(phase)
        
        # Remove existing phase
        result = config.remove_phase("test_phase")
        assert result is True
        assert len(config.phases) == 0
        
        # Try to remove nonexistent phase
        result = config.remove_phase("nonexistent")
        assert result is False

    def test_set_component_parameter(self):
        """Test setting component parameters."""
        config = PipelineConfig()
        phase = PhaseConfig("test_phase")
        component = ComponentConfig("test_component")
        phase.add_component(component)
        config.add_phase(phase)
        
        config.set_component_parameter("test_phase", "test_component", "param1", "value1")
        
        result_component = config.get_phase("test_phase").get_component("test_component")
        assert result_component.parameters["param1"] == "value1"

    def test_set_component_parameter_nonexistent_phase(self):
        """Test setting component parameter for nonexistent phase."""
        config = PipelineConfig()
        
        with pytest.raises(ValueError, match="Phase 'nonexistent' not found"):
            config.set_component_parameter("nonexistent", "comp", "param", "value")

    def test_set_component_parameter_nonexistent_component(self):
        """Test setting component parameter for nonexistent component."""
        config = PipelineConfig()
        phase = PhaseConfig("test_phase")
        config.add_phase(phase)
        
        with pytest.raises(ValueError, match="Component 'nonexistent' not found"):
            config.set_component_parameter("test_phase", "nonexistent", "param", "value")

    def test_get_component_parameter(self):
        """Test getting component parameters."""
        config = PipelineConfig()
        phase = PhaseConfig("test_phase")
        component = ComponentConfig("test_component", parameters={"param1": "value1"})
        phase.add_component(component)
        config.add_phase(phase)
        
        result = config.get_component_parameter("test_phase", "test_component", "param1")
        assert result == "value1"
        
        result = config.get_component_parameter("test_phase", "test_component", "nonexistent", "default")
        assert result == "default"

    def test_get_component_parameter_nonexistent_phase(self):
        """Test getting component parameter for nonexistent phase."""
        config = PipelineConfig()
        
        with pytest.raises(ValueError, match="Phase 'nonexistent' not found"):
            config.get_component_parameter("nonexistent", "comp", "param", "default")

    def test_get_component_parameter_nonexistent_component(self):
        """Test getting component parameter for nonexistent component."""
        config = PipelineConfig()
        phase = PhaseConfig("test_phase")
        config.add_phase(phase)
        
        with pytest.raises(ValueError, match="Component 'nonexistent' not found"):
            config.get_component_parameter("test_phase", "nonexistent", "param", "default")

    def test_enable_phase(self):
        """Test enabling/disabling phases."""
        config = PipelineConfig()
        phase = PhaseConfig("test_phase", enabled=False)
        config.add_phase(phase)
        
        config.enable_phase("test_phase", True)
        assert config.get_phase("test_phase").enabled is True
        
        config.enable_phase("test_phase", False)
        assert config.get_phase("test_phase").enabled is False

    def test_enable_phase_nonexistent(self):
        """Test enabling nonexistent phase."""
        config = PipelineConfig()
        
        with pytest.raises(ValueError, match="Phase 'nonexistent' not found"):
            config.enable_phase("nonexistent", True)

    def test_enable_component(self):
        """Test enabling/disabling components."""
        config = PipelineConfig()
        phase = PhaseConfig("test_phase")
        component = ComponentConfig("test_component", enabled=False)
        phase.add_component(component)
        config.add_phase(phase)
        
        config.enable_component("test_phase", "test_component", True)
        result_component = config.get_phase("test_phase").get_component("test_component")
        assert result_component.enabled is True

    def test_enable_component_nonexistent_phase(self):
        """Test enabling component in nonexistent phase."""
        config = PipelineConfig()
        
        with pytest.raises(ValueError, match="Phase 'nonexistent' not found"):
            config.enable_component("nonexistent", "comp", True)

    def test_enable_component_nonexistent_component(self):
        """Test enabling nonexistent component."""
        config = PipelineConfig()
        phase = PhaseConfig("test_phase")
        config.add_phase(phase)
        
        with pytest.raises(ValueError, match="Component 'nonexistent' not found"):
            config.enable_component("test_phase", "nonexistent", True)

    def test_is_phase_enabled(self):
        """Test checking if phase is enabled."""
        config = PipelineConfig()
        phase = PhaseConfig("test_phase", enabled=True)
        config.add_phase(phase)
        
        assert config.is_phase_enabled("test_phase") is True
        assert config.is_phase_enabled("nonexistent") is False

    def test_is_component_enabled(self):
        """Test checking if component is enabled."""
        config = PipelineConfig()
        phase = PhaseConfig("test_phase")
        component = ComponentConfig("test_component", enabled=True)
        phase.add_component(component)
        config.add_phase(phase)
        
        assert config.is_component_enabled("test_phase", "test_component") is True
        assert config.is_component_enabled("nonexistent", "test_component") is False
        assert config.is_component_enabled("test_phase", "nonexistent") is False

    def test_to_dict(self):
        """Test converting pipeline config to dictionary."""
        config = PipelineConfig()
        config.global_parameters = {"param1": "value1"}
        phase = PhaseConfig("test_phase")
        config.add_phase(phase)
        
        result = config.to_dict()
        
        assert "global_parameters" in result
        assert "phases" in result
        assert result["global_parameters"] == {"param1": "value1"}
        assert len(result["phases"]) == 1

    def test_from_dict(self):
        """Test creating pipeline config from dictionary."""
        data = {
            "global_parameters": {"param1": "value1"},
            "phases": {
                "test_phase": {
                    "enabled": True,
                    "components": [],
                    "parameters": {}
                }
            }
        }
        
        config = PipelineConfig.from_dict(data)
        
        assert config.global_parameters == {"param1": "value1"}
        assert len(config.phases) == 1
        assert config.phases["test_phase"].phase_name == "test_phase"

    def test_save_to_file(self):
        """Test saving pipeline config to file."""
        config = PipelineConfig()
        config.global_parameters = {"param1": "value1"}
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            config.save_to_file(temp_file)
            
            # Verify file was created and contains expected data
            with open(temp_file, 'r') as f:
                data = json.load(f)
            
            assert "global_parameters" in data
            assert data["global_parameters"] == {"param1": "value1"}
        finally: pass
            os.unlink(temp_file)

    def test_load_from_file(self):
        """Test loading pipeline config from file."""
        data = {
            "global_parameters": {"param1": "value1"},
            "phases": {}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(data, f)
            temp_file = f.name
        
        try:
            config = PipelineConfig.load_from_file(temp_file)
            
            assert config.global_parameters == {"param1": "value1"}
            assert len(config.phases) == 0
        finally: pass
            os.unlink(temp_file)

    def test_load_from_file_not_found(self):
        """Test loading pipeline config from nonexistent file."""
        with pytest.raises(FileNotFoundError):
            PipelineConfig.load_from_file("nonexistent.json")

    def test_validate(self):
        """Test validating pipeline configuration."""
        config = PipelineConfig()
        # Add at least one enabled phase with enabled components to pass validation
        phase = PhaseConfig("test_phase", enabled=True)
        component = ComponentConfig("test_component", enabled=True)
        phase.add_component(component)
        config.add_phase(phase)
        
        # Valid configuration should return empty list
        errors = config.validate()
        assert errors == []

    def test_validate_with_errors(self):
        """Test validating pipeline configuration with errors."""
        config = PipelineConfig()
        
        # Add parameter definition with validation
        param_def = ParameterDefinition(
            "test_param",
            ParameterType.INTEGER,
            min_value=0,
            max_value=100,
            required=True
        )
        config.add_parameter_definition(param_def)
        
        # Set invalid value
        config.global_parameters["test_param"] = 150  # Above max
        
        errors = config.validate()
        assert len(errors) > 0
        assert any("must be <= 100" in error for error in errors)

    def test_clone(self):
        """Test cloning pipeline configuration."""
        config = PipelineConfig()
        config.global_parameters = {"param1": "value1"}
        phase = PhaseConfig("test_phase")
        config.add_phase(phase)
        
        cloned = config.clone()
        
        assert cloned.global_parameters == config.global_parameters
        assert len(cloned.phases) == len(config.phases)
        assert cloned.phases["test_phase"].phase_name == config.phases["test_phase"].phase_name
        
        # Verify it's a deep copy by checking that they are different objects
        assert cloned.global_parameters is not config.global_parameters
        assert cloned.phases is not config.phases

    def test_merge(self):
        """Test merging pipeline configurations."""
        config1 = PipelineConfig()
        config1.global_parameters = {"param1": "value1"}
        phase1 = PhaseConfig("phase1")
        config1.add_phase(phase1)
        
        config2 = PipelineConfig()
        config2.global_parameters = {"param2": "value2"}
        phase2 = PhaseConfig("phase2")
        config2.add_phase(phase2)
        
        merged = config1.merge(config2)
        
        assert "param1" in merged.global_parameters
        assert "param2" in merged.global_parameters
        assert len(merged.phases) == 2


class TestCreateDefaultPipelineConfig:
    """Test the create_default_pipeline_config function."""

    def test_create_default_pipeline_config(self):
        """Test creating default pipeline configuration."""
        config = create_default_pipeline_config()
        
        assert isinstance(config, PipelineConfig)
        assert len(config.phases) > 0  # Should have some default phases
        
        # Check for expected phases (based on actual implementation)
        phase_names = list(config.phases.keys())
        expected_phases = ["elevation", "biome_placement", "coastline_smoothing"]
        
        for expected_phase in expected_phases:
            assert expected_phase in phase_names 