from backend.systems.shared.config import PipelineConfig
from backend.systems.economy.models import Resource
from backend.systems.shared.config import PipelineConfig
from backend.systems.economy.models import Resource
from backend.systems.shared.config import PipelineConfig
from backend.systems.economy.models import Resource
from backend.systems.shared.config import PipelineConfig
from backend.systems.economy.models import Resource
from backend.systems.shared.config import PipelineConfig
from backend.systems.economy.models import Resource
from backend.systems.shared.config import PipelineConfig
from backend.systems.economy.models import Resource
from typing import Type
"""
Tests for world generation components.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import time

from backend.systems.world_generation.components import (
    ComponentRegistry,
    GenerationComponent,
    ComponentResult,
    WorldGenerationContext,
    ComponentType,
    ComponentPriority,
    BiomeGenerationComponent,
    ElevationGenerationComponent,
    RiverGenerationComponent,
    ResourceGenerationComponent,
    CoastlineGenerationComponent,
    ClimateGenerationComponent,
    UtilityComponent,
    BiomeAdjacencyComponent,
    CoastlineSmoothingComponent,
    ElevationGeneratorComponent,
    RiverGeneratorComponent,
    ResourceGeneratorComponent,
)
from backend.systems.world_generation.models import WorldSeed, World
from backend.systems.world_generation.config import PipelineConfig


class TestComponentRegistry: pass
    """Test the ComponentRegistry class."""

    @pytest.fixture
    def registry(self): pass
        """Create a fresh component registry for each test."""
        return ComponentRegistry()

    @pytest.fixture
    def mock_component(self): pass
        """Create a mock component for testing."""
        component = Mock(spec=GenerationComponent)
        component.name = "test_component"
        component.component_type = ComponentType.CUSTOM
        return component

    def test_register_component(self, registry, mock_component): pass
        """Test registering a component."""
        registry.register(mock_component)
        assert registry.get("test_component") == mock_component
        assert "test_component" in registry.get_names()

    def test_register_duplicate_component(self, registry, mock_component): pass
        """Test registering a component with the same name twice."""
        registry.register(mock_component)
        
        # Create another component with the same name
        duplicate_component = Mock(spec=GenerationComponent)
        duplicate_component.name = "test_component"
        duplicate_component.component_type = ComponentType.CUSTOM
        
        # Should overwrite the first one
        registry.register(duplicate_component)
        assert registry.get("test_component") == duplicate_component

    def test_unregister_component(self, registry, mock_component): pass
        """Test unregistering a component."""
        registry.register(mock_component)
        result = registry.unregister("test_component")
        assert result == mock_component
        assert registry.get("test_component") is None

    def test_unregister_nonexistent_component(self, registry): pass
        """Test unregistering a component that doesn't exist."""
        result = registry.unregister("nonexistent")
        assert result is None

    def test_get_component(self, registry, mock_component): pass
        """Test getting a component by name."""
        registry.register(mock_component)
        result = registry.get("test_component")
        assert result == mock_component

    def test_get_nonexistent_component(self, registry): pass
        """Test getting a component that doesn't exist."""
        result = registry.get("nonexistent")
        assert result is None

    def test_get_components_by_type(self, registry): pass
        """Test getting components by type."""
        # Create components of different types
        biome_component = Mock(spec=GenerationComponent)
        biome_component.name = "biome_component"
        biome_component.component_type = ComponentType.BIOME
        
        elevation_component = Mock(spec=GenerationComponent)
        elevation_component.name = "elevation_component"
        elevation_component.component_type = ComponentType.ELEVATION
        
        registry.register(biome_component)
        registry.register(elevation_component)
        
        biome_components = registry.get_by_type(ComponentType.BIOME)
        assert len(biome_components) == 1
        assert biome_components[0] == biome_component
        
        elevation_components = registry.get_by_type(ComponentType.ELEVATION)
        assert len(elevation_components) == 1
        assert elevation_components[0] == elevation_component

    def test_has_component(self, registry, mock_component): pass
        """Test checking if a component exists."""
        # Use get() method to check existence since there's no has() method
        assert registry.get("test_component") is None
        registry.register(mock_component)
        assert registry.get("test_component") is not None

    def test_get_all_components(self, registry, mock_component): pass
        """Test getting all components."""
        registry.register(mock_component)
        all_components = registry.get_all()
        assert len(all_components) == 1
        assert all_components[0] == mock_component


class TestGenerationComponent: pass
    """Test the GenerationComponent base class."""

    @pytest.fixture
    def mock_component(self): pass
        """Create a mock component for testing."""
        # Create a concrete implementation for testing
        class TestComponent(GenerationComponent): pass
            def execute(self, context): pass
                return ComponentResult(success=True, data={"test": "data"})
        
        return TestComponent("test_component", ComponentType.CUSTOM)

    def test_component_attributes(self, mock_component): pass
        """Test component attributes."""
        assert mock_component.name == "test_component"
        assert mock_component.component_type == ComponentType.CUSTOM
        assert mock_component.priority == ComponentPriority.NORMAL
        assert len(mock_component.dependencies) == 0

    def test_component_execution(self, mock_component): pass
        """Test component execution."""
        # Create a mock context
        context = Mock(spec=WorldGenerationContext)
        
        result = mock_component.execute(context)
        assert isinstance(result, ComponentResult)
        assert result.success is True
        assert result.data == {"test": "data"}


class TestComponentResult: pass
    """Test the ComponentResult class."""

    def test_successful_result(self): pass
        """Test creating a successful result."""
        result = ComponentResult(success=True, data={"test": "data"})
        assert result.success is True
        assert result.data == {"test": "data"}
        assert result.error_message == ""  # Default empty string, not None
        assert result.execution_time == 0.0
        assert result.metadata == {}

    def test_failed_result(self): pass
        """Test creating a failed result."""
        result = ComponentResult(success=False, error_message="Something went wrong")
        assert result.success is False
        assert result.data is None  # Default None for failed results
        assert result.error_message == "Something went wrong"
        assert result.execution_time == 0.0
        assert result.metadata == {}

    def test_result_with_execution_time(self): pass
        """Test creating a result with execution time."""
        result = ComponentResult(success=True, execution_time=1.5)
        assert result.execution_time == 1.5


class TestWorldGenerationContext: pass
    """Test the WorldGenerationContext class."""

    @pytest.fixture
    def test_seed(self): pass
        """Create a test world seed."""
        return WorldSeed(
            name="test_world",
            version="1.0",
            metadata={"author": "test", "description": "test world"}
        )

    @pytest.fixture
    def test_config(self): pass
        """Create a test pipeline config."""
        return PipelineConfig()

    @pytest.fixture
    def test_generation_context(self, test_seed, test_config): pass
        """Create a test generation context."""
        return WorldGenerationContext(test_seed, test_config)

    def test_context_initialization(self, test_generation_context, test_seed, test_config): pass
        """Test context initialization."""
        assert test_generation_context.seed_data == test_seed
        assert test_generation_context.config == test_config
        assert isinstance(test_generation_context.world, World)
        assert test_generation_context.world.name == "test_world"
        assert len(test_generation_context.component_results) == 0
        assert len(test_generation_context.execution_log) == 0

    def test_log_execution(self, test_generation_context): pass
        """Test logging component execution."""
        result = ComponentResult(success=True, data={"test": "data"})
        test_generation_context.log_execution("test_component", result)
        
        assert test_generation_context.get_result("test_component") == result
        assert len(test_generation_context.execution_log) == 1
        
        log_entry = test_generation_context.execution_log[0]
        assert log_entry["component"] == "test_component"
        assert log_entry["success"] is True

    def test_get_component_result(self, test_generation_context): pass
        """Test getting component results."""
        result = ComponentResult(success=True, data={"test": "data"})
        test_generation_context.log_execution("test_component", result)
        
        retrieved_result = test_generation_context.get_result("test_component")
        assert retrieved_result == result

    def test_get_nonexistent_component_result(self, test_generation_context): pass
        """Test getting a result for a component that hasn't been executed."""
        result = test_generation_context.get_result("nonexistent_component")
        assert result is None

    def test_has_result(self, test_generation_context): pass
        """Test checking if a component has been executed."""
        assert not test_generation_context.has_result("test_component")
        
        result = ComponentResult(success=True, data={"test": "data"})
        test_generation_context.log_execution("test_component", result)
        
        assert test_generation_context.has_result("test_component")

    def test_cache_operations(self, test_generation_context): pass
        """Test caching operations."""
        # Test caching data
        test_generation_context.cache_data("test_key", "test_value")
        assert test_generation_context.has_cached_data("test_key")
        assert test_generation_context.get_cached_data("test_key") == "test_value"
        
        # Test getting non-existent cached data
        assert not test_generation_context.has_cached_data("nonexistent_key")
        assert test_generation_context.get_cached_data("nonexistent_key") is None
        assert test_generation_context.get_cached_data("nonexistent_key", "default") == "default"

    def test_get_data_from_component(self, test_generation_context): pass
        """Test getting data from a component result."""
        result1 = ComponentResult(success=True, data={"key1": "value1"})
        result2 = ComponentResult(success=True, data={"key2": "value2"})
        
        test_generation_context.log_execution("component1", result1)
        test_generation_context.log_execution("component2", result2)
        
        # Get data from component1
        data1 = test_generation_context.get_result("component1").data
        assert data1 == {"key1": "value1"}
        
        # Get data from component2
        data2 = test_generation_context.get_result("component2").data
        assert data2 == {"key2": "value2"}

    def test_world_data_access(self, test_generation_context): pass
        """Test accessing world data."""
        # The world object should be accessible
        world = test_generation_context.world
        assert isinstance(world, World)
        assert world.name == "test_world"
        
        # We can modify world attributes directly using valid fields
        world.custom_data = {"test_key": "test_value"}
        assert world.custom_data["test_key"] == "test_value"

    def test_get_world_data(self, test_generation_context): pass
        """Test getting world data."""
        # Access the world object directly
        world = test_generation_context.world
        assert world.name == "test_world"
        
        # Modify world data using valid fields
        world.custom_data = {"test_key": "test_value"}
        assert world.custom_data["test_key"] == "test_value"
