from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from typing import Type

# Import EventBase and EventDispatcher with fallbacks
try: pass
    from backend.systems.events import EventBase, EventDispatcher
except ImportError: pass
    # Fallback for tests or when events system isn't available
    class EventBase: pass
        def __init__(self, **data): pass
            for key, value in data.items(): pass
                setattr(self, key, value)
    
    class EventDispatcher: pass
        @classmethod
        def get_instance(cls): pass
            return cls()
        
        def dispatch(self, event): pass
            pass
        
        def publish(self, event): pass
            pass
        
        def emit(self, event): pass
            pass

"""
Tests for world generation API.

This module contains tests for the high-level world generation API functions.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, MagicMock, patch, mock_open
import json

from backend.systems.world_generation.api import (
    generate_world,
    generate_world_async,
    generate_custom_world,
    generate_custom_world_async,
    load_world,
    save_world,
    subscribe_to_world_events,
    get_world_info,
    DEFAULT_SIZES,
    DEFAULT_SETTINGS,
)
from backend.systems.world_generation.events import WorldGenerationEventType


class TestWorldGenerationAPI: pass
    """Tests for world generation API functions."""

    @pytest.fixture
    def mock_world_generator(self): pass
        """Create a mock WorldGenerator."""
        with patch('backend.systems.world_generation.api.WorldGenerator') as mock_gen: pass
            instance = Mock()
            instance.generate_world.return_value = {
                "name": "test_world",
                "seed": 12345,
                "regions": {"0_0": {"size": 512, "coordinates": {"x": 0, "y": 0}}},
                "metadata": {"generated_at": "2023-01-01T00:00:00Z"}
            }
            instance.generate_world_async.return_value = asyncio.Future()
            instance.generate_world_async.return_value.set_result({
                "name": "test_world_async",
                "seed": 12345,
                "regions": {"0_0": {"size": 512, "coordinates": {"x": 0, "y": 0}}},
                "metadata": {"generated_at": "2023-01-01T00:00:00Z"}
            })
            mock_gen.get_instance.return_value = instance
            yield instance

    def test_generate_world_default(self, mock_world_generator): pass
        """Test generating a world with default settings."""
        result = generate_world(seed=12345)
        
        # Verify the result
        assert result["name"] == "test_world"
        assert result["seed"] == 12345
        assert "regions" in result
        
        # Verify WorldGenerator was called
        mock_world_generator.generate_world.assert_called_once()
        call_args = mock_world_generator.generate_world.call_args
        assert call_args[1]["seed"] == 12345

    def test_generate_world_with_string_size(self, mock_world_generator): pass
        """Test generating a world with string size."""
        result = generate_world(seed=12345, size="large")
        
        # Verify the result
        assert result["name"] == "test_world"
        mock_world_generator.generate_world.assert_called_once()

    def test_generate_world_with_integer_size(self, mock_world_generator): pass
        """Test generating a world with integer size."""
        result = generate_world(seed=12345, size=400)
        
        # Verify the result
        assert result["name"] == "test_world"
        mock_world_generator.generate_world.assert_called_once()

    def test_generate_world_invalid_size(self, mock_world_generator): pass
        """Test generating a world with invalid string size."""
        with pytest.raises(ValueError, match="Invalid size"): pass
            generate_world(size="invalid")

    def test_generate_world_no_seed(self, mock_world_generator): pass
        """Test generating a world without providing a seed."""
        with patch('backend.systems.world_generation.api.time.time', return_value=123456): pass
            result = generate_world()
            
            # Verify a seed was generated
            mock_world_generator.generate_world.assert_called_once()
            call_args = mock_world_generator.generate_world.call_args
            assert call_args[1]["seed"] == 123456

    def test_generate_world_multiple_regions(self, mock_world_generator): pass
        """Test generating a world with multiple regions."""
        result = generate_world(seed=12345, regions=3)
        
        # Verify the result
        assert result["name"] == "test_world"
        mock_world_generator.generate_world.assert_called_once()
        
        # Check that seed_data contains multiple regions
        call_args = mock_world_generator.generate_world.call_args
        seed_data = call_args[1]["seed_data"]
        assert len(seed_data["regions"]) == 3

    def test_generate_world_custom_name(self, mock_world_generator): pass
        """Test generating a world with custom name."""
        result = generate_world(seed=12345, name="My Custom World")
        
        # Verify the result
        assert result["name"] == "test_world"
        mock_world_generator.generate_world.assert_called_once()
        
        # Check that seed_data contains the custom name
        call_args = mock_world_generator.generate_world.call_args
        seed_data = call_args[1]["seed_data"]
        assert seed_data["name"] == "My Custom World"

    @pytest.mark.asyncio
    async def test_generate_world_async(self, mock_world_generator): pass
        """Test generating a world asynchronously."""
        result = await generate_world_async(seed=12345)
        
        # Verify the result
        assert result["name"] == "test_world_async"
        assert result["seed"] == 12345

    def test_generate_custom_world_default(self, mock_world_generator): pass
        """Test generating a custom world with default settings."""
        result = generate_custom_world(seed=12345)
        
        # Verify the result
        assert result["name"] == "test_world"
        mock_world_generator.generate_world.assert_called_once()

    def test_generate_custom_world_with_settings(self, mock_world_generator): pass
        """Test generating a custom world with custom settings."""
        elevation_settings = {"mountain_density": 0.8}
        biome_settings = {"use_temperature": False}
        
        result = generate_custom_world(
            seed=12345,
            elevation_settings=elevation_settings,
            biome_settings=biome_settings
        )
        
        # Verify the result
        assert result["name"] == "test_world"
        mock_world_generator.generate_world.assert_called_once()
        
        # Check that custom settings were merged
        call_args = mock_world_generator.generate_world.call_args
        seed_data = call_args[1]["seed_data"]
        assert seed_data["elevation_settings"]["mountain_density"] == 0.8
        assert seed_data["biome_settings"]["use_temperature"] is False

    @pytest.mark.asyncio
    async def test_generate_custom_world_async(self, mock_world_generator): pass
        """Test generating a custom world asynchronously."""
        result = await generate_custom_world_async(seed=12345)
        
        # Verify the result
        assert result["name"] == "test_world_async"

    def test_load_world_success(self): pass
        """Test loading a world from file successfully."""
        world_data = {
            "name": "loaded_world",
            "seed": 54321,
            "regions": {}
        }
        
        with patch('backend.systems.world_generation.api.WorldGenerator') as mock_gen: pass
            instance = Mock()
            instance.load_world.return_value = world_data
            mock_gen.get_instance.return_value = instance
            
            result = load_world("test_world.json")
            
            assert result == world_data
            instance.load_world.assert_called_once_with("test_world.json")

    def test_load_world_failure(self): pass
        """Test loading a world when file doesn't exist."""
        with patch('backend.systems.world_generation.api.WorldGenerator') as mock_gen: pass
            instance = Mock()
            instance.load_world.side_effect = FileNotFoundError("File not found")
            mock_gen.get_instance.return_value = instance
            
            with pytest.raises(FileNotFoundError): pass
                load_world("nonexistent.json")

    def test_save_world_success(self): pass
        """Test saving a world to file successfully."""
        world_data = {
            "name": "test_world",
            "seed": 12345,
            "regions": {}
        }
        
        with patch('backend.systems.world_generation.api.WorldGenerator') as mock_gen: pass
            instance = Mock()
            instance.save_world.return_value = True
            mock_gen.get_instance.return_value = instance
            
            result = save_world(world_data, "test_world.json")
            
            assert result is True
            instance.save_world.assert_called_once_with("test_world.json", world_data)

    def test_save_world_failure(self): pass
        """Test saving a world when write fails."""
        world_data = {
            "name": "test_world",
            "seed": 12345,
            "regions": {}
        }
        
        with patch('backend.systems.world_generation.api.WorldGenerator') as mock_gen: pass
            instance = Mock()
            instance.save_world.side_effect = IOError("Write failed")
            mock_gen.get_instance.return_value = instance
            
            with pytest.raises(IOError): pass
                save_world(world_data, "test_world.json")

    def test_subscribe_to_world_events(self): pass
        """Test subscribing to world generation events."""
        mock_handler = Mock()
        
        with patch('backend.systems.world_generation.api.EventDispatcher') as mock_dispatcher: pass
            instance = Mock()
            mock_dispatcher.get_instance.return_value = instance
            
            # Use string event type to avoid enum conversion issues
            subscribe_to_world_events("generation_started", mock_handler)
            
            # The function should subscribe with the event class, not the string
            from backend.systems.world_generation.events import GenerationStartedEvent
            instance.subscribe.assert_called_once_with(GenerationStartedEvent, mock_handler)

    def test_subscribe_to_world_events_string(self): pass
        """Test subscribing to world generation events with string event type."""
        mock_handler = Mock()
        
        with patch('backend.systems.world_generation.api.EventDispatcher') as mock_dispatcher: pass
            instance = Mock()
            mock_dispatcher.get_instance.return_value = instance
            
            subscribe_to_world_events("generation_completed", mock_handler)
            
            # The function should subscribe with the event class, not the string
            from backend.systems.world_generation.events import GenerationCompletedEvent
            instance.subscribe.assert_called_once_with(GenerationCompletedEvent, mock_handler)

    def test_get_world_info_basic(self): pass
        """Test getting basic world information."""
        world_data = {
            "regions": {
                "0_0": {"tiles": {"0,0": {"biome": "forest"}, "0,1": {"biome": "plains"}}},
                "1_0": {"tiles": {"1,0": {"biome": "mountain"}, "1,1": {"biome": "ocean"}}}
            },
            "metadata": {
                "name": "test_world",
                "seed": 12345,
                "version": "1.0.0",
                "author": "test_author",
                "creation_date": "2023-01-01T00:00:00Z"
            }
        }
        
        info = get_world_info(world_data)
        
        assert info["name"] == "test_world"
        assert info["seed"] == 12345
        assert info["regions"] == 2
        assert info["total_tiles"] == 4
        assert info["land_tiles"] == 3  # forest, plains, mountain
        assert info["water_tiles"] == 1  # ocean
        assert info["version"] == "1.0.0"
        assert info["author"] == "test_author"

    def test_get_world_info_missing_fields(self): pass
        """Test getting world info with missing optional fields."""
        world_data = {
            "regions": {}
        }
        
        info = get_world_info(world_data)
        
        assert info["name"] == "Unknown World"
        assert info["seed"] == 0
        assert info["regions"] == 0
        assert info["total_tiles"] == 0

    def test_default_sizes_constant(self): pass
        """Test that DEFAULT_SIZES contains expected values."""
        assert "tiny" in DEFAULT_SIZES
        assert "small" in DEFAULT_SIZES
        assert "medium" in DEFAULT_SIZES
        assert "large" in DEFAULT_SIZES
        assert "huge" in DEFAULT_SIZES
        
        # Verify sizes are reasonable
        assert DEFAULT_SIZES["tiny"] < DEFAULT_SIZES["small"]
        assert DEFAULT_SIZES["small"] < DEFAULT_SIZES["medium"]
        assert DEFAULT_SIZES["medium"] < DEFAULT_SIZES["large"]
        assert DEFAULT_SIZES["large"] < DEFAULT_SIZES["huge"]

    def test_default_settings_constant(self): pass
        """Test that DEFAULT_SETTINGS contains expected sections."""
        assert "elevation_settings" in DEFAULT_SETTINGS
        assert "biome_settings" in DEFAULT_SETTINGS
        assert "river_settings" in DEFAULT_SETTINGS
        assert "resource_settings" in DEFAULT_SETTINGS
        assert "climate_settings" in DEFAULT_SETTINGS
        
        # Verify some key settings exist
        assert "mountain_density" in DEFAULT_SETTINGS["elevation_settings"]
        assert "use_temperature" in DEFAULT_SETTINGS["biome_settings"]
        assert "num_rivers" in DEFAULT_SETTINGS["river_settings"]


class TestAPIIntegration: pass
    """Integration tests for API functions."""

    def test_api_workflow(self): pass
        """Test a complete API workflow."""
        with patch('backend.systems.world_generation.api.WorldGenerator') as mock_gen: pass
            # Setup mock
            instance = Mock()
            world_data = {
                "name": "workflow_world",
                "seed": 12345,
                "regions": {"0_0": {"size": 256}},
                "metadata": {"version": "1.0.0"}
            }
            instance.generate_world.return_value = world_data
            mock_gen.get_instance.return_value = instance
            
            # Generate world
            result = generate_world(seed=12345, size="small", name="workflow_world")
            assert result["name"] == "workflow_world"
            
                         # Get world info - need to structure the data correctly for get_world_info
            result_with_metadata = {
                "regions": result.get("regions", {}),
                "metadata": {
                    "name": result["name"],
                    "seed": result["seed"],
                    "version": result.get("metadata", {}).get("version", "1.0.0")
                }
            }
            info = get_world_info(result_with_metadata)
            assert info["name"] == "workflow_world"
            assert info["seed"] == 12345
            
                         # Test save/load workflow
            with patch('backend.systems.world_generation.api.WorldGenerator') as mock_gen2: pass
                instance2 = Mock()
                instance2.save_world.return_value = True
                instance2.load_world.return_value = world_data
                mock_gen2.get_instance.return_value = instance2
                
                # Save world
                save_result = save_world(result, "workflow_world.json")
                assert save_result is True
                
                # Load world
                loaded_world = load_world("workflow_world.json")
                assert loaded_world["name"] == "workflow_world"
